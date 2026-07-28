"""panel_builder.py の contract テスト"""

import pytest
import pandas as pd

from src.panel_builder import build_ranking_panel, build_host_summary, merge_confounders


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
