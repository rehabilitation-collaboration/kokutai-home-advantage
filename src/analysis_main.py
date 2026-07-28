"""Phase 2 主モデル: 順序 logit + 二値 logit (top-1 / top-8)

Balmer2003 型 (pooled) + 舟橋2016 型 (pref+year FE) の両先行研究 estimator を並走。
選択肢A (Deviation #4) により Subj_i は主モデル入れず・副次
analysis_cross_section_2024_2025.py で 2年断面 Subj×Host 交互作用を扱う。

DV エンコーディング:
- rank_ordinal: 1-8 + 「圏外 9」の 9 カテゴリ (rank NA → 9)。1-8位のみ観測される
  実データ制約に対する censored ordinal の実用近似。
- top1: rank == 1 の二値 (優勝可否)
- top8: rank <= 8 の二値 (入賞可否・= rank not NA)

分析期間: 2012-2022 (Deviation #3 / ESRI 令和4年度版カバー範囲)
母集団: is_special == False & cancelled == False & log_pop/log_gdp not NA
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.panel_builder import merge_confounders

RANK_OUTSIDE = 9

Cup = Literal["tennou", "kougou", "both"]
Dv = Literal["top1", "top8"]


@dataclass
class ModelResult:
    name: str
    model_type: str
    dv: str
    coef_is_host: float
    se_is_host: float
    p_is_host: float
    n_obs: int
    n_params: int
    converged: bool
    llf: float
    result_obj: object


def build_analysis_frame(
    panel: pd.DataFrame | None = None,
    year_min: int = 2012,
    year_max: int = 2022,
    cup: Cup = "tennou",
) -> pd.DataFrame:
    """主モデル用の分析フレーム構築

    - is_special / cancelled 除外
    - year_min-year_max 範囲
    - cup で filter (both は tennou+kougou 統合・cup dummy を追加可)
    - rank NA → RANK_OUTSIDE (9)・top1/top8 派生
    - log_pop/log_gdp not NA 保証
    """
    if panel is None:
        panel = merge_confounders()
    mask = (
        (~panel["is_special"])
        & (~panel["cancelled"])
        & (panel["year"] >= year_min)
        & (panel["year"] <= year_max)
        & panel["log_population"].notna()
        & panel["log_gdp"].notna()
    )
    if cup != "both":
        mask &= panel["cup"] == cup
    df = panel[mask].copy()
    df["rank_ordinal"] = df["rank"].fillna(RANK_OUTSIDE).astype(int)
    df["top1"] = (df["rank"] == 1).astype(int)
    df["top8"] = df["rank"].notna().astype(int)
    df["is_host_int"] = df["is_host"].astype(int)
    return df.reset_index(drop=True)


def _build_design_matrix(
    df: pd.DataFrame,
    add_pref_fe: bool,
    add_year_fe: bool,
    add_cup_fe: bool = False,
    add_const: bool = True,
) -> pd.DataFrame:
    exog_cols = ["is_host_int", "log_population", "log_gdp"]
    X = df[exog_cols].astype(float).copy()
    if add_pref_fe:
        pref_dummies = pd.get_dummies(df["pref_code"], prefix="pref", drop_first=True, dtype=float)
        X = pd.concat([X, pref_dummies], axis=1)
    if add_year_fe:
        year_dummies = pd.get_dummies(df["year"], prefix="year", drop_first=True, dtype=float)
        X = pd.concat([X, year_dummies], axis=1)
    if add_cup_fe and "cup" in df.columns and df["cup"].nunique() > 1:
        cup_dummies = pd.get_dummies(df["cup"], prefix="cup", drop_first=True, dtype=float)
        X = pd.concat([X, cup_dummies], axis=1)
    if add_const:
        X = sm.add_constant(X, has_constant="add")
    return X


def _make_result(
    name: str,
    model_type: str,
    dv: str,
    result: object,
) -> ModelResult:
    params = result.params
    bse = result.bse
    pvalues = result.pvalues
    coef = float(params.get("is_host_int", np.nan)) if hasattr(params, "get") else float(params["is_host_int"])
    se = float(bse.get("is_host_int", np.nan)) if hasattr(bse, "get") else float(bse["is_host_int"])
    p = float(pvalues.get("is_host_int", np.nan)) if hasattr(pvalues, "get") else float(pvalues["is_host_int"])
    converged = bool(result.mle_retvals.get("converged", False)) if hasattr(result, "mle_retvals") else True
    return ModelResult(
        name=name,
        model_type=model_type,
        dv=dv,
        coef_is_host=coef,
        se_is_host=se,
        p_is_host=p,
        n_obs=int(result.nobs),
        n_params=len(result.params),
        converged=converged,
        llf=float(result.llf),
        result_obj=result,
    )


def _fit_kwargs_for_cluster(cluster_groups: pd.Series | None) -> dict:
    if cluster_groups is None:
        return {}
    return {"cov_type": "cluster", "cov_kwds": {"groups": cluster_groups}}


def fit_ordered_logit(
    df: pd.DataFrame,
    add_pref_fe: bool = False,
    add_year_fe: bool = False,
    add_cup_fe: bool = False,
    name: str = "ordered_pooled",
    cluster_groups: pd.Series | None = None,
) -> ModelResult:
    """rank_ordinal ~ is_host + log_pop + log_gdp (+ FE)

    cluster_groups: 渡すと prefecture-clustered SE (repeated-observations 対応)。
    None なら Fisher-information SE (backward compatible)。
    """
    X = _build_design_matrix(df, add_pref_fe, add_year_fe, add_cup_fe, add_const=False)
    y = df["rank_ordinal"]
    model = OrderedModel(y, X, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=500,
                       **_fit_kwargs_for_cluster(cluster_groups))
    return _make_result(name, "ordered_logit", "rank_ordinal", result)


def fit_logit(
    df: pd.DataFrame,
    dv: Dv = "top1",
    add_pref_fe: bool = False,
    add_year_fe: bool = False,
    add_cup_fe: bool = False,
    name: str | None = None,
    cluster_groups: pd.Series | None = None,
) -> ModelResult:
    """{top1|top8} ~ is_host + log_pop + log_gdp (+ FE)

    cluster_groups: 渡すと prefecture-clustered SE。None なら Fisher-information SE。
    """
    X = _build_design_matrix(df, add_pref_fe, add_year_fe, add_cup_fe, add_const=True)
    y = df[dv]
    model = sm.Logit(y, X)
    result = model.fit(method="bfgs", disp=False, maxiter=500,
                       **_fit_kwargs_for_cluster(cluster_groups))
    return _make_result(name or f"logit_{dv}_pooled", "logit", dv, result)


def run_main_models(
    year_min: int = 2012,
    year_max: int = 2022,
    cup: Cup = "tennou",
) -> list[ModelResult]:
    """主モデル一式 (4 モデル)

    (a) Balmer2003 型 = pooled (FE なし)
    (b) 舟橋2016 型 = pref FE + year FE
    ×
    (i) 順序 logit / (ii) 二値 top1

    top8 は 2012-2022 tennou で 9/9 host が入賞 = complete separation により
    logit で係数が発散するため主モデルから除外。descriptive_host_summary() で
    記述統計として提示する。
    """
    df = build_analysis_frame(year_min=year_min, year_max=year_max, cup=cup)
    add_cup = cup == "both"
    pref_clusters = df["pref_code"]
    return [
        fit_ordered_logit(df, add_pref_fe=False, add_year_fe=False, add_cup_fe=add_cup,
                          name="ordered_pooled", cluster_groups=pref_clusters),
        fit_ordered_logit(df, add_pref_fe=True, add_year_fe=True, add_cup_fe=add_cup,
                          name="ordered_prefFE_yearFE"),
        fit_logit(df, dv="top1", add_pref_fe=False, add_year_fe=False, add_cup_fe=add_cup,
                  name="logit_top1_pooled", cluster_groups=pref_clusters),
        fit_logit(df, dv="top1", add_pref_fe=True, add_year_fe=True, add_cup_fe=add_cup,
                  name="logit_top1_prefFE_yearFE"),
    ]


def descriptive_host_summary(
    year_min: int = 2012,
    year_max: int = 2022,
    cup: Cup = "tennou",
) -> dict:
    """host effect の記述統計

    top8 が complete separation する事実自体が host dominance の証拠
    (Discussion で「9 host のうち 9 全員が top-8 入賞」と提示)。
    """
    df = build_analysis_frame(year_min=year_min, year_max=year_max, cup=cup)
    host = df[df["is_host"]]
    nonhost = df[~df["is_host"]]
    return {
        "n_obs": len(df),
        "n_host": len(host),
        "n_nonhost": len(nonhost),
        "n_host_top1": int(host["top1"].sum()),
        "n_host_top8": int(host["top8"].sum()),
        "n_nonhost_top1": int(nonhost["top1"].sum()),
        "n_nonhost_top8": int(nonhost["top8"].sum()),
        "host_top1_rate": float(host["top1"].mean()) if len(host) else float("nan"),
        "host_top8_rate": float(host["top8"].mean()) if len(host) else float("nan"),
        "nonhost_top1_rate": float(nonhost["top1"].mean()) if len(nonhost) else float("nan"),
        "nonhost_top8_rate": float(nonhost["top8"].mean()) if len(nonhost) else float("nan"),
        "host_mean_rank_when_ranked": float(host["rank"].mean()) if host["rank"].notna().any() else float("nan"),
    }


def results_to_dataframe(results: list[ModelResult]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "name": r.name,
            "model_type": r.model_type,
            "dv": r.dv,
            "coef_is_host": r.coef_is_host,
            "se_is_host": r.se_is_host,
            "p_is_host": r.p_is_host,
            "n_obs": r.n_obs,
            "n_params": r.n_params,
            "converged": r.converged,
            "llf": r.llf,
        }
        for r in results
    ])
