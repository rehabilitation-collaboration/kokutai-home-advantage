"""analysis_event_study.py: 2層 event-study + parallel trend"""

import numpy as np
import pandas as pd
import pytest

from src.analysis_event_study import (
    LAYER1_SHOCKS,
    LAYER2_SHOCKS,
    build_event_study_frame,
    compute_pre_post_means,
    fit_event_study_lp,
    parallel_trend_test,
)


class TestShocksConstants:
    def test_layer1_single_2002_kochi(self):
        assert LAYER1_SHOCKS == {2002: "高知"}

    def test_layer2_five_shocks(self):
        assert set(LAYER2_SHOCKS.keys()) == {2016, 2017, 2022, 2023, 2024}
        assert LAYER2_SHOCKS[2016] == "岩手"
        assert LAYER2_SHOCKS[2017] == "愛媛"
        assert LAYER2_SHOCKS[2022] == "栃木"
        assert LAYER2_SHOCKS[2023] == "鹿児島"
        assert LAYER2_SHOCKS[2024] == "佐賀"


class TestBuildEventStudyFrame:
    def test_layer1_2002_kochi_frame(self):
        df = build_event_study_frame("L1_pre2005", pre_window=3, post_window=3, cup="tennou")
        assert not df.empty
        assert (df["shock_year"] == 2002).all()
        assert (df["host_pref"] == "高知").all()
        # 47県 × (2002±3=1999..2005=7年) = 329 max・cancelled/special 除外
        assert df["year"].min() == 1999
        assert df["year"].max() == 2005
        assert df["relative_time"].min() == -3
        assert df["relative_time"].max() == 3

    def test_layer2_stacked_5_shocks(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        shock_ids = set(df["shock_id"].unique())
        assert shock_ids == {"shock_2016", "shock_2017", "shock_2022", "shock_2023", "shock_2024"}

    def test_treated_flag_correct(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        # 各 shock で treated=True は 1 pref のみ (host県)
        for shock_id, sub in df.groupby("shock_id"):
            treated_prefs = sub[sub["is_treated"]]["pref_name"].unique()
            assert len(treated_prefs) == 1

    def test_cancelled_excluded(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        assert not df["cancelled"].any()
        assert not df["is_special"].any()

    def test_rank_ordinal_top1_derived(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        assert df["rank_ordinal"].min() >= 1
        assert df["rank_ordinal"].max() <= 9
        assert df["top1"].isin([0, 1]).all()


class TestFitEventStudyLp:
    def test_returns_coef_df_and_result(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        coef_df, result = fit_event_study_lp(df, dv="top1", reference_time=-1)
        assert not coef_df.empty
        assert result is not None
        assert {"relative_time", "coef", "se", "p", "is_reference"}.issubset(coef_df.columns)

    def test_reference_time_zero_coef(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        coef_df, _ = fit_event_study_lp(df, dv="top1", reference_time=-1)
        ref = coef_df[coef_df["relative_time"] == -1]
        assert len(ref) == 1
        assert ref.iloc[0]["coef"] == 0.0
        assert ref.iloc[0]["is_reference"]

    def test_empty_frame_returns_empty(self):
        coef_df, result = fit_event_study_lp(pd.DataFrame(), dv="top1")
        assert coef_df.empty
        assert result is None


class TestParallelTrendTest:
    def test_layer2_returns_wald_stat(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        stat = parallel_trend_test(df, dv="top1", reference_time=-1)
        assert "wald_p" in stat
        assert "n_pre_dummies" in stat
        assert stat["n_pre_dummies"] >= 1
        # wald_p は数値 (nan の可能性は separation で残るが frame は非空)
        assert isinstance(stat["wald_p"], float)

    def test_empty_frame(self):
        stat = parallel_trend_test(pd.DataFrame(), dv="top1")
        assert stat["n_pre_dummies"] == 0


class TestPrePostMeans:
    def test_returns_grouped_summary(self):
        df = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        means = compute_pre_post_means(df, dv="top1")
        assert not means.empty
        assert {"period", "group", "mean", "count"}.issubset(means.columns)
        assert set(means["period"].unique()).issubset({"pre", "post"})
        assert set(means["group"].unique()).issubset({"treated", "control"})


class TestLayerKeyIntegration:
    """v1.2 で発覚した layer key silent fallback bug (Finding #1・Monju B3) の regression guard"""

    def test_layer1_and_layer2_frames_are_structurally_distinct(self):
        # Layer 1 = 2002 単発 shock / Layer 2 = 5 shock stacked → shock_year 集合が別物
        df1 = build_event_study_frame("L1_pre2005", pre_window=3, post_window=3, cup="tennou")
        df2 = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        assert set(df1["shock_year"].unique()) == {2002}
        assert set(df2["shock_year"].unique()) == {2016, 2017, 2022, 2023, 2024}
        # frame shape も別 (Layer 2 は 5 shock stacked で明らかに大きい)
        assert df1.shape[0] < df2.shape[0]

    def test_layer1_wald_stat_differs_from_layer2(self):
        # v1.2 バグ時は Layer 1 が Layer 2 の pixel-identical 複製になっており wald_stat が完全一致していた
        df1 = build_event_study_frame("L1_pre2005", pre_window=3, post_window=3, cup="tennou")
        df2 = build_event_study_frame("L2_post2016", pre_window=3, post_window=3, cup="tennou")
        stat1 = parallel_trend_test(df1, dv="top1", reference_time=-1)
        stat2 = parallel_trend_test(df2, dv="top1", reference_time=-1)
        # 両方数値が出ていること (nan でない) + wald_stat が一致していないこと
        assert not np.isnan(stat1["wald_stat"])
        assert not np.isnan(stat2["wald_stat"])
        assert stat1["wald_stat"] != stat2["wald_stat"]

    def test_get_shocks_rejects_invalid_layer_key(self):
        # silent fallback 廃止・不正 key で ValueError
        from src.analysis_event_study import _get_shocks
        with pytest.raises(ValueError, match="Unknown layer"):
            _get_shocks("layer1")  # 旧 buggy key
        with pytest.raises(ValueError, match="Unknown layer"):
            _get_shocks("layer2")
        with pytest.raises(ValueError, match="Unknown layer"):
            _get_shocks("bogus")

    def test_run_all_models_source_uses_literal_layer_keys(self):
        # run_all_models.py が Literal 型準拠 ("layer1"/"layer2" 旧 key 使わない) の source-level 保証
        from pathlib import Path
        proj_root = Path(__file__).resolve().parents[1]
        src_text = (proj_root / "run_all_models.py").read_text()
        assert '"L1_pre2005"' in src_text
        assert '"L2_post2016"' in src_text
        assert '"layer1"' not in src_text
        assert '"layer2"' not in src_text

    def test_plots_source_uses_literal_layer_keys(self):
        # src/plots.py::plot_fig3_event_study_two_layers が Literal 型準拠の source-level 保証
        from pathlib import Path
        proj_root = Path(__file__).resolve().parents[1]
        plots_text = (proj_root / "src" / "plots.py").read_text()
        assert '"L1_pre2005"' in plots_text
        assert '"L2_post2016"' in plots_text
        assert '"layer1"' not in plots_text
        assert '"layer2"' not in plots_text
