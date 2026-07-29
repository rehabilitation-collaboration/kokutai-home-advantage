# Asura-Monju Round-1 on v3-final (Integrated v4 修正計画)

- **Date**: 2026-07-29
- **System**: Asura (Sonnet × 3 parallel) + Monju (Opus × 1 verification)
- **Reviewed manuscript**: `pdf/kokutai-v3-final.pdf` (33pp / 979KB・v3 Phase A + Phase B + Phase C 全反映済み)
- **Parallel external review**: GPT round-2 (o3/GPT-5 系推定・同日取得・Major revision 判定・9 findings)
- **Purpose**: v3-final に対する内製合議制 + external LLM の 2 軸クロス比較で v4 サイクル修正計画を最大化

---

## 併走 review path 統合結果

### 検出 findings 総数

| Path | Raw | Unique | Confirmed |
|---|---|---|---|
| GPT round-2 (external) | 9 | 9 | 9 |
| Asura × 3 (Sonnet parallel) | 29 (R1=7 + R2=14 + R3=8) | 25 (4 overlap dedup) | 22 (ACCEPT) + 1 (REFINE) + 3 (carry-over from GPT round-2) = 25 |
| Monju independent (Opus verify) | +12 (M1-M12) | 12 | 12 |
| **統合後 total unique action items** | — | — | **33** |

### GPT round-2 と Asura/Monju の overlap マッピング

| GPT round-2 Finding | Asura/Monju Match | 判定 |
|---|---|---|
| #1 (AI-log leak) | Asura A (R2#14 + R3#3 + R3 追加 L73 "H-03 recommendation") | **3/3 相当・GPT より広範**・v4 で integrate |
| #2 (tone 降下 5 箇所) | Asura J (R2#1・見出し L127 vs 段落末 L129 の単段落内矛盾 angle 追加) | **compound**・v4 で integrate |
| #3 (Zero-imputed sensitivity) | Asura C (R2#10 + R3#6) | **3/3 相当**・v4 で implement |
| #4 (References 引用体裁) | Asura B (R1#1 + R2#4・Cameron & Miller [12]/[13]) + Asura H (R1#2・1896 forward citation) | **compound**・v4 で refactor |
| #5 (11 years → 9 editions) | (asura 独立発見なし) | GPT のみ・v4 で fix |
| #6 (Event-study 後景化) | (asura 独立発見なし・R2#7 の "Ninth limitation missing" と部分 overlap) | GPT のみ・v4 で structural refactor |
| #7 (Table 5d p<0.001 強調降下) | Asura E (R2#3) + Monju M11 (Methods L79 との paper 内矛盾を追加検出) | **compound**・v4 で integrate |
| #8 (GitHub 先出し) | Monju M12 (SSRN posted 済で既に asymmetric-disclosure gap 発生を追加検出) | **compound**・v4 で URL 配置 |
| #9 (AI 開示言い換え) | Monju M5 (model 版数正確性 + 数値 verification 手順明示 の粒度不足) | **compound**・v4 で refactor |

### asura/monju 独立検出 (GPT round-2 未検出)

**P1 (2 件・★novelty core を揺るがす)**:
- **Finding F + M1**: Balmer 2003 "diving" false claim (PubMed abstract で 5 groups = {athletics, weightlifting, boxing, gymnastics, team games}・diving 含まず)
- **Finding G**: Suetsugu quote 内的矛盾 (L35/L147 quote vs L169 bibliographic-only 自認)

