"""図表生成: v3 M4 Figure 1-3 + Supplement + 旧 F1-F5 (M4-H まで併存)

論文本文用の主要 Figure を生成する。
出力先: `plots/fig{N}_*.{png,pdf}` (PNG は 300 dpi・PDF は vector)

v3 Figure (M4-D で新規・主稿用):
- Fig 1 (v3): Host-rank 1948-2025 era 色分け (early/golden/shock 3 期の非単調変化を可視化)
- Fig 2 (v3): Top-k rate by era × cup bar chart (top1/3/8 × tennou/kougou × 3 era, 95% CI エラーバー)
- Fig 3 (v3): Host boost by sport category 2024-2025 (旧 F2 保持・plot_fig2_subj_vs_obj_host_bias)

旧 Figure (v6-final 遺産・M4-H で整理予定・現在 併存):
- 旧 Fig 1 = plot_fig1_host_win_rate_timeseries (1978-2025・v3 F1 に差替済み)
- 旧 Fig 3 = plot_fig3_event_study_two_layers (Supp Fig S1 に降格予定)
- 旧 Fig 4 = plot_fig4_confounders_attenuation (v3 スコープ外・落とし予定)
- 旧 Fig 5 = plot_fig5_replication_extended (Supp Fig S2 に降格予定)

論文誌 print フレンドリー: グレースケール寄り + 太めの線 + サンセリフフォント。
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis_confounders import compute_attenuation, run_staged_analysis
from src.analysis_cross_section_2024_2025 import (
    build_cross_section_frame,
    descriptive_by_category,
    fit_cross_section_ols,
)
from src.analysis_event_study import (
    build_event_study_frame,
    fit_event_study_lp,
)
from src.analysis_main_v3 import (
    ERA_BOUNDARIES,
    ERA_ORDER,
    RANK_OUTSIDE,
    _classify_era,
    descriptive_by_era,
    load_v3_panel,
    one_sample_proportion_test,
)
from src.analysis_replication import (
    FUNAHASHI_2016_HOST_COEF,
    run_replication_models,
)
from src.definitions import KOKUTAI_HOSTS
from src.panel_builder import build_ranking_panel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = PROJECT_ROOT / "plots"

# 開催地敗北6ショック年
SHOCK_YEARS: dict[int, str] = {
    2002: "Kochi",
    2016: "Iwate",
    2017: "Ehime",
    2022: "Tochigi",
    2023: "Kagoshima (special)",
    2024: "Saga",
}

# Print-friendly styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.linestyle": ":",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.6,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.autolayout": False,
})


def _ensure_plots_dir() -> Path:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return PLOTS_DIR


def _save(fig, stem: str) -> tuple[Path, Path]:
    outdir = _ensure_plots_dir()
    png = outdir / f"{stem}.png"
    pdf = outdir / f"{stem}.pdf"
    fig.savefig(png)
    fig.savefig(pdf)
    plt.close(fig)
    return png, pdf


def plot_fig1_host_win_rate_timeseries(cup: str = "tennou") -> tuple[Path, Path]:
    """Fig 1: 開催地優勝率の時系列 (1978-2025) + 6ショック年マーカー

    - 単年 host_win = 1 (host が rank1) / 0 (host が非rank1)
    - 5年移動平均も重ねる (トレンド可視化)
    - 6ショック年 = 赤マーカーでハイライト
    """
    panel = build_ranking_panel()
    host_only = panel[(panel["cup"] == cup) & (panel["is_host"]) & (~panel["is_special"]) & (~panel["cancelled"])].copy()
    host_only["host_win"] = (host_only["rank"] == 1).astype(int)
    host_only = host_only[host_only["year"] >= 1978].sort_values("year")

    yearly = host_only.groupby("year")["host_win"].mean().reset_index()
    yearly["rolling_5yr"] = yearly["host_win"].rolling(window=5, min_periods=3, center=True).mean()

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.scatter(yearly["year"], yearly["host_win"], s=30, color="#444444", label="host win (per year)", zorder=3)
    ax.plot(yearly["year"], yearly["rolling_5yr"], color="#0066cc", linewidth=1.8, label="5-yr rolling mean")

    for shock_yr, shock_name in SHOCK_YEARS.items():
        if shock_yr < 1978 or shock_yr > yearly["year"].max():
            continue
        ax.axvline(shock_yr, color="#cc0033", linewidth=0.9, alpha=0.5, linestyle="--", zorder=1)
        ax.text(shock_yr, 1.06, shock_name, rotation=45, fontsize=7,
                color="#cc0033", ha="left", va="bottom", zorder=4)

    ax.set_xlabel("Year")
    ax.set_ylabel("Host prefecture wins (1 = won overall)")
    ax.set_title("Host prefecture win rate over time (1978-2025, tennou cup)")
    ax.set_ylim(-0.08, 1.20)
    ax.legend(loc="lower left", frameon=False)
    return _save(fig, "fig1_host_win_rate_timeseries")


def plot_fig2_subj_vs_obj_host_bias() -> tuple[Path, Path]:
    """Fig 2: 3 分類の host bias 係数比較 (cross_section・エラーバー = 95% CI)

    Balmer2003 novelty core: subjective が objective/semi_subjective を有意に上回るか。
    baseline 係数 = coef_is_host (= objective の host boost) + 分類別 additive coef.

    Finding #8 fix: SE は per-category `score ~ is_host` OLS の prefecture-clustered
    SE (47 clusters) を使う。旧実装の two-sample var/n formula は cell 独立性を
    仮定していて、同一県内の年内多sport clustering を過小推定する。
    """
    import statsmodels.api as sm

    df = build_cross_section_frame()
    desc = descriptive_by_category(df).set_index("category")

    categories = ["objective", "semi_subjective", "subjective"]
    labels = ["Objective\n(measurement)", "Semi-subjective\n(team sports)", "Subjective\n(judged)"]
    means = [desc.loc[cat, "diff_mean_host_minus_nonhost"] for cat in categories]
    n_hosts = [int(desc.loc[cat, "count_host"]) for cat in categories]

    # Per-category prefecture-clustered SE from `score ~ is_host` OLS
    ses = []
    for cat in categories:
        sub = df[df["category"] == cat].copy()
        sub["is_host_int"] = sub["is_host"].astype(int)
        X = sm.add_constant(sub[["is_host_int"]].astype(float))
        y = sub["score"].astype(float)
        model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": sub["pref_code"]})
        ses.append(float(model.bse["is_host_int"]))
    ci95 = [1.96 * s for s in ses]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    colors = ["#7f9dbf", "#a89b70", "#c25050"]
    xs = np.arange(len(categories))
    ax.bar(xs, means, yerr=ci95, capsize=6, color=colors, edgecolor="black", linewidth=0.8, alpha=0.85)
    for i, (x, m, n) in enumerate(zip(xs, means, n_hosts)):
        ax.text(x, m + ci95[i] + 1.5, f"+{m:.1f}\n(n_host={n})", ha="center", va="bottom", fontsize=8)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Host - Nonhost mean score (points)")
    ax.set_title("Host bias by sport category (2024 Saga + 2025 Shiga, tennou+kougou pooled;\n"
                 "error bars = 95% CI from prefecture-clustered SE, 47 clusters)")
    ax.set_ylim(0, max(means) + max(ci95) + 8)
    return _save(fig, "fig2_subj_vs_obj_host_bias")


def plot_fig3_event_study_two_layers(cup: str = "tennou") -> tuple[Path, Path]:
    """Fig 3: event-study 2層 (Layer1 単発 + Layer2 stacked) の τ プロット (95% CI)"""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, layer, title in [
        (axes[0], "L1_pre2005", "Layer 1: 2002 Kochi (pre-2005)"),
        (axes[1], "L2_post2016", "Layer 2: post-2016 stacked (5 shocks)"),
    ]:
        df = build_event_study_frame(layer=layer, cup=cup)
        coef_df, _ = fit_event_study_lp(df, dv="top1", reference_time=-1)
        if coef_df.empty:
            ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(title)
            continue
        ci95 = 1.96 * coef_df["se"]
        ax.errorbar(
            coef_df["relative_time"], coef_df["coef"], yerr=ci95,
            fmt="o", color="#003377", ecolor="#666666",
            capsize=4, markersize=6, linewidth=1.2,
        )
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axvline(0, color="#cc0033", linewidth=1.0, linestyle="--", alpha=0.5)
        ax.set_xlabel(r"Relative time $\tau$ (years from shock)")
        if ax is axes[0]:
            ax.set_ylabel("Effect on Host top-1 probability (LP coef)")
        ax.set_title(title)

    fig.suptitle("Event-study: host effect on top-1 probability (LP model, clustered SE)", y=1.02)
    return _save(fig, "fig3_event_study_two_layers")


def plot_fig4_confounders_attenuation(cup: str = "tennou") -> tuple[Path, Path]:
    """Fig 4: Csurilla型交絡変数統制 (M1-M5) の host effect 減衰"""
    staged = run_staged_analysis(dv="top1", cup=cup)
    att_df = compute_attenuation(staged)
    labels = att_df["name"].tolist()
    coefs = att_df["coef_is_host"].tolist()
    ses = att_df["se_is_host"].tolist()
    ci95 = [1.96 * s if not np.isnan(s) else 0 for s in ses]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = np.arange(len(labels))
    ax.errorbar(xs, coefs, yerr=ci95, fmt="o-", color="#333333", ecolor="#888888",
                capsize=5, markersize=7, linewidth=1.2)
    for i, c in enumerate(coefs):
        ax.text(xs[i], c + 0.4, f"{c:.2f}", ha="center", va="bottom", fontsize=8)

    ax.axhline(0, color="#cc0033", linewidth=0.7, linestyle="--", alpha=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("coef_is_host (logit top-1)")
    ax.set_title("Csurilla-type confounder attenuation (2012-2022 tennou)")
    return _save(fig, "fig4_confounders_attenuation")


def plot_fig5_replication_extended(cup: str = "tennou") -> tuple[Path, Path]:
    """Fig 5: 舟橋2016 再現 (2003-2011) + 拡張 (2003-2012) の Host 係数比較 + 舟橋 reference"""
    results = run_replication_models(cup=cup)
    names = [r.name for r in results]
    coefs = [r.coef_is_host for r in results]
    ses = [r.se_is_host for r in results]
    ci95 = [1.96 * s for s in ses]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ys = np.arange(len(names))
    labels = {
        "funahashi_base": "Funahashi2016 base\n(2003-2011, pref+year FE)",
        "pooled_no_fe": "Pooled OLS\n(2003-2011, no FE)",
        "extended_2003_2012": "Extended +1yr\n(2003-2012, pref+year FE)",
    }
    disp = [labels.get(n, n) for n in names]

    ax.errorbar(coefs, ys, xerr=ci95, fmt="s", color="#003377", ecolor="#888888",
                capsize=5, markersize=8, linewidth=1.2)
    for i, c in enumerate(coefs):
        ax.text(c, ys[i] + 0.18, f"{c:+.0f}", ha="center", va="bottom", fontsize=8)

    ax.axvline(FUNAHASHI_2016_HOST_COEF, color="#cc0033", linewidth=1.0, linestyle="--",
               label=f"Funahashi2016 ref = {FUNAHASHI_2016_HOST_COEF:+.0f}")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_yticks(ys)
    ax.set_yticklabels(disp)
    ax.set_ylim(-0.6, len(names) - 0.1)
    ax.set_xlabel("Host coefficient (points)")
    ax.set_title("Replication of Funahashi 2016 + 1-year extension (tennou score DV)", pad=12)
    ax.legend(loc="lower right", frameon=True, facecolor="white", framealpha=0.9,
              edgecolor="none")
    fig.tight_layout()
    return _save(fig, "fig5_replication_extended")


def plot_fig1_v3_host_rank_1948_2025_era() -> tuple[Path, Path]:
    """Fig 1 (v3): Host-rank 1948-2025 era 色分け (両 cup 重畳・非単調時代パターン可視化)

    - x = year (1948-2025・第 3-79 回・kai 1/2/75/76 除外)
    - y = host_rank (1-8・top8 圏外は 9 = "out")
    - color = era (early gray / golden blue / shock red・ERA_BOUNDARIES 準拠)
    - marker = cup (tennou o / kougou x)
    - y 軸反転 (rank 1 が上・rank 9 が下)
    - era 境界破線 (year=1978, 2016) を垂直破線で追加
    - descriptive_by_era の非単調変化 (early 43.3% → golden 94.7% → shock 42.9%) を視覚化
    """
    from matplotlib.lines import Line2D

    panel = load_v3_panel().sort_values(["year", "cup"]).reset_index(drop=True)

    era_colors = {"early": "#888888", "golden": "#0066cc", "shock": "#cc0033"}
    cup_markers = {"tennou": "o", "kougou": "x"}
    cup_size = {"tennou": 42, "kougou": 32}

    fig, ax = plt.subplots(figsize=(10, 5.0))

    # Jitter kougou by +0.25 year to reduce over-plotting on the same (year, rank) cell
    year_offset = {"tennou": -0.15, "kougou": 0.15}

    for c in ["tennou", "kougou"]:
        for era_name in ERA_ORDER:
            sub = panel[(panel["cup"] == c) & (panel["era"] == era_name)]
            xs = sub["year"].to_numpy() + year_offset[c]
            ys = sub["rank_ordinal"].to_numpy()
            # tennou = filled circle with black edge; kougou = unfilled x (no edgecolor)
            if c == "tennou":
                ax.scatter(xs, ys,
                           marker=cup_markers[c],
                           s=cup_size[c],
                           color=era_colors[era_name],
                           edgecolor="black",
                           linewidths=0.5,
                           alpha=0.85,
                           zorder=3)
            else:
                ax.scatter(xs, ys,
                           marker=cup_markers[c],
                           s=cup_size[c],
                           color=era_colors[era_name],
                           linewidths=1.0,
                           alpha=0.85,
                           zorder=3)

    # era 境界破線
    for boundary_year in [1978, 2016]:
        ax.axvline(boundary_year - 0.5, color="#333333", linewidth=0.8,
                   linestyle="--", alpha=0.6, zorder=1)

    # y 軸反転 (rank 1 が上・rank 9 = out (>8) が下)
    ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8, RANK_OUTSIDE])
    ax.set_yticklabels(["1", "2", "3", "4", "5", "6", "7", "8", "out (>8)"])
    ax.set_ylim(RANK_OUTSIDE + 0.5, 0.5)

    # era ラベル (chart 内下部の empty space に配置・title と重ならないよう)
    ax.text(1963, 5.5, "early (1948-1977)\n30 editions/cup\ntop-1: 43.3%",
            ha="center", va="center",
            color=era_colors["early"], fontsize=8, fontweight="bold",
            bbox=dict(facecolor="white", edgecolor=era_colors["early"],
                      linewidth=0.5, boxstyle="round,pad=0.3"))
    ax.text(1996, 5.5, "golden (1978-2015)\n38 editions/cup\ntop-1: 94.7%",
            ha="center", va="center",
            color=era_colors["golden"], fontsize=8, fontweight="bold",
            bbox=dict(facecolor="white", edgecolor=era_colors["golden"],
                      linewidth=0.5, boxstyle="round,pad=0.3"))
    ax.text(2020.5, 5.5, "shock (2016-2025)\n7 editions/cup\ntop-1: 42.9%",
            ha="center", va="center",
            color=era_colors["shock"], fontsize=8, fontweight="bold",
            bbox=dict(facecolor="white", edgecolor=era_colors["shock"],
                      linewidth=0.5, boxstyle="round,pad=0.3"))

    ax.set_xlim(1946, 2027)
    ax.set_xlabel("Year")
    ax.set_ylabel("Host prefecture rank (1 = won overall; 'out' = >8)")
    ax.set_title("Host prefecture rank at the Kokutai, 1948-2025 "
                 "(75 editions × 2 cups; era colour, cup marker)")

    legend_elems = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#555555",
               markeredgecolor="black", markersize=7, label="tennou (emperor)"),
        Line2D([0], [0], marker="x", color="#555555", markersize=8,
               linestyle="None", label="kougou (empress)"),
    ]
    ax.legend(handles=legend_elems, loc="lower left", frameon=True,
              framealpha=0.9, fontsize=8)

    return _save(fig, "fig1_v3_host_rank_1948_2025_era")


def plot_fig2_v3_topk_rate_by_era_cup() -> tuple[Path, Path]:
    """Fig 2 (v3): Top-k rate by era × cup × threshold (bar chart with 95% Wilson CI)

    - 左パネル tennou・右パネル kougou (sharey)
    - 各 era で 3 bar (top-1 / top-3 / top-8)
    - 95% CI エラーバー = ci_wilson_low/high from one_sample_proportion_test
    - null_rate (k=1: 2.13%) の水平点線を参照として追加
    """
    panel = load_v3_panel()

    rows = []
    for era_name in ERA_ORDER:
        for cup_name in ["tennou", "kougou"]:
            for threshold in [1, 3, 8]:
                res = one_sample_proportion_test(panel, threshold=threshold,
                                                 cup=cup_name, era=era_name)
                rows.append({
                    "era": era_name,
                    "cup": cup_name,
                    "threshold": threshold,
                    "n": res["n"],
                    "rate": res["observed_rate"],
                    "ci_lo": res["ci_wilson_low"],
                    "ci_hi": res["ci_wilson_high"],
                })
    d = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)

    era_x_positions = {"early": 0, "golden": 1, "shock": 2}
    threshold_colors = {1: "#cc0033", 3: "#0066cc", 8: "#666666"}
    threshold_offsets = {1: -0.25, 3: 0.0, 8: 0.25}
    bar_width = 0.22
    era_n = {"early": 30, "golden": 38, "shock": 7}

    for i, cup_name in enumerate(["tennou", "kougou"]):
        ax = axes[i]
        for threshold in [1, 3, 8]:
            for era_name in ERA_ORDER:
                sub = d[(d["cup"] == cup_name) & (d["era"] == era_name) &
                        (d["threshold"] == threshold)]
                r = sub.iloc[0]
                x = era_x_positions[era_name] + threshold_offsets[threshold]
                rate = r["rate"]
                yerr_lo = max(0.0, rate - r["ci_lo"])
                yerr_hi = max(0.0, r["ci_hi"] - rate)
                # Only attach label on the first (leftmost) bar of each threshold group
                bar_label = f"top-{threshold}" if era_name == "early" else None
                ax.bar(x, rate,
                       width=bar_width,
                       color=threshold_colors[threshold],
                       edgecolor="black", linewidth=0.5,
                       alpha=0.82,
                       yerr=[[yerr_lo], [yerr_hi]],
                       capsize=3, ecolor="#333333",
                       label=bar_label)

        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels([f"early\n(1948-77, n={era_n['early']})",
                            f"golden\n(1978-2015, n={era_n['golden']})",
                            f"shock\n(2016-25, n={era_n['shock']})"])
        ax.set_ylim(0, 1.10)
        if i == 0:
            ax.set_ylabel("Host top-k rate (95% Wilson CI)")
        ax.set_title(f"{cup_name} cup")

        # null rate reference: k=1 case (1/47 ≈ 0.0213) as visual anchor
        ax.axhline(1 / 47, color="#888888", linewidth=0.6, linestyle=":", alpha=0.7)
        ax.text(2.42, 1 / 47 + 0.005, "null=1/47", fontsize=7,
                color="#666666", va="bottom", ha="right")

        if i == 0:
            ax.legend(loc="upper left", frameon=True, framealpha=0.9,
                      fontsize=8, title="Threshold")

    fig.suptitle("Host top-k rate by era × cup, with 95% Wilson CI "
                 "(n = 150 = 75 editions × 2 cups; source: descriptive_by_era)",
                 y=1.02)
    return _save(fig, "fig2_v3_topk_rate_by_era_cup")


def generate_v3_figures() -> dict[str, tuple[Path, Path]]:
    """v3 M4-D 主稿用 Figure (F1 era 色分け / F2 top-k rate bar / F3 subj vs obj) を生成"""
    return {
        "fig1_v3": plot_fig1_v3_host_rank_1948_2025_era(),
        "fig2_v3": plot_fig2_v3_topk_rate_by_era_cup(),
        "fig3_v3": plot_fig2_subj_vs_obj_host_bias(),
    }


def generate_all_figures(cup: str = "tennou") -> dict[str, tuple[Path, Path]]:
    """Fig 1-5 を全て生成し、{fig_key: (png, pdf)} を返す"""
    return {
        "fig1": plot_fig1_host_win_rate_timeseries(cup=cup),
        "fig2": plot_fig2_subj_vs_obj_host_bias(),
        "fig3": plot_fig3_event_study_two_layers(cup=cup),
        "fig4": plot_fig4_confounders_attenuation(cup=cup),
        "fig5": plot_fig5_replication_extended(cup=cup),
    }
