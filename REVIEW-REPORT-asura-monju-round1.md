# Review Report: Kokutai Home-Advantage Paper v1.2

Date: 2026-07-28
System: Asura (Sonnet×3 parallel independent) + Monju (Opus×1 verification with WebSearch/WebFetch)
Paper: `manuscript.md` / `pdf/kokutai-v1.2.pdf` (23 pages, 889 KB)
Pre-processing: `verify_refs.py` **run** (`output/reference_verification.md` + `.json`; 7 MATCH / 3 not-indexed-on-Crossref annotated / 2 CrossRef mismatches corrected → v1.1 → v1.2)

---

## Critical Findings (P1) — 7 items

| # | ID | Issue | Source | Action Required |
|---|---|---|---|---|
| 1 | B-02/B-18 | **event_study layer key bug**: `_get_shocks()` expects "L1_pre2005"/"L2_post2016" but `run_all_models.py` L89 and `src/plots.py` L160-164 pass "layer1"/"layer2" → silent fallback to LAYER2 → **Figure 3 Layer 1 panel is a pixel-identical duplicate of Layer 2** (verified: identical `wald_stat=3.232942418521892e-27`, identical `frame shape (1081, 22)`, identical pre/post means). Layer 1 (2002 Kochi single event) was **never actually computed** in any manuscript-facing artifact | Asura(3/3) + Monju ACCEPT | Fix `run_all_models.py` L89 + `src/plots.py` L160-164 to use "L1_pre2005"/"L2_post2016". Regenerate `results/analysis_event_study.txt` + `plots/fig3_*.{png,pdf}`. Verify Layer 1 wald test and pre/post means actually differ from Layer 2. **Add assertion tests** (Monju B3): `assert set(L1['shock_year'].unique()) == {2002}` |
| 2 | A-04 | **Table 1 footnote lists wrong host years**: states "9 host years in 2012-2022 panel are 2013 Tokyo, ..., 2022 Tochigi, and **2025 Shiga**" — 2025 Shiga is outside the panel window; **2012 Gifu (kai=67, host+winner)** is silently missing. Discussion self-contradicts: "The **three** host wins" then lists **six** items | Asura(2/3) + Monju ACCEPT + code cross-check with `refs/host_mapping_raw.json` + `refs/nagano_high_rank.html` | Rewrite Table 1 footnote listing correct 9 hosts (2012 Gifu, 2013 Tokyo, 2014 Nagasaki, 2015 Wakayama, 2016 Iwate, 2017 Ehime, 2018 Fukui, 2019 Ibaraki, 2022 Tochigi) with Gifu's actual outcome (host+winner per Nagano data). Fix Results paragraph "three host wins" wording. Verify n=6 top-1 wins match |
| 3 | B-11 (Fig5) | **arithmetic-false claim** in Results L99 and Figure 5 caption: "all three within one standard error of Funahashi +1,675" is false. Actual gaps from `results/analysis_replication.txt`: funahashi_base **1.72 SE** away (99.20/57.58); extended_2003_2012 **1.17 SE** away (70.29/60.08); pooled_no_fe genuinely within 1 SE (0.42). `src/plots.py` actually plots **1.96×SE (95% CI)** not 1 SE | Asura(1/3 singleton) + Monju ACCEPT (elevated to P1: arithmetic independently verified) | Change "within one standard error" → "within 1.96 SE (95% CI)" in Results text + Fig 5 caption. Or restate as: "pooled_no_fe within 1 SE; funahashi_base and extended within 2 SE" |
| 4 | A-07 (pooled=M3) | **hidden covariates**: `src/analysis_main.py::_build_design_matrix` L89 always includes `log_population + log_gdp` regardless of `add_pref_fe`/`add_year_fe` flags. Table 2 "Ordered logit, pooled" (coef=-13.73) and "Top-1 logit, pooled" (+9.09) are **bit-for-bit identical** to Table 4 "M3 (+log_gdp)". Methods L57 "pooled ordered logit on rank" implies host-only; **Abstract's headline -13.73 / +9.09 are already covariate-adjusted**, not raw pooled | Asura(1/3 singleton) + Monju ACCEPT (elevated P2→P1: affects interpretation of primary panel result) | Two options: (a) rename Table 2 rows "Pooled ordered logit (+log_pop +log_gdp)" and "Pooled top-1 logit (+log_pop +log_gdp)"; refactor Abstract Methods sentence; add explicit note that pooled = M3 baseline. (b) Refactor `_build_design_matrix` to actually run host-only M0 as the true "pooled" spec, keeping M3 separately in Table 4 |
| 5 | B-03 (cluster) | **cross_section clustered SE has only 2 treated clusters** (Saga 2024 + Shiga 2025) out of 47 → severe anti-conservative SE risk (Cameron-Miller); undisclosed. Limitations only mention year-FE-collinearity aspect. **Directly threatens headline p=0.031** | Asura(1/3 singleton) + Monju ACCEPT (elevated to P1) | Add wild-cluster bootstrap on prefecture axis (Monte Carlo) or randomization inference; report bootstrap p-value alongside cluster-robust p. Add explicit Limitations paragraph on few-treated-clusters problem |
| 6 | Monju B1 | **Csurilla apples-to-oranges**: comparison of Csurilla's ~45% attenuation of IRR (ZINB on medal counts) to this paper's ~62%/~125% *increase* in logit odds (top-1) / ordered logit (rank) glosses over: (a) different DVs (medals vs top-1), (b) different link functions (log vs logit), (c) non-comparable covariate identifying variance (country-Olympics vs prefecture-Kokutai). "Opposite of Csurilla" framing is defensible only in absolute-percentage-change terms | Monju independent (P1) | Rewrite Discussion "Robustness to socioeconomic controls" paragraph to make scale/family mismatch explicit; either drop the "opposite" framing or add a footnote clarifying the comparison is in absolute-percentage-change of the host coefficient magnitude within each paper's own scale, not IRR-to-IRR |
| 7 | Monju B2 | **"pre-registered" claim without registry URL**: Methods L55 "Three complementary specifications were pre-registered" — no OSF/AsPredicted URL, no timestamp. `PLAN-DEVIATIONS.md` documents 7 deviations including addition of clay-target-shooting sport class after Phase 2 started. Claim is materially misleading | Monju independent (P1) + partial overlap with Asura A-16 | Either (a) remove the word "pre-registered" (safest), or (b) upload PLAN.md to OSF and cite, or (c) reword as "specifications were pre-declared in the project PLAN (see supplementary material at [URL])" |

