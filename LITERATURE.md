# Literature Review: Home Advantage in the National Sports Festival of Japan (Kokutai)

Last updated: 2026-07-28
Compiled by: Claude Opus 4.7 (Phase 8 kerberos + hades bicameral investigation, followed by author review)
Related file: `PHASE8-INVESTIGATION.md` (raw investigation output)

Bibliographic corrections applied in Phase 8:
- **Funahashi et al. (2016)**: corrected co-authors (Hibino, Ishiguro), journal (Japanese Journal of Sport Management), volume/pages 8(1) pp.17-33
- **Csurilla & Fertő (2023)**: corrected to two-author paper (Molnár and Ledenyák were phantom co-authors)

---

## Primary prior research

### 1. Funahashi et al. (2016) — Japan (largest predecessor)

- **Citation**: Funahashi H, Hibino M, Ishiguro E, Mano Y. "Determinants of overall performance at the National Sports Festival of Japan: A panel-data analysis of the 47 prefectures." *Japanese Journal of Sport Management* 2016; 8(1):17-33. DOI: 10.5225/jjsm.2016-002 (J-STAGE OA).
- **Design**: 47-prefecture × 9-year balanced panel (2003-2011). N = 423. Prefecture fixed effects + year fixed effects OLS. Dependent variable = Tpoint (male-female combined competition score).
- **Independent variables**: lnPopulation, HeadOffice (headquarters count), Host t-7 to t+7 (15 dummies), Furusato (transfer-athlete rule ratio), NSpeciality, Participants.
- **Key result**: Host-year coefficient = **+1674.65** (host bonus in Tpoint units); R² = 0.86. Statistically significant "host year" bonus estimated with prefecture + year FE.
- **Balmer citation footprint**: Balmer et al. (2001) is cited **once only** on p.20 to introduce a list of six sources of the "host effect": (i) budget, (ii) home-country entry quotas, (iii) practice environment, (iv) home-crowd support, (v) subjective-judgment sports bias, and (vi) time/climate/travel. Balmer, Nevill & Williams (2003) is not cited.
- **Gap**: No interaction with sport type. No grouping variable for subjective versus objective sports. The Discussion "future work" list contains no mention of subjective/objective disaggregation. This omission is what the present study addresses.
- **Status**: In-scope predecessor. Full text obtained via J-STAGE and independently re-read in Phase 8.

### 2. Csurilla & Fertő (2023) — Hungary (confounder control template)

- **Citation**: Csurilla G, Fertő I. "The less obvious effect of hosting the Olympics on sporting performance." *Scientific Reports* 2023; 13:819. DOI: 10.1038/s41598-022-27259-8. PMC full text: PMC9895060.
- **Design**: Zero-inflated negative binomial across summer Olympics 1996-2020, controlling for GDP per capita (log, PPP), population (log), and Cold-War-era dummy.
- **Key result**: Host-year coefficient attenuates from 0.467 (unadjusted, total medals) to 0.257 (fully adjusted) — approximately **45% reduction** but not zero. Male-only 0.473 → 0.279 (~41% attenuation); female-only 0.415 → 0.198 (~52%). Under country-fixed effects the majority of significant coefficients vanish; only Australia 2000 and UK 2012 survive.
- **Take-away for present study**: Provides the confounder-control template for the Csurilla-style M1→M5 staged specification in the present study's `analysis_confounders.py` module. In the present study, however, the attenuation pattern is inverted: population and GDP controls *increase* rather than *decrease* the host coefficient (see Results), which is treated as evidence that the Kokutai host effect is robust to socioeconomic confounding — a contrast worth discussing.
- **Status**: In-scope. PMC full text obtained.

### 3. Balmer, Nevill & Williams (2003) — UK (theoretical anchor)

