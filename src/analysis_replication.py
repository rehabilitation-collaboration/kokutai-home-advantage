"""Phase 2 副次: 舟橋2016 再現 (2003-2011) + 2012 拡張 sanity check

舟橋弘晃・日比野幹生・石黒えみ・間野義之 (2016)
「国民体育大会総合成績の決定要因: 都道府県別パネルデータによる計量分析」
スポーツマネジメント研究 8(1) pp.17-33 の base spec を再現する。

データ源: JSPO 個別回 PDF 第58-67回 (2003-2012) の 47県総合得点 (Tpoint)
モデル: score ~ is_host + pref FE + year FE (OLS + clustered SE / pref)

Controls (log_population + log_gdp) は ESRI 令和4年度版 (2011-2022) の範囲外 =
Deviation #3 で「必要時点で ESRI 旧SNA 別ページから追加取得」に留保・
本モジュールでは controls 抜き simple spec (舟橋 base モデルの再現主目的)。

2012-2022 の score DV OLS 拡張は JSPO PDF 68-77 が 404/画像 PDF で取得不能
(Deviation #2) = 順位 DV 順序 logit 主モデル (`analysis_main.py`) で代替済。
本モジュールでは 2012 単年拡張 (第67回大分) 1年分を舟橋+1 として提供する。
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.data_loader import load_jspo_kai_pdf
from src.definitions import KOKUTAI_HOSTS, PREFECTURE_TO_CODE, is_host

# 舟橋2016 の対象期間 = 第58回2003 (静岡) 〜 第66回2011 (山口)
FUNAHASHI_KAI_RANGE = (58, 66)
# +1 拡張 = 第67回2012 (岐阜)
EXTENDED_KAI = 67

# 舟橋2016 Table 3 の Model 4 (pref FE + year FE + controls) の開催年係数 (円換算前・素点スケール)
# Reference value for sanity assertion in tests / manuscript
FUNAHASHI_2016_HOST_COEF = 1674.65


@dataclass
class ReplicationResult:
    name: str
    dv: str
    year_min: int
    year_max: int
    coef_is_host: float
    se_is_host: float
    p_is_host: float
    n_obs: int
    n_params: int
    n_clusters: int
    r2: float
    r2_adj: float
    result_obj: object


def load_score_panel(
    year_min_kai: int = FUNAHASHI_KAI_RANGE[0],
    year_max_kai: int = FUNAHASHI_KAI_RANGE[1],
    cup: str = "tennou",
) -> pd.DataFrame:
    """JSPO PDF 個別回 (58-67 対応) を stack して pref × kai の score panel を返す

    Args:
        year_min_kai / year_max_kai: 対象 kai 番号の範囲 (両端含む)
        cup: 'tennou' or 'kougou'

    Returns:
        long format DataFrame:
        - kai_num / year / pref_name / pref_code / cup / score / rank / is_host / is_host_int
    """
    frames = []
    for kai in range(year_min_kai, year_max_kai + 1):
        df = load_jspo_kai_pdf(kai_num=kai, cup=cup).copy()
        df["pref_code"] = df["pref_name"].map(PREFECTURE_TO_CODE)
        if df["pref_code"].isna().any():
            missing = df.loc[df["pref_code"].isna(), "pref_name"].tolist()
            raise ValueError(f"kai={kai} cup={cup}: unmapped pref names {missing}")
        df["year"] = KOKUTAI_HOSTS[kai]["year"]
        df["is_host"] = df["pref_code"].apply(lambda c: is_host(int(c), kai))
        frames.append(df)
    panel = pd.concat(frames, ignore_index=True)
    panel["is_host_int"] = panel["is_host"].astype(int)
    return panel.reset_index(drop=True)


def _build_design(
    df: pd.DataFrame,
    add_pref_fe: bool,
    add_year_fe: bool,
) -> pd.DataFrame:
    """OLS design matrix: is_host_int (+ optional pref/year FE) + const"""
    X = df[["is_host_int"]].astype(float).copy()
    if add_pref_fe:
        X = pd.concat([X, pd.get_dummies(df["pref_code"], prefix="pref", drop_first=True, dtype=float)], axis=1)
    if add_year_fe and df["year"].nunique() > 1:
        X = pd.concat([X, pd.get_dummies(df["year"], prefix="year", drop_first=True, dtype=float)], axis=1)
    return sm.add_constant(X, has_constant="add")


def fit_ols_score(
    df: pd.DataFrame,
    add_pref_fe: bool = True,
    add_year_fe: bool = True,
    cluster_col: str = "pref_code",
    name: str = "funahashi_base",
) -> ReplicationResult:
    """score ~ is_host + pref FE + year FE (OLS + clustered SE by pref)"""
    X = _build_design(df, add_pref_fe, add_year_fe)
    y = df["score"].astype(float)
    model = sm.OLS(y, X)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})

    coef = float(result.params.get("is_host_int", np.nan))
    se = float(result.bse.get("is_host_int", np.nan))
    p = float(result.pvalues.get("is_host_int", np.nan))
    return ReplicationResult(
        name=name,
        dv="score",
        year_min=int(df["year"].min()),
        year_max=int(df["year"].max()),
        coef_is_host=coef,
        se_is_host=se,
        p_is_host=p,
        n_obs=int(result.nobs),
        n_params=len(result.params),
        n_clusters=int(df[cluster_col].nunique()),
        r2=float(result.rsquared),
        r2_adj=float(result.rsquared_adj),
        result_obj=result,
    )


def run_replication_models(cup: str = "tennou") -> list[ReplicationResult]:
    """舟橋 base spec 再現 + FE 単純化 Robustness + 2003-2012 拡張

    (M1) funahashi_base: 舟橋2016 base spec 完全再現 (2003-2011・pref FE + year FE)
    (M2) pooled_no_fe: FE なし単純 pooled OLS (host bias 素反映・descriptive)
    (M3) extended_2003_2012: 舟橋+1年拡張 (第67回2012 大分 追加・pref FE + year FE)
    """
    panel = load_score_panel(
        year_min_kai=FUNAHASHI_KAI_RANGE[0],
        year_max_kai=FUNAHASHI_KAI_RANGE[1],
        cup=cup,
    )
    extended_panel = load_score_panel(
        year_min_kai=FUNAHASHI_KAI_RANGE[0],
        year_max_kai=EXTENDED_KAI,
        cup=cup,
    )
    return [
        fit_ols_score(panel, add_pref_fe=True, add_year_fe=True, name="funahashi_base"),
        fit_ols_score(panel, add_pref_fe=False, add_year_fe=False, name="pooled_no_fe"),
        fit_ols_score(extended_panel, add_pref_fe=True, add_year_fe=True, name="extended_2003_2012"),
    ]


def descriptive_host_score_gap(cup: str = "tennou") -> dict:
    """舟橋期間の host vs nonhost の生 score 差 (sanity check・Discussion 用)"""
    panel = load_score_panel(cup=cup)
    host = panel[panel["is_host"]]
    nonhost = panel[~panel["is_host"]]
    return {
        "n_obs": len(panel),
        "n_host": len(host),
        "n_nonhost": len(nonhost),
        "host_mean_score": float(host["score"].mean()),
        "nonhost_mean_score": float(nonhost["score"].mean()),
        "raw_diff": float(host["score"].mean() - nonhost["score"].mean()),
        "funahashi_2016_reference": FUNAHASHI_2016_HOST_COEF,
    }


def results_to_dataframe(results: list[ReplicationResult]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "name": r.name,
            "dv": r.dv,
            "year_min": r.year_min,
            "year_max": r.year_max,
            "coef_is_host": r.coef_is_host,
            "se_is_host": r.se_is_host,
            "p_is_host": r.p_is_host,
            "n_obs": r.n_obs,
            "n_params": r.n_params,
            "n_clusters": r.n_clusters,
            "r2": r.r2,
            "r2_adj": r.r2_adj,
        }
        for r in results
    ])