---

## Important Findings (P2) — 12 items

| # | ID | Issue | Source | Action Required |
|---|---|---|---|---|
| 8 | B-11 (Fig2) | Figure 2 legend "±1 SE (prefecture-clustered)" vs Results body "95% confidence intervals" contradiction; `src/plots.py::plot_fig2` code confirms 1.96×SE with non-clustered plain two-sample variance formula | Asura(3/3) + Monju ACCEPT | Fix code to actually cluster on prefecture OR fix legend/text to match code (unified: "95% CI" from non-clustered SE, and note the limitation). Recommend the former |
| 9 | B-08 | No multiple-comparisons discussion (Bonferroni/FDR absent) despite 15+ tests. Headline p=0.031 marginal | Asura(3/3) + Monju ACCEPT | Add Methods paragraph on multiple-comparisons handling. Options: (a) Bonferroni across the primary specifications only; (b) explicit pre-registration statement that Table 5 baseline is the sole confirmatory test, everything else exploratory |
| 10 | B-16 | No 95% CI reported in any coefficient table (Tables 2-5) | Asura(3/3) + Monju ACCEPT | Add "95% CI" column to Tables 2, 4, 5 (compute as coef ± 1.96×SE for OLS/normal-approx; for logit report OR CIs where applicable) |
| 11 | B-19 | No model-fit statistic (log-likelihood / AIC / pseudo-R²) in logit tables 2, 4, 5 despite `llf` being computed | Asura(3/3) + Monju ACCEPT | Add pseudo-R² (McFadden) + log-likelihood columns to Table 2, 4; expose `llf` from `results/*.txt` |
| 12 | B-20/A-15 | Tokyo outlier: no formal Tokyo-exclusion sensitivity for Csurilla-reverse claim; narrative-only attribution | Asura(3/3) + Monju ACCEPT | Add `analysis_confounders.py` variant `run_staged_analysis(cup, dv, exclude_pref_codes=[13])` (Tokyo=13); report Table 4b or Fig 4b with Tokyo excluded |
| 13 | A-07 (n_obj) | Objective sport count "n=16" repeated 4 places (Abstract, Methods, Table 6, Fig 2) but implementation has 17 (clay-target added per Deviation #5) | Asura(2/3) + Monju ACCEPT + PLAN-DEVIATIONS #5 | Change all 4 places to "n = 17" (or "n = 16-17" with note on clay-target/boxing swap between 2024/2025); update Abstract sport totals to "40-41 sports (objective 17, subjective 11, semi-subjective 13)" |
| 14 | A-13 | Manuscript arithmetic "47 × [40+35+40+36] = 6,991" is wrong; correct = 7,097 (106 missing cells / 1.5% shortfall). Actual regression n=6,991 correct, but 106 missing cells undocumented (likely unbalanced prefecture-sport participation) | Asura(1/3 singleton) + Monju ACCEPT | Fix Methods L61 arithmetic and add a footnote explaining the 106-cell shortfall (e.g., "prefectures with no participation in specific sports are dropped by design in the JSPO overall-standings publication") |
| 15 | B-09 | p=6.7×10⁻¹⁹ (Results L93) unreproducible from reported coef/SE; correct value from `results/analysis_confounders.txt` is 4.807824×10⁻¹⁹ (~40% off from what manuscript claims) | Asura(1/3 singleton) + Monju ACCEPT | Change "p = 6.7 × 10⁻¹⁹" → "p = 4.8 × 10⁻¹⁹" or cap at "p < 0.001" (see Finding #16 for p-precision policy) |
| 16 | B-10 | Excessive p-value precision (p<10⁻¹⁵⁰, p=6.7×10⁻¹⁹) inconsistent with paper's other disciplined precision (p=0.001 exact 0.00115) | Asura(3/3) + Monju ACCEPT | Standardize p-value reporting: cap at "p < 0.001" or "p < 10⁻⁵" for very small; retain exact 3-4 significant digits only where the precision is genuinely meaningful (e.g., interaction p=0.031) |
| 17 | B-03 (pooled SE) | Table 2 "pooled" uses non-clustered Fisher-info SE on a 47×9 panel (repeated-observations structure) → risks understating SE / overstating significance for Abstract-headline -13.73 / +9.09 | Asura(1/3 singleton) + Monju ACCEPT | Add prefecture-clustered SE to `fit_logit` in `src/analysis_main.py`; report both non-clustered and clustered SE in Table 2 (or replace non-clustered with clustered as primary) |
| 18 | B-03 (prop-odds) | Ordered-logit proportional-odds (parallel-lines) assumption never tested or acknowledged | Asura(1/3 singleton) + Monju ACCEPT | Add Brant test OR partial-proportional-odds diagnostic to `analysis_main.py`; report result in Methods or Limitations |
| 19 | A-16 | "pre-registered" claim (overlaps with Monju B2 above): 2/3 Asura vote reinforces Monju P1 verdict | Asura(2/3) + Monju independent P1 | See Finding #7 above |
| 20 | Monju B4 | Table 5 rank-deficient row (three-way spec, coef=+12.99/+20.31, SE=NaN) shown next to inferential rows → reader could misread as estimate | Monju independent (P2) | Move rank-deficient row to supplementary material OR prefix with "Diagnostic only — not identified" tag |
| 21 | Monju B5 | Cross-section identification is asymmetric: with only 2 host prefectures, β_HS is identified from "Shiga vs Saga in subjective sports vs Shiga vs Saga in objective sports" — fragile 2-prefecture identification structure | Monju independent (P2) | Add explicit paragraph to Limitations describing the 2-prefecture identification structure for β_HS; make explicit that the interaction is essentially estimated off ~38 subjective host cells split between 2 host prefectures |

---

## Minor Findings (P3) — 11 items

| # | ID | Issue | Source | Action Required |
|---|---|---|---|---|
| 22 | E-03 | Abbreviations used without first-use expansion: FE, DID, OLS, ICMJE, CRediT, 2008SNA | Asura(3/3) + Monju ACCEPT | Spell out at first use in Abstract (FE) and Methods (DID, OLS, 2008SNA); expand ICMJE/CRediT in metadata sections |
| 23 | C-14 | Analysis code not publicly released at SSRN posting time | Asura(3/3) + Monju ACCEPT + B7 | Commit to a release timeline (OSF/GitHub/Zenodo) in Data Availability, or defer to a supplementary release note |
| 24 | A-05 | "2013 Tokyo dropped for host-effect identification" ambiguous — 2013 Tokyo is actually retained in the n=423 regression per `build_analysis_frame` code | Asura(2/3) + Monju ACCEPT (severity notes "higher than P3") | Rewrite footnote: "2013 Tokyo is Tokyo's own host year and is retained in the regression sample (n=423) but is not used in the descriptive '6 of 9 host-year top-1' count since Tokyo dominates non-host years generally" |
| 25 | E-04 (Fig5) | Figure 5 label overlaps (+1,604 vs title, +1,733 vs error-bar cap, +1,675 ref vs +1,575) | Asura(1/3 singleton) + Monju ACCEPT marginal | Adjust `src/plots.py::plot_fig5_replication_extended` label offsets to prevent collision |
| 26 | E-04 (Table 4 collision) | "Table 4" used 3× in-text to mean Funahashi's Table 4 (external), clashing with manuscript's own Table 4 | Asura(1/3 singleton) + Monju ACCEPT | Qualify all 3 external references as "Funahashi (2016) Table 4" or "Funahashi's Table 4" (author's already partial — fully explicit) |
| 27 | C-02 | IRB exemption citation ("Japanese Ethical Guidelines for Medical and Biological Research Involving Human Subjects") is domain-mismatched for a sports-record econometric paper | Asura(1/3 singleton) + Monju ACCEPT | Either (a) omit specific guideline citation and note "public non-personal data — no ethics review required," or (b) cite MEXT policy for non-medical research using public data |
| 28 | B-13 | Table 2 SE precision inconsistent: "172.4" (1 decimal) vs "1.54"/"2.80" (2 decimals) | Asura(1/3 singleton) + Monju ACCEPT | Standardize to 2 decimals throughout Table 2 SE column |
| 29 | Monju B3 | Test suite (259 tests) does NOT catch the layer1/layer2 event-study bug (Finding #1) | Monju independent (P2/P3) | Add assertion-based tests: `test_event_study_layer_shocks_are_distinct` asserting `set(L1_frame.shock_year.unique()) == {2002}` |
| 30 | Monju B7 | AI-assist disclosure is ahead-of-curve specific; data disclosure lags | Monju independent (P3) | Commit timeline for OSF/GitHub code release in Data Availability |
| 31 | A-07 (Fig1) | Figure 1 shows y≈0.5 fractional point near x=1993 (mechanism not documented) | Asura(1/3 singleton) + Monju UNCERTAIN | Verify visually; if real, add note explaining the fractional value (multi-host / co-host year) |
| 32 | Monju B9 | `LITERATURE.md` describes Ref [2] as "Home advantage in the Commonwealth Games" but manuscript Ref [2] is correctly "A comparative analysis of home advantage in the Olympic and Paralympic Games 1988-2018" (LITERATURE.md is internal doc; not SSRN-visible) | Monju independent (P3) | Update `LITERATURE.md` §11 title description to match the corrected manuscript reference |

---

## Rejected by Monju

| # | Asura Finding | Rejection Reason |
|---|---|---|
| — | (none) | Monju REJECTed 0 of 27 Asura findings. 1 PARTIAL (A-24 tone: "not a hard contradiction but a stylistic inconsistency — recommend hedge phrase in Results"). 1 UNCERTAIN (Fig 1 fractional point; not verified without image inspection) |

---

## Review Statistics

- **Asura**: 49 checklist items × 3 parallel Sonnet agents = 147 item-checks. Raw findings: 18 (asura 1) + 20 (asura 2) + 16 (asura 3) = **54 raw findings**. After 2/3+ vote filter and singleton-with-strong-evidence promotion: **27 aggregated findings**.
- **Monju verification**: **ACCEPT 26** / PARTIAL 1 / UNCERTAIN 1 / REJECT 0.
- **Monju independent** (checklist B-01 through E-08, Opus + WebSearch/WebFetch): **9 additional findings** (P1×2, P2×3, P3×4).
- **Total confirmed findings**: **36** (Critical 7, Important 12, Minor 11 = 30 confirmed by vote or Monju; 5 PARTIAL/UNCERTAIN/duplicate items rolled up; 1 duplicate #12 = #7).
- **Bibliographic verification** (`verify_refs.py` pre-processing): 7 refs CrossRef-MATCH (including 2 corrections applied v1→v1.2: Ref 2 Wilson & Ramchandani, Ref 6 Funahashi title, Ref 10 Nomura author/title); 3 refs correctly annotated "not indexed on Crossref" (Suetsugu 2024/2025, Lan & Yu 2012); 0 fabrications.
- **Pre-processing**: **run** (`output/reference_verification.md` + `.json`).

---

## Priority Repair Ordering (for v2 writing)

1. **P1 code fixes first** (Findings #1, #4): actually running code changes propagates to Fig 3, Table 2, results/*.txt regeneration — do these before any text edits so downstream numbers stay in sync.
2. **P1 fact fixes** (Findings #2, #3, #5, #6, #7): text-only corrections that can be applied after the code fix.
3. **P2 quantitative additions** (Findings #10-#12, #17, #18, #20, #21): require code changes (CI computation, wild-cluster bootstrap, Tokyo-exclusion re-run, Brant test) with corresponding table/figure updates.
4. **P2 text-only corrections** (Findings #8, #9, #13-#16, #19): straightforward text edits.
5. **P3 cleanup** (Findings #22-#32): batch at end before v2 PDF build.

## v2 P1 Completion Status (added 2026-07-28)

All 7 P1 findings resolved in an additional session on 2026-07-28. Draft PDF `pdf/kokutai-v2-p1-complete.pdf` (25 pages, 929 KB) was built after P1 completion as a rollback checkpoint before P2/P3 begin.

| Finding | Status | Commit | Notes |
|---|---|---|---|
| #1 event_study layer key | ✅ FIXED | `56b3a7b` | `_get_shocks` now raises ValueError; +5 assertion tests; Layer 1 truly computes as 2002-only single-event |
| #2 Table 1 footnote | ✅ FIXED | `28de498` | 9-host list corrected (2012 Gifu added, 2025 Shiga removed, three/six typo fixed) |
| #3 Fig 5 "within one SE" | ✅ FIXED | `28de498` | Text + caption unified as "within 1.96 SE (95% CI)" |
| #4 pooled = M3 hidden covariates | ✅ FIXED | `8983824` | Rename option (a) adopted — 6 locations updated to disclose log_pop + log_gdp explicitly. Numerical values unchanged. |
| #5 cross_section 2-treated-cluster | ✅ FIXED (**substantive**) | `38c4597` | Wild-cluster bootstrap implemented; **p moves from 0.031 to 0.155**. Reflected honestly in 7 manuscript locations + Table 5 new row + References 13/14 added. |
| #6 Csurilla apples-to-oranges | ✅ FIXED | `28de498` | "Opposite of Csurilla" framing dropped; DV/link/identification-variance mismatch explicitly disclosed |
| #7 "pre-registered" claim | ✅ FIXED | `28de498` | Methods L55 rewritten as "The primary analysis is organized around three complementary specifications" |

Pytest: 259 → 267 (all pass). `verify_refs.py`: Refs 13/14 checked (Ref 13 shows a crossref author-field-mapping artifact, AMA style preserved).

**Substantive impact of #5**: The novelty-core claim was downgraded from "first quantitative confirmation" to "directionally consistent first quantitative anchor". The descriptive monotonicity (+37.9 subj vs. +17.6 obj) and log-outcome interaction direction (+0.293) continue to support the Balmer2003 direction independently.

## Remaining v2 work (P2/P3)

- **P2 quantitative additions** (12 items, some with code work): Findings #8 Fig 2 clustered SE, #9 multiple-comparisons discussion, #10 CI columns (Tables 2/4/5), #11 pseudo-R²/llf columns, #12 Tokyo-exclusion sensitivity, #13 objective-sport count 16→17, #14 arithmetic 6,991 vs 7,097, #15 p = 6.7×10⁻¹⁹ → 4.8×10⁻¹⁹, #16 p-precision policy, #17 pooled clustered SE, #18 Brant test, #20 Table 5 rank-deficient tagging, #21 2-prefecture asymmetric identification.
- **P3 cleanup** (11 items, mostly text): #22-#32 (abbreviation expansion, 2013 Tokyo footnote, Fig 5 label overlap, IRB citation domain, Table 2 SE precision, assertion tests documentation, Fig 1 y≈0.5 point investigation, LITERATURE.md §11 update).
- **Then**: rebuild PDF as `pdf/kokutai-v2-final.pdf` (edit `generate_pdf.py` out_path), rerun verify_refs.py, self-QA 100% via pdftotext -layout, then GPT round-1 iteration cycle.

## Post-v2 workflow

1. Regenerate `results/*.txt` after code fixes
2. Rebuild PDF → `pdf/kokutai-v2.pdf`
3. Rerun `verify_refs.py`
4. `pdftotext -layout` self-QA (100%)
5. Consider GPT round-1 review (per friday13th precedent V1→V10 iteration)
6. Update handoff-kokutai-home-advantage.md with v2 milestone

---

## Notes on emphasis items (per original review request)

1. **Novelty defense (Balmer2003 gap vs Funahashi 2016)**: All 3 Asura + Monju CONFIRMED. `PHASE8-INVESTIGATION.md` Part 2 §B-1 documents an independent full-text read (hades ACCEPT verdict); Funahashi cites Balmer 2001 once (p.20), does not cite Balmer 2003, does not fit any sport-type interaction. Novelty claim stands.
2. **Bibliographic accuracy (Funahashi + Csurilla corrections)**: All 3 Asura + Monju CONFIRMED. Applied correctly in Ref [6] (Funahashi H, Hibino M, Ishiguro E, Mano Y — added Hibino/Ishiguro; corrected journal to *Japanese Journal of Sport Management* 8(1):17-33) and Ref [9] (Csurilla G, Fertő I — two-author correction).
3. **Cross-section interpretation (2-year year FE ≈ single dummy)**: honestly disclosed in Limitations; supplemented by Monju B5 (fragile 2-prefecture identification structure) as an additional Limitations paragraph to add.
4. **Csurilla-attenuation reversal credibility**: FLAGGED as Monju B1 (P1) — the "opposite of Csurilla" framing is defensible only under narrow conditions; requires rewrite.
5. **Event-study identification honesty**: The paper's *prose* disclosure is adequate, but Finding #1 shows the *actual* Layer 1 was never computed. Fix code + regenerate before any further claims.
6. **Reference bibliography (12 refs)**: 7 CrossRef-MATCH + 3 correctly-annotated-non-Crossref + 2 corrected v1→v1.2. Handling is honest.
7. **Statistical reporting (results/*.txt vs manuscript)**: Overwhelmingly consistent (Monju cross-checked; "essentially perfect agreement" per asura 3). Two exceptions: Finding #15 (p=6.7×10⁻¹⁹ manuscript vs 4.8×10⁻¹⁹ actual) and Finding #1 (event-study results file is corrupted by the layer-key bug).
