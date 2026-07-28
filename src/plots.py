"""Phase 2 図表: Figure 1-5

論文本文用 (Phase 3・英語論文執筆) の主要 Figure を生成する。
出力先: `plots/fig{N}_*.{png,pdf}` (PNG は 300 dpi・PDF は vector)

Figure 一覧:
- Fig 1: 開催地優勝率の時系列 (1978-2025) + 開催地敗北6ショック年マーカー
- Fig 2: 3 分類 (主観 / 客観 / 準主観) の host bias 係数比較 (cross_section 由来・エラーバー)
- Fig 3: event-study 2層 (Layer1 2002 高知単独 + Layer2 post-2016 5ショック stacked) の τ プロット
- Fig 4: Csurilla型交絡変数統制の host effect 減衰 (M1_host_only → M5_full_FE)
- Fig 5: 舟橋2016 再現 (2003-2011) + 2003-2012 拡張 の Host 係数比較 + 舟橋 reference

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
    """
    df = build_cross_section_frame()
    desc = descriptive_by_category(df).set_index("category")

    categories = ["objective", "semi_subjective", "subjective"]
    labels = ["Objective\n(measurement)", "Semi-subjective\n(team sports)", "Subjective\n(judged)"]
    means = [desc.loc[cat, "diff_mean_host_minus_nonhost"] for cat in categories]
    n_hosts = [int(desc.loc[cat, "count_host"]) for cat in categories]

    # SE from OLS-per-category baseline: score ~ is_host in each subset
    ses = []
    for cat in categories:
        sub = df[df["category"] == cat]
        # 簡易 SE = std / sqrt(n_host) + std / sqrt(n_nonhost) の diff SE
        h = sub[sub["is_host"]]["score"]
        nh = sub[~sub["is_host"]]["score"]
        se = np.sqrt(h.var(ddof=1) / len(h) + nh.var(ddof=1) / len(nh))
        ses.append(float(se))
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
    ax.set_title("Host bias by sport category (2024 Saga + 2025 Shiga, tennou+kougou pooled)")
    ax.set_ylim(0, max(means) + max(ci95) + 8)
    return _save(fig, "fig2_subj_vs_obj_host_bias")


def plot_fig3_event_study_two_layers(cup: str = "tennou") -> tuple[Path, Path]:
    """Fig 3: event-study 2層 (Layer1 単発 + Layer2 stacked) の τ プロット (95% CI)"""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, layer, title in [
        (axes[0], "layer1", "Layer 1: 2002 Kochi (pre-2005)"),
        (axes[1], "layer2", "Layer 2: post-2016 stacked (5 shocks)"),
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
        ax.text(c, ys[i] + 0.15, f"{c:+.0f}", ha="center", va="bottom", fontsize=8)

    ax.axvline(FUNAHASHI_2016_HOST_COEF, color="#cc0033", linewidth=1.0, linestyle="--",
               label=f"Funahashi2016 ref = {FUNAHASHI_2016_HOST_COEF:+.0f}")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_yticks(ys)
    ax.set_yticklabels(disp)
    ax.set_xlabel("Host coefficient (points)")
    ax.set_title("Replication of Funahashi 2016 + 1-year extension (tennou score DV)")
    ax.legend(loc="lower right", frameon=False)
    return _save(fig, "fig5_replication_extended")


def generate_all_figures(cup: str = "tennou") -> dict[str, tuple[Path, Path]]:
    """Fig 1-5 を全て生成し、{fig_key: (png, pdf)} を返す"""
    return {
        "fig1": plot_fig1_host_win_rate_timeseries(cup=cup),
        "fig2": plot_fig2_subj_vs_obj_host_bias(),
        "fig3": plot_fig3_event_study_two_layers(cup=cup),
        "fig4": plot_fig4_confounders_attenuation(cup=cup),
        "fig5": plot_fig5_replication_extended(cup=cup),
    }
