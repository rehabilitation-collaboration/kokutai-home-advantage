# PLAN: 第8弾 国民体育大会×開催地優勝バイアス (英語論文・SSRN)

## ゴール宣誓（段取り八分・祝福済み）

- **祝福日時**: 2026-07-27 (Phase 4-5 で祝福・Phase 8 で一部修正 2026-07-27)
- **プロジェクトディレクトリ**: `~/claude/analysis/kokutai-home-advantage/`
- **関連 handoff**: `~/.claude/projects/-Users-mizukishirai/memory/handoff-kokutai-home-advantage.md`
- **Phase 8 成果物**: `~/claude/analysis/kokutai-home-advantage/PHASE8-INVESTIGATION.md` (kerberos+hades 二院制)

### このタスクが終わったら、こうなってる:
- 国体 (国民スポーツ大会) の80年分の成績データを集めて「開催した県が優勝しやすい」って昔から言われてる噂を数字で確かめた**英語論文**が、SSRN で公開されてる (Abstract ID + 公開 URL 付き)
- 「剣道みたいな審判の判定で勝ち負けが決まる競技」と「陸上みたいなタイムで勝ち負けが決まる競技」で開催地の有利さがどれくらい違うかを**世界で初めて数字で示した**論文になってる (従属変数は順位ベース・順序 logit)
- 2016年以降は「2016-17 (2年) + 2022-24 (3年) の post-2016 2クラスター + pre-2005 の 2002 単独 = **合計6ショック年**」の構造変化まで捕まえてる
- 論文シリーズ「日本の風習 vs データ」第8弾として並ぶ

### 具体的に、こうなってへんかったら失敗:
- SSRN POSTED 未達成 (SUBMITTED 止まりは失敗)
- 日本語のみで英語版がない (瑞樹指示違反・SSRN 実運用不適合)
- 主観判定 vs 客観競技の分離検証がない (= 舟橋2016 劣化コピー)
- 2016年以降の開催地敗北6ショックの構造変化を捕まえてない
- 舟橋2016/末次2025 の先行研究への差別化説明不十分で査読で刺される
- Phase 2 で判明した認識誤り4件 + Phase 8 で判明した書誌誤り2件+2016年5連覇仮説誤りが論文に混入
- 「奈良判定」を剣道の話として書く (正=ボクシング山根明系)

### 成果物:
- `~/claude/analysis/kokutai-home-advantage/` プロジェクトディレクトリ
- SSRN 公開論文 (英語版 PDF・Abstract ID + 公開 URL)
- 3 handoff ファイル (handoff-kokutai-home-advantage.md + handoff-paper-brainstorm.md 第8弾ブロック + handoff-index.md)
- MEMORY.md 索引 (max-plan / -Users-mizukishirai 両方) 更新
- 論文シリーズ表更新: 現状 風習系 POSTED 4本 (厄年/六曜/五月病/満月) + 進行中1本 (13金 SUBMITTED) + 本論文 POSTED 達成で **風習系5本 POSTED**

---

## ロードマップ

| # | やること | 出力 | 該当 Phase |
|---|---|---|---|
| **M1** | データ取得 + 競技分類完備 | 全79大会パネル CSV + 主観/客観競技分類 | Phase 1 |
| **M2** | 統計分析完了 | 順位ベース (順序 logit) + 2012-2024 期間拡張 + event-study 2層設計 + 交絡変数統制 (Csurilla型) | Phase 2 |
| **M3** | 英語論文執筆 + PDF 初版 | manuscript.md (英語) + PDF v1 (pdftotext 自己 QA 100%) | Phase 3 |
| **M4** | asura-monju + GPT 査読サイクル完遂 | Accept 確定版 (Vn) | Phase 4 |
| **M5** | SSRN 投稿 + POSTED 到達 | Abstract ID + URL + 4 ファイル更新 | Phase 5 |

### やらんこと (YAGNI 宣言):
- **主軸② 採点員属性の氏名レベル分析** (Phase 8 で審判員名簿4系統独立確認で発見できず→主軸落とし)
- **④東アジア4カ国対比の独自データ収集** (韓国 KSOC 20%加算 + 中国 兰彤2012 アブスト範囲のみ引用・独自国別分析はやらない)
- **BMJ Christmas 併用投稿** (SSRN 単独完結・次段派生)
- **舟橋2016 パネル完全再現 (2003-2011 の全変数再現)** (2012-2024 拡張に注力・2003-2011 は舟橋再現副次比較のみ)
- **全40競技悉皆分析** (JFA/JIHF/剣道以外 Not found → 主観 vs 客観分離は分析可能範囲で)
- **末次2024/2025 本文取得** (瑞樹却下・書誌+CiNii リンクレベル引用のみ)
- **中国 兰彤2012 本文 (フルテキスト) 取得** (アブスト範囲の Low confidence 引用のみ・Phase 9 補遺で再検討)
- **判定バイアス認知心理学メカニズム論** (scope 外)

### 分岐条件 (Phase 8 発火状況+将来分岐):

