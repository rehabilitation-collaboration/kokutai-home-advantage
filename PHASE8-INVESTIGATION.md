# Phase 8 本格調査 統合サマリ

## メタ情報
- **プロジェクト**: 論文シリーズ第8弾「国民体育大会×開催地優勝バイアス」(英語論文 SSRN 投稿)
- **実施日**: 2026-07-27
- **手法**: kerberos 3体並列 (Sonnet fan-out) + hades 検証 (Opus)
  - kerberos A系 = データ入手可能性 (subagent_tokens 141675)
  - kerberos B系 = 先行研究一次確認 (subagent_tokens 210307)
  - kerberos C系 = 統計手法詳細設計 (subagent_tokens 171800)
  - hades = 原典突合検証 (subagent_tokens 101527)
- **関連 handoff**: `~/.claude/projects/-Users-mizukishirai/memory/handoff-kokutai-home-advantage.md`
- **プロジェクトディレクトリ**: `~/claude/analysis/kokutai-home-advantage/` (Phase 8 前倒しで新規作成)

---

## TL;DR

### 分岐条件発火状況 (最重要)
- **発火①**: 主軸① 素点ベース分析実質不可能 → **順位ベース (順序 logit) ピボット必須**
- **発火②**: 主軸② 審判員名簿 (氏名+所属都道府県) 不在 → **C判定・主軸落とし推奨**
- **発火なし**: 舟橋2016 は主観 vs 客観分離検証を行っていない (Balmer2001のみ引用・2003非引用) → 本論の novelty は維持

### 書誌誤り2件確定 (チェックリスト即時修正必須)
- **舟橋2016**: 実際は「舟橋弘晃・**日比野幹生・石黒えみ**・間野義之 (2016) 『国民体育大会総合成績の決定要因：都道府県別パネルデータによる計量分析』**スポーツマネジメント研究** 8(1), pp.**17-33**」DOI 10.5225/jjsm.2016-002
  - チェックリスト旧記載 (松永敬子・体育経営管理学研究 3(1) 15-28) は完全誤り
- **Csurilla2023**: 実際は **Csurilla, G. and Fertő, I.** の2名共著 (Molnár, Ledenyák は幻)

### 「2016年5連覇仮説」棄却
- 2018福井 (福井2896点/東京2246点) と 2019茨城 (茨城2569点/東京2217点) で開催地優勝
- 開催地敗北年は 2002/2016/2017/2022/2023/2024 の**6ショック**
- 単一の post-2016 DID 不可 → **event-study 型 (2層設計)** への切替推奨

---

## Part 1: kerberos A系 (データ入手可能性)

### A-1 JSPO tabid183 index の全リンク抽出 (83件)
- 第1回〜第80回 + 特別大会 + 特別国体 = 83件のマッピング完了
- 命名規則は予測不能 (連番でない)
- 詳細マッピング表は kerberos A return value 参照

### A-2 JSPO 個別回ページの実態 (7点サンプリング)
| 回 | 開催 | tabid | 掲載PDF |
|---|---|---|---|
| 40 | 1985鳥取 | 709 | なし |
| 58 | 2003静岡 | 691 | 58_tennou.pdf + 58_kougou.pdf のみ |
| 65 | 2010千葉 | 684 | 65_tennou.pdf + 65_kougou.pdf のみ |
| 71 | 2016岩手 | 1101 | 2016seiseki2.pdf (統合) |
| 73 | 2018福井 | 1215 | 73hukuisougouseiseki.pdf |
| 79 | 2025滋賀 | 1462 | 79_score_all.pdf + score.pdf + score_women.pdf + 2 xls |
| 80 | 2026青森 | 1476 | 冬季のみ (本大会未実施) |

**確認パターン (2003-2025 の22年間で一貫)**: JSPO中央サイトは常に「天皇杯・皇后杯総合順位/得点のみ」。**競技別得点内訳PDFは一度も発見できず**。審判員関連も皆無。

