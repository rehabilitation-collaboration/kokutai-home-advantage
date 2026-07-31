"""M2 主分析の結果を results/analysis_main_v3.txt に人読みできる形で出力

Phase 3 (論文執筆) の素材。実行:
    cd ~/claude/analysis/kokutai-home-advantage
    source venv/bin/activate
    python scripts/dump_analysis_main_v3.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis_main_v3 import (  # noqa: E402
    chi_square_era_comparison,
    descriptive_by_era,
    era_boundary_sensitivity_grid,
    load_v3_panel,
    one_sample_proportion_test,
    pairwise_fisher_with_holm,
    permutation_test,
    run_ordered_logit_v3,
)

OUT_PATH = ROOT / "results" / "analysis_main_v3.txt"


def fmt(v, prec: int = 4) -> str:
    if isinstance(v, float):
        if v != v:  # NaN
            return "NaN"
        return f"{v:.{prec}f}"
    return str(v)


def main() -> None:
    df = load_v3_panel()
    lines: list[str] = []

    lines.append("=" * 80)
    lines.append("analysis_main_v3.py — v3 M2 主分析 (実質77大会 host top1/3/8 真偽検定)")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"panel shape: {df.shape}")
    lines.append(f"era 分布: {df['era'].value_counts().to_dict()}")
    lines.append(f"host_rank 分布: {df['host_rank'].value_counts(dropna=False).sort_index().to_dict()}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("[1] descriptive_by_era")
    lines.append("-" * 80)
    d = descriptive_by_era(df)
    lines.append(d.to_string(index=False))
    lines.append("")

    lines.append("-" * 80)
    lines.append("[2] one_sample_proportion_test (帰無 = k/47 vs 観測 host top-k 率・exact binomial + Wilson 95%CI)")
    lines.append("-" * 80)
    header = f"  {'threshold':>3}  {'cup':>7}  {'era':>7}  {'n':>3}  {'obs':>3}  {'obs_rate':>8}  {'null_rate':>9}  {'excess':>8}  {'p_greater':>12}  {'CI_low':>7}  {'CI_high':>7}"
    lines.append(header)
    for cup in ["tennou", "kougou", "both"]:
        for era in ["all", "early", "golden", "shock"]:
            for k in [1, 3, 8]:
                r = one_sample_proportion_test(df, k, cup=cup, era=era)  # type: ignore
                lines.append(
                    f"  {r['threshold']:>3}  {str(r['cup']):>7}  {str(r['era']):>7}  {r['n']:>3}  "
                    f"{r['n_success']:>3}  {fmt(r['observed_rate'],4):>8}  {fmt(r['null_rate'],4):>9}  "
                    f"{fmt(r['excess'],4):>8}  {fmt(r['p_value_greater'],2):>12}  "
                    f"{fmt(r['ci_wilson_low'],3):>7}  {fmt(r['ci_wilson_high'],3):>7}"
                )
    lines.append("")

    lines.append("-" * 80)
    lines.append("[2b] sensitivity_46_states (M3-T1: 1972 沖縄復帰前 46県帰無・early era 30 大会に一律適用)")
    lines.append("     ※ 対象=early era 30 大会 (第 3-32 回・1948-1977) 全体を n_states=46 で再計算。")
    lines.append("     ※ 史実上 46 県は第 3-26 回 24 大会のみ・第 27-32 回 6 大会は 47 県。ここでは保守的な worst-case bound。")
    lines.append("     ※ null_rate=k/n_states は分母大きいほど小さいため、default 47 は excess を過大評価する方向。")
    lines.append("-" * 80)
    lines.append(header)
    for cup in ["tennou", "kougou", "both"]:
        for k in [1, 3, 8]:
            r = one_sample_proportion_test(df, k, cup=cup, era="early", n_states=46)  # type: ignore
            lines.append(
                f"  {r['threshold']:>3}  {str(r['cup']):>7}  {str(r['era']):>7}  {r['n']:>3}  "
                f"{r['n_success']:>3}  {fmt(r['observed_rate'],4):>8}  {fmt(r['null_rate'],4):>9}  "
                f"{fmt(r['excess'],4):>8}  {fmt(r['p_value_greater'],2):>12}  "
                f"{fmt(r['ci_wilson_low'],3):>7}  {fmt(r['ci_wilson_high'],3):>7}"
            )
    lines.append("")

    lines.append("-" * 80)
    lines.append("[3] permutation_test (host_pref を 47県からランダム再割当・n_perm=10,000)")
    lines.append("-" * 80)
    lines.append(f"  {'threshold':>3}  {'cup':>7}  {'obs_rate':>8}  {'null_mean':>9}  {'null_std':>8}  {'null_p05':>8}  {'null_p95':>8}  {'p_perm':>7}")
    for cup in ["tennou", "kougou"]:
        for k in [1, 3, 8]:
            r = permutation_test(k, cup=cup, n_perm=10_000, seed=0)  # type: ignore
            lines.append(
                f"  {r['threshold']:>3}  {str(r['cup']):>7}  {fmt(r['obs_rate'],4):>8}  "
                f"{fmt(r['null_mean'],4):>9}  {fmt(r['null_std'],4):>8}  "
                f"{fmt(r['null_p05'],4):>8}  {fmt(r['null_p95'],4):>8}  {fmt(r['p_value_permutation'],4):>7}"
            )
    lines.append("")

    lines.append("-" * 80)
    lines.append("[4] chi_square_era_comparison (3期間 top-k 率の差 + conditional exact / MC-perm / Pearson χ² + pairwise Fisher exact)")
    lines.append("     ※ Phase 7A (GPT round-8 「必須修正 1」): 完全列挙 conditional Pearson χ² exact p を primary global test に格上げ。")
    lines.append("     ※ 2×3 tables は 100-200 通り程度で列挙可能 → Monte Carlo 近似より精密。")
    lines.append("     ※ MC-perm p (n_perm=10,000) は下方互換のため保持 (旧 Phase 6A primary)。")
    lines.append("     ※ Pearson χ² は sensitivity として保持 (shock 期 n=7 で期待度数不足=漸近近似条件違反)。")
    lines.append("-" * 80)
    for cup in ["tennou", "kougou", "both"]:
        for k in [1, 3, 8]:
            r = chi_square_era_comparison(df, k, cup=cup, n_perm=10_000, seed=0)  # type: ignore
            lines.append(
                f"  cup={cup:>7} top{k}: rates early={fmt(r['rates']['early'],3)} "
                f"golden={fmt(r['rates']['golden'],3)} shock={fmt(r['rates']['shock'],3)} "
                f"| exact p={fmt(r['exact_p_conditional'],6)} (primary; N_tables={r['n_tables_enumerated']}) "
                f"| MC-perm p={fmt(r['mc_permutation_p'],4)} "
                f"| Pearson χ²={fmt(r['chi2'],2)} dof={r['chi2_dof']} p={fmt(r['chi2_p'],4)} (sensitivity)"
            )
            pw = r["pairwise_fisher"]
            lines.append(
                f"      pairwise Fisher: early_vs_golden={fmt(pw['early_vs_golden'],4)} "
                f"golden_vs_shock={fmt(pw['golden_vs_shock'],4)} "
                f"early_vs_shock={fmt(pw['early_vs_shock'],4)}"
            )
    lines.append("")

    lines.append("-" * 80)
    lines.append("[4b] pairwise_fisher_with_holm (Phase 7A: Table 4 pairwise Fisher に Holm-Bonferroni 補正)")
    lines.append("-" * 80)
    for k in [1, 3, 8]:
        lines.append(f"  threshold=top{k}")
        holm = pairwise_fisher_with_holm(df, threshold=k)
        lines.append(holm.to_string(index=False))
        lines.append("")

    lines.append("-" * 80)
    lines.append("[4c] era_boundary_sensitivity_grid (Phase 7A: GPT round-8 「必須修正 4」)")
    lines.append("     ※ golden_start ∈ {1975..1980} × shock_start ∈ {2014..2018} × 2 cups = 60 combinations")
    lines.append("     ※ 各 combination で per-cup top-1 rate と exact p (conditional Pearson χ²) を再算出")
    lines.append("     ※ 非単調 top-1 pattern が特定境界に依存しないことを示す")
    lines.append("-" * 80)
    grid = era_boundary_sensitivity_grid(df, threshold=1)
    lines.append(grid.to_string(index=False))
    lines.append("")

    lines.append("-" * 80)
    lines.append("[5] run_ordered_logit_v3 (rank_ordinal ~ C(era) + C(cup)?・cluster SE at host_pref_code)")
    lines.append("-" * 80)
    lines.append("  ref: era=early, cup=kougou (drop_first)")
    for mode in ["tennou", "kougou", "pooled"]:
        r = run_ordered_logit_v3(df, cup_mode=mode)  # type: ignore
        lines.append("")
        lines.append(f"  cup_mode={mode}  n_obs={r['n_obs']}  converged={r['converged']}  "
                     f"cluster={r.get('cluster_used', '?')}  llf={fmt(r.get('llf', float('nan')), 3)}")
        for name, coef in r.get("params", {}).items():
            se = r["bse"].get(name, float("nan"))
            p = r["pvalues"].get(name, float("nan"))
            lines.append(f"    {name:>20}  coef={fmt(coef,4):>10}  se={fmt(se,4):>8}  p={fmt(p,4):>7}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