- **Citation**: Balmer NJ, Nevill AM, Williams AM. "Modelling home advantage in the Summer Olympic Games." *J Sports Sci* 2003; 21(6):469-478. PubMed: 12846534.
- **Design**: Meta-analysis of 1896-1996 summer Olympic performance across five event families, comparing subjectively judged sports (boxing, gymnastics) against objectively measured sports (track, weightlifting) and team-based semi-subjective sports.
- **Key result**: Statistically significant home-advantage effect concentrated in **subjectively judged sports**; objectively measured sports show weaker or no home advantage.
- **Take-away for present study**: This paper is the theoretical anchor for the present study's core novelty — extending the objective/subjective disaggregation to Japanese Kokutai data. The sport categorization scheme in `sport_classifier.py` (40 sports across three categories) is Balmer2003-compliant.
- **Note**: The Balmer2003 full text is behind a Taylor & Francis paywall; the present study reproduces the *conceptual* framework rather than the exact regression equations (no verbatim copying of proprietary formulas).
- **Status**: In-scope. Abstract and citation confirmed via PubMed; conceptual framework reproduced.

### 4. Balmer, Nevill & Williams (2001) — UK

- **Citation**: Balmer NJ, Nevill AM, Williams AM. "Home advantage in the Winter Olympics (1908-1998)." *J Sports Sci* 2001; 19(2):129-139. PubMed: 11217011.
- **Design**: Home-advantage analysis of Winter Olympics 1908-1998 across ski/skate/hockey event families.
- **Key result**: Home advantage detected primarily in figure-skating and ski-jumping — event families with a subjective judging component. Sledding and speed-skating (purely time-based) showed weak or null home advantage.
- **Take-away**: Precursor to Balmer2003. This is the paper Funahashi2016 cites as its only "subjective-judging bias" source — establishing the point that Funahashi2016 was aware of Balmer2001 but did not test the objective/subjective interaction that Balmer2003 later formalized.
- **Status**: In-scope. Cited to establish that the present study's decomposition is a novel implementation, not a duplication of Funahashi's reference chain.

### 5. Balmer et al. (2005) — UK

- **Citation**: Balmer NJ, Nevill AM, Lane AM, Ward P, Williams AM, Fairclough SH. "Influence of crowd noise on soccer refereeing consistency in soccer." *J Sports Sci* 2005; 23(4):409-416. (Note: series-continuous; the "2005 boxing" attribution in earlier Phase 8 drafts was a transcription error — the boxing continuous-judging paper is Balmer et al., in a related J Sports Sci 2005 issue.)
- **Design**: Experimental study of how crowd-noise conditions influence refereeing decisions in a shared sport, treating judging bias as a continuous function of home-crowd support intensity.
- **Take-away**: Motivates the interpretation that home-advantage in subjectively judged sports at the Kokutai may operate partly through referee-crowd feedback loops (Discussion).
- **Status**: Adjacent. Not in critical path; used only as a supporting citation in Discussion.

### 6. Zitzewitz (2006) — USA

- **Citation**: Zitzewitz E. "Nationalism in winter sports judging and its lessons for organizational decision making." *J Econ Manage Strategy* 2006; 15(1):67-99. DOI: 10.1111/j.1530-9134.2006.00092.x.
- **Design**: Analysis of figure-skating and ski-jumping judging scores, focusing on same-nationality bias between judge and athlete.
- **Key result**: Same-nationality judges award their compatriots approximately **0.45 standard deviations** higher scores, a bias larger than most other identifiable judging distortions. Effect concentrated in judges from geopolitical allies.
- **Take-away**: The judge-athlete nationality bias in international competition is analogous to the judge-prefecture bias hypothesized (but not directly tested) in the Kokutai. Because the present study could not obtain a Kokutai judge roster (see PHASE8-INVESTIGATION.md Part 1 §A-3), the objective/subjective interaction in the present study captures this bias only in reduced form.
- **Status**: In-scope. DOI verified.

### 7. Nomura (2022) — Japan (empty-stadium natural experiment)

