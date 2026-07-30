> ⛔️ **参照は経緯記録用のみ・v7 サイクル計画は廃止 (2026-07-30 4th session)**: 本 round-4 を受けての v7 サイクル計画 (下部の「v7 対応表」+「v7 実施計画」節) は瑞樹指示で全面ピボット。**最新の真実源は `~/claude/analysis/kokutai-home-advantage/PLAN.md` 冒頭 v2 節** (80 大会真偽検定 + 主観/客観分離)。GPT 原文・判定内容は経緯参照用として本文保持。Finding #7 (References 番号浮き) は GPT ハルシネーション確定 (瑞樹目視結果)。

# GPT Review Round-4

- **Date received**: 2026-07-30 (kokutai セッション末・瑞樹貼付)
- **Reviewed manuscript**: `pdf/kokutai-v6-final.pdf` (35pp, 997KB, v5-T10 + v6-T11+promote 完遂反映・HEAD `f63144e`)
- **Reviewer model** (瑞樹側で使用): 未確定 (o3 / GPT-5 系推定)
- **総合判定**: プレプリント OK / **査読誌 = Major revision (Reject 寄りでなく "promising but under-identified")**
- **本 round handling**: v7 サイクルで対応 (P0 データ調達方針決定 → T1-T3 text-only fixes → T4-T7 統計手法系 → T8 Phase C build + 全 35 ページ pdftoppm 目視 → T9 GPT round-5 → M5 SSRN 投稿)

---

## GPT 原文 (瑞樹貼付・逐語保存)

この論文は、アイデアは良い。でも査読誌にそのまま出すなら、統計手法面で Major revision 相当。

理由は単純で、中心主張である「主観判定競技で開催地効果が大きい」は、実質的には 2024佐賀・2025滋賀の2開催地だけから推定されている。本文でも、主分析は 2024–2025 の2年クロスセクションで、treated prefecture clusters は Saga と Shiga の2つだけと認めている。そのうえで wild-cluster bootstrap は primary p = 0.175、inclusive p = 0.156 なので、統計的には帰無仮説を棄却できていない。

だから、この論文の現時点で言えることは「方向は Balmer 型仮説と一致する探索的証拠」まで。「日本国体で主観判定競技に開催地効果が集中している」と言うには、まだ足りない。そこを厳密に押さえないと査読で刺される。

### 総合判定

**プレプリント**: 出してよい。ただしタイトル・Abstract・Conclusion はさらに探索的に寄せた方が安全。

**査読誌**: Major revision。致命傷ではないが、中心推定の識別が弱い。特に以下の3つは、査読者がまともなら突いてくる。

- 主分析が2開催地だけ
- prefecture × sport 固定効果がない
- raw score をそのまま使っており、競技ごとの点数スケール差に弱い

この3つを追加分析で潰せるなら、かなり強くなる。

### 一番大きい統計上の問題

**1. 現在の主分析は「開催地効果」ではなく「佐賀・滋賀の主観競技パフォーマンス差」を拾っている可能性がある**

今の cross-section モデルは、prefecture FE、sport FE、year FE、trophy FE を入れている。これは悪くない。でも、**prefecture × sport 固定効果がない**。

つまり、佐賀や滋賀がもともと剣道・柔道・体操・馬術などで強い、または開催に向けて特定競技を重点強化していた場合、それが host × subjective に乗る。本文でも、interaction は実質的に Saga と Shiga の subjective-vs-objective host-cell contrasts から識別されており、38 subjective host cells がほぼ全ての identifying variance を持つと認めている。

これはかなり大きい。今のモデルでは「主観判定競技だから開催地効果が大きい」のか、「この2県が主観系競技に強かった／重点強化した」のかが分離しきれていない。

**追加すべき主分析はこれ**:

```
score ~ host × subjective + prefecture × sport FE + year FE + trophy FE
```

可能ならさらに:

```
score ~ host × subjective + prefecture × sport FE + sport × year FE + trophy FE
```

をやるべき。これにより、「各県が各競技でもともと強い」という固定差を吸収できる。2024・2025 の 2 年しかないので苦しいが、Saga は 2024 host / 2025 non-host、Shiga は 2024 non-host / 2025 host という構造なら、少なくとも同一県・同一競技の前年差を使う形に近づけられる。

この仕様で β_HS がまだ +方向なら、論文の説得力が一段上がる。逆にこれで消えるなら、今の主張はかなり危ない。

**2. raw score をそのまま使っているのは弱い**

