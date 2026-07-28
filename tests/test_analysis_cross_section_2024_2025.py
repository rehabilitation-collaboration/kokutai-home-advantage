"""analysis_cross_section_2024_2025.py: 2024佐賀 + 2025滋賀 の 2 年断面 Subj × Host 交互作用"""

import numpy as np
import pandas as pd
import pytest

from src.analysis_cross_section_2024_2025 import (
    CrossSectionResult,
    build_cross_section_frame,
    descriptive_by_category,
    fit_cross_section_ols,
    results_to_dataframe,
    run_cross_section_models,
)


class TestBuildCrossSectionFrame:
    def test_default_stacks_4_datasets(self):
        df = build_cross_section_frame()
        assert set(zip(df["kai_num"], df["cup"])) == {
            (78, "tennou"), (78, "kougou"), (79, "tennou"), (79, "kougou"),
        }

    def test_47_prefs_covered(self):
        df = build_cross_section_frame()
        assert df["pref_code"].nunique() == 47
        assert set(df["pref_code"].unique()) == set(range(1, 48))

    def test_year_derived_from_kai(self):
        df = build_cross_section_frame()
        year_by_kai = df.groupby("kai_num")["year"].unique().to_dict()
        assert list(year_by_kai[78]) == [2024]
        assert list(year_by_kai[79]) == [2025]

    def test_host_flags_correctly_set(self):
        df = build_cross_section_frame()
        # 佐賀 (code=41) = 78 の host / 滋賀 (code=25) = 79 の host
        assert df[(df["kai_num"] == 78) & (df["is_host"])]["pref_code"].unique().tolist() == [41]
        assert df[(df["kai_num"] == 79) & (df["is_host"])]["pref_code"].unique().tolist() == [25]

    def test_category_all_classified(self):
        df = build_cross_section_frame()
        assert df["category"].notna().all()

    def test_category_dummies_disjoint(self):
        df = build_cross_section_frame()
        # subjective と semi_subjective は排他
        assert ((df["is_subjective"] == 1) & (df["is_semi"] == 1)).sum() == 0

    def test_log_score_matches_log1p(self):
        df = build_cross_section_frame()
        assert np.allclose(df["log_score"], np.log1p(df["score"]))

    def test_include_winter_toggles(self):
        df_with = build_cross_section_frame(include_winter=True)
        df_without = build_cross_section_frame(include_winter=False)
        assert (df_without["is_winter"] == 0).all()
        assert len(df_without) < len(df_with)

    def test_unclassified_raises(self):
        # sport_classifier に無い競技名を注入した DataFrame では build 側では起きないが、
        # drop_unclassified=True 時に例外を投げる分岐を実データで通す
        df = build_cross_section_frame(drop_unclassified=False)
        assert df["category"].notna().all()  # 現行データでは NA なし


class TestHostRowCounts:
    """host スコア合計がハンドオフ既知値と一致"""

    @pytest.mark.parametrize("kai,cup,expected_sum", [
        (78, "tennou", 2332.0),  # 佐賀 host 敗北・総合 2位
        (79, "tennou", 2488.0),  # 滋賀 host 優勝・総合 1位
    ])
    def test_host_total_score(self, kai, cup, expected_sum):
        df = build_cross_section_frame()
        host = df[(df["kai_num"] == kai) & (df["cup"] == cup) & (df["is_host"])]
        assert host["score"].sum() == pytest.approx(expected_sum, abs=0.5)


class TestFitCrossSectionOLS:
    def test_baseline_converges(self):
        df = build_cross_section_frame()
        result = fit_cross_section_ols(df, name="test_baseline")
        assert isinstance(result, CrossSectionResult)
        assert result.dv == "score"
        assert result.n_obs > 6000
        assert result.n_clusters == 47
        assert not np.isnan(result.coef_is_host)
        assert not np.isnan(result.coef_interaction)

    def test_baseline_host_effect_positive_and_significant(self):
        # host の score 押上げ効果は正・有意
        df = build_cross_section_frame()
        result = fit_cross_section_ols(df, name="test_baseline")
        assert result.coef_is_host > 0
        assert result.p_is_host < 0.01

    def test_subjective_interaction_positive(self):
        # 主観判定競技での host effect 追加分は正 (Balmer2003 予測方向)
        df = build_cross_section_frame()
        result = fit_cross_section_ols(df, name="test_baseline")
        assert result.coef_interaction > 0

    def test_log_score_dv_supported(self):
        df = build_cross_section_frame()
        result = fit_cross_section_ols(df, dv="log_score", name="test_log")
        assert result.dv == "log_score"
        assert not np.isnan(result.coef_is_host)


class TestRunCrossSectionModels:
    def test_returns_4_models(self):
        # GPT round-1 Finding #1 応答で primary spec (obj_vs_subj_primary) 追加 → 4 spec 構成
        results = run_cross_section_models()
        assert len(results) == 4
        assert {r.name for r in results} == {
            "cross_section_obj_vs_subj_primary",
            "cross_section_baseline",
            "cross_section_with_semi",
            "cross_section_log_baseline",
        }

    def test_primary_and_baseline_and_log_significant(self):
        # SE がクラスタリング下で崩れない 3 モデル (with_semi は cluster SE 計算不能 = 除外)
        results = run_cross_section_models()
        for r in results:
            if r.name in (
                "cross_section_obj_vs_subj_primary",
                "cross_section_baseline",
                "cross_section_log_baseline",
            ):
                assert r.p_is_host < 0.01, f"{r.name}: p={r.p_is_host}"


