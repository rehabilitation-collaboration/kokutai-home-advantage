"""v3 執筆用: 各モデルの実測値 (coef/SE/p 生値・n_obs) を results/ に出力する。

丸め表記に頼らず manuscript.md の p 値・係数表記を確定するための一次ソース。
[[feedback-paper-precision-over-effort]] + [[feedback-paper-pdf-selfqa-before-gpt]] 対応。

v3 主モデル (analysis_main_v3.py) の dump は `scripts/dump_analysis_main_v3.py` で
別実行する (v3 host-rank パネル・n=150)。本 script は v3 副次分析 (Funahashi replication・
event-study 2 層・2024-2025 cross-section) を dump する。

M4-H 整理履歴: 旧 `main_models()` (2012-2022 legacy 47-prefecture-year panel) と
`confounders_models()` (Csurilla-style staged specification) は v3 スコープ外として削除。
両実装は commit `fa07fd2` 以前の git 履歴で参照可能 (`src/analysis_main.py` +
`src/analysis_confounders.py`)。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

RESULTS_DIR = PROJECT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def dump_line(f, label: str, value):
    f.write(f"{label:<40} {value}\n")


def replication_models():
    from src import analysis_replication

    out = RESULTS_DIR / "analysis_replication.txt"
    with out.open("w") as f:
        f.write("=" * 80 + "\n")
        f.write("analysis_replication.py — 舟橋2016 再現 (2003-2011)\n")
        f.write("=" * 80 + "\n\n")

        for cup in ["tennou", "kougou"]:
            f.write(f"[descriptive_host_score_gap cup={cup}]\n")
            desc = analysis_replication.descriptive_host_score_gap(cup=cup)
            for k, v in desc.items():
                dump_line(f, k, v)
            f.write("\n")

            f.write(f"[run_replication_models cup={cup}]\n")
            results = analysis_replication.run_replication_models(cup=cup)
            for r in results:
                # ReplicationResult は dataclass — 全属性を書き出す
                d = r.__dict__
                for k, v in d.items():
                    if k in ("result_obj",):
                        continue
                    dump_line(f, f"  {r.name}.{k}", v)
                f.write("\n")
    print(f"[OK] {out}")


def event_study_models():
    from src import analysis_event_study

    out = RESULTS_DIR / "analysis_event_study.txt"
    with out.open("w") as f:
        f.write("=" * 80 + "\n")
        f.write("analysis_event_study.py — Layer1 (2002高知) + Layer2 (post-2016 5ショック)\n")
        f.write("=" * 80 + "\n\n")

        for layer in ["L1_pre2005", "L2_post2016"]:
            f.write(f"[build + fit_event_study_lp layer={layer}]\n")
            try:
                df = analysis_event_study.build_event_study_frame(layer=layer)
                f.write(f"  frame shape: {df.shape}\n")
                f.write(f"  columns: {list(df.columns)}\n")
                fit = analysis_event_study.fit_event_study_lp(df)
                f.write(f"  fit type: {type(fit).__name__}\n")
                if hasattr(fit, "params"):
                    for k, v in fit.params.items():
                        f.write(f"  param {k:<30} coef={v:+.6f}\n")
                if hasattr(fit, "pvalues"):
                    for k, v in fit.pvalues.items():
                        f.write(f"  pval  {k:<30} p={v:.6f}\n")
                if hasattr(fit, "bse"):
                    for k, v in fit.bse.items():
                        f.write(f"  se    {k:<30} se={v:.6f}\n")
                if hasattr(fit, "nobs"):
                    f.write(f"  n_obs: {int(fit.nobs)}\n")
            except Exception as e:
                f.write(f"  ERROR: {type(e).__name__}: {e}\n")
            f.write("\n")

            f.write(f"[parallel_trend_test layer={layer}]\n")
            try:
                df = analysis_event_study.build_event_study_frame(layer=layer)
                result = analysis_event_study.parallel_trend_test(df)
                for k, v in result.items():
                    dump_line(f, f"  {k}", v)
            except Exception as e:
                f.write(f"  ERROR: {type(e).__name__}: {e}\n")
            f.write("\n")

            f.write(f"[compute_pre_post_means layer={layer}]\n")
            try:
                df = analysis_event_study.build_event_study_frame(layer=layer)
                means = analysis_event_study.compute_pre_post_means(df)
                f.write(f"  means:\n{means.to_string()}\n")
            except Exception as e:
                f.write(f"  ERROR: {type(e).__name__}: {e}\n")
            f.write("\n")
    print(f"[OK] {out}")


def cross_section_models():
    from src import analysis_cross_section_2024_2025 as csm

    out = RESULTS_DIR / "analysis_cross_section.txt"
    with out.open("w") as f:
        f.write("=" * 80 + "\n")
        f.write("analysis_cross_section_2024_2025.py — 2024佐賀 + 2025滋賀 断面\n")
        f.write("Subj×Host 交互作用 (novelty core)\n")
        f.write("=" * 80 + "\n\n")

        f.write("[descriptive_by_category — 3分類 host boost]\n")
        desc = csm.descriptive_by_category()
        f.write(f"{desc.to_string()}\n\n")

        f.write("[run_cross_section_models — 3 spec]\n")
        results = csm.run_cross_section_models()
        for r in results:
            # CrossSectionResult dataclass の全属性を書き出す
            d = r.__dict__
            for k, v in d.items():
                if k in ("result_obj",):
                    continue
                dump_line(f, f"  {r.name}.{k}", v)
            f.write("\n")

        f.write("[wild_cluster_bootstrap — few-treated-clusters robust p (Finding #5)]\n")
        df_cs = csm.build_cross_section_frame()
        wcb = csm.wild_cluster_bootstrap(df_cs, dv="score", test_coef="host_x_subj", n_bootstrap=999)
        for k, v in wcb.items():
            dump_line(f, f"  wild_cluster.{k}", v)
        f.write("\n")

        f.write("[run_cross_section_normalized — Phase 7A GPT round-8 「必須修正 3」: sport-year-cup 内 normalized outcomes]\n")
        norm_results = csm.run_cross_section_normalized()
        for r in norm_results:
            d = r.__dict__
            for k, v in d.items():
                if k in ("result_obj",):
                    continue
                dump_line(f, f"  {r.name}.{k}", v)
            f.write("\n")

        f.write("[wild_cluster_bootstrap normalized (z_score) — Phase 7A]\n")
        df_cs_norm = csm.build_cross_section_frame()
        wcb_z = csm.wild_cluster_bootstrap(df_cs_norm, dv="z_score", test_coef="host_x_subj", n_bootstrap=999)
        for k, v in wcb_z.items():
            dump_line(f, f"  wild_cluster_z.{k}", v)
        f.write("\n")

        f.write("[wild_cluster_bootstrap normalized (pct_rank) — Phase 7A]\n")
        wcb_pr = csm.wild_cluster_bootstrap(df_cs_norm, dv="pct_rank", test_coef="host_x_subj", n_bootstrap=999)
        for k, v in wcb_pr.items():
            dump_line(f, f"  wild_cluster_pr.{k}", v)
        f.write("\n")

        f.write("[run_cross_section_inclusive_zero_imputed — Table 6 row (v) reproducibility (Phase 6B)]\n")
        zi_result = csm.run_cross_section_inclusive_zero_imputed()
        d = zi_result.__dict__
        for k, v in d.items():
            if k in ("result_obj",):
                continue
            dump_line(f, f"  {zi_result.name}.{k}", v)
        f.write("\n")

        f.write("[wild_cluster_bootstrap inclusive zero-imputed — Table 6 row (v) bootstrap (Phase 6B)]\n")
        df_zi = csm.build_cross_section_frame_zero_imputed()
        wcb_zi = csm.wild_cluster_bootstrap(df_zi, dv="score", test_coef="host_x_subj", n_bootstrap=999)
        for k, v in wcb_zi.items():
            dump_line(f, f"  wild_cluster_zi.{k}", v)
        f.write("\n")
    print(f"[OK] {out}")


if __name__ == "__main__":
    replication_models()
    event_study_models()
    cross_section_models()
    print("\n[DONE] all results saved to results/")
