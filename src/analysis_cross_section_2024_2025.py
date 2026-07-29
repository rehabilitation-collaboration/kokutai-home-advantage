"""Phase 2 副次: 2024佐賀 + 2025滋賀 の 2 年断面 Subj × Host 交互作用

本論 novelty core (選択肢A 実装・Deviation #4)。
主モデル (analysis_main.py) は総合順位 Host のみで推定し、Subj_i は 2 年断面専用。
Balmer2003 の主観 vs 客観分離を国体で世界初検証する。

データセット (4 stack):
- 78-tennou (2024 佐賀 host 敗北・総合 2位 2332 点)
- 78-kougou (2024 佐賀)
- 79-tennou (2025 滋賀 host 優勝・総合 1位 2488 点)
- 79-kougou (2025 滋賀)

母集団: 47県 × sport (78/79 で入替あり = クレー射撃 78 のみ・ボクシング 79 のみ) × 2 cup

モデル (main):
- score ~ is_host + is_subjective + is_host × is_subjective + pref FE + sport FE + year FE + cup FE
- clustered SE (pref・7332 obs 相当だがここは ~7000obs で 47 cluster)

Robustness:
- with_semi: subjective/semi_subjective を分離して 2 交互作用項
- log_score: log(score+1) 変換版
- sport_cup interaction: primary spec に sport × cup 交互作用を追加 (GPT round-1 Finding #5
  診断・rank-deficient regime k/G≈2.8 で cluster SE 計算不能・point-estimate-only diagnostic)
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.data_loader import parse_jspo_xls_long_format
from src.sport_classifier import get_category

Category = Literal["objective", "subjective", "semi_subjective"]

# 2 年断面の対象 (kai, cup, host_pref_code は definitions.KOKUTAI_HOSTS で確定)
_CROSS_SECTION_TARGETS: list[tuple[int, str]] = [
    (78, "tennou"), (78, "kougou"),
    (79, "tennou"), (79, "kougou"),
]


@dataclass
class CrossSectionResult:
    name: str
    dv: str
    coef_is_host: float
    se_is_host: float
    p_is_host: float
    coef_interaction: float | None  # is_host × is_subjective
    se_interaction: float | None
    p_interaction: float | None
    n_obs: int
    n_params: int
    n_clusters: int
    r2: float
    result_obj: object


def build_cross_section_frame(
    targets: list[tuple[int, str]] | None = None,
    include_winter: bool = True,
    drop_unclassified: bool = True,
    category_variant: str = "default",
) -> pd.DataFrame:
    """4 dataset を stack + Balmer2003 3 分類を付与

    Args:
        targets: (kai_num, cup) の list。省略時は 78+79 × tennou+kougou の 4件
        include_winter: 冬季3競技を含めるか (default True・Balmer2003 は Winter/Summer 別分析だが本論では pooled)
        drop_unclassified: sport_classifier で分類不能な競技行を除外するか
        category_variant: 分類 variant (default / pure_judged / no_combat / combat_to_semi)
            GPT round-1 Finding #6 感度分析用。詳細は sport_classifier.get_category 参照。
            "no_combat" は combat sport 9 を意図的に None 返却 = 除外対象。

    Returns:
        long format DataFrame・以下の列を持つ:
        - pref_code / pref_name / kai_num / year / cup / sport / score / is_winter (from parser)
        - is_host: bool (host_pref か)
        - category: str ("objective"/"subjective"/"semi_subjective")
        - is_subjective: int (0/1・Balmer2003 主観判定)
        - is_semi: int (0/1・団体競技)
        - is_host_int: int
    """
    from src.definitions import get_host_code

    targets = targets or _CROSS_SECTION_TARGETS

    frames = []
    for kai, cup in targets:
        df = parse_jspo_xls_long_format(kai, cup)
        host_code = get_host_code(kai)
        df["is_host"] = df["pref_code"] == host_code
        frames.append(df)
    stacked = pd.concat(frames, ignore_index=True)

    if not include_winter:
        stacked = stacked[~stacked["is_winter"]]

    stacked["category"] = stacked["sport"].map(
        lambda s: get_category(s, variant=category_variant)
    )
    if drop_unclassified:
        unclassified = stacked["category"].isna()
        if unclassified.any():
            if category_variant == "no_combat":
                # no_combat variant では combat sport 9 の意図的除外 = drop で正しい挙動
                stacked = stacked[stacked["category"].notna()].reset_index(drop=True)
            else:
                missing = sorted(stacked.loc[unclassified, "sport"].unique().tolist())
                raise ValueError(
                    f"Unclassified sports found (add to sport_classifier.SPORT_CATEGORIES): {missing}"
                )

    stacked["is_subjective"] = (stacked["category"] == "subjective").astype(int)
    stacked["is_semi"] = (stacked["category"] == "semi_subjective").astype(int)
    stacked["is_host_int"] = stacked["is_host"].astype(int)
    stacked["log_score"] = np.log1p(stacked["score"])

    return stacked.reset_index(drop=True)


def build_cross_section_frame_zero_imputed(
    include_winter: bool = True,
    category_variant: str = "default",
) -> pd.DataFrame:
    """欠測 106 セル (7,097 - 6,991) を score=0 埋めた full cartesian variant.

    GPT round-2 #3 応答: non-participation vs missing-data の解釈弾力性 sensitivity.
    prefecture が JSPO overall-standings publication から欠落しているセルを
    "non-participation → score=0" として扱う仮定で primary spec を再推定する。

    Full cartesian n = 47 prefectures × ([40 tennou + 35 kougou] + [40 tennou + 36 kougou])
                    = 47 × 151 = 7,097 cells (Table 1 theoretical n と一致)
    """
    from src.definitions import get_host_code

    # drop_unclassified=False で分類不能 sport も残す (zero-imputed の対象を広げる)
    df = build_cross_section_frame(
        include_winter=include_winter,
        drop_unclassified=False,
        category_variant=category_variant,
    )

    # 各 (kai, cup) の unique sport set を取得
    stack_sports = df.groupby(["kai_num", "cup"]).agg(
        year=("year", "first"),
        sports=("sport", lambda s: sorted(s.unique().tolist())),
    ).reset_index()

    prefs = sorted(df["pref_code"].unique())
    pref_names = df.groupby("pref_code")["pref_name"].first().to_dict()

    # full cartesian rows
    rows = []
    for _, s in stack_sports.iterrows():
        for sport in s["sports"]:
            for pref in prefs:
                rows.append({
                    "kai_num": s["kai_num"],
                    "cup": s["cup"],
                    "year": s["year"],
                    "sport": sport,
                    "pref_code": pref,
                    "pref_name": pref_names[pref],
                })
    full = pd.DataFrame(rows)

    # merge with original scores + is_winter (missing rows = non-participation)
    merged = full.merge(
        df[["pref_code", "kai_num", "cup", "sport", "score", "is_winter"]],
        on=["pref_code", "kai_num", "cup", "sport"],
        how="left",
    )
    merged["score"] = merged["score"].fillna(0)
    merged["is_winter"] = merged["is_winter"].fillna(False)

    # is_host 再付与 (host_pref は kai から解決)
    kai_to_host = {int(kai): get_host_code(int(kai)) for kai in merged["kai_num"].unique()}
    merged["is_host"] = merged.apply(
        lambda r: r["pref_code"] == kai_to_host[int(r["kai_num"])], axis=1
    )
    merged["is_host_int"] = merged["is_host"].astype(int)

    # category 再付与
    merged["category"] = merged["sport"].map(
        lambda s: get_category(s, variant=category_variant)
    )
    merged["is_subjective"] = (merged["category"] == "subjective").astype(int)
    merged["is_semi"] = (merged["category"] == "semi_subjective").astype(int)
    merged["log_score"] = np.log1p(merged["score"])

    return merged.reset_index(drop=True)


def _build_design(
    df: pd.DataFrame,
    with_semi_interaction: bool,
    add_pref_fe: bool,
    add_sport_fe: bool,
    add_year_fe: bool,
    add_cup_fe: bool,
    add_sport_cup_interaction: bool = False,
) -> pd.DataFrame:
    """OLS design matrix

    列順:
    - const
    - is_host_int
    - is_subjective (Balmer2003 主観判定ダミー)
    - [is_semi] (with_semi_interaction=True 時のみ)
    - host_x_subj = is_host_int × is_subjective  ← 主目的の交互作用項
    - [host_x_semi] (with_semi_interaction=True 時のみ)
    - pref FE / sport FE / year FE / cup FE
    - [sport × cup FE] (add_sport_cup_interaction=True 時のみ・GPT round-1 Finding #5 診断用)
    """
    base = pd.DataFrame({
        "is_host_int": df["is_host_int"].astype(float),
        "is_subjective": df["is_subjective"].astype(float),
    })
    base["host_x_subj"] = base["is_host_int"] * base["is_subjective"]

    if with_semi_interaction:
        base["is_semi"] = df["is_semi"].astype(float)
        base["host_x_semi"] = base["is_host_int"] * base["is_semi"]

    X = base.copy()
    if add_pref_fe:
        X = pd.concat([X, pd.get_dummies(df["pref_code"], prefix="pref", drop_first=True, dtype=float)], axis=1)
    if add_sport_fe:
        X = pd.concat([X, pd.get_dummies(df["sport"], prefix="sport", drop_first=True, dtype=float)], axis=1)
    if add_year_fe:
        X = pd.concat([X, pd.get_dummies(df["year"], prefix="year", drop_first=True, dtype=float)], axis=1)
    if add_cup_fe and df["cup"].nunique() > 1:
        X = pd.concat([X, pd.get_dummies(df["cup"], prefix="cup", drop_first=True, dtype=float)], axis=1)
    if add_sport_cup_interaction and df["cup"].nunique() > 1:
        sport_cup = df["sport"].astype(str) + "__" + df["cup"].astype(str)
        X = pd.concat([X, pd.get_dummies(sport_cup, prefix="sport_cup", drop_first=True, dtype=float)], axis=1)

    X = sm.add_constant(X, has_constant="add")
    return X


def _extract_coef(result: object, key: str) -> tuple[float, float, float]:
    """(coef, se, p) を安全に取り出す"""
    params = result.params
    bse = result.bse
    pvalues = result.pvalues
    if key not in params.index:
        return (float("nan"), float("nan"), float("nan"))
    return (float(params[key]), float(bse[key]), float(pvalues[key]))


def fit_cross_section_ols(
    df: pd.DataFrame,
    dv: str = "score",
    with_semi_interaction: bool = False,
    add_pref_fe: bool = True,
    add_sport_fe: bool = True,
    add_year_fe: bool = True,
    add_cup_fe: bool = True,
    add_sport_cup_interaction: bool = False,
    cluster_col: str = "pref_code",
    name: str = "cross_section_baseline",
) -> CrossSectionResult:
    """score ~ is_host + is_subjective + is_host × is_subjective + FE (clustered SE)

    Args:
        dv: "score" or "log_score"
        with_semi_interaction: True で semi_subjective も同時交互作用推定 (3 分類対比)
        add_sport_cup_interaction: True で sport × cup FE を追加 (GPT round-1 Finding #5
            診断用・k/G≈2.8 で cluster SE 計算不能 = point-estimate-only diagnostic)
        cluster_col: SE clustering キー (default = "pref_code")
    """
    X = _build_design(df, with_semi_interaction, add_pref_fe, add_sport_fe, add_year_fe, add_cup_fe, add_sport_cup_interaction)
    y = df[dv].astype(float)
    model = sm.OLS(y, X)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})

    coef_h, se_h, p_h = _extract_coef(result, "is_host_int")
    coef_i, se_i, p_i = _extract_coef(result, "host_x_subj")

    return CrossSectionResult(
        name=name,
        dv=dv,
        coef_is_host=coef_h,
        se_is_host=se_h,
        p_is_host=p_h,
        coef_interaction=coef_i,
        se_interaction=se_i,
        p_interaction=p_i,
        n_obs=int(result.nobs),
        n_params=len(result.params),
        n_clusters=int(df[cluster_col].nunique()),
        r2=float(result.rsquared),
        result_obj=result,
    )


def run_cross_section_models(include_winter: bool = True) -> list[CrossSectionResult]:
    """副次分析の主モデル一式 (Table 5 primary + sensitivity + diagnostic 構成)

    GPT round-1 Finding #1 応答: 主回帰を obj vs subj pure に純化する (semi 除外)。
    inclusive spec (semi 含む) は sensitivity として retention。
    GPT round-1 Finding #5 応答: sport × cup interaction を primary base に追加した
    diagnostic spec を新設 (rank-deficient regime k/G≈2.8 で cluster SE 計算不能・
    point-estimate-only として β_HS の direction/magnitude 頑健性確認に使用)。

    (Primary)     obj_vs_subj_primary:            semi 除外・obj vs subj pure 比較 (n≈4,744)
                  score ~ is_host + is_subjective + host×subj + FE
    (Diagnostic)  obj_vs_subj_primary_sport_cup:  primary base + sport×cup interaction
                  (Finding #5 診断・cluster SE 計算不能・point estimate only)
    (Sensitivity) baseline:                       semi 含む全 sample (旧 M1・n=6,991)
                  score ~ is_host + is_subjective + host×subj + FE
    (Descriptive) with_semi:                      3-way (subj + semi 両交互作用・cluster SE 計算不能)
                  score ~ is_host + subj + semi + host×subj + host×semi + FE
    (Robustness)  log_baseline:                   log(score+1) inclusive (旧 M3)
    """
    df = build_cross_section_frame(include_winter=include_winter)
    df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
    return [
        fit_cross_section_ols(df_obj_subj, dv="score", with_semi_interaction=False, name="cross_section_obj_vs_subj_primary"),
        fit_cross_section_ols(df_obj_subj, dv="score", with_semi_interaction=False, add_sport_cup_interaction=True, name="cross_section_obj_vs_subj_primary_sport_cup"),
        fit_cross_section_ols(df, dv="score", with_semi_interaction=False, name="cross_section_baseline"),
        fit_cross_section_ols(df, dv="score", with_semi_interaction=True, name="cross_section_with_semi"),
        fit_cross_section_ols(df, dv="log_score", with_semi_interaction=False, name="cross_section_log_baseline"),
    ]


def run_cross_section_models_by_variant(
    variants: tuple[str, ...] = ("pure_judged", "no_combat", "combat_to_semi"),
    include_winter: bool = True,
) -> dict[str, CrossSectionResult]:
    """GPT round-1 Finding #6 応答: 各 variant で primary spec (semi 除外・obj-vs-subj pure)
    を再推定して β_HS の分類 sensitivity を検証する。

    Table 5d の 3 行分の数値を返す。default variant は run_cross_section_models で提供済み
    (primary +20.27・SE 9.15・p 0.027・n 4744)。

    Args:
        variants: 対象 variant 名 tuple (sport_classifier._VARIANT_OVERRIDES キー)
        include_winter: 冬季3競技を含めるか
    """
    results = {}
    for v in variants:
        df = build_cross_section_frame(include_winter=include_winter, category_variant=v)
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result = fit_cross_section_ols(
            df_obj_subj,
            dv="score",
            with_semi_interaction=False,
            name=f"cross_section_primary_{v}",
        )
        results[v] = result
    return results


def run_cross_section_zero_imputed(include_winter: bool = True) -> CrossSectionResult:
    """GPT round-2 #3 応答: 欠測 106 セル (7,097 - 6,991) を score=0 埋めた
    primary spec (semi 除外・obj-vs-subj pure) の zero-imputed variant.

    non-participation vs missing-data の解釈弾力性 sensitivity check.
    Table 5 primary (+20.27) との direction 一致 + magnitude 保持を確認する
    ("results were directionally unchanged" 主張の実測根拠)。
    """
    df = build_cross_section_frame_zero_imputed(include_winter=include_winter)
    # primary spec = semi 除外 (obj vs subj pure)
    df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
    return fit_cross_section_ols(
        df_obj_subj,
        dv="score",
        with_semi_interaction=False,
        name="cross_section_obj_vs_subj_zero_imputed",
    )


def wild_cluster_bootstrap(
    df: pd.DataFrame,
    dv: str = "score",
    with_semi_interaction: bool = False,
    add_pref_fe: bool = True,
    add_sport_fe: bool = True,
    add_year_fe: bool = True,
    add_cup_fe: bool = True,
    cluster_col: str = "pref_code",
    test_coef: str = "host_x_subj",
    n_bootstrap: int = 999,
    seed: int = 20260728,
) -> dict:
    """Wild-cluster bootstrap p-value for a single coefficient under a restricted null.

    Implements the Cameron-Gelbach-Miller (2008) wild-cluster bootstrap with Rademacher
    weights and restricted null (H0: β_{test_coef} = 0). Addresses the Cameron-Miller
    (2015) few-treated-clusters problem when the cross-section has only 2 treated
    prefecture clusters (2024 Saga, 2025 Shiga) out of 47.

    Two-sided bootstrap p = share of |t*_b| ≥ |t_observed|.
    """
    rng = np.random.default_rng(seed)

    X_full = _build_design(df, with_semi_interaction, add_pref_fe, add_sport_fe, add_year_fe, add_cup_fe)
    y = df[dv].astype(float).values

    model_full = sm.OLS(y, X_full)
    result_full = model_full.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})

    n_clusters = int(df[cluster_col].nunique())
    treated_clusters = int(df.loc[df["is_host_int"] == 1, cluster_col].nunique())

    if test_coef not in result_full.params.index:
        return {
            "test_coef": test_coef,
            "observed_coef": float("nan"),
            "observed_se": float("nan"),
            "observed_t": float("nan"),
            "cluster_robust_p": float("nan"),
            "bootstrap_p": float("nan"),
            "n_bootstrap_used": 0,
            "n_bootstrap_requested": n_bootstrap,
            "seed": seed,
            "n_clusters": n_clusters,
            "treated_clusters": treated_clusters,
        }

    observed_coef = float(result_full.params[test_coef])
    observed_se = float(result_full.bse[test_coef])
    observed_t = observed_coef / observed_se
    cluster_robust_p = float(result_full.pvalues[test_coef])

    X_restricted = X_full.drop(columns=[test_coef])
    model_restricted = sm.OLS(y, X_restricted)
    result_restricted = model_restricted.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})
    y_hat_restricted = np.asarray(result_restricted.predict(X_restricted), dtype=float)
    residuals_restricted = y - y_hat_restricted

    clusters = df[cluster_col].values
    unique_clusters = np.unique(clusters)

    bootstrap_ts = []
    for _ in range(n_bootstrap):
        omega = rng.choice([-1.0, 1.0], size=len(unique_clusters))
        omega_map = dict(zip(unique_clusters, omega))
        omega_i = np.array([omega_map[c] for c in clusters], dtype=float)
        y_star = y_hat_restricted + residuals_restricted * omega_i
        try:
            result_star = sm.OLS(y_star, X_full).fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})
            t_star = float(result_star.params[test_coef] / result_star.bse[test_coef])
            if np.isfinite(t_star):
                bootstrap_ts.append(t_star)
        except Exception:
            continue

    bootstrap_ts_arr = np.array(bootstrap_ts)
    bootstrap_p = float(np.mean(np.abs(bootstrap_ts_arr) >= abs(observed_t))) if len(bootstrap_ts_arr) else float("nan")

    return {
        "test_coef": test_coef,
        "observed_coef": observed_coef,
        "observed_se": observed_se,
        "observed_t": observed_t,
        "cluster_robust_p": cluster_robust_p,
        "bootstrap_p": bootstrap_p,
        "n_bootstrap_used": len(bootstrap_ts_arr),
        "n_bootstrap_requested": n_bootstrap,
        "seed": seed,
        "n_clusters": n_clusters,
        "treated_clusters": treated_clusters,
    }


def run_bootstrap_by_variant(
    variants: tuple[str, ...] = ("default", "pure_judged", "no_combat", "combat_to_semi"),
    include_winter: bool = True,
    n_bootstrap: int = 999,
    seed: int = 20260728,
) -> dict[str, dict]:
    """v4 Phase A-2 (GPT round-2 追加応答・Finding L): Table 5d 4 variant 全てで
    wild-cluster bootstrap を計算し、classification sensitivity の inferential
    consistency を検証する.

    Table 5d の cluster-robust p だけでは "selective standard" (primary/inclusive
    は wild-cluster bootstrap で降下・variant は cluster-robust のまま) の疑いあり
    → 全 4 variant で同一 seed・同一 B で bootstrap を計算して inferential
    consistency を担保する。

    default variant の bootstrap は Table 5 primary bootstrap (seed=20260728) と
    bit-identical になる (consistency check として使える)。

    Returns:
        {variant_name: wild_cluster_bootstrap 返り値 dict} 形式
    """
    results = {}
    for v in variants:
        df = build_cross_section_frame(include_winter=include_winter, category_variant=v)
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result = wild_cluster_bootstrap(
            df_obj_subj,
            dv="score",
            with_semi_interaction=False,
            test_coef="host_x_subj",
            n_bootstrap=n_bootstrap,
            seed=seed,
        )
        results[v] = result
    return results


def descriptive_by_category(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """カテゴリ × host のクロス集計 (Discussion 用)

    行 = category (objective / subjective / semi_subjective)
    列 = mean_score_host / mean_score_nonhost / diff / n_host_obs / n_nonhost_obs
    """
    if df is None:
        df = build_cross_section_frame()
    agg = (
        df.groupby(["category", "is_host"])["score"]
        .agg(["mean", "count"])
        .reset_index()
    )
    wide = agg.pivot(index="category", columns="is_host", values=["mean", "count"])
    wide.columns = [f"{v}_{'host' if h else 'nonhost'}" for v, h in wide.columns]
    wide["diff_mean_host_minus_nonhost"] = wide["mean_host"] - wide["mean_nonhost"]
    return wide.reset_index()


def results_to_dataframe(results: list[CrossSectionResult]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "name": r.name,
            "dv": r.dv,
            "coef_is_host": r.coef_is_host,
            "se_is_host": r.se_is_host,
            "p_is_host": r.p_is_host,
            "coef_interaction": r.coef_interaction,
            "se_interaction": r.se_interaction,
            "p_interaction": r.p_interaction,
            "n_obs": r.n_obs,
            "n_params": r.n_params,
            "n_clusters": r.n_clusters,
            "r2": r.r2,
        }
        for r in results
    ])