現在の従属変数は sport-level score の点数。sport FE と trophy FE は入っているが、点数の分散・上限・配点構造の違いまでは吸収できない。競技 A は点数レンジが大きく、競技 B は小さい、という構造があるなら、raw points の +20 は競技間で同じ意味を持たない。

Table 5a では raw score で primary β_HS = +20.27、inclusive β_HS = +16.68。log(1+score) の方向確認は入っていて、interaction は +0.293 だが、まだ足りない。

**追加すべき感度分析**:
- sport × year × trophy 内で z-score 化した score
- sport × year × trophy 内で percentile/rank 化した score
- 各 sport-year-trophy の最大点に対する割合
- top-N placement indicator、可能なら top8 / top3 / champion within sport

特に z-score 版で β_HS が残るかは重要。raw points でだけ出て、標準化スコアで消えるなら、「主観判定競技の開催地効果」ではなく「点数スケールの重い競技の影響」かもしれない。

**3. cluster-robust p を Abstract で並べるのは危うい**

Abstract Results では cluster-robust p = 0.027 を出した後、wild-cluster bootstrap p = 0.175 を並べている。誠実ではある。でも、査読者の目線では、2 treated clusters なら primary inference は bootstrap p の方。cluster-robust p は補助的・参考値であって、Abstract で同格に見えるのはやや危ない。

**言い方を変えるべき**:

- 今: `cluster-robust p = 0.027; wild-cluster bootstrap p = 0.175`
- 修正案: `The point estimate was positive and large (+20.27 points), but did not reach conventional significance under the few-treated-clusters wild-cluster bootstrap correction (p = 0.175; naive cluster-robust p = 0.027).`

これなら「有意っぽく見せてから下げる」感じが消える。

### 研究デザイン上の問題

**4. 「confirmatory test」という言葉はやめた方がいい**

Methods に「single confirmatory test of the paper's central hypothesis」とあるが、事前登録がないなら、査読者は confirmatory と言われると引っかかる。さらに、その confirmatory test は wild-cluster bootstrap では非有意。だから「confirmatory」と呼ぶメリットがない。

**primary planned test** でいい:

> We treated β_HS in the 2024–2025 cross-section as the primary hypothesis test.

くらいで十分。「confirmatory」という言葉は消した方がよい。

**5. 主観・準主観・客観の分類はまだ強引**

分類感度分析は入っていて良い。Table 5d では全 4 variant で β_HS > 0、ただし wild-cluster bootstrap では default p = 0.175、combat-excluded p = 0.174、combat-to-semi p = 0.153、pure-judged p = 0.647。

ここから言えるのは:

> 分類を変えても点推定は正方向だった。

まで。でも、

> host bias is strongest under pure artistic scoring

は少し強い。Table 5d の combat-excluded は cluster-robust p < 0.001 だが、bootstrap p = 0.174 で、結局 primary と同じ。

「pure artistic scoring で strongest」と機序っぽく言うより:

> The largest point estimate occurred in the combat-excluded variant, but this variant shares the same few-treated-clusters limitation.

で止めた方がいい。

**6. 「審判バイアス」の論文ではなく「reduced-form sport-type heterogeneity」の論文**

ここは本文ではかなり認められている。judge roster が取れず、直接の Zitzewitz-style 分析はできない。また、観察された interaction は judge-bias、crowd-effect、practice-environment、transfer-athlete channels の reduced-form estimate であると honestly disclose されている。

これは正しい。でもタイトルが「Subjective Judging and the Host Effect」なので、読者は「審判バイアスを示した論文」と読みに行く。実際にはそこまでは言えない。

**タイトルを少し弱めるなら**:

- Main: `Sport-Type Heterogeneity in the Kokutai Host Effect`
- Sub: `An Objective-versus-Subjective Decomposition of Japan's National Sports Festival`

今のタイトルでもギリギリ許容だが、査読では「judging と言っているが judge-level data がない」と言われる可能性が高い。

### main panel の統計手法について

**7. ordered logit は正直かなり微妙**

2012–2022 panel では、rank 1–8 と outside top8 を rank 9 にして ordered logit を使っている。しかし outside top8 = 9 は、実際には 9 位ではなく「9 位以下すべて」。39 府県が同じカテゴリに潰れている。さらに host は 9/9 で top8、完全分離に近い。本文でも PO assumption は正式には検証不能で、top1 以外の threshold は singularity と書かれている。

だから ordered logit は「モデルとして美しい」より、「ほぼ分離した記述統計をロジットで表現しただけ」に近い。**主張の中心に置かない方がいい**。Table 2 に載せるのは良いが、本文では:

> The ordered-logit coefficient is descriptive and should not be interpreted as a stable behavioral log-odds estimate.

