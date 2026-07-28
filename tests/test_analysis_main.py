"""analysis_main.py: 順序 logit + 二値 logit + 記述統計"""

import pandas as pd
import pytest

from src.analysis_main import (
    RANK_OUTSIDE,
    ModelResult,
    build_analysis_frame,
    descriptive_host_summary,
    fit_logit,
    fit_ordered_logit,
    results_to_dataframe,
    run_main_models,
)


class TestBuildAnalysisFrame:
    def test_default_tennou_shape(self):
        df = build_analysis_frame(cup="tennou")
        assert df.shape[0] == 423  # 47県 × 9年 (2012-2022 11年 - COVID 2年)

    def test_derived_columns_exist(self):
        df = build_analysis_frame(cup="tennou")
        required = {"rank_ordinal", "top1", "top8", "is_host_int", "log_population", "log_gdp"}
        assert required.issubset(df.columns)

    def test_rank_ordinal_encoding(self):
        df = build_analysis_frame(cup="tennou")
        assert df["rank_ordinal"].dtype.kind == "i"
        assert df["rank_ordinal"].min() == 1
        assert df["rank_ordinal"].max() == RANK_OUTSIDE
        assert (df.loc[df["rank"].isna(), "rank_ordinal"] == RANK_OUTSIDE).all()

    def test_top1_top8_counts(self):
        df = build_analysis_frame(cup="tennou")
        assert df["top1"].sum() == 9
        assert df["top8"].sum() == 71  # 8×9 - 2016年6位欠測1件

    def test_is_host_true_count(self):
        df = build_analysis_frame(cup="tennou")
        assert df["is_host"].sum() == 9

    def test_special_and_cancelled_excluded(self):
        df = build_analysis_frame(cup="tennou")
        assert not df["is_special"].any()
        assert not df["cancelled"].any()

    def test_cup_both_doubles_size(self):
        df = build_analysis_frame(cup="both")
        assert df.shape[0] == 846
        assert set(df["cup"].unique()) == {"tennou", "kougou"}

    def test_year_range_outside_coverage_empty(self):
        df = build_analysis_frame(cup="tennou", year_min=2000, year_max=2010)
        assert df.shape[0] == 0

    def test_log_pop_and_log_gdp_notna(self):
        df = build_analysis_frame(cup="tennou")
        assert df["log_population"].notna().all()
        assert df["log_gdp"].notna().all()


class TestFitOrderedLogit:
    def test_pooled_converges_and_host_effect_negative(self):
        df = build_analysis_frame(cup="tennou")
        result = fit_ordered_logit(df, add_pref_fe=False, add_year_fe=False, name="test_pooled")
        assert isinstance(result, ModelResult)
        assert result.model_type == "ordered_logit"
        assert result.converged
        assert result.coef_is_host < 0
        assert result.p_is_host < 0.01
        assert result.n_obs == 423

    def test_prefFE_yearFE_sign_preserved(self):
        df = build_analysis_frame(cup="tennou")
        result = fit_ordered_logit(df, add_pref_fe=True, add_year_fe=True, name="test_fe")
        assert result.coef_is_host < 0


class TestFitLogit:
    def test_top1_pooled_converges_and_host_effect_positive(self):
        df = build_analysis_frame(cup="tennou")
        result = fit_logit(df, dv="top1", add_pref_fe=False, add_year_fe=False, name="test_top1")
        assert result.model_type == "logit"
        assert result.dv == "top1"
        assert result.converged
        assert result.coef_is_host > 0
        assert result.p_is_host < 0.01

    def test_top8_pooled_sign_positive(self):
        df = build_analysis_frame(cup="tennou")
        result = fit_logit(df, dv="top8", add_pref_fe=False, add_year_fe=False, name="test_top8")
        assert result.coef_is_host > 0


class TestRunMainModels:
    def test_returns_4_models(self):
        results = run_main_models(cup="tennou")
        assert len(results) == 4
        names = [r.name for r in results]
        assert set(names) == {
            "ordered_pooled",
            "ordered_prefFE_yearFE",
            "logit_top1_pooled",
            "logit_top1_prefFE_yearFE",
        }

    def test_pooled_models_all_significant(self):
        results = run_main_models(cup="tennou")
        pooled = [r for r in results if r.name.endswith("_pooled")]
        assert len(pooled) == 2
        for r in pooled:
            assert r.p_is_host < 0.01, f"{r.name}: p={r.p_is_host}"


