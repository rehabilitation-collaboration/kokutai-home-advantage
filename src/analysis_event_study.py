"""event-study 2層設計 + parallel trend 検定

Layer 1: pre-2005 = 2002高知単独 (ふるさと選手制度導入前)
Layer 2: post-2016 = 5ショック (2016岩手/2017愛媛/2022栃木/2023鹿児島特別/2024佐賀)

Reference time = τ=-1。stacked event-study の interaction dummy を
線形確率モデル (LP・OLS) で推定 (順序 logit は event-study の incidental
parameter で収束が悪いため OLS 主軸)。

parallel trend 検定 = pre-shock 期間 (τ ∈ [-3, -2]) の interaction 係数の
joint Wald test (H0: 全て 0)。
"""

from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.panel_builder import merge_confounders

Layer = Literal["L1_pre2005", "L2_post2016"]

LAYER1_SHOCKS: dict[int, str] = {2002: "高知"}
LAYER2_SHOCKS: dict[int, str] = {
    2016: "岩手",
    2017: "愛媛",
    2022: "栃木",
    2023: "鹿児島",
    2024: "佐賀",
}


def _get_shocks(layer: Layer) -> dict[int, str]:
    return LAYER1_SHOCKS if layer == "L1_pre2005" else LAYER2_SHOCKS


def build_event_study_frame(
    layer: Layer,
    pre_window: int = 3,
    post_window: int = 3,
    cup: str = "tennou",
    panel: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """stacked event-study panel builder

    各 shock (year, host県) について relative time τ ∈ [-pre, +post] の窓を切り、
    47県 × 窓長 の panel を stack。cancelled 年は除外。特別大会 (2023 特別) は
    year=2023 で通常大会と同じ扱い (nagano panel には special_2023 として入るが、
    is_special True で除外されるため通常年 (2023) の 47県 tennou を使う)。

    Returns:
        DataFrame with cols:
        - pref_code, pref_name, year, cup, kai_label
        - rank, is_host, is_special, cancelled
        - shock_year (int), shock_id (str), host_pref (str)
        - relative_time (int), is_treated (bool)
        - rank_ordinal (int, 1-9), top1 (int), top8 (int)
    """
    if panel is None:
        panel = merge_confounders()
    shocks = _get_shocks(layer)

    frames = []
    for shock_year, host_pref in shocks.items():
        window_min = shock_year - pre_window
        window_max = shock_year + post_window
        sub = panel[
            (panel["cup"] == cup)
            & (panel["year"] >= window_min)
            & (panel["year"] <= window_max)
            & (~panel["cancelled"])
            & (~panel["is_special"])
        ].copy()
        if sub.empty:
            continue
        sub["shock_year"] = shock_year
        sub["shock_id"] = f"shock_{shock_year}"
        sub["host_pref"] = host_pref
        sub["relative_time"] = (sub["year"] - shock_year).astype(int)
        sub["is_treated"] = sub["pref_name"] == host_pref
        sub["rank_ordinal"] = sub["rank"].fillna(9).astype(int)
        sub["top1"] = (sub["rank"] == 1).astype(int)
        sub["top8"] = sub["rank"].notna().astype(int)
        frames.append(sub)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def fit_event_study_lp(
    df: pd.DataFrame,
    dv: Literal["top1", "top8", "rank_ordinal"] = "top1",
    reference_time: int = -1,
) -> tuple[pd.DataFrame, object]:
    """LP モデルで event-study 係数推定 (2wayFE, clustered SE)

    outcome ~ Σ_{τ ≠ ref} β_τ · 1{relative_time=τ} × is_treated
              + unit_event FE + calendar year FE

    Reference time = -1 (直前1年をベース)。clustered SE は pref_code でクラスタ。

    Returns:
        (coef_df, fitted_result) の2-tuple
        coef_df cols: relative_time, coef, se, p, is_reference
    """
    if df.empty:
        return pd.DataFrame(), None

    times = sorted(df["relative_time"].unique())
    interaction_cols: list[str] = []
    df = df.copy()
    for t in times:
        if t == reference_time:
            continue
        col = f"treated_tau_{t:+d}"
        df[col] = ((df["relative_time"] == t) & df["is_treated"]).astype(int)
        interaction_cols.append(col)

    df["unit_event"] = df["pref_code"].astype(str) + "_" + df["shock_id"]
    unit_event_dummies = pd.get_dummies(df["unit_event"], prefix="ue", drop_first=True, dtype=float)
    year_dummies = pd.get_dummies(df["year"], prefix="year", drop_first=True, dtype=float)

    X = pd.concat([df[interaction_cols].astype(float), unit_event_dummies, year_dummies], axis=1)
    X = sm.add_constant(X, has_constant="add")
    y = df[dv].astype(float)

    model = sm.OLS(y, X)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": df["pref_code"]})

    rows = []
    for t in times:
        if t == reference_time:
            rows.append({"relative_time": t, "coef": 0.0, "se": 0.0, "p": np.nan, "is_reference": True})
            continue
        col = f"treated_tau_{t:+d}"
        coef = float(result.params.get(col, np.nan))
        se = float(result.bse.get(col, np.nan))
        p = float(result.pvalues.get(col, np.nan))
        rows.append({"relative_time": t, "coef": coef, "se": se, "p": p, "is_reference": False})
    coef_df = pd.DataFrame(rows).sort_values("relative_time").reset_index(drop=True)
    return coef_df, result


def parallel_trend_test(
    df: pd.DataFrame,
    dv: Literal["top1", "top8", "rank_ordinal"] = "top1",
    reference_time: int = -1,
) -> dict:
    """pre-shock 期間 (τ < 0 かつ ≠ reference) の joint Wald test

    H0: 全ての pre-shock interaction 係数 = 0 (parallel trend 前提)
    帰無仮説棄却 (p < 0.05) → parallel trend 崩壊。

    Returns:
        dict: {n_pre_dummies, wald_stat, wald_df, wald_p}
    """
    coef_df, result = fit_event_study_lp(df, dv=dv, reference_time=reference_time)
    if result is None or coef_df.empty:
        return {"n_pre_dummies": 0, "wald_stat": np.nan, "wald_df": 0, "wald_p": np.nan}

    pre_dummies = [
        f"treated_tau_{t:+d}"
        for t in coef_df["relative_time"]
        if t < 0 and t != reference_time
    ]
    if not pre_dummies:
        return {"n_pre_dummies": 0, "wald_stat": np.nan, "wald_df": 0, "wald_p": np.nan}

    hypotheses = " = 0, ".join(pre_dummies) + " = 0"
    test = result.wald_test(hypotheses, use_f=False)
    stat = float(np.array(test.statistic).flatten()[0])
    p = float(np.array(test.pvalue).flatten()[0])
    return {"n_pre_dummies": len(pre_dummies), "wald_stat": stat, "wald_df": len(pre_dummies), "wald_p": p}


def compute_pre_post_means(df: pd.DataFrame, dv: str = "top1") -> pd.DataFrame:
    """descriptive: shock 前後 × treated/control で DV 平均を集計"""
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["period"] = np.where(df["relative_time"] < 0, "pre", "post")
    df["group"] = np.where(df["is_treated"], "treated", "control")
    return (
        df.groupby(["period", "group"], observed=True)[dv]
        .agg(["mean", "count"])
        .reset_index()
    )