### A-3 審判員属性の公開範囲
- JSPO 諸規程集約 tabid188 精読
- 該当2件のみ: 「競技役員編成基準」「役職名及び人数」
- タイトル文言自体が個人名簿でなく組織構造・員数の標準を示唆
- **4系統独立確認 (JSPO規程/JSPO個別回5点/剣道最詳細/広範WebSearch) が全て否定的**
- 個人名+所属都道府県の審判員名簿は本調査で発見できず

### A-4 長野県体協 (Positive finding)
- game_score.html「国スポ (国体) 競技別得点」= 実在確認
- ただし **長野県単独のみ×2016年以降9年分のみ** (2003年まで遡らず・47都道府県比較には別途46県分探索必須)

### A-5 競技団体別歴代アーカイブ
- **客観競技 (リファレンス役)**: JFA (勝敗/順位のみ・得点なし) / JIHF (2012年で更新停止)
- **主観競技**: 剣道 old2.kendo.or.jp で **2016年 (第71回) 岩手のみ**「競技得点/参加得点/合計得点」表を発見・2022年 (第77回) 栃木の同形式は消失
- 柔道: 全柔連公式にアーカイブなし
- 体操/卓球: 接続不可 or 未検証

### A-6 JSPO 692p PDF
- URL: https://www.japan-sports.or.jp/Portals/0/images/archives/01_kokutai.pdf
- 第1-65回 (2010まで) 収録
- WebFetch でテキスト抽出不可 (Phase 9 で pdftotext 必須)

### Phase 8 データ入手可能性判定
- **主軸①**: **B (分析可能な範囲で実施可) ただし素点ベースはC寄り**
  - 従属変数を「競技得点(連続値)」→「順位/入賞可否(順序/二値)」に組み替えれば実施可能性大幅向上
- **主軸②**: **C (データ不足で主軸落とし推奨)**
  - ただし47都道府県×全競技悉皆確認ではないため「存在しない証明」ではなく「Not found」

### Phase 9 実装への次アクション (A系)
1. JSPO 79回 xls (`79_score_all_data.xls`) 実物開封 (競技別内訳の可能性残存)
2. 体操 (jpn-gym.or.jp) 再接続試行 (別ツール経由)
3. 剣道の得点表2016→2022消失原因特定
4. 長野以外の都道府県サイト横断サンプリング (5-10県)

---

## Part 2: kerberos B系 (先行研究一次確認)

### B-1 舟橋2016 本文精読 (最重要・分岐条件判定)

**分岐条件は発火なし**。舟橋2016 は主観 vs 客観分離検証を**行っていない**ことを本文精読で確認。

**発見された書誌エラー**:
- 実際の書誌 = 舟橋弘晃・日比野幹生・石黒えみ・間野義之 (2016)「国民体育大会総合成績の決定要因：都道府県別パネルデータによる計量分析」スポーツマネジメント研究 8(1) pp.17-33
- Balmer引用は**1箇所のみ (p.20)**: 「開催効果」の6理由 (①予算増/②開催国枠/③練習環境/④地元応援/**⑤採点競技の地元有利判定**/⑥時差気候距離) を **Balmer et al. 2001; Bernard and Busse 2004; Shibli et al. 2012** の3文献で一括引用 (Balmer 2003 は非引用)
- 従属変数 = Tpoint (男女総合競技得点) 単一
- 独立変数リスト = lnPopulation, Headoffice, Host t-7〜t+7 (15ダミー), Furusato, NSpeciality, Participants
- **交互作用項ゼロ・主観/客観競技のグルーピング変数不在**
- パネル = 47都道府県 × 9年 (2003-2011) n=423 完全バランス
- Discussion「今後の課題」7項目に主観/客観分離への言及ゼロ

### B-2 末次美樹2024/2025 (書誌のみ確認)
- 末次美樹 (駒澤大学、専門=空手道) 著
- 2024年紀要 = 「国民体育大会『空手道競技』の大会成績から見える課題」駒澤大学総合教育研究部紀要18, pp.137-153
- 2025年紀要 = 「国民体育大会 空手道競技の課題の可視化と構造原理の解明」駒澤大学総合教育研究部紀要19, pp.103-117, DOI 10.69200/0002033886
- **本文PDF は WEKO3 octet-stream 配信で抽出不能** (Phase 9 で熊大リポジトリ司書 or 著者直接 email での取得試行推奨)
- 「インチキ」「開催地優勝至上主義」等の批判的フレーミングはタイトル/件名標目から確認