class TestClusteredSE:
    """Finding #17: pooled specifications must use prefecture-clustered SE (47 clusters)

    Repeated-observations across years per prefecture violates the independence assumption
    of Fisher-information SE. run_main_models() must therefore apply cov_type='cluster'
    with groups=pref_code to the pooled ordered logit and pooled top-1 logit.
    """

    def test_pooled_models_use_cluster_cov(self):
        results = run_main_models(cup="tennou")
        pooled = [r for r in results if r.name.endswith("_pooled")]
        assert len(pooled) == 2
        for r in pooled:
            assert getattr(r.result_obj, "cov_type", None) == "cluster", (
                f"{r.name}: expected cov_type='cluster' but got {getattr(r.result_obj, 'cov_type', None)}"
            )

    def test_pooled_cluster_se_differs_from_fisher(self):
        df = build_analysis_frame(cup="tennou")
        # top1 pooled: Fisher SE ≈ 2.80, clustered SE ≈ 2.13 (Fisher overstates)
        fisher = fit_logit(df, dv="top1", name="fisher_top1")
        clustered = fit_logit(df, dv="top1", name="clustered_top1", cluster_groups=df["pref_code"])
        assert abs(fisher.se_is_host - clustered.se_is_host) > 0.3, (
            f"Fisher/clustered SE should differ meaningfully: "
            f"Fisher={fisher.se_is_host:.4f} vs clustered={clustered.se_is_host:.4f}"
        )
        # ordered pooled: Fisher SE ≈ 1.54, clustered SE ≈ 2.03 (Fisher understates)
        fisher_ord = fit_ordered_logit(df, name="fisher_ord")
        clustered_ord = fit_ordered_logit(df, name="clustered_ord", cluster_groups=df["pref_code"])
        assert abs(fisher_ord.se_is_host - clustered_ord.se_is_host) > 0.3, (
            f"ordered Fisher/clustered SE should differ meaningfully: "
            f"Fisher={fisher_ord.se_is_host:.4f} vs clustered={clustered_ord.se_is_host:.4f}"
        )

    def test_fe_models_remain_nonrobust(self):
        # FE モデルは pref FE と cluster が冗長 + separation blowup で SE=NaN のため
        # clustered 化しない。cov_type='nonrobust' のままであることを保証。
        results = run_main_models(cup="tennou")
        fe = [r for r in results if "FE" in r.name]
        assert len(fe) == 2
        for r in fe:
            assert getattr(r.result_obj, "cov_type", None) == "nonrobust", (
                f"{r.name}: FE models should remain nonrobust (Fisher info)"
            )

    def test_pooled_headline_directions_preserved_under_cluster(self):
        # 論文正確性最優先: clustered SE 化しても headline 方向は不変
        # ordered_pooled coef < 0 (better rank), logit_top1_pooled coef > 0 (higher top-1 prob)
        # 両モデルとも clustered p < 0.001 で有意
        results = run_main_models(cup="tennou")
        by_name = {r.name: r for r in results}
        assert by_name["ordered_pooled"].coef_is_host < 0
        assert by_name["ordered_pooled"].p_is_host < 0.001
        assert by_name["logit_top1_pooled"].coef_is_host > 0
        assert by_name["logit_top1_pooled"].p_is_host < 0.001


class TestResultsToDataframe:
    def test_shape_and_columns(self):
        results = run_main_models(cup="tennou")
        df = results_to_dataframe(results)
        assert df.shape == (4, 10)
        expected_cols = {"name", "model_type", "dv", "coef_is_host", "se_is_host",
                         "p_is_host", "n_obs", "n_params", "converged", "llf"}
        assert set(df.columns) == expected_cols


class TestDescriptiveHostSummary:
    def test_tennou_2012_2022_dominance(self):
        s = descriptive_host_summary(cup="tennou")
        assert s["n_obs"] == 423
        assert s["n_host"] == 9
        assert s["n_nonhost"] == 414
        assert s["n_host_top1"] == 6  # 岐阜/東京/長崎/和歌山/福井/茨城
        assert s["n_host_top8"] == 9  # 全 host が top8 入賞 (complete separation)
        assert s["n_nonhost_top1"] == 3  # 東京 x 3年 (2016/2017/2022)
        assert abs(s["host_top1_rate"] - 6 / 9) < 1e-9
        assert s["host_top8_rate"] == 1.0
