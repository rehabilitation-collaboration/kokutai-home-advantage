# Review Report: Kokutai Host-Advantage Paper (v3-final)

- **Date**: 2026-07-29
- **System**: Asura (Sonnet × 3 parallel) + Monju (Opus × 1 verification)
- **Reviewed manuscript**: `pdf/kokutai-v3-final.pdf` (33pp / 979KB) + `manuscript.md` (349 行・v3 Phase A + Phase B + Phase C 全反映済み)
- **Overall verdict**: **Major revision required** (併走で取得した GPT round-2 も同一判定・別 review path で相互補強)

## Critical Findings (P1) — 4 items

| # | ID | Issue | Source | Action Required |
|---|-----|-------|--------|----------------|
| 1 | A-02 (novelty core) | **Balmer et al. (2003) 5 event groups の specific 記述に "diving" が含まれるが、PubMed で verify した Balmer 2003 abstract の 5 groups = {athletics, weightlifting, boxing, gymnastics, team games}・diving は含まれず** = full-text 未読 (LITERATURE.md L39 自認) で追加された false factual claim | Asura(1/3・R3#1) + Monju-independent verify (M1・PubMed sourced) | manuscript.md L33 Introduction から "diving" 削除・"boxing, gymnastics" のみに restrict。Balmer 2003 novelty core の主張根拠を abstract-level scope に厳格 restrict |
| 2 | A-02 (source integrity) | **Suetsugu (2024, 2025) の "cheating" / "host-victory-first mindset" specific quote を L35 Introduction + L147 Discussion で 2 箇所使用しているが、L169 Limitations は「full texts... could not be reliably extracted; the citations are at bibliographic-plus-CiNii-link level only」と自認** = quote の出所が bibliographic-only source からは論理的に導けない | Asura(1/3・R3#2) | L35 + L147 の specific quote 削除 or "as characterized in secondary sources" 等 hedged framing に。L169 の bibliographic-only self-admission と一貫性回復 |
| 3 | C-08 (AI-log leak) | 本文に AI 作業ログが 18+ 箇所残存: "per GPT round-1 Finding #N" (Abstract/Methods/Results/Table 5/5d caption) + "Finding #12" (Table 4b caption) + "Phase 8 investigation" (Acknowledgments) + "H-03 recommendation" (Methods L73・R3 追加検出) | Asura(2/3・R2#14 + R3#3) + GPT round-2 #1/#9 = **3/3 相当** | 全 18+ 箇所を substantive rationale (semi 除外 = pure obj-vs-subj contrast 等) に置換。Table 見出しから Finding #N 削除 |
| 4 | E-04 (citation number) | Cameron & Miller (2015) が L163 で "^12^" (誤り・ref 12 = Zitzewitz 2006) vs L115/L177 で "^13^" (正しい) | Asura(2/3・R1#1 + R2#4) + GPT round-2 #4 = **3/3 相当** | L163 の "^12^" → "^13^" 修正 |

## Important Findings (P2) — 12 items

| # | ID | Issue | Source | Action Required |
|---|-----|-------|--------|----------------|
| 5 | A-13 | Zero-imputed sensitivity variant 未実装: 106 セル (7,097 → 6,991) の non-participation vs missing-data 区別が Table 5 に無い | Asura(2/3・R2#10 + R3#6) + GPT round-2 #3 = **3/3 相当** | `src/analysis_cross_section_2024_2025.py` に zero-imputed variant 実装 + Table 5 新行追加 + Methods §3 一文追加 + pytest +3 |
| 6 | A-24 + M11 | **Conclusion L181「additionally reaches conventional significance」(no_combat variant) は Methods §Multiple comparisons L79「does not survive either... correction」と paper 内直接矛盾**・かつ Table 5d 4-variant で wild-cluster bootstrap 未計算 (Table 5 primary/inclusive はしてる = selective standard) | Asura(1/3・R2#3 + R3#4) + Monju-independent(M11) + GPT round-2 #7 | Conclusion L181 tone 降下 ("preserved positive point estimates") + Table 5d 4 variant で wild-cluster bootstrap 計算追加 + Methods self-consistency 回復 |
| 7 | A-02 | Introduction L31「an effect documented at every summer Olympics from 1896 forward.^1,2^」= ref 1 (Balmer 2001 Winter Olympics 1908-1998) + ref 2 (Wilson 2021 Olympic/Paralympic 1988-2018) は両方 summer 1896- を支持せず。正しくは ref 3 (Balmer 2003 Summer Olympics 1896-1996) | Asura(1/3・R1#2) + Monju verify | L31 引用番号 refactor: "^1,2^" → "^3^" 中心に変更 |
| 8 | B-11 | Results L115 「bootstrap p = 0.155 (observed t = 2.16)」が primary/inclusive **unlabeled**・arithmetic (16.68/7.72=2.16) で inclusive spec 由来と判明・直前が primary spec 話 = 誤読誘発リスク | Asura(1/3・R1#3) + Monju verify | L115 に "(inclusive spec)" ラベル明示 + primary spec bootstrap p (0.174, t=2.22) も並列記載 |
| 9 | A-24 | Discussion 見出し L127 "The Balmer et al. (2003) decomposition **holds** at the Kokutai" vs 同段落末 L129 "we frame this as a *directionally* consistent first quantitative anchor... rather than a decisive statistical confirmation" = 単段落内の内的矛盾 | Asura(1/3・R2#1) + GPT round-2 #2 部分 overlap | 見出しを "The Balmer et al. (2003) decomposition is directionally supported at the Kokutai" 等 tentative framing に修正 |
| 10 | B-03 (REFINE) + M7 | Table 4b M1-M3 complete separation vs finite SE 矛盾: caption「8/8 hosts / 0/406 non-hosts」= 完全分離なのに M1-M3 は finite SE で非退化・M4/M5 のみ "degenerate" flag。code (analysis_confounders.py L92-95) は maxiter=500 hit で optimizer 早期終了して finite estimates を返す挙動 | Asura(1/3・R2#8・code hedge) + Monju-independent(M7・code trace) | Table 4b M1-M3 SE cell に "*separation-regime; interpret directionally*" footnote 追加。complete separation regime の M1-M3 SE も "degenerate" flag |
| 11 | B-30 / E-04 | Table 7 "+33 pts subj / +17 pts obj per sport" = **inclusive spec 由来** (16.60+16.68=33.28≈33 / 16.60≈17) だが本文他所は primary spec (+11.18 / total ≈+31.45)・spec 混在の footnote 不在 | Asura(1/3・R3#5) + Monju verify | Table 7 セルに "(inclusive spec; see Table 5)" footnote 追加 + primary spec 数値との integration 説明 |
| 12 | A-24 | Discussion "Overlap and boundary with Suetsugu" L147/L149 で "establishes" + "approximately two" (どの ratio 参照？ primary +2.81× / inclusive +2.00× / descriptive +2.15×) = "first empirical anchor" register 逸脱 + magnitude 不特定 | Asura(1/3・R2#2) | L147 "establishes" → "provides quantitative evidence consistent with"・L149 "approximately two" → "2.00× (inclusive) to 2.81× (primary)" 明示化 |
| 13 | B-11 | Table 5 wild-cluster bootstrap 行 (L296/L298) に 95% CI 記載なし ("(bootstrap CI not tabulated)") = few-treated-clusters 補正下の interval 情報ゼロ | Asura(1/3・R1#4) | Bootstrap 行に percentile-method 95% CI 追加 (bootstrap_ts 分布から計算可) |
| 14 | M3 (independent) | Wild-cluster bootstrap は Rademacher weights 単独使用・treated cluster G_1=2 で bootstrap distribution lumpy リスク | Monju-independent(M3・econometric theory) | Limitations に "Rademacher weight sensitivity check" 追加 (Mammen weights sensitivity 実装は次回) |
| 15 | M6 (independent) | Judge-affiliation missing confounder の bias-direction discussion 不足: Limitations Second で言及ありだが systematic direction (host prefecture が gymnastics 判定員派遣枠を持つ場合の bias 方向) 論なし | Monju-independent(M6・unmeasured confounding) | Discussion に "the identified interaction is a reduced-form estimate that lumps judge-bias, crowd-effect, and practice-environment channels" 明記 |
| 16 | M8 (independent) | "few-treated-clusters" attribution が Cameron & Miller (2015) 単独に集中しているが、より正確な attribution は MacKinnon & Webb (2017) or Djogbenou, MacKinnon & Nielsen (2019) | Monju-independent(M8・citation-context match) | Ref 15 (MacKinnon & Webb 2017) 追加、L163/L177 の attribution を two-reference 化 |

## Minor Findings (P3) — 17 items

| # | ID | Issue | Source | Action Required |
|---|-----|-------|--------|----------------|
| 17 | E-04 | Table 1/6/7 が narrative (Results/Discussion) 内で番号引用ゼロ (他の Table 2/3/4/4b/5/5d は全て cite あり) | Asura(2/2・R1#5 + R2#6) | narrative 内で `(Table 1)` `(Table 6)` `(Table 7)` in-text cite 追加 |
| 18 | A-02 | L35 Nara hantei 記述 (2018 boxing scandal / 山根明 / amateur boxing federation) が specific factual claim だが citation なし | Asura(1/3・R3#7) | Yamane Akira 事件 news source or wiki citation 追加 |
| 19 | A-13 (code) | src/data_loader.py L206-208 docstring 算術矛盾: 78-kougou 33 → 79-kougou 34 で「ボクシング/軟式野球追加」= 2 sports 追加なのに net +1 = 1 sport 削除の言及なし | Asura(1/3・R3#8・code-verified) | docstring 算術訂正 (削除競技言及 or 追加 sport 数訂正) |
| 20 | B-01 (code) + M4 | `wild_cluster_bootstrap()` L349-364: (a) bare `except Exception: continue` で silently drop・code は n_bootstrap_used 保持だが manuscript "B = 999" のみ報告 (b) p 計算が raw proportion で `(1+count)/(1+B)` convention 逸脱 (Davison & Hinkley) | Asura(1/3・R1#7・code-verified) + Monju-independent(M4) | Bootstrap p convention を `(1+count)/(1+B)` に変更 + Results で `B = 999 requested, N_used = ...` 明記 |
| 21 | E-03 | Abstract L19 で "FE" 使用・first-expand は Methods §1 L57 (順序逆) + Ethics L83 で MEXT/MHLW 未展開 | Asura(1/3・R1#6) | Abstract L19 "FE" → "fixed effects (FE)" first-expand・L83 MEXT/MHLW 括弧展開 |
| 22 | E-04 | "Table 4" が Funahashi's Table 4 (external・L37/L59) と現論文 Table 4 (Csurilla staged・L57/L267) の 2 通り混用 | Asura(1/3・R2#5) | L37/L59 "Funahashi's Table 4" → "Funahashi (2016)'s Table 4" で区別 |
| 23 | A-15 | Limitations「Eight limitations」に event-study の thin identifying variation 項目なし (Methods L73 / Results L109 で論じてる) | Asura(1/3・R2#7) | Limitations に "Ninth" 追加 = event-study thin identifying variation limitation 明記 |
| 24 | E-03 | "PO" (proportional-odds) 略語 L57 で first-use 括弧展開なし | Asura(1/3・R2#9) | L57 "proportional-odds (PO) assumption" first-expand |
| 25 | A-12 | Sample size (n=423/n=4,744/n=6,991) は availability-driven で power/precision justification なし (secondary-data 分析の inherent constraint でもある = mitigating factor) | Asura(1/3・R2#11) | Limitations に sample-size availability-driven 節追加 (First 項目に統合可) |
| 26 | A-16 | Post-hoc reviewer-driven analyses を "sensitivity" と label・機能的には "exploratory" | Asura(1/3・R2#12) | Reviewer-driven analyses を "exploratory sensitivity analyses" と re-label |
| 27 | E-01 | Discussion L139 "do not treat 2016 as a single break" 命令調が academic register 逸脱 | Asura(1/3・R2#13) | "we recommend that future Japanese work... avoid treating 2016 as a single structural break" 等 passive/formal に変更 |
| 28 | M2 (independent) | src/sport_classifier.py L26 コメント "# === objective (客観記録・16競技) ===" だが実際 17 sports = code-doc drift | Monju-independent(M2・code review) | L26 コメント "17競技" に修正 |
| 29 | M5 (independent) | Acknowledgments AI 開示の粒度不足: Claude Opus 4.7 の specific model 版数正確性 + どの部分が LLM 生成か区別 + 数値 verification 手順明示が欠落 | Monju-independent(M5・AI disclosure) | Acknowledgments に "author manually verified all numerical results by re-executing code" 追記 |
| 30 | M9 (independent) | Unit tests 297 の specific breakdown 未報告 (どの module に何 test) | Monju-independent(M9・model validation) | Methods §Statistical software に "297 unit tests, covering: sport_classifier X tests, analysis_cross_section Y tests, ..." 内訳追記 |
| 31 | M10 (independent) | Reference format inconsistency: Ref 1/2 略誌名 vs Ref 4/5 full 誌名 (ICMJE Vancouver は NLM abbreviation 統一推奨) | Monju-independent(M10・target journal formatting) | Ref 4/5 誌名を "Bull Inst Liberal Arts Sci Komazawa Univ" 統一 (NLM 未 index の場合 full 誌名維持 acceptable) |
| 32 | M12 (independent) | L224 Data Availability「will be released concurrent with SSRN posting」だが SSRN posted 済 (7/24) で GitHub URL manuscript 未記載 = paper 自身の warning 通り asymmetric-disclosure gap 既発生 | Monju-independent(M12・data availability) | Data Availability に実際の GitHub URL + Zenodo DOI 配置 (瑞樹判断で repo 作成) |
| 33 | (metadata) | Finding A の L73 重複 (P1 で対応済のため二重 count 回避) | — | — |

## Rejected by Monju

| # | Asura Finding | Rejection Reason |
|---|--------------|-----------------|
| — | (none) | Asura×3 の全 25 findings が Monju verification で ACCEPT or REFINE 判定 = REJECT 0 件 |

## Review Statistics

- **Asura**: 49 checklist items × 3 agents = 147 checks・29 raw findings (R1=7 + R2=14 + R3=8)・4 cross-agent overlap で dedup → **25 unique aggregated findings**
- **Monju verification**: ACCEPT 21 / REFINE 1 / REJECT 0 / Carry-over ACCEPT 3
- **Monju independent**: 12 new findings (M1-M12・P2×6 + P3×6)
- **Total v4 action items**: 33 unique (P1×4 + P2×12 + P3×17)
- **Cross-review overlap with GPT round-2**: 4 findings (A/B/C/E) → integrate for v4
- **Pre-processing**: `verify_refs.py` run (v3 Phase C commit `f1b8bb3`・既知アーティファクト 4 件 [4][5][11][13] は放置判断済み)

## ★特筆発見 (novelty core を揺るがす)

1. **Balmer 2003 "diving" false claim (P1 = Finding F + M1)**: Introduction L33 の specific event list "boxing, gymnastics, diving" のうち **diving は Balmer 2003 の 5 event groups {athletics, weightlifting, boxing, gymnastics, team games} に含まれず**。PubMed abstract で Monju が独立 verify。LITERATURE.md 側の「full text 未読・conceptual framework only」self-admission と併せて = full-text 未読で追加された factual embellishment。novelty core の主張根拠を abstract-level scope に厳格 restrict 要。

2. **Suetsugu quote 内的矛盾 (P1 = Finding G)**: Introduction L35 + Discussion L147 の "cheating" / "host-victory-first mindset" specific quote は L169 Limitations の bibliographic-only self-admission と論理的に両立せず = quote の出所が abstract or CiNii metadata レベルで導けない。

3. **Conclusion 自己矛盾 (P2 = Finding E + M11)**: Conclusion L181「no_combat variant additionally reaches conventional significance」は Methods §Multiple comparisons L79「the confirmatory interaction is significant under the uncorrected cluster-robust test only, and does not survive either the few-treated-clusters correction」と paper 内直接矛盾。no_combat variant も同じ 2-treated-prefecture 構造で same 論理適用。

## v4 サイクル修正計画

詳細な 33-item integration guide は `asura-monju-round-1-on-v3.md` (別 file) を参照。GPT round-2 (9 finding) + asura-monju (25 + 12 = 37 findings) から重複除外して 33 unique action items に整理済み。Phase A (code+text 統合) / Phase B (text-only) / Phase C (build) 分類も同 file に記載。

## Environment State

- Reviewed at commit `217c518` (docs(gpt-reviews): round-2 起票) の 1 commit 前 = `f1b8bb3` v3 final PDF 状態
- pytest 297 all passing (v3 Phase A で 285 → 297)
- 未コミット差分 (matplotlib timestamp のみ): plots/*.pdf + __pycache__/*.pyc (discard 安全・Phase B pattern 継続)
