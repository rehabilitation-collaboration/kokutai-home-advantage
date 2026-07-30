"""panel_builder.py の contract テスト"""

import pytest
import pandas as pd

from src.panel_builder import build_ranking_panel, build_host_summary, merge_confounders, build_host_rank_panel


class TestRankingPanel:
    @pytest.fixture(scope="class")
    def panel(self):
        return build_ranking_panel()

    def test_shape(self, panel):
        # 78大会 × 2杯 × 47県 = 7332行
        assert len(panel) == 78 * 2 * 47

    def test_columns(self, panel):
        expected = {"pref_code", "pref_name", "kai_num", "kai_label", "year", "cup",
                    "rank", "is_host", "is_special", "cancelled"}
        assert set(panel.columns) == expected

    def test_79_shiga_host_win_tennou(self, panel):
        # 第79回 天皇杯 滋賀 = 1位 + is_host
        row = panel[
            (panel.kai_label == "79") & (panel.cup == "tennou") & (panel.pref_name == "滋賀")
        ].iloc[0]
        assert row["rank"] == 1
        assert bool(row["is_host"])

    def test_79_tokyo_not_host_tennou(self, panel):
        # 第79回 天皇杯 東京 = 2位 + not host
        row = panel[
            (panel.kai_label == "79") & (panel.cup == "tennou") & (panel.pref_name == "東京")
        ].iloc[0]
        assert row["rank"] == 2
        assert not bool(row["is_host"])

    def test_78_saga_host_defeat(self, panel):
        # 第78回 天皇杯 佐賀 = 2位 + is_host (host敗北6ショック年)
        row = panel[
            (panel.kai_label == "78") & (panel.cup == "tennou") & (panel.pref_name == "佐賀")
        ].iloc[0]
        assert row["rank"] == 2
        assert bool(row["is_host"])

    def test_78_tokyo_won_not_host(self, panel):
        row = panel[
            (panel.kai_label == "78") & (panel.cup == "tennou") & (panel.pref_name == "東京")
        ].iloc[0]
        assert row["rank"] == 1
        assert not bool(row["is_host"])

    def test_out_of_top8_none(self, panel):
        # 8位圏外は rank=None
        row = panel[
            (panel.kai_label == "79") & (panel.cup == "tennou") & (panel.pref_name == "沖縄")
        ].iloc[0]
        assert pd.isna(row["rank"])

    def test_special_2023(self, panel):
        # 特別大会レコード = 47県 × 2杯 = 94行
        special = panel[panel.is_special]
        assert len(special) == 47 * 2
        assert (special["kai_label"] == "special_2023").all()
        assert (special["year"] == 2023).all()

    def test_special_kagoshima_is_host(self, panel):
        row = panel[
            (panel.is_special) & (panel.cup == "tennou") & (panel.pref_name == "鹿児島")
        ].iloc[0]
        assert bool(row["is_host"])
        assert row["rank"] == 2  # 東京優勝で鹿児島2位


class TestHostSummary:
    @pytest.fixture(scope="class")
    def summary(self):
        return build_host_summary()

    def test_columns(self, summary):
        expected = {"kai_label", "year", "is_special", "cancelled",
                    "host_rank_tennou", "host_rank_kougou", "host_win_tennou"}
        assert set(summary.columns) == expected

    def test_79_shiga_win(self, summary):
        row = summary[summary.kai_label == "79"].iloc[0]
        assert row["host_rank_tennou"] == 1
        assert bool(row["host_win_tennou"])

    def test_78_saga_defeat(self, summary):
        row = summary[summary.kai_label == "78"].iloc[0]
        assert row["host_rank_tennou"] == 2
        assert not bool(row["host_win_tennou"])  # 6ショック年

    def test_special_2023(self, summary):
        row = summary[summary.kai_label == "special_2023"].iloc[0]
        assert bool(row["is_special"])
        assert not bool(row["host_win_tennou"])  # 特別大会も host敗北

    def test_year_sorted(self, summary):
        years = summary["year"].tolist()
        assert years == sorted(years)


class TestMergeConfounders:
    @pytest.fixture(scope="class")
    def merged(self):
        return merge_confounders()

    def test_row_count_preserved(self, merged):
        assert len(merged) == 7332

    def test_expected_columns_added(self, merged):
        for c in ["population", "gdp_nominal_mil_yen", "log_population", "log_gdp"]:
            assert c in merged.columns

    def test_2011_2022_non_special_fully_covered(self, merged):
        window = merged[(merged.year >= 2011) & (merged.year <= 2022) & (~merged.is_special)]
        assert window.population.notna().all()
        assert window.gdp_nominal_mil_yen.notna().all()

    def test_outside_coverage_all_nan(self, merged):
        pre = merged[merged.year < 2011]
        post = merged[merged.year > 2022]
        assert pre.population.isna().all() and pre.gdp_nominal_mil_yen.isna().all()
        assert post.population.isna().all() and post.gdp_nominal_mil_yen.isna().all()

    def test_log_columns_are_finite_where_data_present(self, merged):
        import numpy as np
        window = merged[(merged.year >= 2011) & (merged.year <= 2022) & (~merged.is_special)]
        assert np.isfinite(window.log_population).all()
        assert np.isfinite(window.log_gdp).all()

    def test_hokkaido_2011_gdp_matches_esri(self, merged):
        row = merged[(merged.pref_code == 1) & (merged.year == 2011) & (merged.cup == "tennou")].iloc[0]
        assert row.gdp_nominal_mil_yen == 18527065  # ESRI 令和4年度版 実データ


