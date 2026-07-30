"""tests for src/analysis_main_v3.py — v3 M2 主分析"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from src.analysis_main_v3 import (
    ERA_ORDER,
    RANK_OUTSIDE,
    chi_square_era_comparison,
    descriptive_by_era,
    load_v3_panel,
    one_sample_proportion_test,
    permutation_test,
    run_all_v3_analyses,
    run_ordered_logit_v3,
    _classify_era,
)


@pytest.fixture(scope="module")
def panel() -> pd.DataFrame:
    return load_v3_panel()


class TestLoadV3Panel:
    def test_shape_150_rows(self, panel: pd.DataFrame):
        assert panel.shape == (150, 16)

    def test_has_era_and_rank_ordinal(self, panel: pd.DataFrame):
        assert "era" in panel.columns
        assert "rank_ordinal" in panel.columns

    def test_era_distribution(self, panel: pd.DataFrame):
        # early=30大会×2杯=60, golden=38×2=76, shock=7×2=14
        counts = panel["era"].value_counts().to_dict()
        assert counts["early"] == 60
        assert counts["golden"] == 76
        assert counts["shock"] == 14

    def test_rank_ordinal_na_maps_to_9(self, panel: pd.DataFrame):
        na_rows = panel[panel["host_rank"].isna()]
        assert (na_rows["rank_ordinal"] == RANK_OUTSIDE).all()

    def test_rank_ordinal_domain(self, panel: pd.DataFrame):
        # 実観測 = {1,2,3,4,5,8,9} (6,7 未観測)
        assert set(panel["rank_ordinal"].unique()).issubset({1, 2, 3, 4, 5, 6, 7, 8, 9})


class TestClassifyEra:
    def test_early_boundary(self):
        assert _classify_era(1948) == "early"
        assert _classify_era(1977) == "early"

    def test_golden_boundary(self):
        assert _classify_era(1978) == "golden"
        assert _classify_era(2015) == "golden"

    def test_shock_boundary(self):
        assert _classify_era(2016) == "shock"
        assert _classify_era(2025) == "shock"


class TestDescriptiveByEra:
    def test_returns_8_rows(self, panel: pd.DataFrame):
        # 4 era-groups (early/golden/shock/all) × 2 cup = 8 rows
        d = descriptive_by_era(panel)
        assert len(d) == 8

    def test_all_row_matches_totals(self, panel: pd.DataFrame):
        d = descriptive_by_era(panel)
        all_tennou = d[(d["era"] == "all") & (d["cup"] == "tennou")].iloc[0]
        assert all_tennou["n_kai"] == 75
        assert all_tennou["n_top1"] == 57
        assert all_tennou["n_top3"] == 69
        assert all_tennou["n_top8"] == 70

    def test_golden_tennou_top1_high(self, panel: pd.DataFrame):
        # Background 節: golden 期 host 優勝率 97.30%
        d = descriptive_by_era(panel)
        row = d[(d["era"] == "golden") & (d["cup"] == "tennou")].iloc[0]
        assert row["rate_top1"] >= 0.90  # 実データ 0.9737

    def test_shock_tennou_top1_low(self, panel: pd.DataFrame):
        # 敗北 6 ショック期 tennou top1 = 3/7 = 42.9%
        d = descriptive_by_era(panel)
        row = d[(d["era"] == "shock") & (d["cup"] == "tennou")].iloc[0]
        assert row["rate_top1"] <= 0.50


class TestOneSampleProportionTest:
    def test_top1_tennou_all_rejects_null(self, panel: pd.DataFrame):
        r = one_sample_proportion_test(panel, 1, cup="tennou", era="all")
        assert r["n"] == 75
        assert r["n_success"] == 57
        assert r["null_rate"] == pytest.approx(1 / 47, rel=1e-6)
        assert r["p_value_greater"] < 1e-50
        assert r["ci_wilson_low"] > 0.60
        # 両側 Wilson CI なので上限 < 1.0 (code review P1 regression guard)
        assert r["ci_wilson_high"] < 1.0
        assert r["ci_wilson_low"] < r["observed_rate"] < r["ci_wilson_high"]

    def test_null_rate_scales_with_threshold(self, panel: pd.DataFrame):
        r1 = one_sample_proportion_test(panel, 1, cup="tennou", era="all")
        r3 = one_sample_proportion_test(panel, 3, cup="tennou", era="all")
        r8 = one_sample_proportion_test(panel, 8, cup="tennou", era="all")
        assert r1["null_rate"] == pytest.approx(1 / 47)
        assert r3["null_rate"] == pytest.approx(3 / 47)
        assert r8["null_rate"] == pytest.approx(8 / 47)

    def test_excess_positive_all_thresholds(self, panel: pd.DataFrame):
        for k in [1, 3, 8]:
            for cup in ["tennou", "kougou"]:
                r = one_sample_proportion_test(panel, k, cup=cup, era="all")  # type: ignore
                assert r["excess"] > 0.5, f"k={k} cup={cup} excess too low"

    def test_shock_top1_still_greater_than_null(self, panel: pd.DataFrame):
        # shock 期でも観測 42.9% >> 1/47=2.1% なので有意
        r = one_sample_proportion_test(panel, 1, cup="tennou", era="shock")
        assert r["n"] == 7
        assert r["p_value_greater"] < 0.001

    def test_empty_group_returns_nan(self, panel: pd.DataFrame):
        empty = panel[panel["year"] > 3000]
        r = one_sample_proportion_test(empty, 1, cup="tennou", era="all")
        assert r["n"] == 0
        assert math.isnan(r["observed_rate"])

    def test_null_rate_uses_n_states_46(self, panel: pd.DataFrame):
        # M3-T1: 1972 沖縄復帰前 sensitivity。n_states=46 で null_rate = k/46
        r1 = one_sample_proportion_test(panel, 1, cup="tennou", era="early", n_states=46)
        r3 = one_sample_proportion_test(panel, 3, cup="tennou", era="early", n_states=46)
        r8 = one_sample_proportion_test(panel, 8, cup="tennou", era="early", n_states=46)
        assert r1["n_states"] == 46
        assert r1["null_rate"] == pytest.approx(1 / 46)
        assert r3["null_rate"] == pytest.approx(3 / 46)
        assert r8["null_rate"] == pytest.approx(8 / 46)

    def test_default_n_states_is_47(self, panel: pd.DataFrame):
        # n_states 未指定で従来通り 47 が使われる (backward compat regression guard)
        r = one_sample_proportion_test(panel, 1, cup="tennou", era="all")
        assert r["n_states"] == 47
        assert r["null_rate"] == pytest.approx(1 / 47)

    def test_early_era_46_vs_47_marginal_impact(self, panel: pd.DataFrame):
        # handoff 既知の問題「46/47 沖縄穴」の marginal 性を実データで regression guard。
        # 46 と 47 の p_value_greater は両方 <0.001 で結論不変・excess 差 <0.02
        for cup in ["tennou", "kougou"]:
            r46 = one_sample_proportion_test(panel, 1, cup=cup, era="early", n_states=46)  # type: ignore
            r47 = one_sample_proportion_test(panel, 1, cup=cup, era="early", n_states=47)  # type: ignore
            assert r46["p_value_greater"] < 0.001, f"cup={cup} 46 states p not sig"
            assert r47["p_value_greater"] < 0.001, f"cup={cup} 47 states p not sig"
            assert abs(r46["excess"] - r47["excess"]) < 0.02, f"cup={cup} excess drift too large"


class TestPermutationTest:
    def test_top1_tennou_p_lower_bound(self):
        r = permutation_test(1, cup="tennou", n_perm=1000, seed=0)
        assert r["n_events"] == 75
        assert r["obs_count"] == 57
        # Monte Carlo 下限補正 p = 1/(n_perm+1) = 0.000999... (真の 0 は取れない)
        assert r["p_value_permutation"] == pytest.approx(1 / 1001, abs=1e-9)
        assert r["null_mean"] < 0.10

    def test_top8_kougou_p_lower_bound(self):
        r = permutation_test(8, cup="kougou", n_perm=1000, seed=0)
        assert r["obs_rate"] > 0.90
        assert r["null_mean"] < 0.30  # ~ 8/47*factor
        assert r["p_value_permutation"] == pytest.approx(1 / 1001, abs=1e-9)

    def test_null_mean_matches_analytic(self):
        # permutation null_mean ≈ k/47 (with slight variance due to ties)
        r = permutation_test(1, cup="tennou", n_perm=10_000, seed=0)
        assert r["null_mean"] == pytest.approx(1 / 47, abs=0.01)

    def test_reproducibility_with_seed(self):
        r1 = permutation_test(1, cup="tennou", n_perm=500, seed=42)
        r2 = permutation_test(1, cup="tennou", n_perm=500, seed=42)
        assert r1["null_mean"] == r2["null_mean"]


class TestChiSquareEraComparison:
    def test_top1_tennou_significant(self, panel: pd.DataFrame):
        r = chi_square_era_comparison(panel, 1, cup="tennou")
        # early=56.7% / golden=97.4% / shock=42.9% で非単調 → χ² 有意
        assert r["chi2"] > 15
        assert r["chi2_dof"] == 2
        assert r["chi2_p"] < 0.001

    def test_pairwise_golden_vs_early_and_shock_significant(self, panel: pd.DataFrame):
        r = chi_square_era_comparison(panel, 1, cup="tennou")
        assert r["pairwise_fisher"]["early_vs_golden"] < 0.001
        assert r["pairwise_fisher"]["golden_vs_shock"] < 0.05

    def test_early_vs_shock_not_significant(self, panel: pd.DataFrame):
        # 両端は差なし = golden 期の突出を示す
        r = chi_square_era_comparison(panel, 1, cup="tennou")
        assert r["pairwise_fisher"]["early_vs_shock"] > 0.10

    def test_rates_dict_covers_3_eras(self, panel: pd.DataFrame):
        r = chi_square_era_comparison(panel, 1, cup="tennou")
        for era in ERA_ORDER:
            assert era in r["rates"]


class TestOrderedLogit:
    def test_pooled_converged(self, panel: pd.DataFrame):
        r = run_ordered_logit_v3(panel, cup_mode="pooled")
        assert r["converged"]
        assert r["n_obs"] == 150

    def test_pooled_era_golden_negative_significant(self, panel: pd.DataFrame):
        # golden 期は host_rank が有意に低い (= 良い rank = 負係数)
        r = run_ordered_logit_v3(panel, cup_mode="pooled")
        assert r["params"]["era_golden"] < 0
        assert r["pvalues"]["era_golden"] < 0.05

    def test_pooled_cup_tennou_negative_significant(self, panel: pd.DataFrame):
        # tennou (男女総合) の方が rank 良い
        r = run_ordered_logit_v3(panel, cup_mode="pooled")
        assert r["params"]["cup_tennou"] < 0
        assert r["pvalues"]["cup_tennou"] < 0.05

    def test_tennou_only_converged(self, panel: pd.DataFrame):
        r = run_ordered_logit_v3(panel, cup_mode="tennou")
        assert r["converged"]
        assert r["n_obs"] == 75


class TestRunAllV3Analyses:
    def test_returns_all_sections(self):
        out = run_all_v3_analyses(seed=0, n_perm=200)
        assert "panel_shape" in out
        assert "descriptive_by_era" in out
        assert "one_sample_tests" in out
        assert "permutation_tests" in out
        assert "era_chi_square" in out
        assert "ordered_logit" in out
        assert "sensitivity_46_states" in out
        # 3 threshold × 4 era × 3 cup = 36 one-sample tests
        assert len(out["one_sample_tests"]) == 36
        # 3 threshold × 2 cup = 6 permutation tests
        assert len(out["permutation_tests"]) == 6
        # 3 threshold × 3 cup = 9 era-chi2 tests
        assert len(out["era_chi_square"]) == 9
        # 3 cup mode = 3 ordered logit
        assert len(out["ordered_logit"]) == 3
        # M3-T1: 3 threshold × 3 cup = 9 sensitivity (early era only, n_states=46)
        assert len(out["sensitivity_46_states"]) == 9
        for r in out["sensitivity_46_states"]:
            assert r["n_states"] == 46
            assert r["era"] == "early"