**Phase 8 で発火済み (対応方針確定):**
- **部分発火①**: 主軸① 素点ベース不可能 → 順位ベース (順序 logit) にピボット確定 (Key Decision #8)
- **完全発火②**: 主軸② 審判員名簿不在 → 主軸落として ①③⑤ の3本立てに縮小確定 (Key Decision #9)
- **部分発火③**: Csurilla2023「大幅減衰」判明 (約45%減衰) → 交絡変数統制モデル必須追加確定 (Key Decision #13)

**Phase 9 補遺で判定済み (発火状況 2026-07-27 深夜):**
- **発火 (発見)**: JSPO 第79回 (2025滋賀) `79_score_deta.xls` に **47県 × 37競技 (冬季3+本大会34) の得点内訳完全公開** (Phase 8 判定を単年サンプルで部分的に覆す) → Phase 1 に「他年度 (第58-78回) xls 探索」タスク追加 + Phase 2 に「単年断面 素点ベース副次分析」追加。順位ベースピボット本体は覆らない。**★Deviation #1 で追加確定 (2026-07-27 深夜)**: 他年度探索完遂 → **2024佐賀 + 2025滋賀の2年で発見 (第58-77回ゼロ)**・順位ベースピボット維持継続・副次分析は 2年断面比較 (host推移) に拡張 (詳細=`PLAN-DEVIATIONS.md#deviation-1`)
- **発火 (成功)**: 兰彤2012 アブスト+書誌完全取得 (参考网 m.fx361.com 経由・5特徴の分類 高效性/渐增性/延迟性/排他性/双刃性) → Discussion 章で **Low-Medium confidence** の東アジア文脈参考例として2-3文言及可 (中国国際比較を韓国 KSOC と2本立てに拡張)
- **詳細**: `PHASE9-SUPPLEMENT.md` 参照

**Phase 1-2 で判定 (実装分岐):**
- 剣道以外の主観判定競技 (体操/柔道等) で得点表発見時 → 主軸① 分析対象拡大
- Phase 2 event-study parallel trend 検定で pre-2005 群と post-2016 群の傾向線が有意に発散 → hades H-03 の2層設計を保持 (単一モデルに統合しない)
- GDP 系列断絶で 2012-2024 と 2003-2011 の係数比較不能 → Phase 2 で2窓分離 (主推定=2012-2024 + 副次比較=2003-2011) 確定

---

## Background（なぜ必要か）

- **国民体育大会** (2024 年以降「国民スポーツ大会」に改称) は 1946 年から続く日本の47都道府県対抗大会で、開催地県 (会場を担当した県) の総合成績が突出して高い現象が古くから知られている
- 実データ (JSPO 公式総合成績): 1978-2015 の開催地優勝率 **97.30%** vs 2016-2025 の開催地優勝率 **37.50%** (Phase 8 一次資料確認済)
- 「開催地敗北6ショック年」 = 2002 高知 / 2016 岩手 / 2017 愛媛 / 2022 栃木 / 2023 鹿児島特別 / 2024 佐賀 (Phase 8 独立ソース全件追認済)
- 先行研究の空白: 舟橋2016 (2003-2011 パネル 47都道府県×9年 n=423 完全バランス・R²=0.86) が最大先行研究だが **主観 vs 客観分離検証は行われていない** (Balmer 2001 のみ引用・Balmer 2003 非引用・交互作用項ゼロ・主観/客観競技のグルーピング変数不在)
- 論文シリーズ「日本の風習 vs データ」第8弾 (第1-7弾: 厄年/六曜/五月病/満月/13金/花粉自殺/温冷食品)

## Goals（成功の定義）

- 国体 79 大会の総合成績データ (JSPO 公式 + 都道府県体協 + 競技団体アーカイブ) で開催地バイアスを競技属性別 (主観判定 vs 客観記録) に検証した査読可能な英語論文を完成
- writing-guide.md に沿って執筆し、asura-monju レビューをパスする
- GPT 査読サイクル (V1-Vn) を Accept 到達まで反復する
- SSRN Abstract ID 取得 + POSTED 到達 (SUBMITTED 止まりは失敗)

## Non-Goals

- 主軸② 採点員属性の氏名レベル分析 (審判員名簿不在確定)
- 全40競技悉皆分析 (公開範囲外)
- 中国・韓国の独自データ再分析 (先行研究アブスト or 記事引用のみ)
- 末次2024/2025 の本文取得を試みる (書誌+CiNii リンクレベル引用のみ・瑞樹却下)
- BMJ Christmas 併用投稿

## Test Strategy

- **分析コード pytest**: 順位ベース (順序 logit) 実装・panel 構築・event-study 2層設計・交絡変数統制モデル (Csurilla型) の数値整合性テスト
- **書誌整合性チェック**: CrossRef API で全引用文献の書誌照合 (書誌訂正2件 = 舟橋2016 + Csurilla2023 が正しく反映されているか)
- **PDF 自己 QA**: `pdftotext -layout` で全ページ抽出→目視 100% ([[feedback-paper-pdf-selfqa-before-gpt]])。asura-monju/GPT 査読投入**前**に必須
- **論文レビュー**: asura-monju round-1 実施→修正→再査読
- **GPT 査読サイクル**: V1→Vn 反復・Accept 到達まで (friday13th で GPT round-1〜9 の運用実績あり・[[feedback-paper-precision-over-effort]])
- **書誌情報の伝播チェック**: PHASE8-INVESTIGATION.md 書誌訂正2件が manuscript.md/references セクションに正しく転記されているか

---

## 研究デザイン

### データソース (一次確定)

| 種別 | ソース | URL | カバー範囲 |
|---|---|---|---|
| 総合順位 index | JSPO tabid183 | https://www.japan-sports.or.jp/kokutai/tabid183.html | 第1-80回 + 特別大会 = 全**82件** (Phase 8 マッピング確定・KOKUTAI_HOSTS 80 + KOKUTAI_SPECIAL 2) |
| 個別回 PDF | JSPO 概要ページ相対リンク | 第58-77回一貫「天皇杯・皇后杯総合順位/得点のみ」(内訳ゼロ)・**★第78回2024佐賀 + 第79回2025滋賀の2年のみ**: `{回}_score_deta.xls` (or `_data.xls`) に 47県×37競技詳細内訳あり (両年で構造完全一致・天皇杯57×70/皇后杯57×48・**Deviation #1 で全件確認済**) | PDF=要 `pdftotext -layout` / xls=要 `python-calamine` (xlrd 不可) |
| 総合順位 (第3-79回) | 長野県体協 high_rank.html | https://www.nagano-sports.or.jp/kokutai/record/high_rank.html | 天皇杯/皇后杯 1-8位 |
| 長野競技別得点 | 長野県体協 game_score.html | https://www.nagano-sports.or.jp/kokutai/record/game_score.html | **長野1県時系列のみ×2016年以降9年分のみ** (47県パネル不可) |
| 692p PDF | JSPO archives | https://www.japan-sports.or.jp/Portals/0/images/archives/01_kokutai.pdf | 第1-65回 (2010まで)・要 `pdftotext -layout` |
| 交絡変数 (人口+GDP) | 内閣府 ESRI 県民経済計算 総括表 | https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/files/contents/main_2022.html | soukatu1=名目GDP + soukatu9=総人口・47県×2011-2022 (12年)・2008SNA平成27年基準・**Deviation #3 で e-Stat 統合廃止**・python-calamine 必須 |

### データソース (二次補助・競技別)

| 競技 | ソース | 特記 |
|---|---|---|
| サッカー (客観リファレンス) | JFA https://www.jfa.jp/match/nationalsportsfestival_2024/history.html | 勝敗/順位のみ・得点なし |
| アイスホッケー (客観リファレンス) | JIHF https://www.jihf.or.jp/watching_games/tournament/detail.php?meet_id=6 | 2012年で更新停止 |
| 剣道 (主観判定) | old2 https://old2.kendo.or.jp/competition/kokutai/71st/result/ | **2016年 (第71回) 岩手のみ**得点表発見・2022年 (第77回) 栃木で消失 |
| 柔道 | 全柔連公式 | アーカイブなし |
| 体操 | jpn-gym.or.jp | **Phase 1 中盤 (2026-07-28) 接続復旧確認済 (HTTP 200)**・**ただしサイト内 (トップ/event/) に国体データ非公開**でパーサ実装不要・Limitations 明記に確定 (Deviation #2) |

### データソース (先行研究一次確保・書誌訂正済み)

| 引用 | 書誌 | DOI/URL |
|---|---|---|
| 舟橋2016 (最大先行研究) | 舟橋弘晃・**日比野幹生・石黒えみ**・間野義之 (2016)「国民体育大会総合成績の決定要因：都道府県別パネルデータによる計量分析」**スポーツマネジメント研究** 8(1) **pp.17-33** | DOI 10.5225/jjsm.2016-002 (J-STAGE OA) |
| Csurilla2023 (交絡統制モデル) | **Csurilla, G. and Fertő, I.** (2023) "The less obvious effect of hosting the Olympics on sporting performance" **Scientific Reports** 13:819 | DOI 10.1038/s41598-022-27259-8 (PMC 全文 https://pmc.ncbi.nlm.nih.gov/articles/PMC9895060/) |
| Balmer2003 (主観/客観分離モデル) | Balmer, Nevill & Williams (2003) J Sports Sci 21(6):469-478 | PubMed 12846534 |
| Balmer2001 (Winter Olympics) | Balmer, Nevill & Williams (2001) J Sports Sci 19:129-139 | PubMed 11217011 |
| Balmer2005 (ボクシング判定タイプ連続変化) | Balmer et al. (2005) J Sports Sci 23:409-416 | (国体採点競技分析に直接応用可) |
| Zitzewitz2006 (フィギュア同郷バイアス) | Zitzewitz (2006) J Econ Manage Strategy | DOI 10.1111/j.1530-9134.2006.00092.x |
| Nomura2022 (J1無観客 SEM) | Nomura (2022) Frontiers in Sports and Active Living | DOI 10.3389/fspor.2022.927774 |
| 千葉1987 (国体開催県優勝の5要因) | 千葉 (1987) J-STAGE 38a_204 | DOI 10.20693/jspeconf.38a.0_204 |
| 末次2024 (書誌のみ) | 末次美樹 (2024)「国民体育大会『空手道競技』の大会成績から見える課題」駒澤大学総合教育研究部紀要 18, pp.137-153 | CiNii https://cir.nii.ac.jp/crid/1390303254959134848 |
| 末次2025 (書誌のみ) | 末次美樹 (2025)「国民体育大会 空手道競技の課題の可視化と構造原理の解明」駒澤大学総合教育研究部紀要 19, pp.103-117 | DOI 10.69200/0002033886 |
| 韓国 KSOC 20%加算 (国際比較) | 문화일보 2025-10-13 김태형記者記事 | https://v.daum.net/v/20251013192536045 |
| 兰彤2012 (中国・アブスト取得済み Low-Medium 引用) | 兰彤・于晓光 (2012)「全运会东道主效应特征的理论和实证研究」沈阳体育学院学报 31(4) pp.1-5 (5特徴の分類 = 高效性/渐增性/延迟性/排他性/双刃性) | 参考网 https://m.fx361.com/news/2012/1109/12534183.html (Phase 9 補遺 2026-07-27 で取得) |

### 主モデル (Phase 8 決定事項反映)

**主軸① 主観 vs 客観分離 (順位ベース・順序 logit)**:
```
P(Rank_it ≤ k) = F(α_k + β1·Host_it + β2·Subj_i + β3·Host_it × Subj_i
                  + γ·Controls_it + μ_i + ν_t)
```
- Rank_it = 都道府県 i の年 t における順位 (1-47)
- Host_it = 開催地ダミー (1 if 都道府県 i が年 t の開催地)
- Subj_i = 主観判定競技ダミー (Balmer2003 の主観客観分離定義に準拠)
- **交互作用項 β3** = 主観判定競技で開催地バイアスがどれだけ増強されるか (本論の novelty コア)
- Controls_it = 人口 (対数)・県内 GDP (対数)・都道府県 FE (μ_i)・年 FE (ν_t)
- 従属変数は **順位ベース (順序 logit)** で確定 (素点ベースは長野1県のみで不可能)

**主軸③ 2012-2024 パネル拡張 (舟橋2016 差別化)**:
- 舟橋2016 (2003-2011) 再現副次比較 + 2012-2024 主推定 (SNA 同一基準内)
- GDP 系列は 2 窓分離 (H-04)

**event-study 2層設計 (H-03)**:
```
Y_it = Σ_τ β_τ · 1{t = ShockYear + τ} + γ·X_it + μ_i + ν_t + ε_it
```
- **Layer 1 (pre-2005)**: 2002 高知単独 (ふるさと選手制度導入前)
- **Layer 2 (post-2016)**: 5ショック (2016 岩手 / 2017 愛媛 / 2022 栃木 / 2023 鹿児島特別 / 2024 佐賀)
- 単一 DID (post-2016 一括) は不可 (2018 福井/2019 茨城で開催地優勝・parallel trend 前提崩壊)
- 2層分離により parallel trend 前提を各層内で保持

**交絡変数統制 (Csurilla型)**:
- 人口 (対数) + 県内 GDP (対数): **内閣府 ESRI 県民経済計算 総括表に一本化** (soukatu9=総人口 + soukatu1=名目GDP・同一基準・同一年カバー・同一データソース組織)。**Deviation #3 (2026-07-28) で e-Stat 統合廃止**・整合性/再現性/書誌シンプル化/Csurilla2023 準拠の4点で ESRI 一本化が最適判定
- **主推定期間 = 2012-2022 (11年)**: ESRI 令和4年度版が最新公表 (2026-07-28 時点)・カバー範囲 2011-2022 に合わせて主推定期間短縮 (元 PLAN の 2012-2024 → 実データ範囲に整合)。舟橋2016 の 9年×47=423 と同水準の統計パワー確保 (11年×47=517)
- 副次比較 (2003-2011): 必要時点で ESRI 旧SNA 基準ページ (main_2011.html 等) から追加取得
- スポーツ振興予算 (国): 文科省/スポーツ庁 (取得容易)
- スポーツ振興予算 (都道府県): 47県×13年の手集計要 (取得困難・実装時に必要性判断)

### 時間軸スコープ整理 (5層・混同注意)

| # | 用途 | 期間 |
|---|---|---|
| 全体パネル | 統計母集団 | 第3回1948〜第79回2025 (計77大会) + 特別2件 = **合計79大会**。**★特別2の内訳確定 (Phase 1 前半 2026-07-28)** = (a) **2023鹿児島特別大会** (COVID 延期分・第20回鹿児島国体) + (b) **1973沖縄若夏国体** (沖縄本土復帰後初の国体・第28回本大会外の特別枠・ただし nagano データ不在で順位ベース分析母集団からは実質除外) |
| 舟橋2016 比較+新規収集範囲 | 主軸③ 期間拡張 | **2003-2022** (舟橋 2003-2011 + 拡張 2012-2022・**Deviation #3 で 2024→2022 短縮**・ESRI 令和4年度版が最新公表) |
| 見出し統計区分 | 物語上の切れ目 | 1978-2015=97.30% vs 2016-2025=37.50% (実態は 2016-17 + 2022-24 の2クラスター) |
| 学術通説起点 | Introduction 記述用 | 1964 新潟以降 (Wikipedia 本文根拠) |
| event-study 2層設計 | 分析設計 | pre-2005 (2002 高知単独) + post-2016 (5ショック) |

- **総合成績スキーマ**: 総合成績 = 競技得点 + 参加得点 / 天皇杯 = 男女総合1位 / 皇后杯 = 女子総合1位 / 中止時は「空位」規定
- **従属変数の最終選択**: 順位/入賞可否 (順序 logit / 二値) にピボット確定 (Phase 8 Key Decision #8)

---

## パイプライン設計

```
definitions.py         — 都道府県コード・競技分類 (主観/客観)・開催地マッピング (第3-79回)
data_loader.py         — JSPO tabid183 スクレイピング (82件) + PDF pdftotext 変換 + 長野県体協パース
panel_builder.py       — 47都道府県×大会年パネル構築 + 交絡変数 (人口/GDP/予算) 結合
sport_classifier.py    — 競技を主観/客観/準主観にラベル付け (Balmer2003 準拠)
analysis_main.py       — 順位ベース (順序 logit) 主モデル + 交互作用項
analysis_event_study.py — event-study 2層設計 (pre-2005 + post-2016)
analysis_replication.py — 舟橋2016 (2003-2011) 再現 + 2012-2024 拡張
analysis_confounders.py — Csurilla型交絡変数統制 (人口/GDP/予算)
plots.py               — Figure 1-5 生成
tests/
  test_data_loader.py   — スクレイピング/PDF 変換の正確性テスト
  test_panel_builder.py — パネル整合性テスト
  test_analysis.py      — 順序 logit + event-study の数値整合性テスト
```

---

## Phase 別詳細

### Phase 0: ベンチマーク論文の収集・精読 (実質完了扱い)
- **変更対象**: `PHASE8-INVESTIGATION.md` (既存・Phase 8 で完了) + `LITERATURE.md` (Phase 3 で新規作成)
- **ブリーフ**: Phase 8 の kerberos B系 + hades 検証で先行研究一次確認は実質完了。PHASE8-INVESTIGATION.md Part 2 に全 findings を集約済み
- **hades 深掘り 6項目 (H-01〜H-06)** — 全内容は `PHASE8-INVESTIGATION.md` Part 4 Part B 参照:
  - H-01 (High): 主軸① 順位ベース (順序 logit) ピボットは Balmer2003 定義と整合維持可能・舟橋2016 の Balmer2001-only 引用+分離検証ゼロを差別化点として据える推奨
  - H-02 (Medium): JSPO「役職別人数」PDF は氏名なし構造データとして副次利用可能
  - H-03 (Medium): event-study 2層設計 (pre-2005 単独+post-2016 5ショック)・parallel trend 検証必須
  - H-04 (Low): GDP 系列 2窓分離 (2012-2024 主推定+2003-2011 舟橋再現副次比較)
  - H-05 (High): 未検証3件引用強度 (韓国=High格上げ / 中国=Low降格→Phase 9 補遺で Low-Medium 見直し済 / 末次=Medium)
  - H-06 (Medium): 末次論文本文取得 (熊大リポジトリ司書経由の再試行案・瑞樹却下で書誌+CiNii リンクレベル引用に留める)
- [x] 舟橋2016 本文精読 (Phase 8 で完了・書誌訂正済み)
- [x] Csurilla2023 PMC 全文取得 (Phase 8 で完了・書誌訂正済み)
- [x] 千葉1987 骨子確認 (Phase 8 で完了・審判/ジャッジ言及ゼロ確定)
- [x] Balmer2003 骨子確認 (Phase 8 で完了・PubMed 12846534)
- [x] 韓国 KSOC 20%加算 確認 (Phase 8 で完了・문화일보一次資料)
- [x] 末次2024/2025 書誌のみ確認 (Phase 8 で完了・本文取得は瑞樹却下)
- [ ] `LITERATURE.md` 新規作成 (Phase 3 執筆時に PHASE8-INVESTIGATION.md Part 2 を LITERATURE.md 形式に再構成)

### Phase 9-補遺: xls 実物確認 + 兰彤アブスト取得 (完遂 2026-07-27 深夜)
- **変更対象**: `PHASE9-SUPPLEMENT.md` (新規・Part 1-4)
- **ブリーフ**: PLAN 起票後・Phase 1 着手前に Phase 8 未達2件を確認 → 両方成功。詳細=`PHASE9-SUPPLEMENT.md`
- [x] JSPO 第79回 (2025滋賀) `79_score_all_data.xls` + `79_score_deta.xls` を curl でダウンロード成功
- [x] `pandas.read_excel(engine='calamine')` (rust製 python-calamine・xlrd は formula FuncID:186 未知で AssertionError・venv 完結・PEP 668 externally-managed 回避) で全 sheet_names 開封
- [x] 競技別内訳確認 → **決定的発見**: `79_score_deta.xls` に 47県 × 37競技 (冬季3+本大会34) 詳細内訳完全公開 (単年 2025 のみ・他年度は Phase 1 冒頭タスクで探索)
- [x] 兰彤2012 アブストを WebSearch 4回反復で探索 (CNKI/万方/学報公式は 2015 以前非表示のため参考网 m.fx361.com にヒット)
- [x] 参考网 https://m.fx361.com/news/2012/1109/12534183.html で書誌+アブスト+キーワード+5特徴 (高效性/渐增性/延迟性/排他性/双刃性) 完全取得
- [x] 引用強度 Low → Low-Medium 見直し・Discussion 章で東アジア文脈参考例として 2-3 文言及可と確定 (韓国 KSOC と2本立てに拡張)
- [x] `PHASE9-SUPPLEMENT.md` (Part 1-4・186行) に確認結果を記録 + PLAN.md 6箇所編集で反映
- **成果物 (xls 実体)**: `~/claude/analysis/kokutai-home-advantage/refs/79_score_all_data.xls` + `79_score_deta.xls` にコピー保存 (Phase 1 実装時に流用・再 DL 不要)

### Phase 1: データ取得・前処理 + パネル構築
- **変更対象**: `definitions.py`, `data_loader.py`, `panel_builder.py`, `sport_classifier.py`, `tests/test_data_loader.py`, `tests/test_panel_builder.py`
- **ブリーフ**: JSPO tabid183 (82件) をスクレイピングし、個別回 PDF を `pdftotext -layout` で変換。47都道府県×大会年パネルを構築し、競技を主観/客観/準主観に分類
- **★Phase 1 内区分定義** (2026-07-28 初見テスト反映+中盤完遂反映):
  - **Phase 1 冒頭タスク** = JSPO 各回個別ページの xls 全件探索 (Phase 9 補遺タスク・**完遂 Deviation #1**)
  - **Phase 1 前半** = パネル構築骨格 = `definitions.py`/`sport_classifier.py`/`data_loader.py` (長野県体協 high_rank.html + JSPO 78+79 xls パーサのみ)/`panel_builder.py`/`tests/` (**完遂 2026-07-28・113 pytest all passing**)
  - **Phase 1 中盤** = 外部データソース補完 = `data_loader.py` に 5関数追加 = 剣道 old2 / 長野 game_score.html / JFA / JIHF / JSPO 個別回 PDF (58-67回 規則的パス) (**完遂 2026-07-28・153 pytest all passing・+40件追加**)。体操 jpn-gym は接続復旧確認済 (Phase 8 ECONNREFUSED → 200 OK) だがサイト内国体データ非公開で Limitations 明記に確定 (Deviation #2)
  - **Phase 1 後半** = 交絡変数結合 = `data_loader.py` に ESRI 3関数 (`load_esri_soukatu`+`load_esri_population`+`load_esri_gdp_nominal`) + `panel_builder.py` に `merge_confounders()` 追加 (**完遂 2026-07-28・170 pytest all passing・+17件追加・Deviation #3 起票 = ESRI 一本化 + 主推定期間 2012-2022 短縮**)
- [x] **(Phase 9 補遺追加タスク・最優先)** JSPO 各回個別ページ (第58-78回) を再スクレイピングし、`{回}_score_deta.xls` or 類似ファイル (`_data.xls`) の存在有無を全件確認 = **完遂** (2026-07-27 深夜)。**発見結果 = 2024佐賀 (`78_score_data.xls` + `78_score_all_data.xls`) + 2025滋賀 (既知) の2年分・第58-77回はゼロ・第75回2020のみ冬季 xlsx あり (COVID中止年・本論主軸に無関与)**。第78回は第79回と構造完全一致 (天皇杯 57×70 / 皇后杯 57×48)。順位ベースピボット再検討結果 = **維持継続** (2年ではパネル不能・詳細は `PLAN-DEVIATIONS.md#deviation-1`)
- [x] `definitions.py`: 都道府県コード (47) + 開催地マッピング (第3-79回) + 特別大会フラグ列 + 中止年ハンドリング (第75/76 = COVID中止) = **Phase 1 前半で完遂 (2026-07-28)**・KOKUTAI_HOSTS=80大会 + KOKUTAI_SPECIAL=2件 (special_2023鹿児島 + special_1973沖縄若夏国体・後者は nagano データ不在で実質除外)
- [x] `data_loader.py`: JSPO tabid183 スクレイピング (BeautifulSoup + requests・**82件 tabid マッピング** = 第1-80回80件 + 特別2件・Phase 1 前半で確定 → `refs/host_mapping_raw.json`)
- [x] `data_loader.py`: 個別回 PDF を `pdfplumber` で変換 = **Phase 1 中盤で完遂 (2026-07-28)**・`load_jspo_kai_pdf(kai_num, cup)` 実装・**規則的パス `data0/kokutai/{kai}/{kai}_{cup}.pdf` の第58-67回 (10回×2杯=20 PDF・47県総合順位/得点) 完全カバー**。第68-77回は 404 or 画像PDF (74茨城=6ページtext抽出不能) で Phase 2 個別対応 (OCR 検討要)。詳細=`PLAN-DEVIATIONS.md#deviation-2`
- [x] `data_loader.py`: 長野県体協 high_rank.html パース (第3-79回天皇杯/皇后杯 1-8位) = **Phase 1 前半で完遂 (2026-07-28)**・156レコード生成
- [x] `data_loader.py`: 長野県体協 game_score.html パース (長野1県時系列 2016年以降9年分・素点ベース副次比較用) = **Phase 1 中盤で完遂 (2026-07-28)**・`load_nagano_game_score()` 実装・41競技×10大会 (71-79+special_2023)=410レコード long format 生成
- [x] `data_loader.py`: 剣道 old2 第71回岩手 (2016年) 得点表パース (**主観判定競技の副次データ**) = **Phase 1 中盤で完遂 (2026-07-28)**・`load_kendo_2016_iwate()` 実装・9レコード (7位3県同点)・**岩手 host 優勝144点確認 = 主観判定競技での host effect 残存の実データ**
- [x] `data_loader.py`: JFA サッカー歴代パース (**客観記録競技リファレンス**) = **Phase 1 中盤で完遂 (2026-07-28)**・`load_jfa_soccer_history()` 実装・第1-76回まで (2020延期/2021中止マーク付・第77回以降 4部門化行は Phase 2 個別対応)
- [x] `data_loader.py`: JIHF アイスホッケー (2012年まで) パース (**客観記録競技リファレンス**) = **Phase 1 中盤で完遂 (2026-07-28)**・`load_jihf_hockey()` 実装・第1-67回2012 (2012年で更新停止確認・第2回 データ無し)
- [x] `data_loader.py`: 体操 (jpn-gym.or.jp) 別ツール経由再接続試行 = **接続復旧確認済 (Phase 8 ECONNREFUSED → 2026-07-28 HTTP 200)**・ただしサイト内 (トップ/event/) に国体データ非公開でパーサ実装不要・**Limitations 明記に確定** (Deviation #2)
- [x] `sport_classifier.py`: **Balmer2003 定義に厳密準拠**して **40競技全て (冬季3+本大会37)** を 3分類 = **Phase 1 前半で完遂 (2026-07-28)**・objective 16/subjective 11/semi_subjective 13:
  - **主観判定** = 剣道/柔道/体操/空手道/銃剣道/なぎなた/ボクシング/フェンシング/レスリング/相撲/馬術 (審判減点)
  - **客観記録** = 陸上/水泳/自転車/ローイング/カヌー/ウエイトリフティング/セーリング/スキー/スケート/アーチェリー/弓道/ライフル射撃/ゴルフ/ボウリング/トライアスロン/クライミング
  - **準主観 (団体競技=Balmer2003 の semi-subjective 定義)** = サッカー/バスケットボール/バレーボール/ハンドボール/ホッケー/ラグビー/軟式野球/ソフトボール/バドミントン/卓球/ソフトテニス/テニス/アイスホッケー
  - **★注記**: `PHASE9-SUPPLEMENT.md` の滋賀内訳表の分類ラベル (「客観(団体)」「準主観=馬術」等) は Balmer2003 定義とズレる可能性のある暫定推定・実装時に原論文再確認して 37競技×3分類マッピングを最終確定
- [x] `panel_builder.py`: 47都道府県×大会年パネル構築 (総合順位・開催地ダミー・特別大会フラグ) = **Phase 1 前半で完遂 (2026-07-28)**・47県×78大会×2杯=**7332行 long format パネル**生成可 + build_host_summary() で event-study 用サマリ (総合得点は Phase 1 中盤の個別回 PDF パースで追加予定)
- [x] `data_loader.py`: ESRI 県民経済計算パーサ = **Phase 1 後半で完遂 (2026-07-28)**・`load_esri_soukatu()` 汎用パーサ + `load_esri_population()` (soukatu9・47県×12年 単位人) + `load_esri_gdp_nominal()` (soukatu1・47県×12年 単位100万円) + `ESRI_DIR` 定数。**Deviation #3 で e-Stat 統合廃止・ESRI 一本化に確定**
- [x] `panel_builder.py`: 交絡変数結合 = **Phase 1 後半で完遂 (2026-07-28)**・`merge_confounders(panel, population_df, gdp_df)` 実装・7332行 panel に `population`/`gdp_nominal_mil_yen`/`log_population`/`log_gdp` の 4列追加・2011-2022 non-special 100% カバー・範囲外 100% NaN・numpy import 追加
- [x] `tests/test_data_loader.py`: 24+40+**11**=**75 テスト実装** (年号変換・長野HTML・JSPO xls・剣道・長野game_score・JFA・JIHF・JSPO PDF・list_available* + **ESRI soukatu/population/gdp**)
- [x] `tests/test_panel_builder.py`: 14+**6**=**20 テスト実装** (7332行 shape・host優勝/敗北・特別大会・year sorted + **merge_confounders 6件**)
- [x] `tests/test_definitions.py`: 25 テスト (47県・80大会・特別大会・panel母集団・アクセサ)
- [x] `tests/test_sport_classifier.py`: 50 テスト (40競技3分類・alias・冬季)
- [x] **pytest 全パス (計 170 tests・0.94s・2026-07-28・Phase 1 後半完遂で +17件追加・M1 マイルストーン達成)**

### Phase 2: 統計分析
- **変更対象**: `analysis_main.py`, `analysis_event_study.py`, `analysis_replication.py`, `analysis_confounders.py`, `tests/test_analysis.py`, `plots.py`, `requirements.txt`
- **ブリーフ**: 順位ベース (順序 logit) 主モデル + 舟橋2016 再現 + 2012-2022 拡張 (Deviation #3 で 2024→2022 短縮) + event-study 2層設計 + Csurilla型交絡変数統制
- **★Phase 2 着手前セットアップタスク** (2026-07-28 初見テスト指摘 Medium #2 反映):
  - [x] **完遂 (2026-07-28・Deviation #4)** `requirements.txt` に statsmodels==0.14.6 + scipy==1.18.0 + patsy==1.0.2 追加 + pip install 完了 (venv 更新済・pytest 210 all passing)
- **★Subj_i (主観判定競技ダミー) の主モデルへの組込方針 = Phase 2 着手前の設計判断 TODO** (2026-07-28 初見テスト指摘 High #1 反映):
  - **問題**: 現在の主 panel (`build_ranking_panel()` の 7332行・列 = pref/kai/year/cup/rank/is_host/is_special/cancelled) には**競技次元 (sport) が無い**。`sport_classifier.py` は panel_builder から未 import。Subj_i (Balmer2003 主観判定ダミー) を交互作用項 β3·Host_it×Subj_i に組み込むためには、47県×年×競技 の 3次元 panel が必要
  - **競技×県×年の内訳データ実態**: (a) JSPO PDF 58-67回 (2003-2012) = 47県総合順位/得点のみで**競技別内訳なし** (b) 78+79回 xls (2024+2025) のみ 47県×37競技の**完全内訳あり** (Deviation #1) (c) 長野 game_score = 長野1県×2016-2024 の**単県時系列のみ** (d) 剣道岩手 2016 = 単競技×単年 1点
  - **設計選択肢** (Phase 2 着手時に判断):
    - **選択肢A (Cross-section限定)**: 交互作用項推定は 2024佐賀+2025滋賀の 2年断面 (2×47×37=3478 obs) のみで実施・主モデル (順序 logit) は総合順位で Host のみを主推定・Subj_i は副次分析専用。**利点**: データ実態と整合・二重使用回避 / **欠点**: β3 の統計パワー低い (2年のみ)・year FE 実質不可
    - **選択肢B (競技別 panel 別途構築)**: 長野 game_score から長野1県×2016-2024 の競技別 panel を作成し、47県拡張は 2024+2025 の内訳データで補完 (imputation)。**利点**: 期間長い / **欠点**: 長野1県 imputation は Balmer2003 の identification 前提から外れる・査読で刺されるリスク大
    - **選択肢C (2024+2025 の event-study 内)**: post-2016 5ショックの内 2024佐賀 (host敗北) を treatment 直近サンプルとして扱い、Subj_i×Host の交互作用を event-study 内で推定
  - **推奨**: **選択肢A** = Cross-section限定 + main model は総合順位 Host のみ (Balmer2003 は 26大会 host-year を単純OLS で分析している前例あり・「主観 vs 客観分離」は 2024+2025 断面の副次分析で十分 novelty 主張可)
  - **依存**: 選択肢確定まで `analysis_main.py` の交互作用項 (下記 β3 タスク) は着手不可
- **★Phase 1 中盤で追加した5関数の Phase 2 での組込方針** (2026-07-28 明記):
  - `load_kendo_2016_iwate()` = **Discussion 章の事例言及** (主観判定競技で host effect 残存の実データ 1点・岩手 144点)。順序 logit 主モデルには組込まない (単年+単競技でサンプル過小)
  - `load_nagano_game_score()` = **Phase 2 副次分析** (`analysis_nagano_time_series.py` を新規追加候補)。長野1県時系列2016-2025で主観/客観競技別の得点推移を確認・主モデルとは独立
  - `load_jfa_soccer_history()` / `load_jihf_hockey()` = **Discussion 章の客観リファレンス** (「サッカー・アイスホッケー単競技では優勝は開催地に集中しない」の一般傾向確認)。主モデル panel には merge しない
  - `load_jspo_kai_pdf()` (58-67回) = **主モデル 47県×大会年 panel の骨格データ** (`panel_builder.py` に組込・total_score 列として merge)。舟橋2016 再現 (2003-2011) と 2012年 (第67回) 拡張のコアデータ
  - `load_jspo_kai_xls()` (78+79回) = **Phase 2 副次分析** (`analysis_cross_section_2024_2025.py`) 専用
- [x] `analysis_main.py`: 順位ベース (順序 logit) 主モデル実装 (statsmodels `OrderedModel`) = **完遂 (2026-07-28・Phase 2 前半・Deviation #4)**・主要結果 ordered_pooled coef_is_host=-13.73 (p<0.001)
- [x] `analysis_main.py`: 都道府県 FE + 年 FE の実装 = **完遂 (2026-07-28・ordered_prefFE_yearFE + logit_top1_prefFE_yearFE)**
- [~] `analysis_main.py`: Host × Subj 交互作用項 (β3) の推定・95%CI・p値 = **選択肢A採用で cross_section へ移管** (2026-07-28・Deviation #4 + #6)・主モデルは総合順位 Host のみ・Subj×Host は `analysis_cross_section_2024_2025.py` 側で 6991 obs で推定 (**coef=+16.68 p=0.031**)
- [x] `analysis_replication.py`: 舟橋2016 (2003-2011) 再現 (pref FE + year FE OLS・DV = score) = **完遂 (2026-07-28・Deviation #7)**・funahashi_base coef_host=**+1575.45** (SE=57.6・p<0.001・R²=0.939) → 舟橋 base spec +1674.65 に対し **誤差 5.9%** (controls 抜き simple spec)
- [~] `analysis_replication.py`: 2012-2024 拡張推定 = **+1年 (2012) のみ完遂 (extended_2003_2012 coef=+1604.36)**・2013-2022 は JSPO PDF 68-77 が 404/画像 PDF で取得不能 (Deviation #2) → 順位 DV 順序 logit 主モデル (`analysis_main.py`) で代替済 (n_obs=423)・Limitations 明記対応
- [x] `analysis_event_study.py`: event-study **Layer 1** (2002 高知単独・ふるさと選手制度前) = **完遂 (2026-07-28・Phase 2 前半・LP model)**
- [x] `analysis_event_study.py`: event-study **Layer 2** (post-2016 5ショック) = **完遂 (2026-07-28・stacked)**
- [x] `analysis_event_study.py`: parallel trend 検定 (pre-shock 期間のダミー係数が有意にゼロと異ならないか) = **完遂 (2026-07-28・Wald test)**
- [x] `analysis_confounders.py`: Csurilla型交絡統制 (人口対数 + 県内 GDP 対数) 段階投入 Robustness check = **完遂 (2026-07-28・M1-M5 5モデル)**
- [ ] `analysis_confounders.py`: GDP 系列 2 窓分離 (2012-2024 主推定 + 2003-2011 副次比較)
- [x] **(Phase 9 補遺 → Deviation #1 で範囲拡張)** `analysis_cross_section_2024_2025.py`: **2024佐賀 → 2025滋賀 2年断面比較 (host推移)** の素点ベース副次分析 = **完遂 (2026-07-28・Phase 2 後半・Deviation #6)**・6991 obs (47県×41競技×2年×2杯 stack)・**主要結果 baseline coef_is_host=+16.60 (p<0.001) + coef_host×subj=+16.68 (p=0.031)** = **主観判定競技で host effect が有意に大きい (Balmer2003 novelty 検証成功)**・descriptive_by_category で subjective host boost +37.9点 vs objective +17.6点 vs semi +26.2点で3分類中最大
- [x] `plots.py`: Figure 1 (開催地優勝率の時系列・6ショック年マーカー付き) = **完遂 (2026-07-28・Deviation #7)**・PNG+PDF 出力
- [x] `plots.py`: Figure 2 (3 分類 host bias 係数比較・エラーバー・n_host 注記) = **完遂**・objective +17.6 / semi +26.2 / subjective +37.9
- [x] `plots.py`: Figure 3 (event-study 2層 Layer1 2002単独 + Layer2 post-2016 stacked の τ プロット) = **完遂**
- [x] `plots.py`: Figure 4 (Csurilla型 M1→M5 host effect 減衰トレイル) = **完遂**
- [x] `plots.py`: Figure 5 (舟橋2016 再現 3 モデル比較 + 舟橋 reference 縦線) = **完遂**
- [x] `tests/test_analysis_{main,confounders,event_study,cross_section_2024_2025}.py`: 順序 logit + event-study + cross_section の数値整合性テスト = **完遂 (2026-07-28・4分割・main 17 + confounders 10 + event_study 13 + cross_section 21 = 61 tests・全体 231 all passing)**
- [x] pytest 全パス = **259 all passing (2026-07-28・Deviation #7)** (231 → +28: replication 19 + plots 9)
- [ ] 結果テーブルを `results/*.txt` に出力 → Phase 3 執筆時に必要になったら実装 (現状 Python REPL で `run_*_models()` で表示可能)

### Phase 3: 英語論文執筆 + PDF 初版
- **変更対象**: `manuscript.md`, `references/`, `LITERATURE.md`, `pdf/kokutai-v1.pdf`
- **ブリーフ**: 英語で manuscript.md を執筆し、PDF v1 を生成。pdftotext 自己 QA 100% を asura-monju/GPT 査読前に完遂
- [ ] `LITERATURE.md` 新規作成 (PHASE8-INVESTIGATION.md Part 2 を LITERATURE.md 形式に再構成)
- [ ] Title (英語・シリーズ既存4本のトーン踏襲)
- [ ] Abstract (構造化抄録・Background/Methods/Results/Conclusions)
- [ ] Introduction: 舟橋2016 + Balmer2003 の gap 明示 (主観 vs 客観分離検証なし) + 韓国 KSOC 20%加算 + 千葉1987 の5要因中「審判/ジャッジ言及ゼロ」の指摘
- [ ] Methods: データソース + 順位ベース (順序 logit) + 交互作用項 + event-study 2層 + Csurilla型統制
- [ ] Results: 主モデル + 舟橋再現 + 2012-2024 拡張 + event-study 2層 + Robustness check
- [ ] Discussion: 主観 vs 客観分離の novelty + 2016 以降の構造変化 (2クラスター) + **東アジア国際比較 2本立て** (韓国 KSOC 20%加算傍証 + 中国 兰彤2012 の host effect 5特徴分類 [高效性/渐增性/延迟性/排他性/双刃性] を Low-Medium confidence で紹介・本論の主観 vs 客観分離検証は排他性・双刃性の内訳を実証的に分解する試みとして位置付ける) + 末次2025「インチキ」「開催地優勝至上主義」批判との棲み分け
- [ ] Limitations 6点必須列挙: (1) 素点ベース非公開 (順位ベースで代替) (2) 審判員名簿不在 (主軸②落とし) (3) 剣道以外の主観競技データ限定的 (4) 末次論文本文未達 (5) **ESRI 令和4年度版 (2011-2022) の期間外のため舟橋 replication は controls 抜き simple spec で誤差 5.9% 近似再現** (Deviation #7) (6) **cross_section は 2 年断面 window (2024佐賀+2025滋賀) の小ささで year FE 実質 1 dummy** (Deviation #6)
- [ ] References: 全先行研究 + 書誌訂正2件 (舟橋2016 + Csurilla2023) を正しく記載
- [ ] PDF v1 生成 = **weasyprint** (先行4本 [厄年/六曜/五月病/満月] と統一・generate_pdf.py テンプレ流用可)
- [ ] `pdftotext -layout pdf/kokutai-v1.pdf` で全ページ抽出 → 目視 100% ([[feedback-paper-pdf-selfqa-before-gpt]])
- [ ] レイアウト崩れ・書誌欠落・図表参照ズレを潰す

### Phase 4: レビュー・査読サイクル
- **変更対象**: `manuscript.md`, `pdf/kokutai-vN.pdf`, `REVIEW-REPORT.md`
- **ブリーフ**: asura-monju round-1 + GPT 査読 V1-Vn 反復・Accept 到達まで

#### ★PDF体裁QAチェックリスト運用ルール (v5 サイクルから適用・2026-07-30 確立)
各サイクル後 (build 直後・GPT 送信前) に **14 項目チェックリスト全 PASS 必須**。1 件でも FAIL なら回帰・GPT / asura-monju 送信禁止。真実源=`feedback-paper-pdf-selfqa-before-gpt`。運用版=`handoff-kokutai-home-advantage.md` Phase C 節。契機=v4 References 番号浮き行見逃し事案 (pdftotext -layout で 30+ 件検出可・GPT round-3 で最優先指摘)。

- [x] asura-monju round-1 実施 (阿修羅3体 + 文殊検証) — v3 で完遂
- [x] asura-monju 指摘事項を manuscript.md に反映 → V2 生成 + pdftotext 自己 QA — v3→v4 で完遂 (M12 ハルシネ格下げ + 33 items 全消化)
- [x] GPT 査読 round-1 実施 (V2 → 指摘事項 → V3) — 完遂
- [x] GPT 査読 round-2 実施 (V3 → 指摘事項 → V4) — 完遂
- [x] GPT 査読 round-3 実施 (V4 → 「SSRN OK / 査読誌 Minor-Moderate revision」判定 + 5 必修 + 2 追加) — 完遂 (2026-07-30 深夜)
- [ ] **v5 サイクル (10 タスク・v5-T1〜T10)**: システム化 + round-3 消化 + PDF体裁QAチェックリスト全 PASS — **T1-T8 完遂 (2026-07-30・kokutai 8 commits・HEAD `cf3983f`・round-3 6/7 finding 消化・pytest 312)**・残 T9 GitHub URL 埋込 (瑞樹 v5 実施確定) + T10 Phase C build + 14 項目全 PASS
- [ ] GPT 査読 round-4 実施 (v5 → Accept 判定目標)
- [ ] Accept 確定まで反復 (friday13th は V1→V10 で 9 サイクル反復・[[feedback-paper-precision-over-effort]])
- [ ] 各サイクル後に PDF 生成 + **PDF体裁QAチェックリスト全 14 項目 PASS 確認** + REVIEW-REPORT.md 更新

### Phase 5: SSRN 投稿 + POSTED 到達
- **変更対象**: `SUBMISSION-GUIDE.html`, handoff/index/brainstorm 4ファイル
- **ブリーフ**: SSRN 投稿ガイド HTML (gogatsubyo/満月統一フォーマット) を作成し、瑞樹手動投稿 → SUBMITTED → POSTED
- [ ] SSRN 投稿ガイド HTML 作成 (gogatsubyo/満月統一フォーマット・コピーボタン付き)
- [ ] Abstract / Keywords / JEL Codes を投稿ガイドに転記
- [ ] 瑞樹手動投稿 → SUBMITTED (Abstract ID 取得)
- [ ] POSTED メール受領 → Abstract ID + URL 確定
- [ ] handoff-kokutai-home-advantage.md 更新 (状態: POSTED 到達)
- [ ] handoff-paper-brainstorm.md 第8弾ブロック更新 (POSTED 反映)
- [ ] handoff-index.md 更新
- [ ] MEMORY.md (max-plan / -Users-mizukishirai 両方) 索引更新

---

## リスク / Trade-offs

| リスク | 対策 |
|---|---|
| JSPO 692p PDF テキスト抽出困難 | `pdftotext -layout` + `pdfplumber` の2手法併用。手入力フォールバックも視野 |
| 剣道以外の主観判定競技データが公開範囲外 | 剣道単競技での主観判定分析でも novelty 維持 (Balmer2003 の主観客観分離初適用)。Limitations で明記 |
| GDP 系列 SNA 基準改定で 2003-2011 と 2012-2024 の係数比較不能 | Phase 8 H-04 決定通り 2 窓分離 (2012-2024 主推定 + 2003-2011 副次比較) |
| event-study parallel trend 前提崩壊 | Phase 8 H-03 決定通り pre-2005 (2002高知単独) + post-2016 (5ショック) の2層設計で各層内 parallel trend 保持 |
| 兰彤2012 本文 (フルテキスト) 未取得のため詳細主張不可 | アブスト範囲 (5特徴の分類 + 一般的主張) のみ引用・具体的統計モデル/係数/交絡統制の有無等の詳細主張は禁止 (Phase 9 補遺で書誌+アブスト+5特徴取得済み) |
| ~~第79回 (2025滋賀) 以外の年度で `_score_deta.xls` 型競技別内訳 xls の公開状況が未確認~~ (**解消済 2026-07-27 深夜**) | Phase 1 冒頭タスク完遂 = 第78回2024佐賀 + 第79回2025滋賀の**2年**で発見 (第58-77回ゼロ確定・詳細 `PLAN-DEVIATIONS.md#deviation-1`)。副次分析は単年断面 → 2年断面比較 (host推移) に拡張 |
| 末次論文本文未達で先行研究比較が不十分と査読指摘 | 書誌+CiNii リンクレベル引用 + タイトル/件名標目からの間接引用で対応 (Discussion 章「本論は全競技パネル定量分析で棲み分け」) |
| GPT 査読サイクルが 10 ラウンド以上に及ぶ | friday13th は V1→V10 で SSRN SUBMITTED 到達実績あり・工数見積り増を許容 |
| JSPO 個別回 PDF 第68-77回 (2013-2022 拡張期間 10回分) は画像PDF or 404 で抽出困難 (**Phase 1 中盤 2026-07-28 確定**) | Phase 2 で OCR 検討 (工数評価要)・順位ベース主モデルは長野 high_rank.html (第3-79回1-8位) で完全カバー済のため実質影響なし |
| asura-monju レビューで論文構造 (主軸縮小反映) の指摘 | Phase 8 決定事項7項目を PLAN 冒頭に反映済み・レビュー投入前に PLAN 準拠チェック実施 |
| ESRI 令和5年度版 (2023データ含む) 未公表 (**Phase 1 後半 2026-07-28 確定**)・現行主推定は 2012-2022 の 11年 | 公表され次第 `main_2023.html` を追加取得 → data_loader の `refs_dir` 引数で切替・分析コード再訓練で 2012-2023 (12年) or 2012-2024 (13年) に拡張可 (Deviation #3 参照) |

## 工数見積り

| Phase | 内容 | 工数 |
|---|---|---|
| Phase 9-補遺 | xls 確認 + 兰彤アブスト試行 | 0.5 日 |
| Phase 1 | データ取得 + パネル構築 | 3-5 日 (JSPO 82件スクレイピング + PDF 変換が最大コスト) |
| Phase 2 | 統計分析 | 2-3 日 (順序 logit + event-study 2層 + Csurilla型統制) |
| Phase 3 | 英語論文執筆 + PDF v1 | 3-5 日 |
| Phase 4 | レビューサイクル | 3-5 日 (friday13th 実績で V1-V10・9ラウンド反復想定) |
| Phase 5 | SSRN 投稿 | 1-2 日 |
| **合計** | | **約 12-20 日** |

---

## 段取り八分フェーズ対応表

| PLAN Phase | 段取り八分 Phase | 補足 |
|---|---|---|
| Phase 0 (Phase 8 で実質完了) | Phase 8 (本格調査) | PHASE8-INVESTIGATION.md 参照 |
| 本 PLAN 起票 (現時点) | Phase 9 (本計画立案) | 現フェーズ |
| Phase 9-補遺 | Phase 9 (本計画立案) の補遺 | PLAN 起票後・Phase 1 着手前に xls + 兰彤アブスト最後の詰め |
| Phase 1-3 | Phase 10 (実装) | データ取得 + 分析 + 執筆 |
| Phase 4 | Phase 11 (チェック) | レビューサイクル |
| Phase 5 | Phase 12-16 相当 | SSRN 投稿 (英語論文プロジェクトは STG/PROD 概念なし・POSTED = PROD 展開に相当) |

---

## 関連ファイル

- **Phase 8 成果物**: `~/claude/analysis/kokutai-home-advantage/PHASE8-INVESTIGATION.md`
- **handoff (主)**: `~/.claude/projects/-Users-mizukishirai/memory/handoff-kokutai-home-advantage.md`
- **handoff (brainstorm)**: `~/.claude/projects/-Users-mizukishirai/memory/handoff-paper-brainstorm.md` 第8弾ブロック
- **handoff (index)**: `~/.claude/projects/-Users-mizukishirai/memory/handoff-index.md`
- **参考先行 PLAN**: `~/claude/analysis/rokuyo-birth/PLAN.md` (パネル+SSRN 構造) + `~/claude/analysis/friday13th/PLAN.md` (GPT 査読サイクル運用実績)
