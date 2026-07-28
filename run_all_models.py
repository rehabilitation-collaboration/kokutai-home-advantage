"""Phase 3 執筆用: 全モデルの実測値 (coef/SE/p 生値・n_obs) を results/ に出力する。

丸め表記に頼らず manuscript.md の p 値・係数表記を確定するための一次ソース。
[[feedback-paper-precision-over-effort]] + [[feedback-paper-pdf-selfqa-before-gpt]] 対応。
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


def main_models():
    from src import analysis_main

    out = RESULTS_DIR / "analysis_main.txt"
    with out.open("w") as f:
        f.write("=" * 80 + "\n")
        f.write("analysis_main.py — 主モデル (2012-2022 tennou・n<=423)\n")
        f.write("=" * 80 + "\n\n")

        desc = analysis_main.descriptive_host_summary(cup="tennou")
        f.write("[descriptive_host_summary — tennou 2012-2022]\n")
        for k, v in desc.items():
            dump_line(f, k, v)
        f.write("\n")

        for cup in ["tennou", "kougou"]:
            f.write(f"[run_main_models cup={cup}]\n")
            f.write("  # pooled = prefecture-clustered SE (47 clusters); FE = Fisher info\n")
            results = analysis_main.run_main_models(cup=cup)
            for r in results:
                cov = getattr(r.result_obj, "cov_type", "nonrobust")
                prsq = float(getattr(r.result_obj, "prsquared", float("nan")))
                f.write(
                    f"  {r.name:<40} coef={r.coef_is_host:+.6f} "
                    f"se={r.se_is_host:.6f} p={r.p_is_host:.6f} "
                    f"n={r.n_obs} converged={r.converged} llf={r.llf:.4f} "
                    f"pseudoR2={prsq:.4f} cov={cov}\n"
                )
            f.write("\n")

        # Finding #18: Brant-style partial-proportional-odds diagnostic
        f.write("[brant_partial_po_test cup=tennou is_host_int across rank thresholds]\n")
        f.write("  # Y<=j vs Y>j binary logit for each threshold, pref-clustered SE.\n")
        f.write("  # Approximation: independent-threshold assumption (conservative).\n")
        brant = analysis_main.brant_partial_po_test(cup="tennou")
        f.write(f"  chi2={brant['chi2']} df={brant['df']} p_value={brant['p_value']} "
                f"n_thresholds_used={brant['n_thresholds_used']} "
                f"beta_pool_weighted={brant['beta_pool_weighted']}\n")
        f.write("  threshold_rows:\n")
        f.write(brant["threshold_rows"].to_string(index=False) + "\n")
        f.write("\n")
    print(f"[OK] {out}")


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


def confounders_models():
    from src import analysis_confounders

    out = RESULTS_DIR / "analysis_confounders.txt"
    with out.open("w") as f:
        f.write("=" * 80 + "\n")
        f.write("analysis_confounders.py — Csurilla型段階投入 M1→M5\n")
        f.write("=" * 80 + "\n\n")

        for dv in ["top1", "rank_ordinal"]:
            f.write(f"[run_staged_analysis dv={dv} tennou 2012-2022]\n")
            results = analysis_confounders.run_staged_analysis(cup="tennou", dv=dv)
            for r in results:
                cov = getattr(r.result_obj, "cov_type", "nonrobust")
                prsq = float(getattr(r.result_obj, "prsquared", float("nan")))
                f.write(
                    f"  {r.name:<40} coef={r.coef_is_host:+.6f} "
                    f"se={r.se_is_host:.6f} p={r.p_is_host:.6f} "
                    f"n={r.n_obs} converged={r.converged} llf={r.llf:.4f} "
                    f"pseudoR2={prsq:.4f} cov={cov}\n"
                )
            f.write("\n")

            f.write(f"[compute_attenuation dv={dv}]\n")
            att = analysis_confounders.compute_attenuation(results)
            f.write(f"{att.to_string()}\n\n")

        # Finding #12: Tokyo (pref_code=13) exclusion sensitivity
        for dv in ["top1", "rank_ordinal"]:
            f.write(f"[run_staged_analysis dv={dv} tennou 2012-2022 EXCLUDE Tokyo (pref=13)]\n")
            f.write("  # Csurilla-reverse mechanism quantitative check: Tokyo dominates\n")
            f.write("  # non-host top-1 (3/3 = 2016/2017/2022) so removal purges the\n")
            f.write("  # non-host championship mass; expect host coef to strengthen.\n")
            results = analysis_confounders.run_staged_analysis(cup="tennou", dv=dv,
                                                                exclude_pref_codes=[13])
            for r in results:
                cov = getattr(r.result_obj, "cov_type", "nonrobust")
                prsq = float(getattr(r.result_obj, "prsquared", float("nan")))
                f.write(
                    f"  {r.name:<40} coef={r.coef_is_host:+.6f} "
                    f"se={r.se_is_host:.6f} p={r.p_is_host:.6f} "
                    f"n={r.n_obs} converged={r.converged} llf={r.llf:.4f} "
                    f"pseudoR2={prsq:.4f} cov={cov}\n"
                )
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
    print(f"[OK] {out}")


if __name__ == "__main__":
    main_models()
    replication_models()
    event_study_models()
    confounders_models()
    cross_section_models()
    print("\n[DONE] all results saved to results/")