**P2 (11 件・Finding×8 + Monju×3)**:
- Finding H (L31 "1896 forward" ref 1 誤引・Winter Olympics)
- Finding I (Results L115 bootstrap p unlabeled)
- Finding J (Discussion 見出し "holds" vs 段落末単段落内矛盾)
- Finding K + Monju M7 (Table 4b M1-M3 separation vs finite SE 矛盾・compound で 1 count)
- Finding L (Table 5d wild-cluster bootstrap 未計算 = selective standard)
- Finding M (Table 7 primary vs inclusive spec 混在)
- Finding N (Discussion "establishes" / "approximately two" 一貫性欠如)
- Finding O (Table 5 bootstrap 行 95% CI なし)
- Monju M3 (Rademacher weights 単独の弱点)
- Monju M6 (Judge-affiliation bias direction 論議欠如)
- Monju M8 (Cameron & Miller (2015) attribution が MacKinnon & Webb (2017) より weak)

**P3 (14 件・Finding×11 + Monju×3)**:
- **Finding D** (Table 1/6/7 が narrative で番号引用ゼロ・2/2 match だが独立検出扱い)
- Finding P (Nara hantei citation なし)
- Finding Q (data_loader.py docstring 算術矛盾・code)
- Finding R + Monju M4 (wild_cluster_bootstrap code の bare except + p convention 逸脱・compound で 1 count)
- Finding S (Abstract "FE" + Ethics "MEXT/MHLW" 未展開)
- Finding T ("Table 4" Funahashi vs 現論文 混用)
- Finding U (Limitations に event-study 項目なし)
- Finding V ("PO" 略語 first-use 定義なし)
- Finding W (Sample size availability-driven justification)
- Finding X (post-hoc analyses "sensitivity" → "exploratory" labeling)
- Finding Y (命令調 academic register 逸脱)
- Monju M2 (sport_classifier.py L26 コメント 16→17 修正)
- Monju M9 (Unit tests 297 の specific breakdown 未報告)
- Monju M10 (Reference format 略誌名 vs full 誌名 統一)

---

## v4 修正計画 (Phase 分類・1 finding 1 commit・Phase A/B pattern 完全踏襲)

### Phase A (統計モデル拡張・code+text 統合・pytest 追加・3 commits)

**Finding #A1** (P2・Zero-imputed sensitivity 実装・GPT round-2 #3 + Asura C):
- `src/analysis_cross_section_2024_2025.py` に `run_cross_section_zero_imputed` 実装 (欠測 106 セル = `panel.reindex(full_cartesian).fillna(0)` 相当・primary spec regressor で fit)
- Table 5 内新行「Sensitivity: zero-imputed (106 absent cells = 0)」追加 (primary の後・inclusive の前)
- Methods §3 (L61 後) に GPT 推奨文言追加: "Because absent prefecture-sport cells may represent non-participation rather than missing data, we additionally estimated a zero-imputed specification treating absent cells as zero score; results were directionally unchanged."
- Discussion か Results で「directionally unchanged」の実測結果反映
- pytest +3 (test_zero_imputed_sample_size == 7097 / test_zero_imputed_beta_HS direction > 0 / test_zero_imputed_within_5pct_of_primary)

**Finding #A2** (P2・Table 5d wild-cluster bootstrap 追加・Asura L + Monju M3 partial):
- `src/analysis_cross_section_2024_2025.py` の 4 variant 全てで wild_cluster_bootstrap 計算
- Table 5d に bootstrap p 列追加 (4 variant × cluster-robust p + bootstrap p)
- Discussion 分類 sensitivity 段落 L133 で "with wild-cluster bootstrap corrections applied consistently across all variants" 追記
- pytest +4 (each variant の bootstrap n_used check)
- ★特に no_combat variant (β_HS=+31.81) の bootstrap p 実測が Finding #A3 (Conclusion tone 修正) の trigger

**Finding #A3** (P2・Table 5 wild-cluster bootstrap 95% CI 追加・Asura O):
- `wild_cluster_bootstrap()` の return に percentile-method 95% CI 追加 (bootstrap_ts 分布から `np.percentile(observed_t + bootstrap_ts, [2.5, 97.5])` × SE で逆算)
- Table 5 primary/inclusive の bootstrap 行に CI 記載
- Discussion で "95% bootstrap CI = [X, Y]" 明示
- pytest +2 (CI monotonicity + CI range plausibility)