### B-3 韓国KSOC 20%加算規程 (Medium confidence)
- 大韓体育会 (KSOC) 全国体育大会に開催地20%加算規程が実在
- 2001年 10% 開始 → 2010年 20% に引上げ → 現在まで維持
- 根拠規定 = 「全国綜合体育大会規定」(2023年9月11日一部改正)・国家法令情報センター登録
- 一次資料 = 문화일보 2025-10-13 김태형記者記事 https://v.daum.net/v/20251013192536045
- **hades 追認で High confidence に格上げ可能**

### B-4 中国 兰彤2012 沈阳体育学院学报
- kerberos B は参考网+総目次で High confidence 判定
- **hades 再検索で1次原典未到達** → **Low confidence に降格推奨** (Phase 9 で CNKI アカウント経由再検索 or 代替引用に切替)
- 発見された書誌: 兰彤・于晓光 共著「全运会东道主效应特征的理论和实证研究」沈阳体育学院学报 31(4), pp.1-5

### B-5 Csurilla2023 本文取得 (PMC 全文)

**発見された書誌エラー**: 著者は **Csurilla, G. と Fertő, I. の2名のみ** (Molnár, Ledenyák は幻)

- Csurilla & Fertő (2023) "The less obvious effect of hosting the Olympics on sporting performance" Scientific Reports 13:819, DOI 10.1038/s41598-022-27259-8
- PMC全文: https://pmc.ncbi.nlm.nih.gov/articles/PMC9895060/
- **統制変数**: GDP per capita (購買力平価対数), 人口 (対数), 共産圏ダミー
- **Host効果係数の減衰**: 合計メダル 0.467→0.257 (約45%減衰) / 男性 0.473→0.279 (約41%減) / 女性 0.415→0.198 (約52%減)
- **完全消滅ではなく大幅減衰** (プールモデルでは*** 有意残存)
- 国別個別ダミー切替で「大半の有意結果消滅」・オーストラリア2000と英国2012のみ有意維持

### B-6 千葉1987 + Balmer2003 骨子再確認
- **千葉1987** (DOI 10.20693/jspeconf.38a.0_204): 開催県優勝の5要因分析
  1. フルエントリー制
  2. 組み合わせの不公平 (自ら「実体は見当たらない」と否定)
  3. 移入選手の活躍
  4. 県内選手の強化
  5. 県民挙げての支援
  **審判・ジャッジによる作為には一切言及なし**
- **Balmer2003** (PubMed 12846534): 1896-1996年夏季五輪5競技群 (客観=陸上/重量挙げ, 主観=ボクシング/体操, 準主観=団体競技) を比較・主観判定群で有意なhome advantage検出

### Phase 8 先行研究 novelty 判定
- **主軸①主観vs客観分離**: **維持** (国体データへの体系的分離検証は先行研究ゼロ)
- **主軸②採点員属性**: 維持 (推定・先行研究側は Zitzewitz2006 で確立)
- **主軸③2012-2024拡張**: 維持 (舟橋2016 は 2003-2011 のみ)
- **主軸⑤英語投稿**: 維持 (国体英語論文は本調査で発見できず)

---

## Part 3: kerberos C系 (統計手法詳細設計)

### C-1 Balmer2003型交互作用モデル
- Balmer, Nevill & Williams (2003) J Sports Sci 21(6):469-478
- DV = 勝利ポイント比率・二項分布応答変数の GLM interactive modeling
- 5イベント群 (客観/主観/準主観) の比較
- **フルテキストは Taylor & Francis 有料壁** → 概念的再現に留める (原論文数式の逐語複製は不可)
- Balmer2005 派生 (ボクシング, J Sports Sci 23:409-416) は同一競技内で判定タイプが客観→主観に連続変化する設計 → 国体の採点競技分析に直接応用可
- **Balmer 2005 dance/skating は誤り**・正しくは Balmer2001 Winter Olympics (J Sports Sci 19:129-139)

