"""Generate manuscript PDF from manuscript.md using weasyprint.

Tables are embedded in the markdown (no CSV build needed).
Figures are inserted from plots/ (fig1..fig5 PNG).
"""

import re
from pathlib import Path

import markdown
import weasyprint

PROJECT_DIR = Path(__file__).parent
PLOTS_DIR = PROJECT_DIR / "plots"
PDF_DIR = PROJECT_DIR / "pdf"
PDF_DIR.mkdir(exist_ok=True)
MANUSCRIPT_MD = PROJECT_DIR / "manuscript.md"

MAIN_FIGURES = {
    "Figure 1": "fig1_host_win_rate_timeseries.png",
    "Figure 2": "fig2_subj_vs_obj_host_bias.png",
    "Figure 3": "fig4_confounders_attenuation.png",
    "Figure 4": "fig5_replication_extended.png",
}

SUPPLEMENTARY_FIGURES = {
    "Figure S1": "fig3_event_study_two_layers.png",
}

CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
    font-family: "Times New Roman", "DejaVu Serif", Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #111;
}
h1 { font-size: 16pt; margin-top: 0; margin-bottom: 8pt; line-height: 1.3; }
h2 { font-size: 13pt; margin-top: 20pt; margin-bottom: 6pt;
     border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin-top: 14pt; margin-bottom: 4pt; }
p { margin: 6pt 0; text-align: justify; }
sup { font-size: 0.75em; }
table {
    border-collapse: collapse; width: 100%; margin: 10pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #999; padding: 3pt 5pt; text-align: left;
}
th { background: #e8e8e8; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
img { max-width: 100%; height: auto; margin: 10pt 0; }
strong { font-weight: bold; }
em { font-style: italic; }
.figure-block {
    page-break-inside: avoid;
    page-break-before: always;
    margin: 1.5em 0;
    text-align: center;
}
.figure-block img {
    display: block;
    margin: 0 auto;
    max-width: 95%;
    max-height: 78vh;
}
.figure-caption {
    font-size: 10pt;
    text-align: justify;
    margin-top: 0.5em;
}
.supplementary-section {
    page-break-before: always;
}
.supplementary-section h2.supplementary-figures-heading {
    page-break-after: avoid;
}
.supplementary-section .figure-block:first-of-type {
    page-break-before: avoid;
}
"""


def extract_figure_legends(md_text: str) -> dict[str, str]:
    """Extract figure legend text from manuscript."""
    legends = {}
    pattern = (
        r"\*\*(?:Supplementary )?Figure (S?\d+)\.\*\*\s*"
        r"(.*?)(?=\n\n|\*\*(?:Supplementary )?Figure|\Z)"
    )
    for m in re.finditer(pattern, md_text, re.DOTALL):
        fig_num = m.group(1)
        text = m.group(2).strip().replace("\n", " ")
        legends[f"Figure {fig_num}"] = text
    return legends


def _render_figure_block(fig_label: str, fig_file: str, caption: str, label_prefix: str = "") -> str:
    fig_path = PLOTS_DIR / fig_file
    if not fig_path.exists():
        print(f"[WARN] {fig_path} not found, skipping")
        return ""
    html = '<div class="figure-block">'
    html += f'<img src="file://{fig_path.resolve()}" alt="{label_prefix}{fig_label}">'
    html += f'<p class="figure-caption"><strong>{label_prefix}{fig_label}.</strong> '
    html += f"{caption}</p></div>\n"
    return html


def build_main_figures_html(legends: dict[str, str]) -> str:
    """Build HTML for main figures (Figure 1/2/4/5)."""
    html = ""
    for fig_label, fig_file in MAIN_FIGURES.items():
        caption = legends.get(fig_label, "")
        html += _render_figure_block(fig_label, fig_file, caption)
    return html


def build_supplementary_figures_html(legends: dict[str, str]) -> str:
    """Build HTML for supplementary figures (Figure S1...) under a dedicated section heading.

    Wrapped in `.supplementary-section` so CSS keeps the heading on the same page as
    the first supplementary figure (avoids orphan heading at the end of the Main Figures page).
    """
    if not SUPPLEMENTARY_FIGURES:
        return ""
    html = '<div class="supplementary-section">'
    html += '<h2 class="supplementary-figures-heading">Supplementary Figures</h2>\n'
    for fig_label, fig_file in SUPPLEMENTARY_FIGURES.items():
        caption = legends.get(fig_label, "")
        html += _render_figure_block(fig_label, fig_file, caption, label_prefix="Supplementary ")
    html += "</div>\n"
    return html


def convert():
    md_text = MANUSCRIPT_MD.read_text(encoding="utf-8")
    legends = extract_figure_legends(md_text)

    # Remove Figure Legends section (rebuilt with actual images below)
    md_text = re.sub(
        r"### Figure Legends.*",
        "",
        md_text,
        flags=re.DOTALL,
    )

    # Convert pandoc-style superscripts ^text^ to <sup>text</sup>
    md_text = re.sub(r"\^([^^]+?)\^", r"<sup>\1</sup>", md_text)

    html_body = markdown.markdown(md_text, extensions=["tables", "smarty"])
    figures_html = build_main_figures_html(legends) + build_supplementary_figures_html(legends)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}{figures_html}</body></html>"""

    out_path = PDF_DIR / "kokutai-v6-final.pdf"
    weasyprint.HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(str(out_path))
    print(f"[OK] {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    convert()