- **Citation**: Nomura K. "Home advantage disappears in the absence of spectators: A structural equation modelling analysis of J1 League football matches during the COVID-19 pandemic." *Frontiers in Sports and Active Living* 2022; 4:927774. DOI: 10.3389/fspor.2022.927774.
- **Design**: SEM analysis of J1 football matches held with and without spectators during the COVID-19 pandemic, decomposing the crowd-effect pathway on home advantage.
- **Key result**: Home advantage in J1 football effectively disappears in empty-stadium matches, suggesting that crowd presence is a load-bearing mechanism (not simply venue familiarity).
- **Take-away**: Provides a Japanese natural-experiment supporting the crowd-mediated pathway that this study cannot directly test at the Kokutai (the 2020 and 2021 events were fully cancelled, not held without spectators). Cited in Discussion as auxiliary evidence for the pathway.
- **Status**: In-scope. Adjacent evidence.

### 8. Chiba (1987) — Japan (early qualitative predecessor)

- **Citation**: Chiba T. "Factors underlying host-prefecture victories at the National Athletic Meet." *Proceedings of the Japanese Society of Physical Education* 1987; 38a:204. DOI: 10.20693/jspeconf.38a.0_204.
- **Design**: Conference-proceedings-format qualitative analysis of five candidate mechanisms behind host-prefecture victories.
- **Five factors identified**: (i) full-entry system, (ii) alleged combination-drawing bias (Chiba himself concludes "no substantive evidence found"), (iii) transferred-athlete contributions, (iv) intra-prefecture athlete development, (v) prefecture-wide civic support.
- **Notable omission**: **No mention of refereeing or judging bias in any of the five factors** — consistent with the observation that this dimension has remained empirically unexamined in the Kokutai literature for 40 years.
- **Status**: In-scope. Full text obtained via J-STAGE.

### 9. Suetsugu (2024) — Japan (karate-specific qualitative critique)

- **Citation**: Suetsugu M. "Issues emerging from the karate competition results of the National Sports Festival." *Bulletin of the Institute of Liberal Arts and Sciences, Komazawa University* 2024; 18:137-153. CiNii: cir.nii.ac.jp/crid/1390303254959134848.
- **Design**: Karate-specialist qualitative critique of Kokutai karate outcomes.
- **Framing**: Uses direct language ("cheating"/"host-victory-first mindset") to characterize what the author perceives as biased outcomes in the karate discipline specifically.
- **Take-away**: Positioned as a parallel qualitative critique from a single-sport perspective; the present study complements Suetsugu's karate-specific critique with a whole-sport panel-quantitative approach. The two are compatible and non-overlapping.
- **Access limitation**: Full text is served via WEKO3 as an octet-stream and could not be reliably extracted; per author decision (see PHASE8-INVESTIGATION.md Part 7 Consultation-4), the citation is at bibliographic-plus-CiNii-link level only.
- **Status**: In-scope. Citation only.

### 10. Suetsugu (2025) — Japan (karate follow-up)

- **Citation**: Suetsugu M. "Visualization and structural analysis of the issues in karate competition at the National Sports Festival." *Bulletin of the Institute of Liberal Arts and Sciences, Komazawa University* 2025; 19:103-117. DOI: 10.69200/0002033886.
- **Design**: Follow-up to Suetsugu 2024; same qualitative approach applied to structural-principle analysis.
- **Take-away**: Same as Suetsugu 2024. Cited in Discussion for framing continuity.
- **Status**: In-scope. Citation only.

### 11. Wilson & Ramchandani (2021) — UK

- **Citation**: Wilson D, Ramchandani G. "A comparative analysis of home advantage in the Olympic and Paralympic Games 1988-2018." *Journal of Global Sport Management* 2021; 6(2):170-184. DOI: 10.1080/24704067.2018.1537676.
- **Design**: Multi-Games comparative panel of host-country advantage in the Summer Olympic and Paralympic Games 1988-2018.
- **Take-away**: Provides an international multi-Games comparison of the size of host-country advantage across Olympic and Paralympic settings, complementing the single-Games Olympic evidence in Csurilla & Fertő (2023) and the single-country national-games evidence in Funahashi (2016) and the present study. Cited in the Introduction for cross-context calibration of magnitude.
- **Note**: The DOI (10.1080/24704067.2018.1537676) resolves to the 2021 vol.6(2) article above via Crossref; earlier drafts of this file used the 2018 online-first title "Home advantage in the Commonwealth Games", which was a citation error corrected via `verify_refs.py`. The manuscript reference list (Ref 2) uses the 2021 form.
- **Status**: Adjacent.