### C-2 政策DID 介入点候補の妥当性

| 年 | 介入 | 検証結果 |
|---|---|---|
| **2005** | ふるさと選手制度導入 (第60回国体冬季大会スケート競技会から) | **High confidence** JSPO公式規程PDF `jg_kitei_08.pdf` で確認 |
| **2011** | 居住実態半数超基準明文化 | Medium confidence (JSPO一次規程未到達・複数体協解説ページ合成) |
| **2018** | スポーツ基本法改正 | 存在確認 High / host bias 関連条項の実質性 Low |
| **2016** | 東京5連覇構造変化仮説 | **棄却** (下記 C-2-04 参照) |

### C-2-04 「2016年5連覇仮説」棄却の詳細

**タスク前提の修正**:

| 年 | 開催地 | 結果 |
|---|---|---|
| 2013 | 東京 | 東京優勝 (開催地優勝) |
| 2014 | 長崎 | 開催地優勝 |
| 2015 | 和歌山 | 開催地優勝 |
| 2016 | 岩手 | **東京優勝 (開催地敗北・1回目)** |
| 2017 | 愛媛 | **東京優勝 (2回目・2年連続)** |
| **2018** | **福井** | **福井優勝 (開催地優勝・連続性途切れ)** |
| **2019** | **茨城** | **茨城優勝 (開催地優勝)** |
| 2020 | 鹿児島 | COVID中止 (2023特別大会に延期) |
| 2021 | 三重 | COVID中止 |
| 2022 | 栃木 | **東京優勝 (開催地敗北)** |
| 2023 | 鹿児島 (特別) | **東京優勝 (2年連続)** |
| 2024 | 佐賀 | **東京優勝 (3年連続・18度目)** |
| 2025 | 滋賀 | 滋賀優勝 (開催地優勝) |

- 開催地敗北年 = **6回** (2002高知, 2016岩手, 2017愛媛, 2022栃木, 2023鹿児島特別, 2024佐賀)
- 2016-17 (2年) と 2022-24 (3年) の**2クラスターに分断**
- 間の2018-19年は通常通り開催地優勝 (フルエントリー制の効果継続)
- **代替案 (推奨)**:
  - (a) event-study 型で6ショック年を個別ダミー化
  - (b) 東京の人口規模を連続変数として統制し「東京超大型都市効果」として再解釈
  - hades 深掘り H-03: pre-2005 (2002高知単独) と post-2016 (2016-2024の5ショック) の2層設計

### C-3 観客効果 natural experiment (**実装困難**)
- 2020鹿児島 = **全面中止** (無観客開催ではない)
- 2021三重 = **全面中止**
- 2023特別大会 = 通常有観客開催 (2023-05-08 5類移行後の10月開催)
- **国体パネル内では観客効果自然実験不可能** → Discussion 章で日本他競技傍証 (Nomura2022 J1無観客SEM) として引用のみ

### C-4 交絡変数統制データソース

| データ | ソース | カバー範囲 |
|---|---|---|
| 都道府県別人口 | 総務省 e-Stat「人口推計 長期時系列データ」 | 1920-2020 (High confidence) |
| 県内GDP | 内閣府 ESRI 県民経済計算 | 1955〜 (SNA基準改定で単一連続系列接続不可) |
| スポーツ振興予算 (国) | 文科省/スポーツ庁 | 取得容易 |
| スポーツ振興予算 (都道府県) | 各都道府県予算書 | **統一フォーマット公開なし・47県×13年の手集計要** |
| 選手強化予算 (県体協) | 各県体育・スポーツ協会 | **バラバラ・実装困難** |

- hades 深掘り H-04: 2012-2024窓なら SNA同一基準内で接続可能・2003-2011舟橋再現部分とは断絶が発生する点に注意

### C-5 Csurilla型統制モデル
- ゼロ過剰負の二項モデル (zero-inflated negative binomial)
- 社会経済統制 (人口・企業本社数等) を主モデルに搭載
- Robustness check で C-4 変数を段階的投入