### Phase B (表現修正・text-only・1 finding 1 commit・16 commits)

**優先順**: P1 → P2 → P3 (severity 順)。CRITICAL (P1) 4 件は最優先で code touch なし = 安全。

**Finding #B1** (P1・Balmer 2003 "diving" false claim 削除・Finding F + Monju M1):
- manuscript.md L33 Introduction から "diving" 削除
- "boxing, gymnastics, diving" → "boxing, gymnastics" 変更
- LITERATURE.md L39-46 の abstract-only source を明示 (既存)
- 全 Balmer 2003 引用箇所を grep で確認: L17/L33/L37/L61/L65/L113/L127/L129/L133/L153/L181/L189 = 12+ 箇所で "5 event groups" の specific 記述は L33 のみに集中
- commit message で PubMed abstract verify 結果 + LITERATURE.md self-admission との整合回復を明記

**Finding #B2** (P1・Suetsugu quote 内的矛盾解消・Finding G):
- manuscript.md L35 "one scholarly critique... reflect 'cheating' and a 'host-victory-first mindset'" → "one scholarly critique... reflect host-outcome legitimacy concerns (Suetsugu 2024/2025)" 等 hedged framing
- manuscript.md L147 "using pointed language ('cheating' / 'host-victory-first mindset') in a single-sport context" → "in a single-sport context (specific normative framing as characterized in secondary summaries of the Suetsugu papers)"
- L169 Limitations の bibliographic-only self-admission と整合性回復
- LITERATURE.md L86-87 も同時修正 (secondary source note 追加)

**Finding #B3** (P1・AI-log leak 全消し・Finding A・GPT round-2 #1/#9・R3 追加 L73):
- manuscript.md 内 18+ 箇所 grep-and-replace:
  - L21 Abstract "excluded per GPT round-1 Finding #1" → "excluded to preserve a clean objective-versus-subjective contrast"
  - L65 Methods §3 x3 → substantive rationale (semi 除外 = pure obj-vs-subj / trophy FE = emperor/empress cup 構造差統制 / sport × trophy = per-sport tennou-vs-kougou 差の absorb)
  - L79 "(see Finding #5-linked paragraphs in Results and Limitations)" → "(see wild-cluster bootstrap paragraphs in Results and Limitations)"
  - L113/L117/L131/L133 → substantive rationale
  - L279 Table 4b "(Finding #12 sensitivity)" → "(Tokyo-exclusion sensitivity)"
  - L300 Table 5 row → substantive
  - L303 Table 5 footnote x2 → substantive
  - L305 Table 5d "(per GPT round-1 Finding #6)" → "(classification-variant sensitivity)"
  - L314 Table 5d footnote x2 → substantive
  - L206 Acknowledgments "the Phase 8 investigation report (`PHASE8-INVESTIGATION.md`)" → "bibliographic verification records archived with the analysis code"
  - **★R3 追加検出 L73 "the Phase 8 investigation's H-03 recommendation"** → "as recommended by exploratory panel diagnostics"

**Finding #B4** (P1・Cameron & Miller ^12→^13 修正・Finding B・GPT round-2 #4):
- manuscript.md L163 の "^12^" → "^13^" 単発修正
- References 節との整合性再確認

**Finding #B5** (P2・Conclusion no_combat significance tone 降下・Finding E + Monju M11・GPT round-2 #7):
- manuscript.md L181 Conclusion 末尾 "the no-combat variant (pure artistic scoring only) additionally reaches conventional significance (β_HS = +31.81, cluster-robust p < 0.001; Table 5d) — a first empirical anchor that longer panels could sharpen into a decisive test" → "classification variants preserved positive point estimates (range +18.99 to +31.81; Table 5d); the combat-excluded variant's cluster-robust p < 0.001 shares the same two-treated-cluster limitation as the primary specification and should be read in the same "first empirical anchor" register"
- ★temperature 差保持: L133 Discussion + L314 Table 5d footnote は無変更 (Discussion 内 novelty 保持)
- Methods L79 との self-consistency 回復確認