をもっと前に出すべき。

むしろ main panel は:

- host top8 = 9/9
- host top1 = 6/9
- non-host top1 = 3/414
- exact / permutation / Fisher-style test

で示す方が直感的で強い。ロジットの巨大係数より、単純な比率の方が査読者に伝わる。

**8. FE logit の degenerate rows は表に残す必要が薄い**

FE top1 logit は +1,877、SE undefined、pseudo-R² = 1。これは「分離して推定不能」という診断であって、推定結果ではない。本文は正直に書いているが、表に大きく出すと読者が引く。**Supplement に回すべき**。本体 Table 2 は pooled ordered logit / pooled top1 logit / descriptive exact comparison くらいでいい。

**9. Tokyo 除外感度分析は、解釈に注意が必要**

Tokyo を除くと top1 が完全分離し、host coefficient が +17.66 になる。Table 4b でも、その係数は preferred estimate ではなく mechanism diagnostic と書かれている。これは良い。ただし Discussion の「Tokyo's non-host championship mass was suppressing the estimated host coefficient」は正しい方向だが、Tokyo 除外後の推定値自体はほぼ意味がない。ここも **Supplement で良い**。本文で強調しすぎると、「分離したモデルを根拠にしている」と見られる。

### Funahashi replication について

**10. 「replication」という言葉は少し強い**

Funahashi の headline coefficient に近い値を再現しているのは良い。2003–2011 で +1,575.45、Funahashi reported +1,674.65。でも、本文は Funahashi の controls を省いている。Limitations でも、人口、GDP、headquarters、transfer-athlete、participants controls が omit されていると認めている。

なら「replication」より:

- `partial replication`
- `simplified replication`
- `pipeline validation against Funahashi's headline estimate`

が正確。

「5.9% gap is well within what would be expected from omitted controls」も少し言い過ぎ。期待範囲かどうかは、実際に controls を入れないと分からない。**修正案**:

> The 5.9% difference is plausibly attributable to specification differences, including the omitted controls, but a full replication would require assembling the original covariate set.

これで十分。

### Cross-section の追加分析案 (v7 対応)

査読誌を狙うなら、以下は重箱ではなく本質:

**A. prefecture × sport FE 版** — 最優先。現在の主分析では、host 県が特定スポーツに元々強いことを十分に吸収できない。prefecture × sport FE 版で正方向が残るかを見たい。

**B. standardized score 版** — raw score のままだと競技ごとの点数スケールに左右される。z-score、percentile、max-normalized score のどれかは入れるべき。

**C. randomization / permutation inference** — 2 treated clusters なら、クラスタ漸近に頼るより、2024・2025 の host 割当をランダムに置き換える permutation test が説得力を持つ可能性がある。少なくとも supplement に入れる価値がある。

**D. host 県ごとの分解** — Saga 単独、Shiga 単独で subjective-objective gap が同方向かを見るべき。2 県しかない以上、「両方で同方向」なら説得力が増える。片方だけが牽引しているなら、その県固有の話に見える。

### 主張の強さについて

**11. Abstract / Conclusion はまだ少し強い**

Conclusion では「directionally consistent」と書けているが、その後に「closes the specific quantitative gap left by Funahashi」とある。これはやや強い。bootstrap で非有意なので:

- `addresses the specific quantitative gap`
- または `begins to close the specific quantitative gap`

がよい。

あと Abstract の最後も:

- 今: `both support the Balmer direction`
- 修正: `are consistent with the Balmer direction`

の方が安全。「support」は査読者によっては強く読まれる。

### 良いところ

ここはかなり良い。

まず、2 treated clusters 問題を隠していない。Limitations でかなり具体的に、2-prefecture design、38 subjective host cells、65 objective host cells、wild bootstrap divergence を明示している。これは誠実。

Mammen weights も追加され、Rademacher p = 0.175 / 0.156 に対して Mammen p = 0.213 / 0.181 と、結論が変わらないことを示している。これは前稿より明確に改善。

欠測セル 0 点補完も、β_HS +20.27 に対して +19.86 とほぼ変わらず、欠測処理が主結果を作っているわけではないと示している。

Table 6 の記述統計も、objective +17.60、semi +26.18、subjective +37.91 と単調で、論文の主張を直感的に支えている。この図は残すべき。

### 体裁でまだ大きく残っているもの

体裁は重箱ではないレベルで 1 個だけ。

**References の番号がまだ壊れている**。文献リスト途中に 1. 2. 3. 4. が浮いていて、次ページにも 5. 6. ... が浮いている。これは絶対に直す。これが残っているだけで「最終稿ではない」と見える。内容が良くても損する。