### C-6 副次② 追加手法 (審判員データ入手可能な場合のみ)
- Zitzewitz2006 (フィギュアスケート同郷バイアス・約0.45SD高採点)
- Sandberg2018 + 2023年馬場馬術論文 (Multivariable Linear Regression, DV=Total Dressage Score, 予測変数={Home, Same Nationality, Compatriot, FEI Ranking, Starting Order})
- **kerberos A系判定で主軸②は C (データ不足) → 本項目は主軸落としで対応**

---

## Part 4: hades 検証 verdict

### Part A: Kerberos Findings Verification

| # | Finding | Verdict | Notes |
|---|---|---|---|
| A-1 | 舟橋2016 書誌エラー確定 | **ACCEPT** | J-STAGE + PDF実物 p.17 目視で全一致 |
| A-2 | Csurilla2023 著者2名確定 | **ACCEPT** | PMC全文で Molnár/Ledenyák 不在 |
| A-3 | 舟橋2016 主観vs客観分離検証なし | **ACCEPT** | 独立ソース裏取り済 |
| A-4 | JSPO 審判員名簿不在 | **ACCEPT** | 独立精読で追認 |
| A-5 | 長野県体協 game_score.html 存在 | **PARTIAL** | ページ実在も長野1県時系列のみ (47県パネルとしては使えず) |
| A-6 | 剣道 old2 2016年得点表 | **ACCEPT** | 実在 |
| A-7 | 剣道 2022年得点表消失 | **ACCEPT** | 実在 |
| A-8 | JSPO 79回 xls 内訳なし | **PARTIAL/追加検証要** | xls実物未開封・Phase 9冒頭で確認要 |
| A-9 | 2018福井 開催地優勝 (2896/2246) | **ACCEPT** | 福井県公式ページで完全一致 |
| A-10 | 2022栃木 開催地敗北 (2436/2270.5) | **ACCEPT** | 栃木県公式ページで完全一致 |
| A-11 | 2019茨城 開催地優勝 (2569/2217) | **ACCEPT** | Wikipedia独立ソース |
| A-12 | 開催地敗北年 6件網羅 | **ACCEPT** | 独立ソース全件追認 |
| A-13 | Csurilla2023 減衰率 (0.467→0.257 約45%減) | **ACCEPT** | PMC Table 1 完全一致 |
| A-14 | 韓国 KSOC 20%加算 | **ACCEPT** | 문화일보直接記事で確認・High に格上げ可 |
| A-15 | 中国 兰彤2012 | **NOT VERIFIED** | hades でも1次原典到達不可・**High判定は撤回推奨・Low降格** |
| A-16 | 末次論文 本文取得不能 | **ACCEPT** | 独立試行で追認 |

### Part B: Hades 独自深掘り 6項目

| # | ID | Severity | Finding |
|---|---|---|---|
| B-1 | H-01 | **High** | 主軸① 順位ベースピボットは Balmer2003 定義との整合維持可能 (むしろ舟橋2016 の「Balmer2001-only 引用+分離検証ゼロ」を積極的な差別化点に据える推奨) |
| B-2 | H-02 | Medium | 副次案: JSPO「役職別人数」PDF は氏名なしの構造データとして利用可能 (Phase 9 で PDF 実物確認要) |
| B-3 | H-03 | Medium | event-study 6ショックは parallel trend 検証必須・2002高知は制度前(単独扱い) + 2016-2024の5ショックの**2層設計**推奨 |
| B-4 | H-04 | Low | 交絡変数 GDP 系列は 2012-2024 主推定 + 2003-2011 舟橋再現副次比較 の**2窓分離**推奨 |
| B-5 | H-05 | **High** | 未検証3件の SSRN 引用強度: 韓国=High格上げ / 中国=Low降格または代替 / 末次=Medium (熊大司書 or 著者直接 email) |
| B-6 | H-06 | Medium | 末次論文本文取得: 熊本大学リポジトリ司書経由の再試行が有効可能性 |

### Phase 2 False Positive 再発チェック
Phase 2 hades REJECT 2件 (「舟橋2016 審判バイアス言及ゼロ」「末次2025 審判バイアス言及なし」) と同型のエラーは本 Phase 8 検証では**発見されず**。ただし Phase 9 PLAN 起票時は precise 表現「言及はあるが実証仮説として分離検証していない」を使うこと。

