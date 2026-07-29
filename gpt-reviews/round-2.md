# GPT Review Round-2

- **Date received**: 2026-07-29
- **Reviewed manuscript**: `pdf/kokutai-v3-final.pdf` (33pp, 979 KB, v3 Phase A + Phase B + Phase C 全反映済み)
- **Reviewer model** (瑞樹側で使用): 未確定 (o3 / GPT-5 系推定)
- **Verdict**: **Major revision** — 内容の芯は良い (弱点を隠していない誠実さ + 主観>準主観>客観の raw gap 単調は説得力あり + first empirical anchor の位置づけは誠実) / SSRN プレプリントなら出してよい / 今のまま査読誌に投げると「主張が少し強い」「AI作業メモが残っている」「引用体裁が壊れている」で刺される
- **本 round handling**: 全 9 件 = v4 サイクルで一括着手 (Phase A pattern = code+text 統合 1 finding 1 commit・Phase B pattern = text-only 1 finding 1 commit・Phase C build)

---

## Findings summary (severity 順)

| # | severity | 分類 | 一言 | v4 phase |
|---|---|---|---|---|
| 1 | **CRITICAL** | AI-log leak / bibliographic hygiene | 本文から「GPT round-1 Finding #」「Finding #12」を全消し (Abstract〜Table caption まで 15 出現・9 箇所 + Table 4b/5d の見出し 2 箇所) | B |
| 2 | MAJOR | claim/tone | 中心結論を「有意」ではなく「方向一致・探索的」に降下 (L23 "concentrated" / L113 "nearly triple" / L129 "nearly triple/tripling" / L181 "roughly triple") | B |
| 3 | MAJOR | methods/sensitivity | 欠測 106 セル (7,097 → 6,991) の 0 点補完 sensitivity 追加 (non-participation vs missing-data の解釈弾力性) | A |
| 4 | MAJOR | citation style | Vancouver 上付き番号と APA 著者年の混在解消 + References 節番号浮き行 (PDF レンダリング副作用) 修正 | B (text) + C (generate_pdf.py 調査) |
| 5 | MINOR | consistency | L173 Limitations「11 years, n = 423」→「2012-2022 calendar span, 9 non-cancelled editions, n = 423」に統一 | B |
| 6 | MAJOR | structural / paper focus | Event-study 節 (Methods §71 + Results §107 + Fig 3) を Supplement/Appendix に後景化して中心仮説をシャープに | B' (structural) |
| 7 | MINOR | tone (Finding #2 と重複) | Table 5d の p < 0.001 を Conclusion で強調しすぎない ("no-combat variant reaches conventional significance" → "classification variants preserved positive point estimates") | B (Finding #2 と統合) |
| 8 | MINOR | transparency | Data/code availability「will be released concurrent with SSRN posting」→ GitHub 仮リポジトリ先出し推奨 | B (text) + 実 repo 作成判断 (瑞樹要確認) |
| 9 | MINOR | AI disclosure hygiene | Acknowledgments「Claude Opus が regression fitting を assisted」→「code drafting/debugging/literature-search support/manuscript editing を assist・数値は再現コードで著者が検証」に言い換え | B |

---

## Finding #1 (CRITICAL): 本文から「GPT round-1 Finding #」全消し

**GPT 原文**:
> これはかなりまずい。Abstract から Methods、Table 注まで「per GPT round-1 Finding #1/#5/#6」が残っている。これは査読者に「AIの作業ログをそのまま論文化したのでは？」という印象を与える。Acknowledgments で AI 使用を開示するのは良いが、本文中の根拠として "GPT round" を出すのは不要。

**GPT 修正例**:
> per GPT round-1 Finding #1
>
> ではなく、
>
> To preserve a clean objective-versus-subjective contrast, semi-subjective/team sports were excluded from the primary specification.
>
> でよい。Table 5d の "per GPT round-1 Finding #6" も同様に消す。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- manuscript.md 内「GPT round-1」全出現 = **15 出現 / 9 箇所** (L21 Abstract Results / L65 Methods §3 x3 / L113 Descriptive/Results / L117 Results / L131 Results / L133 Table 5d 説明 / L300 Table 5 row 名 / L303 Table 5 footnote x2 / L305 Table 5d 見出し / L314 Table 5d footnote x2)
- ★別種の AI-log leak: L279 「Table 4b. Csurilla-style staged specification with Tokyo excluded (**Finding #12** sensitivity)」= Phase 8 の内部 Finding 番号が Table 見出しに残存
- ★別種の AI-log leak: L79 Multiple comparisons 段落末尾「(see **Finding #5-linked paragraphs** in Results and Limitations)」= Finding #3 (Bonferroni) 修正時の書き換えで残った参照痕跡

**要作業**:
- 全 15 出現 + Table 4b/5d の Finding #12/#6 見出し + L79 の Finding #5-linked 参照 = 計 18+ 箇所を trace-free な substantive 表現に置換
- 置換方針 = GPT 提案通り「なぜその spec 選択なのか」を substantive に言い換え (semi 除外 = pure obj-vs-subj contrast / trophy FE = emperor's/empress's cup 構造差の統制 / 3-variant sensitivity = classification robustness / Tokyo exclusion = non-host championship mass の除去)
- Table 見出し 2 本 (Table 4b / Table 5d) は Finding # 削除・substantive 表現に
- L79 「Finding #5-linked paragraphs」= Bonferroni 修正時の残余なので削除 or 「the wild-cluster bootstrap paragraphs in Results and Limitations」に置換
- Discussion §127 見出し「Balmer et al. (2003) decomposition holds at the Kokutai」も Finding #2 (tone) の観点で「holds」→「is directionally consistent with」等の降下対象 (Finding #6 と #2 の両方で touch する可能性)

**Deferred check**: 「Phase 8」「Phase 9」「Phase 10」等の PHASE 番号本文露出 (L206 Acknowledgments「Phase 8 investigation report」= AI 作業ログ露出 = Finding #9 との統合対応候補) は Finding #1 のスコープ外だが同種問題として Phase B で同時 grep-and-check

---

## Finding #2 (MAJOR): 中心結論を「有意」ではなく「方向一致・探索的」に降下

**GPT 原文**:
> データ上、スポーツ別の中心分析は 2024 佐賀・2025 滋賀の2開催地だけで、著者自身も「2 treated prefecture clusters out of 47」「interaction magnitude should be viewed as a first empirical anchor」と書いている。それなら、タイトル・Abstract・Discussion の「Balmer decomposition holds」「host advantage is concentrated」「roughly tripled」系の言い方は少し強い。"directionally consistent exploratory evidence" に寄せた方が通る。

**GPT 推奨結論文言**:
> These results are directionally consistent with a larger host bonus in subjectively judged sports, but because the interaction is identified from only two host prefectures and does not remain conventionally significant under wild-cluster bootstrap inference, we interpret the estimate as a first empirical anchor rather than definitive evidence of judging bias.

**GPT 追加指摘**: 「judging bias を示した」と読める表現は避ける。本文でも judge-level roster がなく、直接の審判バイアス分析はできないと書いているので、そこは統一する。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L23 Abstract Conclusions: "the host advantage is **concentrated** in — and **roughly tripled** under the obj-vs-subj-pure primary specification..." = Phase B-5 でここまで潰してなかった
- L113 Results: "roughly 31 points in a subjectively judged sport versus about 11 in an objectively measured one — **nearly triple**." = Phase B-5 は Abstract のみ触ってた
- L129 Discussion 冒頭: "the marginal bonus in subjectively judged sports is **nearly triple** the bonus in objectively measured sports..." + "**nearly tripling** the host bonus in subjective sports relative to objective ones."
- L181 Conclusion: "The marginal host bonus in subjectively judged sports is **roughly triple** the bonus in objectively measured sports..." + "the no-combat variant (pure artistic scoring only) **additionally reaches conventional significance** (β_HS = +31.81, cluster-robust p < 0.001; Table 5d)"
- Discussion 見出し L127: "**### The Balmer et al. (2003) decomposition holds at the Kokutai**" = "holds" 断定 → "is directionally consistent with" 降下候補

**要作業**:
- 全 5 箇所 (L23 / L113 / L129 x2 / L181) の "nearly triple / roughly triple / concentrated / decomposition holds" 系表現を "directionally consistent / suggestive / first empirical anchor" 系に降下
- L127 Discussion 見出し降下 (Balmer decomposition holds → is directionally consistent with)
- Conclusion (L181) の no_combat significant 明示は Finding #7 と統合対応 = "additionally reaches conventional significance" → "preserved positive point estimates" 系に降下 (novelty 拡張 = Phase A Finding #6 の pure artistic scoring mechanism 保持は Discussion 分類 sensitivity 段落 L133 に残せば充分)
- ★judging bias 直接言及の grep 追加チェック (現状 L129 に "Whether the observed interaction reflects judging bias..." あり = "cannot be uniquely identified" と honest に書いてる = 触らなくてOK か再確認要)

---

## Finding #3 (MAJOR): 欠測 106 セルの 0 点補完 sensitivity 追加

**GPT 原文**:
> Methods では、理論上 7,097 セルのうち 6,991 セルを保持し、106 セルは不参加・公表欠落などで落ちたと書いている。ここは査読者が必ず聞く。「不参加＝0点」と扱うべきなのか、「出場した競技に条件づけた score」として分析しているのかが重要。開催県は全競技に出やすいので、非開催県の不参加セルを落とすと、開催地効果の構成要素を一部取り除いている可能性がある。欠測は全体の 1.5% なので致命傷ではなさそうだが、0点補完 sensitivity を1本入れるとかなり強くなる。

**GPT 推奨文言 (Methods 追加)**:
> Because absent prefecture-sport cells may represent non-participation rather than missing data, we additionally estimated a zero-imputed specification treating absent cells as zero score; results were directionally unchanged.

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L61 Methods §3: 既に「theoretical n = 7,097 / regression frame n = 6,991 (**a 106-cell, 1.5% shortfall**) after handling of the clay-target-shooting/boxing swap between the two editions and the drop of unbalanced cells for prefectures that did not participate in specific sports and are consequently absent from the JSPO overall-standings publication for that sport-year」= non-participation 認識既にあり = zero-imputed sensitivity 追加は自然
- 現状 sport_classifier / analysis_cross_section_2024_2025 は zero-imputed variant 未実装 = code 追加要 (Phase A 級)

**要作業** (Phase A・code+text 統合):
- `src/analysis_cross_section_2024_2025.py` に zero-imputed variant 実装 (欠測 106 セル = `panel.reindex(full_cartesian).fillna(0)` 相当・primary spec と同じ regressor で fit)
- `run_cross_section_models` に variant として追加 or `run_cross_section_zero_imputed` 新関数
- Table 5 内に新行「Sensitivity: zero-imputed (106 absent cells = 0)」追加 (primary の後・inclusive の前)
- Methods §3 (L61 後) に GPT 推奨文言 1 文追加
- Discussion か Results で「directionally unchanged」の実測結果反映
- pytest 追加 (`test_zero_imputed_sample_size == 7097` / `test_zero_imputed_beta_HS direction > 0` / `test_zero_imputed_within_5pct_of_primary`)

---

## Finding #4 (MAJOR): References / 引用体裁修正

**GPT 原文**:
> References の番号が本文とは別の場所に浮いている。たとえば References の後に文献が並んだ後で "1. 2." が独立行として出ている。さらに次ページでも "3. 4. 5..." が文献の後に浮いている。これは体裁としてかなり悪い。査読以前に「最終稿じゃない」感が出る。
>
> また Introduction で (Suetsugu, 2024, 2025){4,5} みたいな混在表記がある。Vancouver なら全て上付き番号、APA なら全て著者年に統一。どちらでもいいが混ぜない。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L35 Introduction: "one scholarly critique (Suetsugu, 2024, 2025)**^{4,5}^** that host outcomes reflect..." = 上付き番号 + APA 著者年 混在
- 同種混在: L143 "Lan and Yu (2012)**^11^**" / L153 "Csurilla & Fertő (2023)**^9^**" / L115 "Cameron & Miller (2015)**^13^**" / L163 "Cameron & Miller's (2015)**^12^**" (★L115 [13] vs L163 [12] 番号不一致・要精査) / L175 "Cameron, Gelbach & Miller (2008)**^14^**"
- References 節 raw markdown (L185-200) は綺麗 = 「1. 」から「14. 」まで並んでる = 番号浮き行は PDF レンダリング副作用の可能性大 (generate_pdf.py の weasyprint 書式で References 節に対して何かの list style を強制してる)
- 全文の上付き番号出現 = 事前 grep で確認済 (grep 結果参照)

**要作業**:
- 統一方針決定 = Vancouver (全て上付き番号・APA 著者年削除) or APA (全て著者年・上付き番号削除) の 2 択 → **Vancouver 採用推奨** 理由 = (a) References 節既に Vancouver 番号順 (b) 医学系ジャーナル (Balmer et al. J Sports Sci, Csurilla Sci Rep, Nomura Front Sports) は Vancouver が多い (c) SSRN プレプリントも Vancouver で他号 (第7弾以前) と整合
- Vancouver 採用時の作業 = 全 APA 著者年表記 (Suetsugu 2024, 2025 / Balmer et al. 2003 / Funahashi et al. 2016 / Lan & Yu 2012 / Csurilla & Fertő 2023 / Cameron & Miller 2015 / Cameron, Gelbach & Miller 2008 / Nomura 2022 / Zitzewitz 2006 / Kim 2025 / Chiba 1987 / Wilson & Ramchandani 2021 / Balmer et al. 2001) の全出現を「著者名 (year)」→「著者名^[N]」に統一
- L115/L163 の [12] vs [13] 番号不一致精査 (References 現状 12 = Zitzewitz / 13 = Cameron & Miller / 14 = Cameron, Gelbach & Miller = L115 は正解 [13]・L163 は [12] だが実際は Cameron & Miller = [13] 参照要 = 誤植)
- 番号浮き行 = **v4 Phase C で PDF build 時に実測要**・raw markdown は綺麗なので generate_pdf.py 側の CSS 修正で対応 (weasyprint の `ol` list-style-position 等)

---

## Finding #5 (MINOR): 「11 years, n=423」→「9 non-cancelled editions, n=423」統一

**GPT 原文**:
> 2012–2022 はカレンダー上は11年だが、2020・2021が中止なので分析は9開催、47×9 = 423。Table 1ではその説明がある。一方で Limitations では "2012-2022 (11 years, n = 423)" と書いている。ここは「2012–2022 calendar span, 9 non-cancelled editions, n = 423」に統一した方がいい。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L173 Limitations 6th paragraph: "the primary analysis panel window is 2012-2022 (**11 years, n = 423**), constrained by the ESRI 令和4年度版 (2011-2022) coverage..." = **修正必要 1 箇所のみ**
- L89 Descriptive: "the emperor's-cup panel contains 423 prefecture-year observations (47 prefectures × 9 non-special, non-cancelled years)" = 既に「9 non-special, non-cancelled years」表記で OK
- Table 1 caption L243: "9 host years in the panel window (2012-2022)..." = OK
- Table 2 caption L245: "2012-2022 tennou, n = 423" = 年数不記載で OK

**要作業**:
- L173 の 1 箇所のみ書き換え = "2012-2022 (11 years, n = 423)" → "2012-2022 (calendar span; 9 non-cancelled editions; n = 423)"

---

## Finding #6 (MAJOR): Event-study 節を Supplement/Appendix に後景化

**GPT 原文**:
> イベントスタディは、著者自身が「識別変動が薄い」「独立した識別分析ではなく design check」と書いている。なら本文で大きく扱わず、Supplement/Appendix に回していい。今の本文は分析が多すぎて、中心仮説がぼやける。
>
> 主論文の芯は、
> - Funahashi 再現で国体開催地効果は存在する
> - 2024–2025 の競技別データでは、主観判定競技で開催地効果が大きい方向
> - ただし2開催地なので探索的
> これで十分強い。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- Event-study 節本文位置:
  - Methods §Event-study design (two-layer) = L71-73 (Methods §4)
  - Results §Event-study, two-layer design = L107-109 (Results §5)
  - Fig 3 = L345 Figure Legends
- 参照残り箇所:
  - L79 Multiple comparisons 段落: "the two-layer event-study (Figure 3) are treated as replication, sensitivity, and design-check specifications respectively" = event-study の位置づけ既に "design check"
  - L109 Results: "the event-study point estimates are near-zero by construction and should be read as a design check rather than as an independent identifying analysis"
- ★構造化 issue: Event-study は本文 Methods + Results + Figure Legends に散らばってる = supplement 化するには 3 箇所全て移動 + Fig 3 も supplement 化 + 本文からの Fig 3 参照 (Table 5b は event-study 由来なので Table 5b の位置も確認要)

**要作業** (Phase B'・structural):
- Methods §Event-study (L71-73) を Supplement §S1 or Appendix A に移動
- Results §Event-study (L107-109) を Supplement §S1 or Appendix A に移動
- Fig 3 (L345) を Supplement Figure S1 に格下げ (Figure Legends 節の Fig 3 記述も移動)
- L79 Multiple comparisons 段落から event-study 言及削除 or 大幅短縮
- Discussion §Two host-loss clusters, not one (L137) の event-study 参照調整 (2016-2017 / 2022-2024 の 2 クラスター構造自体は Discussion に残す・event-study coefficient 参照のみ supplement 化)
- generate_pdf.py に Supplement 節ページ追加 (Appendix A: Event-Study Design and Results 見出し)
- ★実装コスト大 = Phase B の text-only 修正の中で最重量級

---

## Finding #7 (MINOR): Table 5d の p<0.001 を Conclusion で強調しすぎない

**GPT 原文**:
> Combat-excluded variant は β_HS = +31.81、cluster-robust p < 0.001 とかなり強く見える。ただ、これは感度分析であり、同じく2開催地問題を抱える。Conclusion で「no-combat variant reaches conventional significance」と書くより、「classification variants preserved positive point estimates」と言う方が安全。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L181 Conclusion 末尾: "a three-variant classification sensitivity in which the **no-combat variant (pure artistic scoring only) additionally reaches conventional significance** (β_HS = +31.81, cluster-robust p < 0.001; Table 5d) — a first empirical anchor that longer panels could sharpen into a decisive test."
- L133 Discussion 分類 sensitivity 段落: "yields β_HS = **+31.81** (SE = 8.20, cluster-robust **p < 0.001**) — the largest and most statistically robust point estimate across all four variants, consistent with a mechanism in which host bias is strongest under pure artistic scoring rather than under combat-referee judgment." = Discussion 内は novelty 拡張として残す (Phase A Finding #6 の pure artistic scoring mechanism)
- L314 Table 5d footnote: "yields the largest and most statistically robust interaction (+31.81, cluster-robust p < 0.001), consistent with a mechanism in which host bias is strongest under pure artistic scoring rather than under combat-referee judgment." = ここも Table caption なので残す

**要作業** (Finding #2 と統合):
- L181 Conclusion 末尾のみ書き換え = "the no-combat variant additionally reaches conventional significance..." → "classification variants preserved positive point estimates (range +18.99 to +31.81; Table 5d); the combat-excluded variant's cluster-robust p < 0.001 shares the same two-treated-cluster limitation as the primary specification and should be read in the same "first empirical anchor" register"
- L133 Discussion + L314 Table 5d footnote は **無変更** (Discussion 内の pure artistic scoring mechanism novelty は Phase A で得た成果 = 保持)
- ★temperature 差保持戦略 (Phase A Finding #6 = Discussion 内 novelty 保持 / Phase B Finding #2 + Phase B v4 Finding #7 = Conclusion 内 tone 降下) = Phase B-5 (`f2e8ad1`) と同じ pattern

---

## Finding #8 (MINOR): Data/code availability を GitHub 先出し推奨

**GPT 原文**:
> AI支援を明示しているのは良いが、コードが "will be released concurrent with SSRN posting" だと、読者はまだ検証できない。SSRNに出すなら、GitHub 仮リポジトリでもいいので先に置いた方がよい。AI支援をここまで透明に書くなら、コード公開も同時でないとバランスが悪い。

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L224 Data Availability: "Analysis code... will be released to a public GitHub repository and permanently archived on Zenodo (with a DOI) concurrent with SSRN posting."
- ★実 GitHub repo 未作成 = repo 作成 + 具体 URL 記載が理想

**要作業**:
- **判断分岐 (瑞樹要確認)**: (a) 実 GitHub repo を SSRN 投稿前に作成 (uv Rehabilitation30/kokutai-home-advantage 等) → URL 記載 (b) 現状「concurrent with SSRN posting」維持で SSRN 投稿と同日 push
- (a) 採用時: `git init` → GitHub repo 作成 → push → Data Availability に URL 追記 (「A public GitHub repository (https://github.com/Rehabilitation30/kokutai-home-advantage) hosts the full analysis code..."」)
- (b) 採用時: 現状維持 (Finding #8 は "will be released" の書き方は既に十分・GPT 指摘は「先出しの方が bandwidth 増える」レベル)
- ★推奨 = (a) = 論文シリーズ第8弾として第9弾 (companion paper) 執筆時にも参照される + friday13th (第7弾) が SSRN 投稿時に GitHub repo なしで通ったため必須ではないが望ましい

---

## Finding #9 (MINOR): Acknowledgments の AI 開示言い換え

**GPT 原文**:
> 「Claude Opus が literature search, panel construction, regression fitting... を assisted」と書いている。透明性は良い。ただし "regression fitting" と書くと、AIが数値を出したように読まれる可能性がある。

**GPT 推奨文言**:
> Claude Opus was used to assist with code drafting, debugging, literature-search support, and manuscript editing. All data extraction, statistical outputs, and numerical results were independently checked by the author using reproducible scripts.

**★事前 grep 結果 (2026-07-29 セッション実測)**:
- L206 Acknowledgments: "Data assembly, statistical programming, and manuscript drafting were assisted by **Claude Opus 4.7 (Anthropic), used for literature search, panel construction, regression fitting, PDF text extraction, and drafting**. The author is solely responsible for the accuracy of the numerical results, the choice of specifications, the interpretation of coefficients, and the conclusions. All references were verified against CrossRef, J-STAGE, PubMed, and PMC records where applicable; the **Phase 8 investigation report** (`PHASE8-INVESTIGATION.md`) documents the bibliographic-verification process, including two corrections to entries that appeared in earlier drafts (Funahashi et al. 2016 co-author list and journal; Csurilla & Fertő 2023 author count)."
- ★同種 AI-log leak: 「Phase 8 investigation report」= AI 作業ログ本文露出 = Finding #1 と同種問題 = 本 Finding #9 で統合対応推奨 (Acknowledgments 内なので Finding #9 が主体)

**要作業**:
- L206 Acknowledgments 全書き換え = GPT 推奨文言に置換
- 具体差替: "literature search, panel construction, regression fitting, PDF text extraction, and drafting" → "code drafting, debugging, literature-search support, and manuscript editing"
- 追加文: "All data extraction, statistical outputs, and numerical results were independently checked by the author using reproducible scripts."
- 「Phase 8 investigation report」参照削除 (or 「bibliographic verification records archived with the analysis code」等の substantive 表現に置換)

---

## v4 実施計画 (次セッション着手・順序案)

**Phase A (統計モデル拡張・code+text 統合・1 finding 1 commit・pytest 追加)**:
1. **Finding #3** (0点補完 sensitivity): src/analysis_cross_section_2024_2025.py に zero-imputed variant 実装 + Table 5 内新行 + Methods §3 一文 + Discussion に「directionally unchanged」実測反映 + pytest 追加 (target: 297 → 300 +)

**Phase B (表現修正・text-only・1 finding 1 commit)**:
2. **Finding #1** (CRITICAL・AI-log leak): 全 15+ 出現 + Table 4b/5d 見出し + L79 Finding #5-linked = 18+ 箇所を substantive 表現に置換 (**Phase A 前に先行実施も可**・code touch なしで安全)
3. **Finding #5** (11 years → 9 editions): L173 の 1 箇所のみ
4. **Finding #2 + Finding #7 統合** (tone 降下): L23/L113/L129/L181 + L127 見出し + L181 no_combat significant 表現を substantive 温度降下 (**★temperature 差保持 = L133 Discussion + L314 Table 5d footnote は無変更**)
5. **Finding #4** (Vancouver 統一): 全 APA 著者年表記 (10+ 出現) を Vancouver 上付き番号に統一 + L115/L163 の [12] vs [13] 番号不一致修正
6. **Finding #6** (Event-study 後景化): Methods §71 + Results §107 + Fig 3 + L79 参照を Supplement §S1 に移動 (★Phase B 最重量・structural change・generate_pdf.py にも Supplement セクション追加要)
7. **Finding #9** (AI 開示言い換え): L206 Acknowledgments 全書き換え + 「Phase 8 investigation report」参照削除

**Phase B'' (transparency 判断分岐・瑞樹要確認)**:
8. **Finding #8** (GitHub 先出し): 実 repo 作成 or 現状維持を瑞樹判断 → 判断次第で L224 Data Availability 更新

**Phase C (build)**:
9. v4 final PDF build (`generate_pdf.py` out_path → `kokutai-v4-final.pdf`)
10. **★References 番号浮き行の PDF レンダリング実測** → generate_pdf.py の CSS で References 節 list-style-position 修正 (Finding #4 の残タスク)
11. verify_refs 再実行 (既知アーティファクト 4 件 [4][5][11][13] は想定通り再現予定)
12. pdftotext QA 100% (v4 全 finding 反映 grep validation)
13. Desktop 配置
14. GPT round-3 依頼 (瑞樹手動 ChatGPT 投入)

---

## v4 サイクルの温度差保持戦略 (Phase B-5 pattern 完全踏襲)

Phase B v4 では、以下の温度差を保持する:

- **Discussion 内 (novelty 保持)**: L133 pure artistic scoring mechanism 段落 + L314 Table 5d footnote = **無変更**
- **Conclusion 内 (tone 降下)**: L181 Conclusion 末尾の "no-combat variant reaches conventional significance" は "classification variants preserved positive point estimates" に降下 (Finding #2 + #7 統合)
- **Abstract/Discussion 冒頭 (tone 降下)**: L23/L113/L129 の "nearly triple / roughly triple / concentrated / decomposition holds" は "directionally consistent / suggestive / first empirical anchor" 系に降下

これは v3 Phase B-5 (`f2e8ad1`) で確立した「primary は suggestive・no_combat は significant」の温度差保持を Conclusion まで拡張する動き。

---

## v4 修正時の必読 3 本

1. 本 round-2.md の Findings summary + 各 Finding 節 (事前 grep 結果反映済)
2. `gpt-reviews/round-1.md` (173 行・v3 で潰した 9 finding の pattern 参照 = 1 finding 1 commit + 事前 grep + 副次修正明示 + temperature 差保持)
3. Phase A/B/C 全 10 commits (`b16795f` → `f1b8bb3`) の commit message = `cd ~/claude/analysis/kokutai-home-advantage && git log --format="%h %s%n%n%b" -n 11 b16795f^..f1b8bb3` で一覧取得

---

## 本 round 実施 log

- 2026-07-29 セッション: GPT round-2 応答受領 → 事前 grep で全 9 finding の該当箇所行番号ピン留め → 本 round-2.md 起票 (Phase B/C の traceability 保持)
- v4 サイクル着手は次セッション以降 (Phase A → Phase B → Phase B'' → Phase C の順)

## 良い点評価 (GPT からの評価保持)

- 弱点を隠していない (2 treated clusters 問題 / wild bootstrap 非有意 / judge-level data 不在 / Funahashi 追試での omitted controls / ordered logit の separation 全て honest)
- 主分析の cluster-robust p と wild-cluster p を両方出し「first empirical anchor」と位置づけているのは誠実
- 主観・準主観・客観の raw gap が +37.91 > +26.18 > +17.60 と単調になっているのは、図としてかなり説得力あり = 本論文の一番わかりやすい売り

**GPT 結論**: 「研究アイデアと分析の方向は良い。だが今の原稿は『中身』より『見せ方』で損している。これを直せば、かなりちゃんとした『日本国体における開催地効果の競技タイプ分解』論文になる。今のままでもプレプリントとしては成立するけど、査読誌ではツッコミどころが目立つ。」
