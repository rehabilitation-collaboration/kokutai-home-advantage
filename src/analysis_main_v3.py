"""v3 M2 主分析: 実質 77 大会 host 順位 top1/3/8 真偽検定

対象: data/host_rank_panel.parquet (150 行 = 75 大会 × 2 杯・第 3-79 回・第 75/76 中止除外)

比較群設計 (handoff 申し送り ①):
- (A) 帰無 k/47 一標本比率検定 (scipy.stats.binomtest exact + Wilson 95%CI)
- (C) permutation inference (host_pref を 47 県からランダム再割当・build_ranking_panel 使用)

FE 設計 (handoff 申し送り ②):
- pref FE / year FE 落とし (東京 6 回・他 2-4 回で完全分離リスク)
- era dummy + cup dummy のみ

時代分解 (handoff 申し送り ③・Background 節):
- early: 第 3-32 回 (1948-1977)
- golden: 第 33-70 回 (1978-2015・host 優勝率 97.30%)
- shock: 第 71-79 回 (2016-2025・敗北 6 ショック期 37.50%)
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import scipy.stats as st
from statsmodels.miscmodels.ordinal_model import OrderedModel

RANK_OUTSIDE = 9
PANEL_PATH = Path(__file__).resolve().parent.parent / "data" / "host_rank_panel.parquet"

Cup = Literal["tennou", "kougou"]
CupMode = Literal["tennou", "kougou", "both", "pooled"]
Era = Literal["early", "golden", "shock", "all"]

ERA_BOUNDARIES = {
    "early": (1948, 1977),
    "golden": (1978, 2015),
    "shock": (2016, 2025),
}
ERA_ORDER = ["early", "golden", "shock"]


def _classify_era(year: int) -> str:
    for era in ERA_ORDER:
        lo, hi = ERA_BOUNDARIES[era]
        if lo <= year <= hi:
            return era
    return ERA_ORDER[-1]


def load_v3_panel(parquet_path: Path | str | None = None) -> pd.DataFrame:
    """host_rank_panel.parquet を読み込み + era 列 + rank_ordinal 列を追加

    era: early (1948-1977) / golden (1978-2015) / shock (2016-2025)
    rank_ordinal: host_rank (1-8) or 9 (top-8 圏外)
    """
    path = Path(parquet_path) if parquet_path else PANEL_PATH
    df = pd.read_parquet(path)
    df["era"] = df["year"].map(_classify_era)
    df["rank_ordinal"] = df["host_rank"].fillna(RANK_OUTSIDE).astype(int)
    return df.reset_index(drop=True)


def descriptive_by_era(df: pd.DataFrame) -> pd.DataFrame:
    """era × cup × threshold の記述統計 (n / count / rate)"""
    rows: list[dict] = []
    for era in ERA_ORDER + ["all"]:
        for cup in ["tennou", "kougou"]:
            if era == "all":
                sub = df[df["cup"] == cup]
            else:
                sub = df[(df["era"] == era) & (df["cup"] == cup)]
            n = len(sub)
            rows.append({
                "era": era,
                "cup": cup,
                "n_kai": n,
                "n_top1": int(sub["top1_flag"].sum()),
                "n_top3": int(sub["top3_flag"].sum()),
                "n_top8": int(sub["top8_flag"].sum()),
                "rate_top1": float(sub["top1_flag"].mean()) if n else float("nan"),
                "rate_top3": float(sub["top3_flag"].mean()) if n else float("nan"),
                "rate_top8": float(sub["top8_flag"].mean()) if n else float("nan"),
            })
    return pd.DataFrame(rows)


def one_sample_proportion_test(
    df: pd.DataFrame,
    threshold: int,
    cup: CupMode = "both",
    era: Era = "all",
    n_states: int = 47,
) -> dict:
    """帰無 = k/n_states vs 観測 host top-k 率の exact binomial test + Wilson 95%CI

    Args:
        threshold: 1 / 3 / 8
        cup: "tennou" / "kougou" / "both"
        era: "early" / "golden" / "shock" / "all"
        n_states: 帰無分母 (default 47)。1972 沖縄復帰前 (第 3-26 回・1948-1971)
            の 24 大会は 46 県参加のため、sensitivity check として n_states=46 で
            early era を再計算するのが M3-T1 用途。
    """
    sub = df.copy()
    if cup != "both":
        sub = sub[sub["cup"] == cup]
    if era != "all":
        sub = sub[sub["era"] == era]

    n = len(sub)
    col = f"top{threshold}_flag"
    n_success = int(sub[col].sum())
    observed_rate = n_success / n if n else float("nan")
    null_rate = threshold / n_states

    if n == 0:
        return {
            "threshold": threshold, "cup": cup, "era": era, "n_states": n_states,
            "n": 0, "n_success": 0,
            "observed_rate": float("nan"), "null_rate": null_rate,
            "excess": float("nan"),
            "p_value_greater": float("nan"), "p_value_two_sided": float("nan"),
            "ci_wilson_low": float("nan"), "ci_wilson_high": float("nan"),
        }

    bt_g = st.binomtest(n_success, n, p=null_rate, alternative="greater")
    bt_t = st.binomtest(n_success, n, p=null_rate, alternative="two-sided")
    # Wilson 95%CI は両側の bt_t から取る (片側 bt_g だと上限が 1.0 固定になり
    # CI として使えない・code review P1)
    ci = bt_t.proportion_ci(confidence_level=0.95, method="wilson")

    return {
        "threshold": threshold,
        "cup": cup,
        "era": era,
        "n_states": n_states,
        "n": n,
        "n_success": n_success,
        "observed_rate": observed_rate,
        "null_rate": null_rate,
        "excess": observed_rate - null_rate,
        "p_value_greater": float(bt_g.pvalue),
        "p_value_two_sided": float(bt_t.pvalue),
        "ci_wilson_low": float(ci.low),
        "ci_wilson_high": float(ci.high),
    }


def permutation_test(
    threshold: int,
    cup: Cup,
    n_perm: int = 10_000,
    seed: int = 0,
) -> dict:
    """host_pref を各 (kai, cup) で 47 県からランダム再割当 → top-k 率の帰無分布 vs 観測

    build_ranking_panel() の 7332 行から (kai, cup) 内の top-k 県セットを抽出。
    n_perm 回、47 県から fake host をランダム選択して null 分布を作る。

    p 値は Monte Carlo 下限補正 `(count + 1) / (n_perm + 1)` を使う (真の 0 は
    permutation 検定では原理的に取れないため・code review P3a)。

    共催県の扱い: build_ranking_panel の is_host は複数県共催の全共催県=True。
    ここでは「共催県のいずれかが top-k に入れば成功」で観測を集計する。
    一方 one_sample_proportion_test の入力 host_rank_panel は
    build_host_rank_panel で共催県を主催県 (host_prefs[0]) 1 つに正規化済み。
    現状の実データ (第 3-79 回) に含まれる共催回は 3 大会 (第 7 回=福島他 3 県 /
    第 8 回=愛媛他 4 県 / 第 48 回=香川・徳島)。第 48 回は primary host 香川が
    tennou/kougou 両方で top-1 のため両定義とも count に含める点で一致し、第
    7/8 回も現状の観測範囲で両定義が同じ obs_count を出す。将来データ変更時に
    静かに乖離する可能性あり (code review P3b)。
    """
    from src.panel_builder import build_ranking_panel

    panel = build_ranking_panel()
    panel = panel[
        (panel["cup"] == cup)
        & (~panel["is_special"])
        & (~panel["cancelled"])
    ]

    kai_top_k_sets: list[set[int]] = []
    obs_count = 0
    for (_kai_label, _cup_v), grp in panel.groupby(["kai_label", "cup"]):
        host_rows = grp[grp["is_host"]]
        if len(host_rows) == 0:
            continue
        # host_rank_panel v3 母集団と合わせるため kai_num=1,2 (panel_included=False)
        # は build_ranking_panel の cancelled/panel_included でフィルタされていない可能性あり。
        # → build_ranking_panel は panel_included を見ず nagano 全行を展開している。
        # nagano には第 1-2 回データが無いのでここは自然に除外される。
        top_k_prefs = set(
            grp[grp["rank"].notna() & (grp["rank"] <= threshold)]["pref_code"].tolist()
        )
        host_ranks = host_rows["rank"].dropna().tolist()
        obs = int(any(r <= threshold for r in host_ranks))
        obs_count += obs
        kai_top_k_sets.append(top_k_prefs)

    n_events = len(kai_top_k_sets)
    obs_rate = obs_count / n_events if n_events else float("nan")

    # Vectorized permutation
    top_k_matrix = np.zeros((48, n_events), dtype=bool)  # index 0 unused (pref_code 1-47)
    for j, s in enumerate(kai_top_k_sets):
        for p in s:
            top_k_matrix[p, j] = True

    rng = np.random.default_rng(seed)
    random_prefs = rng.integers(low=1, high=48, size=(n_perm, n_events))
    hits = top_k_matrix[random_prefs, np.arange(n_events)]
    null_counts = hits.sum(axis=1)
    null_rates = null_counts / n_events

    # Monte Carlo 下限補正 p 値 (Phipson & Smyth 2010)
    extreme = int(np.sum(null_counts >= obs_count))
    p_value = (extreme + 1) / (n_perm + 1)

    return {
        "threshold": threshold,
        "cup": cup,
        "n_events": n_events,
        "obs_count": obs_count,
        "obs_rate": obs_rate,
        "null_mean": float(null_rates.mean()),
        "null_std": float(null_rates.std()),
        "null_p05": float(np.percentile(null_rates, 5)),
        "null_p95": float(np.percentile(null_rates, 95)),
        "p_value_permutation": p_value,
        "n_perm": n_perm,
    }


def _mc_permutation_chi2(
    cont_np: np.ndarray,
    n_perm: int = 10_000,
    seed: int = 0,
) -> tuple[float, float]:
    """Conditional Monte Carlo exact test using the Pearson χ² statistic (2×K).

    Terminology note (Phase 7A・GPT round-8): 前 phase では "Fisher-Freeman-Halton exact test
    の近似" と表記したが、FFH の「同等以上に極端」定義は複数流儀ある (log-likelihood 統計量
    or hypergeometric probability 順序 等) ため厳密には別物。本関数は Pearson χ² 統計量を
    使った conditional exact test の Monte Carlo 近似 = "conditional Monte Carlo exact test
    using the Pearson χ² statistic" と呼ぶ方が正確。

    era labels を permutation で shuffle → Pearson χ² 統計量分布 → observed 以上の割合を p 値化.
    marginal totals (row/col sums) は permutation で保存されるので Fisher exact test
    と同じ null (independence given marginals) を持つ. Pearson χ² と違い期待度数
    条件 (≥ 5) を要求しない → shock 期 n=7 の Table 4 主要 test に適合.

    Args:
        cont_np: 2×K contingency table (rows=[False,True], cols=eras)
        n_perm: permutation 回数 (default 10,000)
        seed: RNG seed

    Returns:
        (observed_chi2, mc_p_value): Pearson χ² 統計量 (Yates correction OFF・
        chi2_contingency と同じ定義) と Monte Carlo permutation p 値 (Phipson-Smyth 下限補正).
    """
    row_totals = cont_np.sum(axis=1).astype(int)
    col_totals = cont_np.sum(axis=0).astype(int)
    n_total = int(cont_np.sum())
    K = len(col_totals)

    if n_total == 0 or any(row_totals == 0) or any(col_totals == 0):
        return (float("nan"), float("nan"))

    expected = np.outer(row_totals, col_totals) / n_total
    observed_chi2 = float(np.sum((cont_np - expected) ** 2 / expected))

    row_labels = np.concatenate([
        np.zeros(row_totals[0], dtype=int),
        np.ones(row_totals[1], dtype=int),
    ])
    col_labels_orig = np.concatenate([
        np.full(int(t), i, dtype=int) for i, t in enumerate(col_totals)
    ])

    rng = np.random.default_rng(seed)
    count_ge = 0
    for _ in range(n_perm):
        col_shuffled = rng.permutation(col_labels_orig)
        combined = row_labels * K + col_shuffled
        cont_flat = np.bincount(combined, minlength=2 * K)
        cont_perm = cont_flat.reshape(2, K).astype(float)
        chi2_perm = float(np.sum((cont_perm - expected) ** 2 / expected))
        if chi2_perm >= observed_chi2:
            count_ge += 1

    mc_p = (count_ge + 1) / (n_perm + 1)  # Phipson-Smyth 下限補正
    return (observed_chi2, mc_p)


def _conditional_exact_p_chi2(cont_np: np.ndarray) -> tuple[float, float, int]:
    """Conditional Pearson χ² exact test on 2×K contingency table (full enumeration).

    Phase 7A (GPT round-8 「必須修正 1」応答): 状態数は top-1 でも 124-204 通り程度なので
    10,000 iter の Monte Carlo より完全列挙 exact p 値の方が簡単かつ精密。

    全 marginal 保存 tables を列挙 → 各 table の Pearson χ² を計算 → observed 以上の
    hypergeometric 確率の合計 = exact p 値。Phipson-Smyth 下限補正不要 (真の tail 出せる)。

    Args:
        cont_np: 2×K contingency table (rows=[False,True], cols=eras)

    Returns:
        (observed_chi2, exact_p_value, n_tables_enumerated)
    """
    from itertools import product
    from math import lgamma, exp

    row_totals = cont_np.sum(axis=1).astype(int)
    col_totals = cont_np.sum(axis=0).astype(int)
    n_total = int(cont_np.sum())
    K = len(col_totals)

    if n_total == 0 or any(row_totals == 0) or any(col_totals == 0):
        return (float("nan"), float("nan"), 0)

    expected = np.outer(row_totals, col_totals) / n_total
    observed_chi2 = float(np.sum((cont_np - expected) ** 2 / expected))

    r0 = int(row_totals[0])
    r1 = int(row_totals[1])

    # 2×K の 1 行目 (top 行) の各 cell (c0, c1, ..., c_{K-1}) を enumerate:
    # 各 col j で count[0,j] ∈ [max(0, col_j - r1), min(col_j, r0)]
    ranges = [
        range(max(0, int(col_totals[j]) - r1), min(int(col_totals[j]), r0) + 1)
        for j in range(K)
    ]

    # log(multivariate hypergeometric): 定数部分 = lgamma(r0+1) + lgamma(r1+1) + Σ lgamma(c_j+1) − lgamma(n+1)
    log_const = (
        lgamma(r0 + 1) + lgamma(r1 + 1)
        + sum(lgamma(int(c) + 1) for c in col_totals)
        - lgamma(n_total + 1)
    )

    p_exact = 0.0
    p_total = 0.0
    n_tables = 0
    for combo in product(*ranges):
        if sum(combo) != r0:
            continue
        n_tables += 1
        top = np.asarray(combo, dtype=float)
        bot = col_totals.astype(float) - top
        table = np.vstack([top, bot])
        chi2 = float(np.sum((table - expected) ** 2 / expected))

        log_denom = (
            sum(lgamma(int(x) + 1) for x in top)
            + sum(lgamma(int(x) + 1) for x in bot)
        )
        prob = exp(log_const - log_denom)
        p_total += prob
        if chi2 >= observed_chi2 - 1e-9:
            p_exact += prob

    # p_total should be ≈ 1.0 (sanity check・normalize by p_total to guard against
    # floating-point drift in extremely large tables)
    if p_total > 0:
        p_exact = p_exact / p_total

    return (observed_chi2, p_exact, n_tables)


def chi_square_era_comparison(
    df: pd.DataFrame,
    threshold: int,
    cup: CupMode = "tennou",
    n_perm: int = 10_000,
    seed: int = 0,
) -> dict:
    """3 期間 (early/golden/shock) × top-k 率の χ² + pairwise Fisher exact
    + Monte Carlo permutation p (Fisher-Freeman-Halton 近似)

    GPT round-7 major #5 応答 (Phase 6A): shock 期 n=7 で期待度数不足
    (emperor's 期待非成功 ~1.68・empress's 期待成功 ~4.39・期待非成功 ~2.61)
    → Pearson χ² 漸近近似条件違反。Monte Carlo permutation p (Fisher-Freeman-Halton
    exact の approximation) を追加し、これを primary global test とする。
    Pearson χ² は sensitivity として保持。
    """
    sub = df if cup == "both" else df[df["cup"] == cup]
    col = f"top{threshold}_flag"

    # Contingency table: rows=[False,True]・cols=[early,golden,shock]
    cont = pd.crosstab(sub[col], sub["era"])
    for era in ERA_ORDER:
        if era not in cont.columns:
            cont[era] = 0
    for flag in [False, True]:
        if flag not in cont.index:
            cont.loc[flag] = 0
    cont = cont.reindex(index=[False, True], columns=ERA_ORDER, fill_value=0)

    chi2, chi2_p, chi2_dof, _ = st.chi2_contingency(cont.values)

    # Monte Carlo permutation (conditional Monte Carlo exact test using Pearson χ² statistic)
    _, mc_p = _mc_permutation_chi2(cont.values, n_perm=n_perm, seed=seed)

    # Phase 7A (GPT round-8 「必須修正 1」): 完全列挙 exact p (2×3 は 100-200 通り程度で列挙可能)
    _, exact_p, n_tables = _conditional_exact_p_chi2(cont.values)

    pairs = [("early", "golden"), ("golden", "shock"), ("early", "shock")]
    pairwise = {}
    for a, b in pairs:
        cont2 = cont[[a, b]].values
        try:
            res = st.fisher_exact(cont2)
            pairwise[f"{a}_vs_{b}"] = float(res.pvalue)
        except Exception:  # noqa: BLE001
            pairwise[f"{a}_vs_{b}"] = float("nan")

    rates = {}
    for era in ERA_ORDER:
        sub_e = sub[sub["era"] == era]
        rates[era] = float(sub_e[col].mean()) if len(sub_e) else float("nan")

    return {
        "threshold": threshold,
        "cup": cup,
        "rates": rates,
        "contingency_table": {c: {str(f): int(cont.at[f, c]) for f in [False, True]} for c in ERA_ORDER},
        "chi2": float(chi2),
        "chi2_dof": int(chi2_dof),
        "chi2_p": float(chi2_p),
        "mc_permutation_p": float(mc_p),
        "n_perm": int(n_perm),
        "exact_p_conditional": float(exact_p),
        "n_tables_enumerated": int(n_tables),
        "pairwise_fisher": pairwise,
    }


def era_boundary_sensitivity_grid(
    df: pd.DataFrame,
    threshold: int = 1,
    cups: tuple[str, ...] = ("tennou", "kougou"),
    golden_starts: tuple[int, ...] = (1975, 1976, 1977, 1978, 1979, 1980),
    shock_starts: tuple[int, ...] = (2014, 2015, 2016, 2017, 2018),
) -> pd.DataFrame:
    """Phase 7A (GPT round-8 「必須修正 4」応答): 時代境界感度分析.

    現行 era boundaries (golden=1978, shock=2016) は outcome-informed で選ばれた
    (原稿でも明記)。ここでは境界を ±3 年ずらした 6 × 5 = 30 grid で per-cup top-k rate
    global test を再実行し、非単調パターンが特定境界に依存してないことを示す。

    Args:
        df: v3 host-rank panel (load_v3_panel の返り値)
        threshold: 1 / 3 / 8 (default 1 = 主 non-monotonicity test)
        cups: 対象 cup tuple
        golden_starts: golden era 開始年の grid
        shock_starts: shock era 開始年の grid

    Returns:
        long-format DataFrame (columns = golden_start, shock_start, cup, early_rate,
        golden_rate, shock_rate, n_early, n_golden, n_shock, exact_p, chi2_p, mc_p)
    """
    from itertools import product as iproduct

    col = f"top{threshold}_flag"
    rows = []
    for gs, ss, cup in iproduct(golden_starts, shock_starts, cups):
        if gs >= ss:
            continue
        sub = df[df["cup"] == cup].copy()
        def _era_of(year: int, gs: int = gs, ss: int = ss) -> str:
            if year < gs:
                return "early"
            if year < ss:
                return "golden"
            return "shock"
        sub["era_var"] = sub["year"].map(_era_of)

        cont = pd.crosstab(sub[col], sub["era_var"])
        for era in ["early", "golden", "shock"]:
            if era not in cont.columns:
                cont[era] = 0
        for flag in [False, True]:
            if flag not in cont.index:
                cont.loc[flag] = 0
        cont = cont.reindex(index=[False, True], columns=["early", "golden", "shock"], fill_value=0)

        n_early = int(cont["early"].sum())
        n_golden = int(cont["golden"].sum())
        n_shock = int(cont["shock"].sum())
        rate_early = (cont.at[True, "early"] / n_early) if n_early else float("nan")
        rate_golden = (cont.at[True, "golden"] / n_golden) if n_golden else float("nan")
        rate_shock = (cont.at[True, "shock"] / n_shock) if n_shock else float("nan")

        try:
            _, chi2_p, _, _ = st.chi2_contingency(cont.values)
            chi2_p = float(chi2_p)
        except ValueError:
            chi2_p = float("nan")

        _, exact_p, _n_tables = _conditional_exact_p_chi2(cont.values)

        rows.append({
            "golden_start": gs,
            "shock_start": ss,
            "cup": cup,
            "threshold": threshold,
            "n_early": n_early,
            "n_golden": n_golden,
            "n_shock": n_shock,
            "rate_early": rate_early,
            "rate_golden": rate_golden,
            "rate_shock": rate_shock,
            "chi2_p_asymptotic": chi2_p,
            "exact_p_conditional": float(exact_p),
        })

    return pd.DataFrame(rows)


def pairwise_fisher_with_holm(
    df: pd.DataFrame,
    threshold: int = 1,
    cups: tuple[str, ...] = ("tennou", "kougou"),
) -> pd.DataFrame:
    """Phase 7A (GPT round-8 「統計上の追加修正 1」応答): pairwise Fisher に Holm 補正.

    Table 4 の 6 pairwise Fisher (2 cups × 3 era-pairs) に Holm-Bonferroni 補正を適用。
    独立して有意な contrast を明示する。
    """
    from statsmodels.stats.multitest import multipletests

    col = f"top{threshold}_flag"
    pairs = [("early", "golden"), ("golden", "shock"), ("early", "shock")]
    raw = []
    labels = []
    for cup in cups:
        sub = df[df["cup"] == cup]
        cont = pd.crosstab(sub[col], sub["era"])
        for era in ERA_ORDER:
            if era not in cont.columns:
                cont[era] = 0
        for flag in [False, True]:
            if flag not in cont.index:
                cont.loc[flag] = 0
        cont = cont.reindex(index=[False, True], columns=ERA_ORDER, fill_value=0)
        for a, b in pairs:
            try:
                res = st.fisher_exact(cont[[a, b]].values)
                p = float(res.pvalue)
            except Exception:  # noqa: BLE001
                p = float("nan")
            raw.append(p)
            labels.append((cup, a, b))

    valid = [i for i, p in enumerate(raw) if not np.isnan(p)]
    valid_p = [raw[i] for i in valid]
    _rej, holm_p, _, _ = multipletests(valid_p, alpha=0.05, method="holm")

    holm_all = [float("nan")] * len(raw)
    for k, i in enumerate(valid):
        holm_all[i] = float(holm_p[k])

    rows = []
    for (cup, a, b), p_raw, p_holm in zip(labels, raw, holm_all):
        rows.append({
            "cup": cup,
            "contrast": f"{a}_vs_{b}",
            "p_fisher_raw": p_raw,
            "p_fisher_holm": p_holm,
        })
    return pd.DataFrame(rows)


def run_ordered_logit_v3(
    df: pd.DataFrame,
    cup_mode: CupMode = "pooled",
) -> dict:
    """rank_ordinal ~ C(era) + C(cup) の順序 logit

    - pooled/both: tennou+kougou stack + cup dummy
    - tennou/kougou: 単一 cup

    era reference = "early" (drop_first で alphabetical 順=early が baseline)。
    cluster SE at host_pref_code。
    """
    if cup_mode in ("pooled", "both"):
        sub = df.copy()
    else:
        sub = df[df["cup"] == cup_mode].copy()

    era_dummies = pd.get_dummies(
        sub["era"], prefix="era", drop_first=True, dtype=float
    )
    X = era_dummies.copy()
    if cup_mode in ("pooled", "both"):
        cup_dummies = pd.get_dummies(
            sub["cup"], prefix="cup", drop_first=True, dtype=float
        )
        X = pd.concat([X, cup_dummies], axis=1)

    y = sub["rank_ordinal"].astype(int).reset_index(drop=True)
    X = X.reset_index(drop=True)

    def _fit(with_cluster: bool):
        model = OrderedModel(y, X, distr="logit")
        kwargs = dict(method="bfgs", disp=False, maxiter=500)
        if with_cluster:
            kwargs["cov_type"] = "cluster"
            kwargs["cov_kwds"] = {"groups": sub["host_pref_code"].reset_index(drop=True)}
        return model.fit(**kwargs)

    try:
        result = _fit(with_cluster=True)
        cluster_used = True
    except Exception:  # noqa: BLE001
        try:
            result = _fit(with_cluster=False)
            cluster_used = False
        except Exception as e2:  # noqa: BLE001
            return {
                "cup_mode": cup_mode,
                "n_obs": len(sub),
                "converged": False,
                "error": f"{type(e2).__name__}: {e2}",
            }

    converged = bool(result.mle_retvals.get("converged", True))
    return {
        "cup_mode": cup_mode,
        "n_obs": len(sub),
        "cluster_used": cluster_used,
        "converged": converged,
        "params": {k: float(v) for k, v in result.params.to_dict().items()},
        "bse": {k: float(v) for k, v in result.bse.to_dict().items()},
        "pvalues": {k: float(v) for k, v in result.pvalues.to_dict().items()},
        "llf": float(result.llf),
    }


def run_all_v3_analyses(seed: int = 0, n_perm: int = 10_000) -> dict:
    """M2 主分析一式 (Phase 3 執筆素材)"""
    df = load_v3_panel()
    out: dict = {
        "panel_shape": list(df.shape),
        "panel_columns": df.columns.tolist(),
    }
    out["descriptive_by_era"] = descriptive_by_era(df).to_dict(orient="records")

    prop_tests = []
    for cup in ["tennou", "kougou", "both"]:
        for era in ["all", "early", "golden", "shock"]:
            for k in [1, 3, 8]:
                prop_tests.append(one_sample_proportion_test(df, k, cup=cup, era=era))  # type: ignore
    out["one_sample_tests"] = prop_tests

    # M3-T1: 46 vs 47 states sensitivity。1972 沖縄復帰前の 24 大会 (第 3-26 回・
    # 1948-1971) は 46 県参加。ここでは early era 30 大会 (第 3-32 回・1948-1977)
    # 全体を一律 n_states=46 で再計算する保守的近似 (worst-case bound) を出す
    # (第 27-32 回 6 大会は史実上 47 県だが、影響の上限を評価する目的)。
    # 数学的方向: null_rate = k/n_states は分母大きいほど小さいため、default 47 は
    # excess を過大評価する方向。46 で再計算すると excess は僅かに小さくなる。
    # M4 執筆 Limitations 節で影響 marginal (差 < 0.005) を示す素材。
    sensitivity_46 = []
    for cup in ["tennou", "kougou", "both"]:
        for k in [1, 3, 8]:
            sensitivity_46.append(
                one_sample_proportion_test(df, k, cup=cup, era="early", n_states=46)  # type: ignore
            )
    out["sensitivity_46_states"] = sensitivity_46

    perm_tests = []
    for cup in ["tennou", "kougou"]:
        for k in [1, 3, 8]:
            perm_tests.append(permutation_test(k, cup=cup, n_perm=n_perm, seed=seed))  # type: ignore
    out["permutation_tests"] = perm_tests

    era_tests = []
    for cup in ["tennou", "kougou", "both"]:
        for k in [1, 3, 8]:
            era_tests.append(chi_square_era_comparison(df, k, cup=cup))  # type: ignore
    out["era_chi_square"] = era_tests

    ol_results = []
    for mode in ["tennou", "kougou", "pooled"]:
        ol_results.append(run_ordered_logit_v3(df, cup_mode=mode))  # type: ignore
    out["ordered_logit"] = ol_results

    return out