---

## Part 5: 分岐条件発火状況の最終判定

handoff L86-90 の分岐条件と本 Phase 8 findings の照合:

| 分岐条件 (handoff) | 発火判定 | 対応 |
|---|---|---|
| Phase 8 で「競技別得点データ非公開で主観 vs 客観分離不可能」判明時 | **部分発火** | 素点ベースは実質不可能・**順位ベース (順序 logit) にピボット**で実施継続可 → **瑞樹相談必須** |
| 審判員属性データ (氏名・所属都道府県) 非公開時 | **発火** | 主軸②を完全に落として ①③⑤ の3本立てに → **瑞樹相談推奨** |
| Csurilla2023 本文「社会経済統制で host effect 消滅」が本当なら | **部分発火** | 完全消滅ではなく大幅減衰 (約45%) → **交絡変数統制モデル必須追加** |
| 末次2025 との差別化困難と判明 | 未発火 | 末次は空手道単競技の質的批判 vs 本論は全競技パネル定量分析で棲み分け可 |
| Phase 8 で舟橋2016 が既に類似分析済みと判明 | 未発火 | 主観/客観分離検証なし確定 (Balmer2001のみ引用・2003非引用) |

---

## Part 6: Phase 9 PLAN.md 起票時の決定事項リスト (hades 提示)

1. **書誌 2件即時修正** (最優先)
   - 舟橋2016 → 舟橋弘晃・日比野幹生・石黒えみ・間野義之 (2016)「国民体育大会総合成績の決定要因：都道府県別パネルデータによる計量分析」スポーツマネジメント研究 8(1) pp.17-33
   - Csurilla2023 → Csurilla, G. and Fertő, I. (2023) "The less obvious effect of hosting the Olympics on sporting performance" Scientific Reports 13:819
2. **主軸① を「順位ベース (順序 logit) 拡張案」に確定** (舟橋2016 の Balmer2001-only 引用を差別化点として「Balmer2003 の主観/客観分離を新規実装」で位置付け)
3. **主軸② を C 判定 (主軸落とし)**、副次案として「役職別人数」を Phase 9 で PDF 実物確認 (H-02)
4. **event-study を2層設計** (pre-2005 の 2002高知単独 + post-2016 の 5ショック)
5. **交絡変数 GDP 系列を2窓分離** (2012-2024 主推定 + 2003-2011 舟橋再現副次比較)
6. **未検証3件の SSRN 引用強度を再ランク付け** (韓=High格上げ/中=Low降格/末次=Medium司書ルート)
7. **A-8 JSPO 79回 xls 実物確認**を Phase 9 冒頭タスクに組込む

---

## Part 7: 瑞樹相談項目 (推奨案付き)

### 相談-1 【最重要】主軸① 順位ベースピボット確定

**現状**: ゴール宣誓 (Phase 4 祝福) では「舟橋2016 の素点ベースパネル再現+審判バイアス拡張」を想定。しかし kerberos A + hades で素点ベースは長野県1県時系列しかないと確定。

**推奨**: **順位ベース (順序 logit) にピボット**。舟橋2016 の Balmer2001-only 引用+分離検証ゼロを差別化点として「Balmer2003 の主観/客観分離を新規実装」で位置付け直す。

**ゴール宣誓への影響**: 「素点ベース」明示部分の書き換え必要 (ただし失敗判定「主観判定 vs 客観競技の分離検証がない」は維持可能・むしろ強化)。

### 相談-2 【重要】主軸② 完全落とし判断

**現状**: kerberos A + hades で審判員名簿 (氏名+所属都道府県) 不在確定 (4系統独立確認)。

**推奨**: **主軸②を完全にゴールから外し、①③⑤の3本立てに縮小**。H-02 副次案 (JSPO「役職別人数」PDF) は Phase 9 で PDF 実物確認できたら Discussion 章で言及する程度に留める (追加調査コスト vs リターン低)。

**ゴール宣誓への影響**: 「採点員属性 (副次)」節削除。

### 相談-3 【中位】中国 兰彤2012 の扱い

