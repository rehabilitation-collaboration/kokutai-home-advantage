"""plots.py: Figure 1-5 生成の smoke test + 出力ファイル存在確認"""

from pathlib import Path

import matplotlib
import pytest

# CI/headless 対応 (import 前に backend 固定)
matplotlib.use("Agg")

from src.plots import (  # noqa: E402
    PLOTS_DIR,
    SHOCK_YEARS,
    generate_all_figures,
    plot_fig1_host_win_rate_timeseries,
    plot_fig2_subj_vs_obj_host_bias,
    plot_fig3_event_study_two_layers,
    plot_fig4_confounders_attenuation,
    plot_fig5_replication_extended,
)


class TestConstants:
    def test_shock_years_6(self):
        assert len(SHOCK_YEARS) == 6
        assert set(SHOCK_YEARS.keys()) == {2002, 2016, 2017, 2022, 2023, 2024}

    def test_plots_dir_under_project(self):
        assert PLOTS_DIR.name == "plots"


class TestFig1HostWinRate:
    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig1_host_win_rate_timeseries(cup="tennou")
        assert png.exists() and png.suffix == ".png" and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.suffix == ".pdf" and pdf.stat().st_size > 5_000


class TestFig2SubjVsObj:
    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig2_subj_vs_obj_host_bias()
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestFig3EventStudy:
    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig3_event_study_two_layers(cup="tennou")
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestFig4ConfoundersAttenuation:
    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig4_confounders_attenuation(cup="tennou")
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestFig5ReplicationExtended:
    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig5_replication_extended(cup="tennou")
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestGenerateAllFigures:
    def test_returns_5_fig_dict(self):
        result = generate_all_figures(cup="tennou")
        assert set(result.keys()) == {"fig1", "fig2", "fig3", "fig4", "fig5"}
        for k, (png, pdf) in result.items():
            assert png.exists(), f"{k} PNG missing"
            assert pdf.exists(), f"{k} PDF missing"

    def test_all_files_nontrivial_size(self):
        result = generate_all_figures(cup="tennou")
        for k, (png, pdf) in result.items():
            assert png.stat().st_size > 10_000, f"{k} PNG < 10KB"
            assert pdf.stat().st_size > 3_000, f"{k} PDF < 3KB"
