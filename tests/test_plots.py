"""plots.py: v3 主稿 Fig 1-3 + Supplement Fig S1/S2 の smoke test + 出力ファイル存在確認"""

from pathlib import Path

import matplotlib
import pytest

# CI/headless 対応 (import 前に backend 固定)
matplotlib.use("Agg")

from src.plots import (  # noqa: E402
    PLOTS_DIR,
    generate_all_figures,
    generate_v3_figures,
    plot_fig1_v3_host_rank_1948_2025_era,
    plot_fig2_subj_vs_obj_host_bias,
    plot_fig2_v3_topk_rate_by_era_cup,
    plot_fig3_event_study_two_layers,
    plot_fig5_replication_extended,
)


class TestConstants:
    def test_plots_dir_under_project(self):
        assert PLOTS_DIR.name == "plots"


class TestFig1V3HostRankEra:
    """M4-H P2-a: v3 主稿 Fig 1 snapshot pattern (返り値 tuple + ファイルサイズ >0)"""

    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig1_v3_host_rank_1948_2025_era()
        assert png.exists() and png.suffix == ".png" and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.suffix == ".pdf" and pdf.stat().st_size > 5_000


class TestFig2V3TopkRateByEraCup:
    """M4-H P2-a: v3 主稿 Fig 2 snapshot pattern (返り値 tuple + ファイルサイズ >0)"""

    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig2_v3_topk_rate_by_era_cup()
        assert png.exists() and png.suffix == ".png" and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.suffix == ".pdf" and pdf.stat().st_size > 5_000


class TestFig2SubjVsObj:
    """v3 主稿 Fig 3 (Balmer2003 分離検証)"""

    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig2_subj_vs_obj_host_bias()
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestSuppFigS1EventStudy:
    """Supplement Fig S1 (event-study 2 層・§S1)"""

    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig3_event_study_two_layers(cup="tennou")
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestSuppFigS2ReplicationExtended:
    """Supplement Fig S2 (Funahashi 2003-2011 replication + 2003-2012 extension・§S3)"""

    def test_produces_png_and_pdf(self):
        png, pdf = plot_fig5_replication_extended(cup="tennou")
        assert png.exists() and png.stat().st_size > 10_000
        assert pdf.exists() and pdf.stat().st_size > 5_000


class TestGenerateV3Figures:
    """v3 主稿 3 Figure 一括生成"""

    def test_returns_3_fig_dict(self):
        result = generate_v3_figures()
        assert set(result.keys()) == {"fig1_v3", "fig2_v3", "fig3_v3"}
        for k, (png, pdf) in result.items():
            assert png.exists(), f"{k} PNG missing"
            assert pdf.exists(), f"{k} PDF missing"

    def test_all_files_nontrivial_size(self):
        result = generate_v3_figures()
        for k, (png, pdf) in result.items():
            assert png.stat().st_size > 10_000, f"{k} PNG < 10KB"
            assert pdf.stat().st_size > 3_000, f"{k} PDF < 3KB"


class TestGenerateAllFigures:
    """v3 主稿 Fig 3 + Supp Fig S1/S2 の一括生成"""

    def test_returns_expected_keys(self):
        result = generate_all_figures(cup="tennou")
        assert set(result.keys()) == {
            "fig2_subj_vs_obj",
            "supp_fig_s1_event_study",
            "supp_fig_s2_replication",
        }
        for k, (png, pdf) in result.items():
            assert png.exists(), f"{k} PNG missing"
            assert pdf.exists(), f"{k} PDF missing"

    def test_all_files_nontrivial_size(self):
        result = generate_all_figures(cup="tennou")
        for k, (png, pdf) in result.items():
            assert png.stat().st_size > 10_000, f"{k} PNG < 10KB"
            assert pdf.stat().st_size > 3_000, f"{k} PDF < 3KB"