**現状**: kerberos B High confidence 判定 → hades 独自再検索で1次原典未到達・**Low 降格推奨**。

**推奨**: **Low 扱いで discussion 参考例言及のみ**。CNKI アカウント経由の再検索 or 代替引用への切替は Phase 9 の Optional (SSRN 投稿タイムラインとの兼合いで判断)。

### 相談-4 【中位】末次2024/2025 本文取得

**現状**: WEKO3 octet-stream で本文取得不能・ResearchGate/GoogleScholar キャッシュも不発。

**推奨**: **Phase 9 で熊本大学リポジトリ司書に直接問合せ** (Medium 優先度)。または著者 (末次美樹氏) への直接 email (研究倫理配慮要)。

---

## 引用元 URL リスト

### 一次データソース (JSPO)
- 過去大会概要 index: https://www.japan-sports.or.jp/kokutai/tabid183.html
- 諸規程集約: https://www.japan-sports.or.jp/kokutai/tabid188.html
- 692p PDF: https://www.japan-sports.or.jp/Portals/0/images/archives/01_kokutai.pdf
- 第79回 (滋賀) 個別回: https://www.japan-sports.or.jp/kokutai/tabid1462.html
- 第58回 天皇杯順位PDF: https://www.japan-sports.or.jp/Portals/0/data0/kokutai/58/58_tennou.pdf

### 都道府県公式
- 長野県体協: https://www.nagano-sports.or.jp/kokutai/record/high_rank.html
- 長野県体協 競技別得点: https://www.nagano-sports.or.jp/kokutai/record/game_score.html
- 第73回福井: https://info.pref.fukui.lg.jp/fukuikokutai2018/5NS18/performances_result.html
- 第77回栃木: https://www.pref.tochigi.lg.jp/tochigikokutai2022/kokutai/performances_result.html

### 競技団体
- JFA サッカー歴代: https://www.jfa.jp/match/nationalsportsfestival_2024/history.html
- JIHF アイスホッケー: https://www.jihf.or.jp/watching_games/tournament/detail.php?meet_id=6
- 剣道 old2 第71回: https://old2.kendo.or.jp/competition/kokutai/71st/result/
- 剣道 第77回: https://www.kendo.or.jp/competition/kokutai-77th/

### 主要先行研究
- 舟橋2016 J-STAGE: https://www.jstage.jst.go.jp/article/jjsm/8/1/8_2016-002/
- 千葉1987 J-STAGE: https://doi.org/10.20693/jspeconf.38a.0_204
- Csurilla2023 PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC9895060/
- Csurilla2023 Nature: https://www.nature.com/articles/s41598-022-27259-8
- Balmer2003 PubMed: https://pubmed.ncbi.nlm.nih.gov/12846534/
- Balmer2001 Winter Olympics PubMed: https://pubmed.ncbi.nlm.nih.gov/11217011/
- Nomura2022 Frontiers: https://www.frontiersin.org/articles/10.3389/fspor.2022.927774/full
- Zitzewitz2006 Wiley: https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1530-9134.2006.00092.x
- Sandberg2023 馬場馬術 MDPI: https://www.mdpi.com/2076-2615/13/17/2797

### 国際比較 (韓国/中国)
- 韓国KSOC 문화일보 2025-10-13: https://v.daum.net/v/20251013192536045
- 韓国 나무위키 전국체육대회: https://namu.wiki/w/전국체육대회

### Wikipedia (裏取り用・二次)
- 国民スポーツ大会: https://ja.wikipedia.org/wiki/国民スポーツ大会
- 第74回国民体育大会 (2019茨城): https://ja.wikipedia.org/wiki/第74回国民体育大会
- 第75回国民体育大会 (2020鹿児島COVID中止): https://ja.wikipedia.org/wiki/第75回国民体育大会

### 末次論文 (書誌のみ・本文未達)
- 末次2024 CiNii: https://cir.nii.ac.jp/crid/1390303254959134848
- 末次2025 CiNii: https://cir.nii.ac.jp/crid/1390022609604361344
- 末次2025 リポジトリ: https://komazawa-u.repo.nii.ac.jp/records/2033886
