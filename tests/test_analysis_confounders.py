"""analysis_confounders.py: Csurilla型段階投入 Robustness"""

import pandas as pd
import pytest

from src.analysis_confounders import (
    STAGES,
    StageSpec,
    compute_attenuation,
    fit_staged_logit_top1,
    fit_staged_ordered_logit,
    run_staged_analysis,
)
from src.analysis_main import build_analysis_frame


class TestStages:
    def test_5_stages_defined(self):
        assert len(STAGES) == 5
        names = [s.name for s in STAGES]
        assert names == ["M1_host_only", "M2_add_pop", "M3_add_gdp", "M4_add_prefFE", "M5_full_FE"]

    def test_stage_progression_monotonic(self):
        for i in range(len(STAGES) - 1):
            a, b = STAGES[i], STAGES[i + 1]
            assert (
                b.add_log_pop >= a.add_log_pop
                and b.add_log_gdp >= a.add_log_gdp
                and b.add_pref_fe >= a.add_pref_fe
                and b.add_year_fe >= a.add_year_fe
            )


class TestFitStagedOrderedLogit:
    def test_M1_host_only(self):
        df = build_analysis_frame(cup="tennou")
        r = fit_staged_ordered_logit(df, STAGES[0])
        assert r.model_type == "ordered_logit"
        assert r.converged
        assert r.coef_is_host < 0
        assert r.p_is_host < 0.01

    def test_M3_add_pop_gdp(self):
        df = build_analysis_frame(cup="tennou")
        r = fit_staged_ordered_logit(df, STAGES[2])
        assert r.coef_is_host < 0


class TestFitStagedLogitTop1:
    def test_M1_host_only(self):
        df = build_analysis_frame(cup="tennou")
        r = fit_staged_logit_top1(df, STAGES[0])
        assert r.converged
        assert r.coef_is_host > 0
        assert r.p_is_host < 0.01


class TestRunStagedAnalysis:
    def test_ordered_returns_5_stages(self):
        results = run_staged_analysis(cup="tennou", dv="rank_ordinal")
        assert len(results) == 5

    def test_top1_returns_5_stages(self):
        results = run_staged_analysis(cup="tennou", dv="top1")
        assert len(results) == 5


class TestComputeAttenuation:
    def test_M1_attenuation_zero(self):
        results = run_staged_analysis(cup="tennou", dv="rank_ordinal")
        df = compute_attenuation(results)
        assert df.iloc[0]["attenuation_vs_M1"] == 0.0

    def test_attenuation_dataframe_shape(self):
        results = run_staged_analysis(cup="tennou", dv="rank_ordinal")
        df = compute_attenuation(results)
        assert df.shape[0] == 5
        assert {"name", "coef_is_host", "attenuation_vs_M1", "converged"}.issubset(df.columns)

    def test_empty_results(self):
        assert compute_attenuation([]).empty
