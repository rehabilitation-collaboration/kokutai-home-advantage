# Home Advantage in Japan's Kokutai: Evidence from 77 Editions and Sport-Type Heterogeneity

A 75-edition host-rank truth test (1948-2025) with a 2024-2025 sport-level cross-sectional interaction test.

## Overview

This repository contains the data and analysis code for a study asking whether the host prefecture of Japan's National Sports Festival (Kokutai) actually reaches the top-*k* places at rates above chance. Using host-prefecture rank data for 75 non-cancelled editions (3rd-79th, spanning 1948-2025; editions 1-2 excluded due to complete public-data absence and editions 75-76 excluded due to COVID cancellation) across the emperor's cup and empress's cup (n = 150 host-rank observations), we run one-sample proportion tests, permutation tests, three-era χ² comparisons, and a pooled ordered logit at three top-*k* thresholds (top-1, top-3, top-8). A subsidiary 2024-2025 cross-section (n = 6,991 prefecture-sport-year cells) extends the Balmer et al. (2003) subjective/objective decomposition to a Japanese natural-experiment setting.

**Main finding.** Host prefectures reach top-1 at 76.0% (emperor's cup) and 62.7% (empress's cup) versus a null of 1/47 = 2.13% (both p < 10⁻⁵⁰, exact binomial), replicated at Monte Carlo minimum p = 1/10,001 under permutation. The 3-era comparison reveals a non-monotonic pattern (early 43.3% ≈ shock 42.9% ≪ golden 94.7%, pooled χ² = 46.76, p < 10⁻¹⁰). In the 2024-2025 subsidiary cross-section, the marginal host bonus in subjectively judged sports is directionally larger than in objectively measured sports (β_HS = +16.68 on top of a baseline β_H = +16.60), though the wild-cluster bootstrap p-value under the few-treated-clusters correction (2 out of 47 clusters) is 0.155 — not conventionally significant.

## Repository Structure

```
├── src/
│   ├── data_loader.py                        # JSPO PDF/xls + Nagano HTML parsing
│   ├── panel_builder.py                      # Prefecture × year panel construction
│   ├── sport_classifier.py                   # Subjective/objective/semi-subjective classification
│   ├── definitions.py                        # Host/treatment/era definitions
│   ├── analysis_main_v3.py                   # v3 main: one-sample binomial + permutation + era χ² + pooled ordered logit
│   ├── analysis_replication.py               # Funahashi (2016) OLS replication (Supp §S3)
│   ├── analysis_event_study.py               # Two-layer event-study (Supp §S1)
│   ├── analysis_cross_section_2024_2025.py   # 2024-2025 cross-section + wild-cluster bootstrap (subsidiary)
│   └── plots.py                              # v3 main Fig 1-3 + Supp Fig S1/S2 generation
├── scripts/
│   ├── dump_analysis_main_v3.py              # Dump v3 main analysis results → results/analysis_main_v3.txt
│   └── verify_host_rank_jspo_nagano.py       # Cross-verify JSPO vs Nagano host-rank data
├── tests/                                    # 326 pytest cases across 10 modules
├── refs/                                     # Reference data (JSPO PDFs/xls + Nagano HTML + ESRI)
├── output/                                   # Reference verification tables
├── results/                                  # Regression result tables (analysis_main_v3.txt etc.)
├── plots/                                    # Generated figures (PDF + PNG)
├── pdf/                                      # Formatted manuscript PDFs
├── gpt-reviews/                              # GPT review cycle logs
├── generate_pdf.py                           # Manuscript PDF generation (weasyprint)
├── run_all_models.py                         # v3 subsidiary analyses runner (replication + event-study + 2024-25 cross-section)
├── PLAN-DEVIATIONS.md                        # Plan deviation log
├── REVIEW-REPORT-asura-monju-round1.md       # asura-monju review round 1 (pre-v3 legacy record)
├── asura-monju-round-1-on-v3.md              # asura-monju review round 1 on v3 manuscript
├── requirements.txt                          # Python dependencies
└── manuscript.md                             # Full manuscript text
```

Deprecated legacy modules (`src/analysis_main.py` = 2012-2022 legacy 47-prefecture-year panel with pooled ordered/binary logit and Brant-style partial-proportional-odds diagnostic; `src/analysis_confounders.py` = Csurilla-style staged specification) were removed in M4-H (commit `fb92fe2`, 2026-07-31). They remain archived in the git history at commit `fa07fd2` and earlier for reproducibility of the preliminary diagnostic reported in Limitations §Sixth and the pipeline validation reported in Supplementary Materials §S3.

## Data Sources

- **Host prefecture rankings (aggregated 1948-2025 top-1 to top-8)**: [Nagano Prefecture Sports Association archive](https://www.nagano-sports.or.jp/kokutai/record/high_rank.html)
- **Individual-edition detailed rankings (PDF + XLS)**: [JSPO (Japan Sport Association) official archive](https://www.japan-sports.or.jp/kokutai/tabid183.html)
- **Socioeconomic covariates (for Supp §S3 Funahashi replication only)**: [Cabinet Office ESRI prefectural accounts](https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/files/contents/main_2022.html)

## Reproduction

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests/                       # 326 tests, ~3 min
python3 scripts/dump_analysis_main_v3.py       # v3 main analysis dump → results/analysis_main_v3.txt
python3 run_all_models.py                      # Subsidiary v3 analyses (replication + event-study + 2024-25 cross-section)
python3 generate_pdf.py                        # builds pdf/kokutai-v3-final.pdf
```

Python 3.14, pandas 3.0.5, numpy 2.5.1, statsmodels 0.14.6, patsy 1.0.2, scipy 1.18.0, python-calamine 0.8.2, pdfplumber 0.11.10, matplotlib 3.11.1, pytest 9.1.1, weasyprint 69.0, markdown 3.10.2, pyarrow 25.0.0.

## Citation

Shirai M. Home Advantage in Japan's Kokutai: Evidence from 77 Editions and Sport-Type Heterogeneity. SSRN Preprints. 2026.

## License

- Code: MIT License
- Manuscript and figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Data: Public domain (Japanese government open data + JSPO/prefectural sports association archives)

---

Part of a series on "Japanese customs vs data" (8th installment). See also: [friday13th](https://github.com/rehabilitation-collaboration/friday13th) (7th installment).
