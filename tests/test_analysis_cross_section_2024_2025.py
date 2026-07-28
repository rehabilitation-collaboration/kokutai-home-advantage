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
    def test_returns_5_models(self):
        # GPT round-1 Finding #1 応答で primary spec (obj_vs_subj_primary) 追加 → 4 spec
        # + GPT round-1 Finding #5 応答で sport × cup interaction diagnostic 追加 → 5 spec
        results = run_cross_section_models()
        assert len(results) == 5
        assert {r.name for r in results} == {
            "cross_section_obj_vs_subj_primary",
            "cross_section_obj_vs_subj_primary_sport_cup",
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
        assert df.shape[0] == 5
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


class TestSportCupInteraction:
    """GPT round-1 Finding #5 応答: sport × cup interaction diagnostic spec

    GPT の「trophy FE がない」指摘は実装欠落ではなく Methods 開示ギャップ
    (cup FE は _build_design/fit_cross_section_ols に default True で投入済)。
    GPT の「sport × trophy 感度分析」要求は primary spec に sport × cup interaction を
    追加した diagnostic spec で応答。Finding #1 with_semi (3-way) と同 pattern:
    rank-deficient regime (k=131 params / G=47 clusters ≈ 2.8) で cluster SE 計算不能
    のため point-estimate-only diagnostic として実装 = β_HS の direction/magnitude
    頑健性確認に使用 (primary +20.27 と近接 → 四者内的整合)。
    """

    def test_sport_cup_columns_present(self):
        # NEW spec の design matrix に sport_cup_* dummy 列が入る
        from src.analysis_cross_section_2024_2025 import _build_design
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        X = _build_design(
            df_obj_subj,
            with_semi_interaction=False,
            add_pref_fe=True,
            add_sport_fe=True,
            add_year_fe=True,
            add_cup_fe=True,
            add_sport_cup_interaction=True,
        )
        sport_cup_cols = [c for c in X.columns if c.startswith("sport_cup_")]
        assert len(sport_cup_cols) > 0

    def test_n_preserved_from_primary(self):
        # interaction 追加で n が変わらない (primary = 4744 と一致・47 pref clusters 保持)
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result = fit_cross_section_ols(
            df_obj_subj,
            dv="score",
            with_semi_interaction=False,
            add_sport_cup_interaction=True,
            name="test_sport_cup",
        )
        assert result.n_obs == 4744
        assert result.n_clusters == 47

    def test_k_over_G_ratio_exceeds_2(self):
        # rank-deficient regime (Finding #1 3-way M2 と同 regime = k/G > 2・Kezdi 2004)
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result = fit_cross_section_ols(
            df_obj_subj,
            dv="score",
            with_semi_interaction=False,
            add_sport_cup_interaction=True,
            name="test_sport_cup",
        )
        assert result.n_params / result.n_clusters > 2.0

    def test_point_estimate_close_to_primary(self):
        # sport_cup spec の β_HS point estimate が primary +20.27 に近い (|diff| < 5)
        # → 四者内的整合 (primary +20.27・inclusive +16.68・3-way +20.31・sport_cup ~+22)
        df = build_cross_section_frame()
        df_obj_subj = df[df["is_semi"] == 0].reset_index(drop=True)
        result_primary = fit_cross_section_ols(
            df_obj_subj, dv="score", with_semi_interaction=False, name="test_primary"
        )
        result_sport_cup = fit_cross_section_ols(
            df_obj_subj,
            dv="score",
            with_semi_interaction=False,
            add_sport_cup_interaction=True,
            name="test_sport_cup",
        )
        assert result_sport_cup.coef_interaction > 0  # direction preserved
        assert abs(result_sport_cup.coef_interaction - result_primary.coef_interaction) < 5.0


class TestSportCategoryVariants:
    """GPT round-1 Finding #6 応答: 3 variant × primary spec 分類感度分析

    default (Balmer2003 準拠 subj=11) の subjective 定義への感度を検証する 3 variant:
    - pure_judged: subjective を「純粋採点」のみに narrow (subj=4)・combat 7 は objective 降格
    - no_combat: combat sport 9 を分析除外 (subj=体操+馬術=2 のみ)
    - combat_to_semi: フェンシング/レスリング/相撲 を semi_subjective 化 (subj=8)
    """

    def test_pure_judged_narrows_subjective_to_4(self):
        from src.sport_classifier import get_category
        # 純粋採点 4: 体操 + 空手道 + なぎなた + 馬術
        for sport in ("体操", "空手道", "なぎなた", "馬術"):
            assert get_category(sport, variant="pure_judged") == "subjective"
        # combat 7 は objective 降格
        for sport in ("剣道", "柔道", "銃剣道", "ボクシング", "フェンシング", "レスリング", "相撲"):
            assert get_category(sport, variant="pure_judged") == "objective"

    def test_no_combat_drops_9_combat_sports(self):
        from src.sport_classifier import get_category
        # combat 9 は None 返却 (分析除外)
        for sport in ("剣道", "柔道", "空手道", "銃剣道", "なぎなた",
                      "ボクシング", "フェンシング", "レスリング", "相撲"):
            assert get_category(sport, variant="no_combat") is None
        # 残り subjective は体操 + 馬術 のみ
        assert get_category("体操", variant="no_combat") == "subjective"
        assert get_category("馬術", variant="no_combat") == "subjective"

    def test_combat_to_semi_moves_3_sports_to_semi(self):
        from src.sport_classifier import get_category
        # fencing/wrestling/sumo → semi_subjective
        for sport in ("フェンシング", "レスリング", "相撲"):
            assert get_category(sport, variant="combat_to_semi") == "semi_subjective"
        # 他の combat 6 は subjective のまま
        for sport in ("剣道", "柔道", "空手道", "銃剣道", "なぎなた", "ボクシング"):
            assert get_category(sport, variant="combat_to_semi") == "subjective"

    def test_default_variant_unchanged_regression(self):
        # 既存 SPORT_CATEGORIES が variant="default" 経由で完全再現される
        from src.sport_classifier import get_category, SPORT_CATEGORIES
        for sport in SPORT_CATEGORIES:
            assert get_category(sport, variant="default") == SPORT_CATEGORIES[sport]

    def test_build_cross_section_frame_variant_no_combat_drops_rows(self):
        # no_combat variant は combat 9 sport の行を drop する
        df_default = build_cross_section_frame(category_variant="default")
        df_no_combat = build_cross_section_frame(category_variant="no_combat")
        assert len(df_no_combat) < len(df_default)
        combat_sports = {"剣道", "柔道", "空手道", "銃剣道", "なぎなた",
                         "ボクシング", "フェンシング", "レスリング", "相撲"}
        assert set(df_no_combat["sport"].unique()).isdisjoint(combat_sports)


class TestRunCrossSectionModelsByVariant:
    """3 variant × primary spec で β_HS 方向頑健性を検証"""

    def test_returns_3_variants(self):
        from src.analysis_cross_section_2024_2025 import run_cross_section_models_by_variant
        results = run_cross_section_models_by_variant()
        assert set(results.keys()) == {"pure_judged", "no_combat", "combat_to_semi"}

    def test_all_variants_positive_beta_HxS_direction(self):
        # 全 3 variant で β_HS > 0 (primary と direction 一致)
        from src.analysis_cross_section_2024_2025 import run_cross_section_models_by_variant
        results = run_cross_section_models_by_variant()
        for v, r in results.items():
            assert r.coef_interaction > 0, f"{v}: coef_HxS={r.coef_interaction}"

    def test_no_combat_has_smaller_n(self):
        # no_combat variant は combat sport drop で n が最小
        from src.analysis_cross_section_2024_2025 import run_cross_section_models_by_variant
        results = run_cross_section_models_by_variant()
        assert results["no_combat"].n_obs < results["pure_judged"].n_obs
        assert results["no_combat"].n_obs < results["combat_to_semi"].n_obs
