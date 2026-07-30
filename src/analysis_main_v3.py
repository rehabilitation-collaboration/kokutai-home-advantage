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
    if year <= 1977:
        return "early"
    if year <= 2015:
        return "golden"
    return "shock"


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
) -> dict:
    """帰無 = k/47 vs 観測 host top-k 率の exact binomial test + Wilson 95%CI

    Args:
        threshold: 1 / 3 / 8
        cup: "tennou" / "kougou" / "both"
        era: "early" / "golden" / "shock" / "all"
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
    null_rate = threshold / 47

    if n == 0:
        return {
            "threshold": threshold, "cup": cup, "era": era,
            "n": 0, "n_success": 0,
            "observed_rate": float("nan"), "null_rate": null_rate,
            "excess": float("nan"),
            "p_value_greater": float("nan"), "p_value_two_sided": float("nan"),
            "ci_wilson_low": float("nan"), "ci_wilson_high": float("nan"),
        }

    bt_g = st.binomtest(n_success, n, p=null_rate, alternative="greater")
    bt_t = st.binomtest(n_success, n, p=null_rate, alternative="two-sided")
    ci = bt_g.proportion_ci(confidence_level=0.95, method="wilson")

    return {
        "threshold": threshold,
        "cup": cup,
        "era": era,
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

    p_value = float(np.mean(null_counts >= obs_count))

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


def chi_square_era_comparison(
    df: pd.DataFrame,
    threshold: int,
    cup: CupMode = "tennou",
) -> dict:
    """3 期間 (early/golden/shock) × top-k 率の χ² + pairwise Fisher exact"""
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
        "pairwise_fisher": pairwise,
    }


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
