"""analysis_replication.py: 舟橋2016 (2003-2011) 再現 + 2012 拡張"""

import numpy as np
import pandas as pd
import pytest

from src.analysis_replication import (
    EXTENDED_KAI,
    FUNAHASHI_2016_HOST_COEF,
    FUNAHASHI_KAI_RANGE,
    ReplicationResult,
    descriptive_host_score_gap,
    fit_ols_score,
    load_score_panel,
    results_to_dataframe,
    run_replication_models,
)


class TestLoadScorePanel:
    def test_default_shape_423_obs(self):
        panel = load_score_panel(cup="tennou")
        assert panel.shape[0] == 423  # 47県 × 9年 (第58-66回・2003-2011)

    def test_47_prefs_9_years(self):
        panel = load_score_panel(cup="tennou")
        assert panel["pref_code"].nunique() == 47
        assert panel["year"].nunique() == 9
        assert set(panel["year"].unique()) == set(range(2003, 2012))

    def test_9_host_rows(self):
        panel = load_score_panel(cup="tennou")
        # 各年 1 host のみ (2003-2011 = 単一県開催のみ)
        assert panel["is_host"].sum() == 9
        assert (panel.groupby("year")["is_host"].sum() == 1).all()

    def test_columns_present(self):
        panel = load_score_panel(cup="tennou")
        required = {"kai_num", "year", "pref_name", "pref_code", "cup", "score", "is_host", "is_host_int"}
        assert required.issubset(panel.columns)

    def test_score_positive(self):
        panel = load_score_panel(cup="tennou")
        assert (panel["score"] > 0).all()

    def test_extended_10_years(self):
        panel = load_score_panel(
            year_min_kai=FUNAHASHI_KAI_RANGE[0],
            year_max_kai=EXTENDED_KAI,
            cup="tennou",
        )
        assert panel.shape[0] == 470  # 47県 × 10年 (2003-2012)
        assert panel["year"].nunique() == 10

    def test_kougou_also_loads(self):
        panel = load_score_panel(cup="kougou")
        assert panel.shape[0] == 423

    def test_is_host_int_matches_bool(self):
        panel = load_score_panel(cup="tennou")
        assert ((panel["is_host_int"] == panel["is_host"].astype(int)).all())


class TestFitOLSScore:
    def test_funahashi_base_converges(self):
        panel = load_score_panel(cup="tennou")
        result = fit_ols_score(panel, add_pref_fe=True, add_year_fe=True, name="test_base")
        assert isinstance(result, ReplicationResult)
        assert result.dv == "score"
        assert result.n_obs == 423
        assert result.n_clusters == 47
        assert not np.isnan(result.coef_is_host)

    def test_funahashi_base_coef_positive_significant(self):
        panel = load_score_panel(cup="tennou")
        result = fit_ols_score(panel, add_pref_fe=True, add_year_fe=True, name="test_base")
        # 舟橋2016 host coef = +1674.65 と同方向・有意
        assert result.coef_is_host > 0
        assert result.p_is_host < 0.001

    def test_funahashi_base_coef_near_reference(self):
        # 実装 = pref FE + year FE のみ (controls 抜き) で舟橋 +1674.65 と誤差 10% 以内 の再現性
        panel = load_score_panel(cup="tennou")
        result = fit_ols_score(panel, add_pref_fe=True, add_year_fe=True, name="test_base")
        rel_err = abs(result.coef_is_host - FUNAHASHI_2016_HOST_COEF) / FUNAHASHI_2016_HOST_COEF
        assert rel_err < 0.10, f"coef={result.coef_is_host} vs ref={FUNAHASHI_2016_HOST_COEF} (rel_err={rel_err:.3f})"

    def test_funahashi_base_r2_high(self):
        panel = load_score_panel(cup="tennou")
        result = fit_ols_score(panel, add_pref_fe=True, add_year_fe=True, name="test_base")
        # 舟橋 R²=0.86 / FE-only は R²=0.94 前後 (year FE 追加で説明力上昇)
        assert result.r2 > 0.85

    def test_pooled_no_fe_larger_coef(self):
        # FE 抜きの pooled OLS は host bias を fixed pref/year 効果が吸収せず、
        # 生 diff (~+1733) に近い値になる想定
        panel = load_score_panel(cup="tennou")
        result = fit_ols_score(panel, add_pref_fe=False, add_year_fe=False, name="test_pooled")
        assert result.coef_is_host > 1600
        assert result.r2 < 0.5  # FE 抜きで説明力低い


class TestRunReplicationModels:
    def test_returns_3_models(self):
        results = run_replication_models(cup="tennou")
        assert len(results) == 3
        assert {r.name for r in results} == {
            "funahashi_base",
            "pooled_no_fe",
            "extended_2003_2012",
        }

    def test_extended_covers_10_years(self):
        results = run_replication_models(cup="tennou")
        ext = next(r for r in results if r.name == "extended_2003_2012")
        assert ext.year_min == 2003
        assert ext.year_max == 2012
        assert ext.n_obs == 470

    def test_all_models_host_positive(self):
        results = run_replication_models(cup="tennou")
        for r in results:
            assert r.coef_is_host > 0, f"{r.name}: coef={r.coef_is_host}"


class TestDescriptiveHostScoreGap:
    def test_raw_diff_near_reference(self):
        d = descriptive_host_score_gap("tennou")
        # 舟橋 base +1674.65 と生 diff は近似 (誤差 10% 以内)
        assert abs(d["raw_diff"] - FUNAHASHI_2016_HOST_COEF) / FUNAHASHI_2016_HOST_COEF < 0.10

    def test_counts_9_host_414_nonhost(self):
        d = descriptive_host_score_gap("tennou")
        assert d["n_host"] == 9
        assert d["n_nonhost"] == 414


class TestResultsToDataframe:
    def test_shape_and_columns(self):
        results = run_replication_models(cup="tennou")
        df = results_to_dataframe(results)
        assert df.shape[0] == 3
        expected = {
            "name", "dv", "year_min", "year_max",
            "coef_is_host", "se_is_host", "p_is_host",
            "n_obs", "n_params", "n_clusters", "r2", "r2_adj",
        }
        assert set(df.columns) == expected