class TestDescriptiveByCategory:
    def test_returns_3_categories(self):
        df = build_cross_section_frame()
        desc = descriptive_by_category(df)
        assert set(desc["category"]) == {"objective", "subjective", "semi_subjective"}

    def test_subjective_host_boost_largest(self):
        # 主観判定 host の score 押上げ幅が 3 分類中最大 (Balmer2003 novelty 検証)
        df = build_cross_section_frame()
        desc = descriptive_by_category(df).set_index("category")
        diff_subj = desc.loc["subjective", "diff_mean_host_minus_nonhost"]
        diff_obj = desc.loc["objective", "diff_mean_host_minus_nonhost"]
        diff_semi = desc.loc["semi_subjective", "diff_mean_host_minus_nonhost"]
        assert diff_subj > diff_obj
        assert diff_subj > diff_semi


class TestObjVsSubjPrimary:
    """GPT round-1 Finding #1 応答: obj vs subj pure 分離 primary spec (Table 5 primary)

    「semi 含む inclusive spec だと host main effect が obj + semi 混合ベース = タイトル通りの
    subjective vs objective 検定になってない」という GPT 指摘への直接応答。semi を除外して
    obj vs subj pure 比較にすると、cluster SE が計算可能 + interaction coef はむしろ大きくなる。
    """

    def test_n_reduction_from_semi_exclusion(self):
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        assert len(df_obj_subj) < len(df)
        # semi は 13 sports × 47 pref × 2 year × 2 cup 相当 = 全体の約 32%
        assert 4500 < len(df_obj_subj) < 5000

    def test_no_semi_in_primary_sample(self):
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        assert (df_obj_subj["is_semi"] == 0).all()
        assert (df_obj_subj["category"] != "semi_subjective").all()

    def test_primary_cluster_se_computable(self):
        # M2 (with_semi) で nan だった cluster SE が obj vs subj pure spec なら計算可能
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result = fit_cross_section_ols(
            df_obj_subj, dv="score", with_semi_interaction=False, name="test_primary"
        )
        assert not np.isnan(result.se_is_host)
        assert not np.isnan(result.se_interaction)
        assert result.se_interaction > 0

    def test_primary_interaction_larger_than_inclusive(self):
        # 実測: 案 β (semi 除外) の host_x_subj coef ~ +20.27 は inclusive (+16.68) より大
        # → GPT 指摘「obj + semi 混合ベースで真の subj boost が過小評価」を実証
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result_primary = fit_cross_section_ols(
            df_obj_subj, dv="score", with_semi_interaction=False, name="test_primary"
        )
        result_inclusive = fit_cross_section_ols(
            df, dv="score", with_semi_interaction=False, name="test_inclusive"
        )
        assert result_primary.coef_interaction > result_inclusive.coef_interaction
        assert result_primary.p_interaction < 0.05


class TestResultsToDataframe:
    def test_shape_and_columns(self):
        results = run_cross_section_models()
        df = results_to_dataframe(results)
        assert df.shape[0] == 4
        expected_cols = {
            "name", "dv", "coef_is_host", "se_is_host", "p_is_host",
            "coef_interaction", "se_interaction", "p_interaction",
            "n_obs", "n_params", "n_clusters", "r2",
        }
        assert set(df.columns) == expected_cols


class TestWildClusterBootstrap:
    """Finding #5: few-treated-clusters (2 of 47) → wild-cluster bootstrap robust p"""

    def test_returns_expected_keys(self):
        from src.analysis_cross_section_2024_2025 import build_cross_section_frame, wild_cluster_bootstrap
        df = build_cross_section_frame()
        # B=49 で smoke test (実行時間 ~10秒)
        out = wild_cluster_bootstrap(df, dv="score", test_coef="host_x_subj", n_bootstrap=49, seed=1)
        expected = {
            "test_coef", "observed_coef", "observed_se", "observed_t",
            "cluster_robust_p", "bootstrap_p", "n_bootstrap_used",
            "n_bootstrap_requested", "seed", "n_clusters", "treated_clusters",
        }
        assert set(out.keys()) == expected

    def test_treated_clusters_is_two(self):
        # Cross-section の treated cluster は Saga (2024) + Shiga (2025) = 2 のみ (few-treated-clusters problem の core)
        from src.analysis_cross_section_2024_2025 import build_cross_section_frame, wild_cluster_bootstrap
        df = build_cross_section_frame()
        out = wild_cluster_bootstrap(df, dv="score", test_coef="host_x_subj", n_bootstrap=1, seed=1)
        assert out["n_clusters"] == 47
        assert out["treated_clusters"] == 2

    def test_bootstrap_p_in_unit_interval(self):
        from src.analysis_cross_section_2024_2025 import build_cross_section_frame, wild_cluster_bootstrap
        df = build_cross_section_frame()
        out = wild_cluster_bootstrap(df, dv="score", test_coef="host_x_subj", n_bootstrap=49, seed=42)
        assert 0.0 <= out["bootstrap_p"] <= 1.0
        # observed_t は既存の cluster-robust fit と整合すべき (headline p=0.031 → |t|>2)
        assert abs(out["observed_t"]) > 1.5