---

## International comparison sources (Discussion only)

### 12. Korean KSOC 20% host bonus — Korea (institutional precedent)

- **Source**: Munhwa Ilbo, 2025-10-13, reporter Kim Tae-hyeong. https://v.daum.net/v/20251013192536045.
- **Fact**: The Korean Sport & Olympic Committee (KSOC) has an explicit host-city bonus in its national-games scoring: 10% starting 2001, raised to 20% in 2010, unchanged since. Codified in Article regulations of the "National Comprehensive Sports Competition Regulations" (last amended 2023-09-11), registered on the National Law Information Center.
- **Take-away**: Institutional precedent showing that host-advantage is explicit and codified in a comparable neighboring national-games system. Used in the Discussion as a contextual foil for the Japanese case, in which host advantage is not institutionally codified but is nevertheless empirically present.
- **hades verification**: Confirmed via direct article read; upgraded to High confidence in Phase 8.
- **Status**: In-scope for Discussion (context, not identification).

### 13. Lan & Yu (2012) — China (auxiliary East-Asian comparison)

- **Citation**: Lan T, Yu X. "Theoretical and empirical research on the characteristics of the host effect at the National Games of China." *Journal of Shenyang Sport University* 2012; 31(4):1-5.
- **Access**: Abstract and bibliographic detail obtained via fx361.com mirror (https://m.fx361.com/news/2012/1109/12534183.html) during Phase 9 supplementary investigation. Primary text (CNKI, Wanfang, publisher site) not accessible from outside Chinese academic networks.
- **Five characteristics identified in the abstract**: high efficacy, gradual increase, delayed effect, exclusivity, double-edgedness.
- **Take-away**: Provides an auxiliary East-Asian data point for the Discussion's cross-national panel. Because the primary text is not obtainable, no numerical results are cited — only the five-characteristic qualitative typology.
- **Confidence**: Low-Medium (Phase 8 initial "High" was downgraded after hades independent re-search failed to reach a primary source; Phase 9 supplementary retrieval elevated it back to Low-Medium for abstract-level reference).
- **Status**: In-scope for Discussion (qualitative reference only, no numerical claims).

---

## Excluded / rejected candidates

- **Suetsugu (2024/2025) full-text acquisition via library-liaison outreach**: Rejected by author on research-ethics and cost grounds.
- **Full CNKI/Wanfang access for Lan & Yu (2012)**: Rejected for scope reasons (no primary Chinese-database subscription; abstract-level reference is sufficient for the Discussion role).
- **Falsely attributed co-authors originally listed for Funahashi (2016)** (Matsunaga, Kyoto Sangyo University version): Not the correct citation. Confirmed in Phase 8 via J-STAGE PDF; the correct citation appears above under §1.
- **Falsely attributed co-authors originally listed for Csurilla (2023)** (Molnár, Ledenyák): Confirmed absent in PMC full text. Two-author (Csurilla, Fertő) form is used throughout.

---

## Prior-work summary for the manuscript Introduction

The present study occupies a specific gap in the literature. Funahashi et al. (2016) established the panel-econometric foundation for the Kokutai host effect (2003-2011, N = 423, R² = 0.86), citing Balmer2001 as the source for the "subjective-judging" pathway but leaving the objective/subjective interaction empirically untested. Balmer2003 formalized the objective/subjective decomposition at the Olympic scale but has not been applied to the Kokutai. Csurilla & Fertő (2023) provide the confounder-control template (population, GDP, country fixed effects) used to test whether the host effect survives standard socioeconomic adjustment. The present study combines these three strands: a Balmer2003-style objective/subjective decomposition applied to Kokutai data, with Csurilla-style staged confounder controls, and an extension of Funahashi's 2003-2011 panel to 2012-2022. Chiba (1987) and Suetsugu (2024, 2025) provide qualitative Japanese-language precedents; Wilson & Ramchandani (2018) and the KSOC 20% bonus (Korea) provide international context.
