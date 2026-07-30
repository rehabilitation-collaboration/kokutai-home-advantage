# Subjective Judging and the Host Effect at Japan's National Sports Festival

A 47-prefecture panel analysis with a 2024-2025 cross-sectional interaction test.

## Overview

This repository contains the data and analysis code for a study examining whether hosting Japan's National Sports Festival (Kokutai) confers a larger competitive advantage in **subjectively judged** sports (gymnastics, artistic disciplines) than in **objectively measured** sports (track, weightlifting).

Using a 47-prefecture panel spanning 2012-2022 (n = 423 prefecture-years) plus a 2024-2025 cross-section of 6,991 prefecture-sport-year cells, we replicate Funahashi et al. (2016)'s pooled host bonus and extend the Balmer et al. (2003) subjective/objective decomposition to a Japanese natural-experiment setting. Under the primary specification, the marginal host bonus in subjectively judged sports is directionally consistent with a larger effect than in objectively measured sports (roughly threefold point estimate), though the wild-cluster bootstrap p-value under the few-treated-clusters correction (2 out of 47 clusters) is 0.175 — not conventionally significant.

## Repository Structure

```
├── src/
│   ├── data_loader.py                        # JSPO xls parsing (78/79 editions)
│   ├── panel_builder.py                      # Prefecture × year panel construction
│   ├── sport_classifier.py                   # Subjective/objective/mixed classification
│   ├── definitions.py                        # Host/treatment/period definitions
│   ├── analysis_main.py                      # Pooled ordered/binary logit
│   ├── analysis_replication.py               # Funahashi (2016) replication OLS
│   ├── analysis_confounders.py               # Csurilla-style staged specification
│   ├── analysis_event_study.py               # Two-layer event-study (pre-2005 + post-2016)
│   ├── analysis_cross_section_2024_2025.py   # 2024-2025 cross-section + wild-cluster bootstrap
│   └── plots.py                              # Figure generation
├── tests/                                    # 312 pytest cases across 10 modules
├── refs/                                     # Reference data (ESRI prefectural accounts + JSPO PDFs)
├── output/                                   # Reference verification tables
├── results/                                  # Regression result tables
├── plots/                                    # Generated figures (PDF + PNG)
├── pdf/                                      # Formatted manuscript PDFs
├── gpt-reviews/                              # GPT review cycle (round-1/2/3)
├── generate_pdf.py                           # Manuscript PDF generation (weasyprint)
├── run_all_models.py                         # Full pipeline runner
├── PLAN-DEVIATIONS.md                        # Deviation log
├── REVIEW-REPORT-asura-monju-round1.md       # asura-monju review (v3 → v4 integration)
├── requirements.txt                          # Python dependencies
└── manuscript.md                             # Full manuscript text
```

## Data Sources

- **Prefecture rankings (aggregated)**: [Nagano Prefecture Sports Association archive](https://www.nagano-sports.or.jp/kokutai/record/high_rank.html)
- **Individual-edition rankings (PDF + XLS)**: [JSPO (Japan Sport Association) official archive](https://www.japan-sports.or.jp/kokutai/tabid183.html)
- **Socioeconomic covariates**: [Cabinet Office ESRI prefectural accounts](https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/files/contents/main_2022.html)

## Reproduction

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests/           # 312 tests, ~5 min
python3 run_all_models.py          # runs all regression pipelines
python3 generate_pdf.py            # builds pdf/kokutai-vX-final.pdf
```

Python 3.14, pandas 3.0.5, numpy 2.5.1, statsmodels 0.14.6, patsy 1.0.2, scipy 1.18.0, python-calamine 0.8.2, pdfplumber 0.11.10, matplotlib 3.11.1, pytest 9.1.1, weasyprint 69.0, markdown 3.10.2.

## Citation

Shirai M. Subjective Judging and the Host Effect at Japan's National Sports Festival: A 47-Prefecture Panel Analysis with a 2024-2025 Cross-Sectional Interaction Test. SSRN Preprints. 2026.

## License

- Code: MIT License
- Manuscript and figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Data: Public domain (Japanese government open data + JSPO/prefectural sports association archives)

---

Part of a series on "Japanese customs vs data" (8th installment). See also: [friday13th](https://github.com/rehabilitation-collaboration/friday13th) (7th installment).
