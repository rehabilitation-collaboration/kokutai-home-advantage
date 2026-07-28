"""47都道府県 × 大会年パネル構築層

出力パネル (long format):
- pref_code: int (1-47)
- pref_name: str
- kai_num: int or None (特別大会は None)
- kai_label: str ("79", "78", ..., "special_2023")
- year: int
- cup: str ("tennou" or "kougou")
- rank: int or None (1-8, 1-8位圏外は None)
- is_host: bool
- is_special: bool
- cancelled: bool

順序 logit の DV は rank (1-8, 圏外は 8+ or 欠測)。
Balmer2003 準拠 主観判定 vs 客観競技分離検証は、Phase 2 で xls パースを追加して pref×competition パネルを別途構築。
"""

import numpy as np
import pandas as pd

from src.definitions import (
    PREFECTURES,
    PREFECTURE_TO_CODE,
    KOKUTAI_HOSTS,
    KOKUTAI_SPECIAL,
    get_all_host_codes,
)
from src.data_loader import (
    load_esri_gdp_nominal,
    load_esri_population,
    load_nagano_high_rank,
)


def _rank_from_row(row: pd.Series, pref_name: str) -> int | None:
    """順位表 row から pref_name の順位 (1-8) を返す。圏外は None。"""
    for i in range(1, 9):
        if row[f"rank{i}"] == pref_name:
            return i
    return None


def build_ranking_panel() -> pd.DataFrame:
    """長野県体協 高順位ランキング (1-8位) を 47都道府県×大会年パネルに展開

    Returns:
        DataFrame (long format):
        - pref_code (int, 1-47)
        - pref_name (str)
        - kai_num (int or None・特別大会は None)
        - kai_label (str)
        - year (int)
        - cup (str)
        - rank (int, 1-8) or None (圏外)
        - is_host (bool)
        - is_special (bool)
        - cancelled (bool)
    """
    rank_df = load_nagano_high_rank()

    records = []
    for _, row in rank_df.iterrows():
        kai_num_val = row["kai_num"]
        is_special = bool(row["is_special"])

        # kai_num handling
        if is_special:
            kai_num: int | None = None
            kai_label = f"special_{int(row['year'])}"
            special_entry = KOKUTAI_SPECIAL.get(kai_label, {})
            host_codes = [PREFECTURE_TO_CODE[p] for p in special_entry.get("host_prefs", []) if p in PREFECTURE_TO_CODE]
            cancelled = special_entry.get("cancelled", False)
        else:
            kai_num = int(kai_num_val)
            kai_label = str(kai_num)
            host_codes = get_all_host_codes(kai_num)
            cancelled = KOKUTAI_HOSTS.get(kai_num, {}).get("cancelled", False)

        for pref_code, pref_name in PREFECTURES.items():
            rank = _rank_from_row(row, pref_name)
            records.append({
                "pref_code": pref_code,
                "pref_name": pref_name,
                "kai_num": kai_num,
                "kai_label": kai_label,
                "year": int(row["year"]),
                "cup": row["cup"],
                "rank": rank,
                "is_host": pref_code in host_codes,
                "is_special": is_special,
                "cancelled": cancelled,
            })

    return pd.DataFrame(records)


def build_host_summary() -> pd.DataFrame:
    """開催地×大会年サマリー (Phase 2 event-study 分析用)

    Returns:
        DataFrame:
        - kai_label
        - year
        - host_prefs (list)
        - host_rank_tennou (int or None): 開催地の天皇杯順位 (主開催県)
        - host_rank_kougou (int or None): 開催地の皇后杯順位
        - host_win_tennou (bool): 開催地が天皇杯1位取得
        - is_special
        - cancelled
    """
    panel = build_ranking_panel()

    # 開催地行のみ抽出
    host_rows = panel[panel["is_host"]].copy()

    # kai_label + cup で pivot して主開催県の順位を取る
    summary = (
        host_rows.groupby(["kai_label", "year", "cup", "is_special", "cancelled"], dropna=False)
        .agg(host_rank=("rank", "min"))  # 複数県共催時は最高順位
        .reset_index()
    )

    tennou = summary[summary.cup == "tennou"].rename(columns={"host_rank": "host_rank_tennou"}).drop(columns=["cup"])
    kougou = summary[summary.cup == "kougou"].rename(columns={"host_rank": "host_rank_kougou"}).drop(columns=["cup"])

    merged = tennou.merge(kougou, on=["kai_label", "year", "is_special", "cancelled"], how="outer")
    merged["host_win_tennou"] = merged["host_rank_tennou"] == 1

    return merged.sort_values("year").reset_index(drop=True)


def merge_confounders(
    panel: pd.DataFrame | None = None,
    population_df: pd.DataFrame | None = None,
    gdp_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """ranking_panel に population/GDP を merge + 対数化列 (log_population, log_gdp) 追加

    Csurilla型交絡変数統制モデル (人口対数 + 県内GDP対数) の準備層。
    ESRI 県民経済計算 (2011-2022 の 12年) を主推定期間として merge。
    カバー範囲外の年 (2010以前・2023以降) は population/GDP が NaN のまま。

    Args:
        panel: build_ranking_panel() の出力. None なら内部で構築
        population_df: load_esri_population() 相当. None ならデフォルト load
        gdp_df: load_esri_gdp_nominal() 相当. None ならデフォルト load

    Returns:
        panel + [population, gdp_nominal_mil_yen, log_population, log_gdp]
    """
    if panel is None:
        panel = build_ranking_panel()
    if population_df is None:
        population_df = load_esri_population()
    if gdp_df is None:
        gdp_df = load_esri_gdp_nominal()

    merged = panel.merge(
        population_df[["pref_code", "year", "population"]],
        on=["pref_code", "year"], how="left",
    ).merge(
        gdp_df[["pref_code", "year", "gdp_nominal_mil_yen"]],
        on=["pref_code", "year"], how="left",
    )
    merged["log_population"] = np.log(merged["population"].where(merged["population"] > 0))
    merged["log_gdp"] = np.log(merged["gdp_nominal_mil_yen"].where(merged["gdp_nominal_mil_yen"] > 0))
    return merged
