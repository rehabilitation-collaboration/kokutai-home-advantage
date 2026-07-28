# GPT Review Round-1

- **Date received**: 2026-07-28
- **Reviewed manuscript**: `pdf/kokutai-v2-final.pdf` (28pp, 953 KB, v2 P1+P2+P3 反映済み)
- **Reviewer model** (瑞樹側で使用): 未確定 (o3 / GPT-5 系推定)
- **Verdict**: **Major revision** — 論文の芯は良い / SSRN なら十分 / 査読誌は修正後
- **本 round handling**: CRITICAL 1件 (#3 Bonferroni 誤記) は本セッション内で先行修正・commit。残り 8 件は v3 として新セッションで一括着手。

---

## Findings summary (severity 順)

| # | severity | 分類 | 一言 |
|---|---|---|---|
| 1 | MAJOR | claim/model | 主仮説の検定が "subjective vs objective" になっていない (3群を二値化してるだけ = obj + semi 混合ベース) |
| 2 | MAJOR | claim/tone | Abstract/Conclusion の語調が cluster-p 0.031 / wild-p 0.155 に対して強すぎる ("exhibits" / "empirically anchored" 等) |
| 3 | **CRITICAL** | numerical error | Multiple comparisons 段落で「naive p=0.031 が corrected α=0.01 threshold を below」= 論理的に破綻 (0.031 > 0.01) |
| 4 | MAJOR | consistency | 2013 Tokyo の扱い矛盾: "9 host years 中 6 victories" に含めているが「is not used as a host-effect data point in the '6 of 9'」とも書いている |
| 5 | MAJOR | model | Cross-section が prefecture-sport-year-trophy cells なのに trophy FE がない (sport FE + year FE のみ) |
| 6 | MAJOR | classification | judo/kendo/sumo/wrestling/fencing/equestrian を全部 "subjective judging" は強い。感度分析3種必要 |
| 7 | MINOR | 体裁 | Figure 1 期間表記の齟齬: caption "1948-2025" vs 図タイトル "1978-2025" |
| 8 | MINOR | 体裁 | "Balmer2003" shorthand → "Balmer et al. (2003)" に統一 |
| 9 | MINOR | data availability | LLM assistance を広く開示している以上、コード/データは "投稿時点で同時公開" が望ましい / ESRI 情報も要更新 |

---

## Finding #1 (MAJOR): 主仮説の検定が "subjective vs objective" になっていない

**GPT 原文要約**: Methods ではスポーツを objective / subjective / semi-subjective/team の3群に分けている一方で、主回帰は「subjective vs non-subjective」の二値になっている。つまり host main effect は厳密には objective ではなく、objective + semi-subjective/team の混合ベース。本文ではこれを「objective measured sports」と読ませているので、査読者に突かれる。

**修正案 (GPT 提示)**:
- 主解析を「objective と subjective だけに限定して semi を除外」する
- または host × sport_category を objective reference で推定し直す
- sport FE と category main effect は共線でも、host:category は設計を組めば推定できる

**要作業**:
- `src/analysis_cross_section_2024_2025.py` の modeling コード改修 (`_build_design` L113 + `run_cross_section_models` L209 = **M2 に既に `with_semi` spec が存在 (L213 コメント確認済)**・単に Table 5 primary に昇格するだけで済む可能性大 → まず現状の M1/M2 spec 差を実測確認してから改修方針決定)
- 新 spec = (a) semi 除外 (M1 の spec を semi 除外に絞る) or (b) 3-way category dummies with obj as reference (既存 M2 相当を primary 化)
- Table 5 差替え + Abstract/Results/Discussion 反映
- pytest 追加 (semi 除外時の n / 3-way spec の identifiability)

---

## Finding #2 (MAJOR): Abstract/Conclusion の語調が強すぎる

**GPT 原文要約**: 本文は wild-cluster bootstrap p=0.155 と誠実に書けているが、Abstract/Conclusion の語調がまだ少し強い。「確認的に有意」ではなく「方向は一致するが探索的・仮説生成的」くらいに落とすべき。特に conclusion の "exhibits" や "empirically anchored" はギリギリ = "suggestive evidence" に寄せる。

**修正案 (GPT 提示 abstract 文言)**:
> The estimates are directionally consistent with a larger host bonus in subjectively judged sports, but the few-treated-cluster correction does not reject the null.

**要作業**:
- Abstract の Results 節書き換え
- Discussion 冒頭段落の語調調整
- Conclusion 節 (もしあれば) の "exhibits" / "empirically anchored" 差替え
- ★ Finding #1 の spec 変更後に語調を再検討 (obj-only なら結果が変わる可能性あり)
- **★事前 grep 結果 (v3 Phase A 完遂後 2026-07-28)**:
  - `"exhibits"` = L109 (Results 段落内・"host prefectures exhibits non-zero top-1 status" = data descriptor 用法・**修正不要**) + L177 (Conclusion 冒頭・"Japan's National Sports Festival exhibits a host bonus" = **修正対象**)
  - `"empirically anchored"` = L177 (Conclusion 末尾・"the interaction itself, however, is now empirically anchored" = **修正対象**)
  - Abstract L21-23 は "exhibits" 直接使ってないが overall 語調要再検討 (Phase A で primary/inclusive 両方数値併記 + pure artistic scoring mechanism 追加済で語調降下範囲は Finding #6 novelty 拡張と両立させる要)

---

## Finding #3 (CRITICAL): Bonferroni の数値誤り

**該当箇所**: manuscript.md L79 の *Multiple comparisons* 段落末尾:
> A reader preferring an explicit Bonferroni-style guardrail may note that even a very generous 5-test correction (α_family = 0.05 → α_single = 0.01) would not change the qualitative reading: **the naive cluster-robust p (0.031) would remain below the corrected 0.01 threshold only marginally**, and the bootstrap p (0.155) would remain well above it under either correction.

**問題**: 0.031 > 0.01 なので、0.031 は "below the 0.01 threshold" ではない (むしろ above)。GPT の指摘通り、単純な論理誤り。

**GPT 修正案**:
> Under even a 5-test Bonferroni correction, the naive cluster-robust p-value would not remain significant, and the wild-cluster bootstrap p-value would also remain non-significant.

**本セッション対応**: Bonferroni 誤記は SSRN 投稿前に絶対潰す必要がある単純ミス = **本セッション内で先行修正・commit** (残り 8 findings は新セッション v3 で一括処理)。

---

## Finding #4 (MAJOR): 2013 Tokyo の扱い矛盾

**GPT 原文要約**: Table/本文で 9 host years 中 6 victories の中に 2013 Tokyo self-host を含めている一方で、「2013 Tokyo cell is retained... but is not used as a host-effect data point in the "6 of 9" descriptive rate」と書いている = 「じゃあ6/9に入ってるの？入ってないの？」

**修正案 (GPT 提示)**: 「6/9 には含めるが、Tokyo dominance のため解釈では感度分析対象にする」など、単一の姿勢に統一。

**要作業**:
- Table 1 脚注 + 該当 descriptive 段落 + Discussion の 3 箇所で表現を統一
- 「2013 Tokyo は含まれる / 含まれない」のどちらか一貫を選ぶ (含める方が n 保持できて安全)
- 感度分析として "2013 Tokyo 除外時の 5/8 = 62.5% も同方向" を追記
- **★事前 grep 結果 (v3 Phase A 完遂後 2026-07-28)**: "2013 Tokyo" / "self-host" / "6 of 9" ヒット行 = L21 (Abstract) + L89 (Descriptive・"host wins in 2012 Gifu, 2013 Tokyo (self-host)...") + L91 (Descriptive・"6 of 9 host-years" 説明・matter #4 の core) + L239 (Discussion) + L285 (Table 4b 脚注・"2013 Tokyo's own self-host year also removed") = 5 箇所で表現統一

---

## Finding #5 (MAJOR): trophy FE がない

**GPT 原文要約**: cross-section は prefecture-sport-year-trophy cells (n=6,991) として組んでいるのに、式には sport FE と year FE しかない。天皇杯と皇后杯で競技数・点数構造・参加構造が違うなら、最低でも trophy FE、できれば sport × trophy FE を入れた感度分析が欲しい。Methods 上も trophy を積んでいることは明記されている。

**要作業**:
- `src/analysis_cross_section_2024_2025.py` の regression formula に `+ C(trophy)` 追加
- 感度分析として `+ C(sport):C(trophy)` interaction 版も
- Table 5 に trophy-FE 追加行 or Table 5c 新設
- pytest 追加

---

## Finding #6 (MAJOR): 競技分類の感度分析不足

**GPT 原文要約**: judo/kendo/sumo/wrestling/fencing/equestrian をまとめて "subjective judging" と呼ぶのはやや強い。採点競技/審判判定競技/対人競技は機序が違う。以下の感度分析を出すべき:
- 「純粋採点・審判依存が強い競技のみ」
- 「combat/referee-adjudicated を除外」
- 「fencing/wrestling/sumo を semi に移す」

**要作業**:
- `src/sport_classifier.py` (L22 `Category = Literal[...]` + L26 以降 mapping 辞書) に代替分類 3 種追加 (pure_judged / no_combat / combat_to_semi)
- 実装案: 既存 `SPORT_CATEGORY` 辞書を残しつつ `SPORT_CATEGORY_PURE_JUDGED` / `SPORT_CATEGORY_NO_COMBAT` / `SPORT_CATEGORY_COMBAT_TO_SEMI` を並置 or classify 関数に `variant` param 追加
- 各分類での β_HS 推定を新 Table として提示 (Table 5d)
- Discussion で分類 sensitivity 段落追加
- ★ Finding #1 と組み合わせて実装すると効率的

---

## Finding #7 (MINOR): Figure 1 期間表記の齟齬

**GPT 指摘**: caption "1948-2025" vs 図タイトル "1978-2025" の乖離。

**要作業**:
- caption と図タイトルのどちらが真実か確定 (実際のデータ範囲を実測)
- `src/plots.py::plot_fig1_host_win_rate_timeseries` の title / manuscript caption の一致
- Fig 1 再生成
- **★事前 grep 結果 (v3 Phase A 完遂後 2026-07-28)**: manuscript.md 側 = L337 caption "1948-2025" のみ (Figure Legends 節・第 1 回 Kokutai = 1948 を反映)・"1978-2025" は manuscript.md 内ヒットなし = 図タイトル側 (matplotlib fig 側) の可能性 = **src/plots.py の title 定義を要確認**・実際のデータ範囲 (1948 vs 1978) は Phase 1 データ収集経緯 (archive) で確認可能

---

## Finding #8 (MINOR): "Balmer2003" shorthand 統一

**GPT 指摘**: 本文中 shorthand "Balmer2003" は読めるが、論文では "Balmer et al. (2003)" に統一するのが自然。

**要作業**:
- `grep -n "Balmer2003" manuscript.md` で全出現特定 → "Balmer et al. (2003)" 置換
- "Balmer2001" 同様なら同時修正
- **★事前 grep 結果 (v3 Phase A 完遂後 2026-07-28)**: `"Balmer2003"` ヒット = **22 箇所** (L21, 23, 33, 37, 39, 41, 49, 61, 65, 113, 115, 119, 127, 129, 133, 135, 159, 161, 287, 305, 320, 339) = Edit の replace_all で `"Balmer2003"` → `"Balmer et al. (2003)"` 一括置換可能 (unique 文字列で誤爆リスクなし)

---

## Finding #9 (MINOR): Data Availability 強化 + ESRI 情報更新

**GPT 指摘**:
- LLM assisted analysis を広く開示している以上、コード・データ・再現スクリプトは投稿時点で同時公開が望ましい (現状「投稿と同時、または30日以内」= 30日以内が緩い)
- 本文「令和5年度版が出たら延長可能」の記述は要更新。内閣府 ESRI ページには現在、平成23年度–令和5年度の表が掲載されているが、「31都道府県、2政令指定都市分」注記あり → "complete 47-prefecture R5 data are not yet available" のように正確化

**要作業**:
- Data Availability 節 (manuscript.md L212-214): "concurrent with, or within 30 days of" → "concurrent with" に締める
- ESRI 令和5 情報更新の対象 = **manuscript.md L51 (Methods §2 covariates)** = 現状「covering fiscal 2011-2022 for all 47 prefectures」の後に「令和5 partial data (31 prefectures + 2 designated cities) has been released but complete 47-prefecture R5 data are not yet available; the 2011-2022 window is therefore retained」を追記。Limitations 5th paragraph (L163) は Funahashi replication の pre-2011 gap の話で ESRI R5 更新とは別文脈のため追記対象外 (** 初セッション初見テストで判明・元指示 "Limitations 5th paragraph?" は誤り**)

---

## v3 実施計画 (次セッション着手・順序案)

**Phase A (統計モデル拡張・重量級)**:
1. Finding #1: 主回帰 obj vs subj 二値化 (semi 除外 or 3-way categorical) + `src/analysis_cross_section_2024_2025.py` 改修
2. Finding #5: trophy FE / sport × trophy FE 感度分析追加
3. Finding #6: 分類感度分析 3 種 (pure_judged / no_combat / combat_to_semi)
4. pytest 追加・281 → 300+ 目標
5. Table 5 系列の Table 5b/5c/5d 展開

**Phase B (表現修正・text-only)**:
6. Finding #2: Abstract/Discussion 語調降下 (★ Phase A 結果反映後)
7. Finding #4: 2013 Tokyo 扱い統一
8. Finding #7: Figure 1 期間表記整合
9. Finding #8: "Balmer2003" → "Balmer et al. (2003)" 置換
10. Finding #9: Data Availability 締め + ESRI 情報更新

**Phase C (build)**:
11. v3 final PDF build (`generate_pdf.py` out_path → `kokutai-v3-final.pdf`)
12. verify_refs / pdftotext QA
13. GPT round-2 依頼 → 瑞樹手動 ChatGPT 投入

---

## 本 round 実施 log

- CRITICAL Finding #3 (Bonferroni 誤記) を本セッション内で先行修正・commit
- 残り 8 findings は本ファイルに記録 → 一子相伝で新セッション v3 着手推奨