### 結論: 厳しめの採否判定

**Reject 寄りの Major revision ではなく、Major revision 寄りの "promising but under-identified"**。

研究の問いは良い。データ収集も良い。限界の書き方もかなり誠実。でも、中心の統計的識別がまだ弱い。

現状の最も正確な論文タイトルは:

> Exploratory Evidence for Sport-Type Heterogeneity in the Kokutai Host Effect

であって:

> Subjective Judging and the Host Effect

だと少し強い。

査読誌で勝ちに行くなら、最低限これを追加してほしい:

1. prefecture × sport FE 版
2. sport-year-trophy 内 z-score / percentile / max-normalized score 版
3. Saga 単独・Shiga 単独の分解
4. permutation/randomization inference
5. 「confirmatory」を「primary planned」に変更
6. 「closes the gap」を「addresses / begins to close」に弱める
7. References 番号崩れを修正

これをやれば、かなり強い。逆にこれをやらずに査読誌に出すと、まともな査読者には「方向は面白いが、2 県の探索分析であり、主張がまだ強い」と言われる可能性が高い。

### 瑞樹追加コメント

> 何で佐賀とどこかの2箇所だけにゃ？全部でやれにゃ

= 過去の全国体 host 県データを集めて拡張パネル分析要 (現状 sport-level score data は 2024 Saga・2025 Shiga のみ・過去 host = 1988-2023 の 30+ 開催の sport-level data 調達方針が要 v7 起票の最大課題)

---

## v7 対応表 (13 finding + 追加データ調達)

| # | 分類 | 内容 | 対応 phase |
|---|---|---|---|
| 1 | 統計手法 (最優先) | prefecture × sport FE 版 | v7-T4 |
| 2 | 統計手法 | standardized score 版 (z-score / percentile / max-normalized) | v7-T5 |
| 3 | 統計手法 | Saga 単独・Shiga 単独の分解 | v7-T6 |
| 4 | 統計手法 | permutation / randomization inference | v7-T7 |
| 5 | text (tone) | "confirmatory" → "primary planned" | v7-T1 |
| 6 | text (tone) | "closes the gap" → "addresses / begins to close" | v7-T1 |
| 7 | 体裁 | References 番号崩れ修正 (瑞樹まだ見えてる・要別 viewer 検証) | v7-T2 |
| 8 | text (title) | 「Sport-Type Heterogeneity in the Kokutai Host Effect」等の弱化 | v7-T3 |
| 9 | text (Abstract) | cluster-robust p を主で並べない (bootstrap p を primary に) | v7-T1 |
| 10 | text (Methods) | ordered logit descriptive 扱いを前に出す | v7-T1 |
| 11 | text (Table 2) | FE logit degenerate rows を Supplement に | v7-T2 |
| 12 | text (Table 4b) | Tokyo 除外感度分析を Supplement に | v7-T2 |
| 13 | text (Methods) | Funahashi replication → partial replication に緩和 | v7-T1 |
| **追加** | **データ調達 (最大課題)** | 過去 host 30+ 開催の sport-level score data 調達方針 | **v7-P0 (要瑞樹判断)** |

## v7 実施計画 (次セッション着手)

- **P0 (データ調達方針決定・瑞樹相談必須)**: PLAN-DEVIATIONS.md#deviation-1 の既存結論 (第58-77回ゼロ確定 / JSPO 個別回 PDF 第68-77回は画像 PDF or 404 で抽出困難) を先に確認 → その上で追加調達方針 (手動転記 / 別ソース探索 / 分析範囲縮小の判断) を確定
- **T1 (text-only 系 6 件・Finding #5/6/9/10/11/12/13)**: tone 弱化 + Abstract p 順序変更 + ordered logit descriptive 前出し + FE/Tokyo Supplement 移動 + Funahashi partial replication
- **T2 (体裁 1 件・Finding #7)**: References 番号浮きの瑞樹 viewer 名 + 該当ページ確認 → CSS 深堀り着手
- **T3 (タイトル 1 件・Finding #8)**: タイトル弱化 (「Sport-Type Heterogeneity in the Kokutai Host Effect」等)
- **T4-T7 (統計手法系 4 件・Finding #1/2/3/4)**: prefecture × sport FE / standardized score / Saga/Shiga 分解 / permutation inference (pytest 増加想定)
- **T8**: Phase C build (v7-final PDF) + 全 35 ページ pdftoppm + Read 目視 (T11 pattern 継続) + Desktop 配置
- **T9**: GPT round-5 依頼 → M5 SSRN 投稿