**Finding #B6** (P2・Introduction L31 "1896 forward" citation refactor・Finding H):
- manuscript.md L31 "an effect documented at every summer Olympics from 1896 forward.^1,2^" → "an effect documented at Summer Olympic Games (Balmer et al. 2003)^3^ and Winter Olympic Games (Balmer et al. 2001)^1^"
- References 節 L187-189 の整合再確認

**Finding #B7** (P2・Results L115 bootstrap p disambiguate・Finding I):
- manuscript.md L115 "The bootstrap p for the interaction was p = 0.155 (observed t = 2.16)" → "The bootstrap p for the interaction under the primary specification was p = 0.174 (observed t = 2.22), and under the inclusive specification p = 0.155 (observed t = 2.16); neither attains conventional significance under this correction"
- Abstract L21 の両 p 並列記載と整合

**Finding #B8** (P2・Discussion 見出し "holds" → tentative・Finding J):
- manuscript.md L127 見出し "### The Balmer et al. (2003) decomposition holds at the Kokutai" → "### The Balmer et al. (2003) decomposition is directionally supported at the Kokutai"
- 段落 L129 との整合再確認

**Finding #B9** (P2・Table 4b M1-M3 separation flag・Finding K + Monju M7):
- manuscript.md Table 4b (L279-291) の M1-M3 SE cell に "*separation-regime; interpret directionally*" footnote 追加
- caption L289 の "separation regime distorts... interpret directionally" を M1-M3 rows にも明示的に適用
- ★code touch なし (R2 の code trace + M7 の追加 verify で挙動確認済み)

**Finding #B10** (P2・Table 7 spec 混在 footnote・Finding M):
- manuscript.md Table 7 L330 "Japan Kokutai (present study) | ... | +33 pts subj / +17 pts obj per sport | Present study" → footnote 追加 "(inclusive specification; see Table 5)"
- Alternatively: "+31 pts subj / +11 pts obj (primary spec; +33/+17 under inclusive sensitivity)" 両記載

**Finding #B11** (P2・Discussion "establishes" / "approximately two" 修正・Finding N):
- manuscript.md L147 "our analysis provides the sport-level statistical evidence that... establishes..." → "our analysis provides the sport-level statistical evidence consistent with..."
- L149 "by a factor of approximately two" → "by a factor of 2.00× (inclusive sensitivity) to 2.81× (primary specification)"

**Finding #B12** (P2・GPT round-2 #5・11 years → 9 editions):
- manuscript.md L173 Limitations "2012-2022 (11 years, n = 423)" → "2012-2022 (calendar span; 9 non-cancelled editions; n = 423)"

**Finding #B13** (P2・Event-study 後景化・GPT round-2 #6・★命名固定=**Supplement §S1**):
- Methods §Event-study design (L71-73) を **Supplement §S1** に移動 (命名 = "Supplement" 固定・"Appendix" 表記却下 = 医学系論文で Supplement の方が一般的)
- Results §Event-study (L107-109) を Supplement §S1 に移動
- Fig 3 (L345 Figure Legends) を Supplement Figure S1 に格下げ
- L79 Multiple comparisons 段落から event-study 言及削除 or 大幅短縮
- Discussion §Two host-loss clusters (L137) の event-study 参照調整
- generate_pdf.py に Supplement 節ページ追加 (見出し = "Supplementary Materials §S1: Event-Study Design and Results")
- ★Phase B 最重量・structural change

**Finding #B14** (P2・Judge-affiliation bias direction discussion・Monju M6):
- manuscript.md Discussion (Discussion 節末尾 or Robustness 節) に "the identified interaction is a reduced-form estimate that lumps judge-bias, crowd-effect, and practice-environment channels; the absence of a JSPO judge-of-record roster prevents attribution to any single channel" 追加
- Limitations Second (L165) との整合性強化