class TestHostRankPanel:
    """M2 主分析用パネル: v3 実質 77 大会 (第3-79 回) の host県順位 top1/3/8 真偽検定用"""

    @pytest.fixture(scope="class")
    def panel(self):
        return build_host_rank_panel()

    def test_default_shape_75_kai(self, panel):
        # v3 母集団 = 第3-79 (77 大会) - 第75/76 COVID 中止 (2) = 75 大会 × 2 杯 = 150 行
        assert len(panel) == 150

    def test_columns(self, panel):
        expected = {
            "kai_id", "kai_num", "year", "host_pref", "host_pref_code", "cup",
            "host_rank", "top1_flag", "top3_flag", "top8_flag",
            "is_special", "is_cancelled", "is_winter_only", "is_multi_pref",
        }
        assert set(panel.columns) == expected

    def test_default_excludes_special_and_cancelled(self, panel):
        assert not panel.is_special.any()
        assert not panel.is_cancelled.any()
        assert not panel.is_winter_only.any()

    def test_default_excludes_kai_1_2_80(self, panel):
        kai_nums = set(panel.kai_num.dropna().astype(int).tolist())
        assert 1 not in kai_nums
        assert 2 not in kai_nums
        assert 80 not in kai_nums
        assert min(kai_nums) == 3
        assert max(kai_nums) == 79

    def test_79_shiga_tennou_top1(self, panel):
        # 第79回 滋賀 tennou = 1位 (host 優勝)
        row = panel[(panel.kai_id == "79") & (panel.cup == "tennou")].iloc[0]
        assert row.host_pref == "滋賀"
        assert row.host_rank == 1
        assert bool(row.top1_flag) and bool(row.top3_flag) and bool(row.top8_flag)

    def test_78_saga_tennou_host_defeat_top3(self, panel):
        # 第78回 佐賀 tennou = 2位 (host 敗北6ショック年・ただし top3 圏内)
        row = panel[(panel.kai_id == "78") & (panel.cup == "tennou")].iloc[0]
        assert row.host_pref == "佐賀"
        assert row.host_rank == 2
        assert not bool(row.top1_flag)
        assert bool(row.top3_flag) and bool(row.top8_flag)

    def test_9_hokkaido_regression_guard_uses_main_cup_rank(self, panel):
        # 状態機械化 regression guard: 第9回 tennou の rank は本大会 (夏・秋独立行) から拾う。
        # 旧バグでは冬季ランキング (rank1=北海道) を誤採用していた → 状態機械化で本大会 rank3=北海道 が正解
        row = panel[(panel.kai_id == "9") & (panel.cup == "tennou")].iloc[0]
        assert row.host_pref == "北海道"
        assert row.host_rank == 3

    def test_multi_pref_kai7_uses_first_host_pref(self, panel):
        # 第7回 (福島/宮城/山形 3県共催) → 主催県 = 福島 (KOKUTAI_HOSTS["host_prefs"][0])
        row = panel[(panel.kai_id == "7") & (panel.cup == "tennou")].iloc[0]
        assert row.host_pref == "福島"
        assert bool(row.is_multi_pref)

    def test_multi_pref_kai8_uses_first_host_pref(self, panel):
        # 第8回 (愛媛/香川/徳島/高知 4県共催) → 主催県 = 愛媛
        row = panel[(panel.kai_id == "8") & (panel.cup == "tennou")].iloc[0]
        assert row.host_pref == "愛媛"
        assert bool(row.is_multi_pref)

    def test_include_special_adds_special_2023(self):
        panel = build_host_rank_panel(include_special=True)
        assert len(panel) == 152  # 150 + special_2023 × 2 杯
        specials = panel[panel.is_special]
        assert len(specials) == 2
        assert (specials.kai_id == "special_2023").all()
        assert (specials.host_pref == "鹿児島").all()
        assert specials.kai_num.isna().all()  # 特別大会は kai_num NA

    def test_include_cancelled_adds_kai_75_76(self):
        panel = build_host_rank_panel(include_cancelled=True)
        assert len(panel) == 154  # 150 + 第75/76 × 2 杯
        # 第75 = winter only, 第76 = cancelled
        assert (panel[panel.kai_num == 75].is_winter_only).all()
        assert (panel[panel.kai_num == 76].is_cancelled).all()
        # 中止年は host_pref が rank1-rank8 に不在 → host_rank NA
        assert panel[panel.kai_num.isin([75, 76])].host_rank.isna().all()

    def test_include_both_returns_full_156(self):
        panel = build_host_rank_panel(include_special=True, include_cancelled=True)
        assert len(panel) == 156  # nagano 全体 (77 大会 + special_2023) × 2 杯

    def test_top_flag_monotonicity(self, panel):
        # top1 ⊂ top3 ⊂ top8 (単調性): rank に基づくフラグ整合性
        assert (panel[panel.top1_flag].top3_flag).all()
        assert (panel[panel.top3_flag].top8_flag).all()

    def test_dtypes_nullable(self, panel):
        # kai_num / host_rank は Nullable Int64 (特別大会 NA / top8 圏外 NA 対応)
        assert str(panel.kai_num.dtype) == "Int64"
        assert str(panel.host_rank.dtype) == "Int64"
