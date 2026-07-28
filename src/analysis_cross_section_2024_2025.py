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
) -> pd.DataFrame:
    """4 dataset を stack + Balmer2003 3 分類を付与

    Args:
        targets: (kai_num, cup) の list。省略時は 78+79 × tennou+kougou の 4件
        include_winter: 冬季3競技を含めるか (default True・Balmer2003 は Winter/Summer 別分析だが本論では pooled)
        drop_unclassified: sport_classifier で分類不能な競技行を除外するか

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

    stacked["category"] = stacked["sport"].map(get_category)
    if drop_unclassified:
        unclassified = stacked["category"].isna()
        if unclassified.any():
            missing = sorted(stacked.loc[unclassified, "sport"].unique().tolist())
            raise ValueError(
                f"Unclassified sports found (add to sport_classifier.SPORT_CATEGORIES): {missing}"
            )

    stacked["is_subjective"] = (stacked["category"] == "subjective").astype(int)
    stacked["is_semi"] = (stacked["category"] == "semi_subjective").astype(int)
    stacked["is_host_int"] = stacked["is_host"].astype(int)
    stacked["log_score"] = np.log1p(stacked["score"])

    return stacked.reset_index(drop=True)


def _build_design(
    df: pd.DataFrame,
    with_semi_interaction: bool,
    add_pref_fe: bool,
    add_sport_fe: bool,
    add_year_fe: bool,
    add_cup_fe: bool,
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
    cluster_col: str = "pref_code",
    name: str = "cross_section_baseline",
) -> CrossSectionResult:
    """score ~ is_host + is_subjective + is_host × is_subjective + FE (clustered SE)

    Args:
        dv: "score" or "log_score"
        with_semi_interaction: True で semi_subjective も同時交互作用推定 (3 分類対比)
        cluster_col: SE clustering キー (default = "pref_code")
    """
    X = _build_design(df, with_semi_interaction, add_pref_fe, add_sport_fe, add_year_fe, add_cup_fe)
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
    """副次分析の主モデル一式

    (M1) baseline:            score ~ is_host + is_subjective + host×subj + FE
    (M2) with_semi:           score ~ is_host + subj + semi + host×subj + host×semi + FE
    (M3) log_score baseline:  log(score+1) ~ ... (Robustness・分散安定化)
    """
    df = build_cross_section_frame(include_winter=include_winter)
    return [
        fit_cross_section_ols(df, dv="score", with_semi_interaction=False, name="cross_section_baseline"),
        fit_cross_section_ols(df, dv="score", with_semi_interaction=True, name="cross_section_with_semi"),
        fit_cross_section_ols(df, dv="log_score", with_semi_interaction=False, name="cross_section_log_baseline"),
    ]


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