**Finding #B15** (P2・MacKinnon & Webb (2017) 追加・Monju M8):
- References 節に Ref 15 追加: "MacKinnon JG, Webb MD. Wild bootstrap inference for wildly different cluster sizes. *J Appl Econometrics*. 2017;32(2):233-254."
- manuscript.md L163/L177 の "Cameron & Miller's (2015) few-treated-clusters diagnosis" → "the few-treated-clusters diagnosis (Cameron & Miller 2015; MacKinnon & Webb 2017)^13,15^" attribution 修正

**Finding #B16** (P2・GPT round-2 #9 + Monju M5・Acknowledgments AI 開示言い換え):
- manuscript.md L206 Acknowledgments 全書き換え = GPT 推奨文言に Monju M5 recommendation 統合:
  - Before: "Data assembly, statistical programming, and manuscript drafting were assisted by Claude Opus 4.7 (Anthropic), used for literature search, panel construction, regression fitting, PDF text extraction, and drafting."
  - After: "Claude Opus 4.7 (Anthropic) was used to assist with code drafting, debugging, literature-search support, and manuscript editing. All data extraction, statistical outputs, and numerical results were independently checked by the author using reproducible scripts."
- "Phase 8 investigation report" 参照削除 (Finding #B3 と整合)

### Phase B'' (P3・text-only + judgment 分岐・11 commits)

**Finding #B'1** (Table 1/6/7 in-text cite・Finding D)
**Finding #B'2** (Nara hantei citation・Finding P)
**Finding #B'3** (data_loader.py docstring 算術訂正・Finding Q)
**Finding #B'4** (wild_cluster_bootstrap p convention + n_used 報告・Finding R + Monju M4)
**Finding #B'5** (Abstract FE + MEXT/MHLW 略語展開・Finding S)
**Finding #B'6** ("Table 4" Funahashi vs 現論文 区別・Finding T)
**Finding #B'7** (Limitations event-study Ninth 追加・Finding U・★Finding #B13 と両立要注意 = event-study が Supplement 化される場合は Ninth limitation で "moved to Supplement" 明記)
**Finding #B'8** (PO 略語 first-use・Finding V)
**Finding #B'9** (Sample size availability-driven 節・Finding W)
**Finding #B'10** (Reviewer-driven "exploratory" re-label・Finding X)
**Finding #B'11** (命令調 academic register 修正・Finding Y)
**Finding #B'12** (sport_classifier.py L26 コメント 16→17・Monju M2)
**Finding #B'13** (Rademacher weights sensitivity limitation・Monju M3)
**Finding #B'14** (Unit tests 297 breakdown・Monju M9)
**Finding #B'15** (Reference format 統一・Monju M10)

### Phase B''' (transparency 判断分岐・瑞樹要確認)

**Finding #B'''1** (GPT round-2 #8 + Monju M12・GitHub 先出し + Zenodo DOI):
- **判断分岐**: (a) 実 GitHub repo 作成 (github.com/Rehabilitation30/kokutai-home-advantage 等) + Zenodo DOI 取得 → L224 に URL 記載 / (b) 現状「will be released concurrent with SSRN posting」維持 (但し SSRN 既 posted で asymmetric-disclosure gap 既発生)
- ★推奨 = (a)・理由: (i) Monju M12 で明示された asymmetric-disclosure gap 解消 (ii) SSRN posted 済で「will be」は factually 誤り (iii) 第9弾 companion paper で本論文引用時に URL 参照可能
- 実装: `git init` → GitHub repo 作成 → push → L224 Data Availability に URL 追記

### Phase C (build)

**Finding #C1** (v4 final PDF build):
- `generate_pdf.py` L127 編集: out_path → `kokutai-v4-final.pdf`
- `python -W ignore generate_pdf.py` 実行 → pdf/kokutai-v4-final.pdf 生成 (推定 33pp → 34-36pp = zero-imputed row + Ninth limitation + Supplement §S1 で +1-3pp)

**Finding #C2** (verify_refs 再実行):
- `python ~/claude/internal/tools/verify_refs.py manuscript.md --output-dir output`
- 想定: 既知アーティファクト 4 件 ([4][5][11][13]) は放置・新 Ref 15 (MacKinnon & Webb) が MATCH 追加

**Finding #C3** (References 番号浮き行の PDF レンダリング実測・GPT round-2 #4 の残タスク):
- GPT round-2 で「References の後に番号浮き行 (1. 2. 3. 4. 5...) が出現」の指摘・raw markdown は綺麗なので generate_pdf.py 側の weasyprint CSS 修正
- 実測: pdftotext で References 節 前後の layout 確認 → CSS 修正 (list-style-position or ol reset)

**Finding #C4** (pdftotext QA 100%):
- v4 全 finding 反映の grep validation (Phase B 33 finding 全部の該当行を pdftotext 抽出結果で verify)
- 特に L33 "diving" 削除確認・L35/L147 Suetsugu hedged framing・L79 "wild-cluster bootstrap paragraphs" replacement・L127 見出し変更・L163 Cameron ^13^・L173 "9 non-cancelled editions"・L181 Conclusion tone 降下・L206 Acknowledgments 全書き換え・L224 GitHub URL (Phase B''' 判断次第)・Table 5d bootstrap 行追加・Table 4b M1-M3 footnote・Table 7 spec 混在 footnote・Supplement §S1 event-study 移動

**Finding #C5** (Desktop 配置):
- `~/Desktop/kokutai-v4-final.pdf` 配置済

**Finding #C6** (GPT round-3 依頼):
- 瑞樹に「v4-final PDF を ChatGPT に添付して round-3 判定取得」依頼指示
- round-3 応答受領時: `gpt-reviews/round-3.md` 起票 (round-2.md pattern 完全踏襲)

---

## Commit strategy (Phase A/B/B'' pattern 完全踏襲)

- **1 finding 1 commit** (Key Decision #56/#71 準拠)
- **code+text 統合** (Phase A・Key Decision #56)
- **text-only** (Phase B・Key Decision #71)
- **副次修正明示** (Key Decision #63/#73 準拠・GPT スコープ外の同時修正は commit message で "副次修正" 明記)
- **commit message file は scratchpad 経由必須** (Key Decision #77 準拠・/tmp/ 禁止)

### 推定 commit 数

- **Phase A**: 3 commits (A1 = zero-imputed / A2 = Table 5d bootstrap / A3 = Table 5 CI)
- **Phase B**: 16 commits (B1 = "diving" 削除 / B2 = Suetsugu quote / B3 = AI-log leak / B4 = ^13^ 修正 / B5 = Conclusion tone / B6 = 1896 forward / B7 = L115 disambiguate / B8 = 見出し tentative / B9 = Table 4b footnote / B10 = Table 7 footnote / B11 = "approximately two" 修正 / B12 = 11 years fix / B13 = Event-study Supplement / B14 = Judge affiliation / B15 = MacKinnon & Webb ref / B16 = Acknowledgments)
- **Phase B''**: 15 commits
- **Phase B'''**: 1 commit (瑞樹判断次第で GitHub URL 追記)
- **Phase C**: 6 commits (C1 = build / C2 = verify_refs / C3 = CSS / C4 = QA 実施記録 / C5 = Desktop 配置 record / C6 = GPT round-3 依頼記録)

**総 estimated v4 commits**: 41 commits (v3 の 10 commits に比べ 4 倍)

---

## pytest 追加項目 (Phase A 由来)

**Phase A1 (zero-imputed sensitivity・+3 tests)**:
- `test_zero_imputed_sample_size == 7097`
- `test_zero_imputed_beta_HS_direction > 0`
- `test_zero_imputed_within_5pct_of_primary` (β_HS が primary の 95%〜105% 範囲内)

**Phase A2 (Table 5d bootstrap・+4 tests)**:
- `test_pure_judged_bootstrap_n_used > 900`
- `test_no_combat_bootstrap_n_used > 900`
- `test_combat_to_semi_bootstrap_n_used > 900`
- `test_variant_bootstrap_ts_finite`

**Phase A3 (Bootstrap 95% CI・+2 tests)**:
- `test_bootstrap_ci_monotonic` (lower < upper)
- `test_bootstrap_ci_contains_observed_t`

**Phase B'12 (sport_classifier.py コメント・+1 test)**:
- `test_sport_classifier_objective_count == 17`

**Phase B'4 (wild_cluster_bootstrap p convention・+2 tests)**:
- `test_bootstrap_p_no_degenerate_zero` (raw proportion vs +1 convention の diff 確認)
- `test_bootstrap_p_within_range`

**総 pytest 追加**: 297 → 309 (+12 tests)

---

## Environment State (v4 サイクル前)

- **HEAD**: `217c518` (docs(gpt-reviews): round-2 起票)
- **Phase A/B/C 全 10 commits**: `b16795f` (Finding #1) → `5fb2d57` (Finding #5) → `0ddd770` (Finding #6) → `70f780d` (docs) → `9da5030` (Finding #8) → `30e76f3` (Finding #9) → `10fe43d` (Finding #7) → `6537b53` (Finding #4) → `f2e8ad1` (Finding #2) → `798dcc3` (予告文) → `f1b8bb3` (build)
- **round-2.md 起票**: `217c518`
- **pytest**: 297 all passing (Phase A/B/C は追加なし・Phase B/C は text-only or build)
- **未コミット差分**: plots/*.pdf + __pycache__/*.pyc (matplotlib timestamp・discard 安全)

---

## v4 サイクル着手時の必読 5 本

1. **本ファイル (asura-monju-round-1-on-v3.md)**: 33 unique action items 統合修正計画
2. **REVIEW-REPORT.md** (Phase B 起票同時): P1/P2/P3 分類 summary
3. **gpt-reviews/round-2.md**: GPT round-2 の 9 finding 詳細
4. **gpt-reviews/round-1.md**: v3 で潰した 9 finding pattern (1 finding 1 commit + 事前 grep + 副次修正明示 + temperature 差保持)
5. **Phase A/B/C 全 10 commits の commit message**: `cd ~/claude/analysis/kokutai-home-advantage && git log --format="%h %s%n%n%b" -n 11 b16795f^..f1b8bb3`

---

## 判定 summary

**内容評価** (GPT round-2 の良い点評価 + Asura/Monju verify で強化):
- 弱点を隠していない誠実さ・主観 > 準主観 > 客観の raw gap 単調は説得力あり・first empirical anchor 位置づけは誠実 (GPT round-2 同意)
- 4-variant classification 実装完全性 (Asura R1 で確認)・4 spec (primary/inclusive/three-way/sport×trophy) 内的整合 (Asura R1)

**課題** (v4 で必修):
- **P1 = 4件**: novelty core (Balmer "diving" + Suetsugu quote) + AI-log leak (18+ 箇所) + Cameron 番号
- **P2 = 12件**: methodological rigor (zero-imputed sensitivity + Table 5d bootstrap + separation flag + Judge bias direction + MacKinnon attribution) + self-consistency (Conclusion tone + Discussion 見出し + Table 7 spec 混在)
- **P3 = 17件**: style/formatting/transparency (sub-critical だが SSRN → 査読誌 昇格時に累積影響)

**v4 完了後の予測**:
- 査読誌投稿基準 clear の可能性大 (P1 4 件 = 致命的 = 全部潰せば "刺さり所" 消失)
- GPT round-3 判定は minor revision or accept へ大幅前進の見込み
- 第9弾 companion paper (Sport-level exploratory screen) 執筆時の本論文引用時に traceability 明確化

---

## ★ID/Finding letter 相互参照表 (REVIEW-REPORT.md ↔ 本ファイル)

REVIEW-REPORT.md の「#」列 (severity 順 serial・1-33) と本ファイルの「Finding letter」(aggregated 順・A-Y) + Monju independent (M1-M12) の対応関係。**初見コールドスタート時の混同回避用**。ID 二重体系 (checklist ID `A-02`/`C-08` 等) と Finding letter は別物なので注意。

| REVIEW-REPORT # | 本 file の Finding | Severity | Issue key |
|---|---|---|---|
| 1 | F + Monju M1 | P1 | Balmer 2003 "diving" false claim (L33) |
| 2 | G | P1 | Suetsugu quote 内的矛盾 (L35/L147 vs L169) |
| 3 | A | P1 | AI-log leak 18+ 箇所 (R3 追加 L73 含) |
| 4 | B | P1 | Cameron & Miller ^12→^13 (L163) |
| 5 | C | P2 | Zero-imputed sensitivity 実装 |
| 6 | E + Monju M11 | P2 | Conclusion no_combat tone + Methods L79 self-consistency |
| 7 | H | P2 | Introduction "1896 forward" ^1,2^ citation refactor |
| 8 | I | P2 | Results L115 bootstrap p disambiguate |
| 9 | J | P2 | Discussion 見出し L127 "holds" vs 段落末矛盾 |
| 10 | K + Monju M7 | P2 | Table 4b M1-M3 separation-regime footnote |
| 11 | L | P2 | Table 5d 4-variant wild-cluster bootstrap 追加 |
| 12 | M | P2 | Table 7 primary/inclusive spec 混在 footnote |
| 13 | N | P2 | Discussion "establishes"/"approximately two" 修正 |
| 14 | O | P2 | Table 5 bootstrap 行 95% CI 追加 |
| 15 | Monju M3 | P2 | Rademacher weights sensitivity limitation |
| 16 | Monju M6 | P2 | Judge-affiliation bias direction discussion |
| 17 | Monju M8 | P2 | MacKinnon & Webb 2017 Ref 15 追加 |
| 18 | D | P3 | Table 1/6/7 narrative in-text cite (2/2 match) |
| 19 | P | P3 | Nara hantei citation (L35) |
| 20 | Q | P3 | data_loader.py docstring 算術矛盾 (L206-208) |
| 21 | R + Monju M4 | P3 | wild_cluster_bootstrap code (bare except + p convention + n_used 報告) |
| 22 | S | P3 | Abstract "FE" + Ethics "MEXT/MHLW" 略語展開 |
| 23 | T | P3 | "Table 4" Funahashi vs 現論文 区別 |
| 24 | U | P3 | Limitations Ninth (event-study thin variation) 追加 |
| 25 | V | P3 | "PO" 略語 first-use 定義 |
| 26 | W | P3 | Sample size availability-driven 節 |
| 27 | X | P3 | Reviewer-driven "exploratory" re-label |
| 28 | Y | P3 | 命令調 academic register 修正 (L139) |
| 29 | Monju M2 | P3 | sport_classifier.py L26 コメント 16→17 |
| 30 | Monju M5 | P3 | Acknowledgments 数値 verification 手順明記 |
| 31 | Monju M9 | P3 | Unit tests 297 breakdown |
| 32 | Monju M10 | P3 | Reference format (Vancouver 略誌名 統一) |
| 33 | Monju M12 | P3 | Data Availability GitHub URL 配置 (Phase B''' 判断分岐) |

**内訳合計 (再集計・整合済み)**: P1 = 4 件 (#1-4) / P2 = 13 件 (#5-17) / P3 = 16 件 (#18-33) = **合計 33 unique action items**。

★過去 handoff/summary の「P2×12 + P3×17」は集計時期の compound 定義差異による。**本相互参照表を真実源とする** (initial 記述は summary レベルで大まかな内訳・実行時は本 table 33 items を順に潰していく)。
