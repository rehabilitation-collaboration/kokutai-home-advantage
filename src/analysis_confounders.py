"""Phase 2 Csurilla型段階投入 Robustness

Csurilla & Fertő (2023) Sci Rep 13:819 の Table 2 準拠で交絡変数を段階投入し、
is_host 係数の減衰度を測定する。Csurilla2023 の Olympics 分析では約45%減衰報告
(Key Decision #13)。

段階 (order は Csurilla2023 Table 2 に準拠):
  M1: is_host のみ (base)
  M2: + log_population
  M3: + log_gdp
  M4: + pref FE
  M5: + pref FE + year FE (完全 FE)

DV は analysis_main と同じく順序 logit (rank_ordinal) と二値 logit (top1) の
2 系統で測定 (top8 は complete separation で除外)。
"""

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.analysis_main import (
    ModelResult,
    _build_design_matrix,
    _make_result,
    build_analysis_frame,
)

Dv = Literal["rank_ordinal", "top1"]


@dataclass
class StageSpec:
    name: str
    add_log_pop: bool
    add_log_gdp: bool
    add_pref_fe: bool
    add_year_fe: bool


STAGES: list[StageSpec] = [
    StageSpec("M1_host_only", False, False, False, False),
    StageSpec("M2_add_pop", True, False, False, False),
    StageSpec("M3_add_gdp", True, True, False, False),
    StageSpec("M4_add_prefFE", True, True, True, False),
    StageSpec("M5_full_FE", True, True, True, True),
]


def _build_stage_design(df: pd.DataFrame, spec: StageSpec, add_const: bool) -> pd.DataFrame:
    cols = ["is_host_int"]
    if spec.add_log_pop:
        cols.append("log_population")
    if spec.add_log_gdp:
        cols.append("log_gdp")
    X = df[cols].astype(float).copy()
    if spec.add_pref_fe:
        pref_dummies = pd.get_dummies(df["pref_code"], prefix="pref", drop_first=True, dtype=float)
        X = pd.concat([X, pref_dummies], axis=1)
    if spec.add_year_fe:
        year_dummies = pd.get_dummies(df["year"], prefix="year", drop_first=True, dtype=float)
        X = pd.concat([X, year_dummies], axis=1)
    if add_const:
        X = sm.add_constant(X, has_constant="add")
    return X


def fit_staged_ordered_logit(df: pd.DataFrame, spec: StageSpec) -> ModelResult:
    X = _build_stage_design(df, spec, add_const=False)
    y = df["rank_ordinal"]
    model = OrderedModel(y, X, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=500)
    return _make_result(f"ordered_{spec.name}", "ordered_logit", "rank_ordinal", result)


def fit_staged_logit_top1(df: pd.DataFrame, spec: StageSpec) -> ModelResult:
    X = _build_stage_design(df, spec, add_const=True)
    y = df["top1"]
    model = sm.Logit(y, X)
    result = model.fit(method="bfgs", disp=False, maxiter=500)
    return _make_result(f"logit_top1_{spec.name}", "logit", "top1", result)


def run_staged_analysis(
    year_min: int = 2012,
    year_max: int = 2022,
    cup: Literal["tennou", "kougou", "both"] = "tennou",
    dv: Dv = "rank_ordinal",
) -> list[ModelResult]:
    """段階投入 5 モデルを実行 (DV は 1 種類ずつ・両方欲しければ 2 回呼ぶ)"""
    df = build_analysis_frame(year_min=year_min, year_max=year_max, cup=cup)
    fitter = fit_staged_ordered_logit if dv == "rank_ordinal" else fit_staged_logit_top1
    return [fitter(df, spec) for spec in STAGES]


def compute_attenuation(results: list[ModelResult]) -> pd.DataFrame:
    """M1 から Mn までの is_host 係数の減衰率を計算

    Csurilla2023 との対比用: 減衰率 = 1 - |coef_Mk / coef_M1|
    """
    if not results:
        return pd.DataFrame()
    base = results[0].coef_is_host
    rows = []
    for r in results:
        attenuation = 1.0 - abs(r.coef_is_host / base) if base != 0 else float("nan")
        rows.append({
            "name": r.name,
            "coef_is_host": r.coef_is_host,
            "se_is_host": r.se_is_host,
            "p_is_host": r.p_is_host,
            "attenuation_vs_M1": attenuation,
            "n_obs": r.n_obs,
            "n_params": r.n_params,
            "converged": r.converged,
        })
    return pd.DataFrame(rows)
