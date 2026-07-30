"""data_loader.py の contract テスト (実データ against)"""

import pytest
import pandas as pd

from src.data_loader import (
    parse_japanese_era,
    load_nagano_high_rank,
    load_jspo_kai_xls,
    load_jspo_kai_pdf,
    load_kendo_2016_iwate,
    load_nagano_game_score,
    load_jfa_soccer_history,
    load_jihf_hockey,
    load_esri_soukatu,
    load_esri_population,
    load_esri_gdp_nominal,
    list_available_xls,
    list_available_jspo_pdfs,
    ESRI_DIR,
)


class TestEraParse:
    @pytest.mark.parametrize("era,expected", [
        ("R7", 2025), ("R6", 2024), ("R1", 2019),
        ("H30", 2018), ("H1", 1989),
        ("S24", 1949), ("S63", 1988),
    ])
    def test_parse(self, era, expected):
        assert parse_japanese_era(era) == expected

    def test_invalid_returns_none(self):
        assert parse_japanese_era("") is None
        assert parse_japanese_era("XX7") is None
        assert parse_japanese_era(None) is None


class TestNaganoHighRank:
    @pytest.fixture(scope="class")
    def df(self):
        return load_nagano_high_rank()

    def test_shape(self, df):
        # 第3-79回=77大会 + 特別大会1件 = 78大会 × 2杯 = 156レコード
        assert df.shape == (156, 14)

    def test_columns(self, df):
        assert list(df.columns) == [
            "kai_num", "is_special", "era_raw", "year", "host_raw", "cup",
            "rank1", "rank2", "rank3", "rank4", "rank5", "rank6", "rank7", "rank8",
        ]

    def test_cups_balanced(self, df):
        counts = df["cup"].value_counts().to_dict()
        assert counts["tennou"] == 78
        assert counts["kougou"] == 78

    def test_special_records(self, df):
        # 特別大会 (2023鹿児島) が天皇杯+皇后杯の2件
        assert df["is_special"].sum() == 2
        special = df[df.is_special & (df.cup == "tennou")].iloc[0]
        assert special.year == 2023
        assert special.host_raw == "鹿児島県"

    def test_79th_shiga_host_win(self, df):
        row = df[(df.kai_num == 79) & (df.cup == "tennou")].iloc[0]
        assert row.year == 2025
        assert row.rank1 == "滋賀"  # host優勝
        assert row.rank2 == "東京"

    def test_78th_saga_host_defeat(self, df):
        # 6ショック年の1つ = 佐賀 host敗北 (東京優勝・佐賀2位)
        row = df[(df.kai_num == 78) & (df.cup == "tennou")].iloc[0]
        assert row.year == 2024
        assert row.rank1 == "東京"
        assert row.rank2 == "佐賀"

    def test_oldest_kai_3(self, df):
        # 最古 (第3回1948福岡) が入ってる
        row = df[(df.kai_num == 3) & (df.cup == "tennou")].iloc[0]
        assert row.year == 1948
        assert row.host_raw == "福岡県"

    def test_kai_num_range(self, df):
        kai_set = set(int(k) for k in df["kai_num"].dropna())
        assert 3 in kai_set
        assert 79 in kai_set
        # 中止年 (75/76) もレコードは残る (順位表は掲載される)

    def test_third_kai_tennou_correct_ranks(self, df):
        # 第3回 tennou は「冬・夏・秋」統合行から rank1=東京 rank2=福岡
        row = df[(df.kai_num == 3) & (df.cup == "tennou")].iloc[0]
        assert row.rank1 == "東京"
        assert row.rank2 == "福岡"
        assert row.rank3 == "京都"

    def test_third_kai_kougou_no_season_leak(self, df):
        # 第3回 kougou は「冬・夏・秋」列を skip して rank1=京都 (旧パーサは rank1="冬・夏・秋" のバグ)
        row = df[(df.kai_num == 3) & (df.cup == "kougou")].iloc[0]
        assert row.rank1 == "京都"
        assert row.rank2 == "東京"

    def test_ninth_kai_uses_honmatsuri_not_winter(self, df):
        # 第9回は「冬」と「夏・秋」が別行。主分析は本大会 (夏・秋) を採用。冬季ランキング (rank1=北海道) 混入なし
        row = df[(df.kai_num == 9) & (df.cup == "tennou")].iloc[0]
        assert row.rank1 == "東京"
        assert row.rank2 == "愛知"
        assert row.rank3 == "北海道"  # 本大会で北海道は3位 (冬季1位ではない)

    def test_ninth_kai_kougou_honmatsuri(self, df):
        # 第9回 kougou も本大会 (夏・秋) を採用
        row = df[(df.kai_num == 9) & (df.cup == "kougou")].iloc[0]
        assert row.rank1 == "東京"
        assert row.rank2 == "愛知"

    def test_no_season_mark_in_rank1(self, df):
        # rank1 に季節マーク (「冬」「夏・秋」「冬・夏・秋」) が混入していない (v3 パーサ修正の regression guard)
        season_marks = {"冬", "夏・秋", "冬・夏・秋"}
        rank1_values = set(df["rank1"].dropna())
        assert rank1_values.isdisjoint(season_marks)

    def test_cancelled_75_76(self, df):
        # 第75回2020鹿児島・第76回2021三重は COVID 中止。tennou は rank1="中　止"、kougou は rank1=NaN で残る
        for kai in (75, 76):
            tennou = df[(df.kai_num == kai) & (df.cup == "tennou")].iloc[0]
            assert "中" in str(tennou.rank1)
            assert pd.isna(tennou.rank2)

    def test_recent_hosts_top1_or_top2(self, df):
        # 第68-79回の直近 host 順位 (M2 主分析の主要データ・順位ベース regression 対策)
        expected = {
            68: ("東京都", "東京"),      # 2013 東京 = host tennou 1位
            71: ("岩手県", "岩手"),      # 2016 岩手 = 敗北ショック (東京1位・岩手2位)
            73: ("福井県", "福井"),      # 2018 福井 = host 1位
            74: ("茨城県", "茨城"),      # 2019 茨城 = host 1位
            77: ("栃木県", "栃木"),      # 2022 栃木 = 敗北ショック (東京1位・栃木2位)
        }
        for kai, (host_str, host_short) in expected.items():
            row = df[(df.kai_num == kai) & (df.cup == "tennou")].iloc[0]
            assert row.host_raw == host_str
            top2 = {row.rank1, row.rank2}
            assert host_short in top2, f"kai={kai}: host {host_short} not in top2 ({top2})"


class TestJspoXls:
    def test_79_tennou(self):
        df = load_jspo_kai_xls(79, "tennou")
        assert df.shape == (57, 70)

    def test_78_tennou(self):
        df = load_jspo_kai_xls(78, "tennou")
        assert df.shape == (57, 70)

    def test_79_kougou(self):
        df = load_jspo_kai_xls(79, "kougou")
        assert df.shape == (57, 48)

    def test_78_kougou(self):
        df = load_jspo_kai_xls(78, "kougou")
        assert df.shape == (57, 48)

    def test_invalid_kai_raises(self):
        with pytest.raises(ValueError, match="78 or 79"):
            load_jspo_kai_xls(75)


class TestKendo2016Iwate:
    @pytest.fixture(scope="class")
    def df(self):
        return load_kendo_2016_iwate()

    def test_shape(self, df):
        # 9 データ行 (1-6位 + 7位が3県同点)
        assert df.shape == (9, 5)

    def test_columns(self, df):
        assert list(df.columns) == [
            "rank", "pref_name", "competition_score", "participation_score", "total_score",
        ]

    def test_iwate_host_win(self, df):
        # 主観判定競技=剣道での host effect (岩手 1位 144点)
        row = df[df["rank"] == 1].iloc[0]
        assert row.pref_name == "岩手県"
        assert row.competition_score == 134.0
        assert row.participation_score == 10.0
        assert row.total_score == 144.0

    def test_kumamoto_second(self, df):
        row = df[df["rank"] == 2].iloc[0]
        assert row.pref_name == "熊本県"
        assert row.total_score == 105.0

    def test_rank7_three_way_tie(self, df):
        # 7位が和歌山/岡山/大分の3県同点
        rank7 = df[df["rank"] == 7]
        assert len(rank7) == 3
        prefs = set(rank7.pref_name.tolist())
        assert prefs == {"和歌山県", "岡山県", "大分県"}

    def test_ehime_decimal(self, df):
        # 小数点数の取り扱い確認 (3位愛媛 62.5+10=72.5)
        row = df[df["rank"] == 3].iloc[0]
        assert row.pref_name == "愛媛県"
        assert row.competition_score == 62.5
        assert row.total_score == 72.5

    def test_pref_name_no_english(self, df):
        # "岩手県 Iwate" → "岩手県" に浄化されている
        for pref in df["pref_name"]:
            assert not any(c.isascii() and c.isalpha() for c in pref)

    def test_total_matches_sum(self, df):
        # competition + participation = total の検算
        for _, row in df.iterrows():
            assert row.competition_score + row.participation_score == row.total_score


class TestNaganoGameScore:
    @pytest.fixture(scope="class")
    def df(self):
        return load_nagano_game_score()

    def test_shape_long_format(self, df):
        # 41競技 × 10大会 (71〜79回 + special_2023) = 410 行
        assert df.shape == (410, 5)

    def test_columns(self, df):
        assert list(df.columns) == [
            "competition_no", "competition_name", "kai_label", "year", "score",
        ]

    def test_kai_labels(self, df):
        labels = set(df["kai_label"].unique())
        assert labels == {"71", "72", "73", "74", "75", "76", "77", "78", "79", "special_2023"}

    def test_year_mapping(self, df):
        # kai 71 = 2016
        r = df[(df.kai_label == "71") & (df.competition_no == 1)].iloc[0]
        assert r.year == 2016
        # kai 79 = 2025
        r = df[(df.kai_label == "79") & (df.competition_no == 1)].iloc[0]
        assert r.year == 2025
        # special_2023 = 2023
        r = df[(df.kai_label == "special_2023") & (df.competition_no == 1)].iloc[0]
        assert r.year == 2023

    def test_skate_71_score(self, df):
        # Row 1: スケート 71回 = 195.0
        r = df[(df.competition_no == 1) & (df.kai_label == "71")].iloc[0]
        assert r.competition_name == "スケート"
        assert r.score == 195.0

    def test_kendo_all_nan(self, df):
        # No.30 剣道は全大会 NaN (長野で剣道入賞なし)
        rows = df[df.competition_no == 30]
        assert (rows.competition_name == "剣道").all()
        assert rows.score.isna().all()

    def test_ice_hockey_75_76_nan(self, df):
        # No.2 アイスホッケー・75回2020 (COVID中止本大会) と 76回2021 は NaN
        r75 = df[(df.competition_no == 2) & (df.kai_label == "75")].iloc[0]
        r76 = df[(df.competition_no == 2) & (df.kai_label == "76")].iloc[0]
        assert pd.isna(r75.score) or r75.score == 15.0  # 冬季のみ実施あり
        assert pd.isna(r76.score)

    def test_competition_count(self, df):
        # 冬季3 + 本大会38 = 41競技
        assert df["competition_no"].nunique() == 41

    def test_no_summary_rows(self, df):
        # 集計行 (冬季計/本大会計/合計) が混入していないこと
        names = set(df["competition_name"].unique())
        for banned in ("冬季計", "本大会計", "合計"):
            assert banned not in names


class TestJfaSoccerHistory:
    @pytest.fixture(scope="class")
    def df(self):
        return load_jfa_soccer_history()

    def test_columns(self, df):
        assert list(df.columns) == [
            "kai_num", "year", "host_raw", "adult_male_winner", "youth_male_winner", "status",
        ]

    def test_first_record_1946_kyoto(self, df):
        r = df[df.kai_num == 1].iloc[0]
        assert r.year == 1946
        assert r.host_raw == "京都府"
        assert r.adult_male_winner == "全関学"

    def test_74th_2019_ibaraki(self, df):
        # 第74回2019茨城 (post-2016 開催地敗北 6ショック年に該当しない・茨城が成年男子優勝)
        r = df[df.kai_num == 74].iloc[0]
        assert r.year == 2019
        assert r.host_raw == "茨城県"
        assert r.status == "normal"
        assert r.adult_male_winner == "茨城県選抜"

    def test_75th_2020_postponed(self, df):
        r = df[df.kai_num == 75].iloc[0]
        assert r.status == "postponed"
        assert pd.isna(r.adult_male_winner)

    def test_76th_2021_cancelled(self, df):
        r = df[df.kai_num == 76].iloc[0]
        assert r.status == "cancelled"
        assert pd.isna(r.adult_male_winner)

    def test_kai_range(self, df):
        # 第1-76回まで最低カバー (第77回以降は Phase 2 個別対応で現段階 skip)
        assert df.kai_num.min() == 1
        assert df.kai_num.max() >= 76

    def test_pre_2016_baseline(self, df):
        # post-2016 の4ショック年 (2016岩手/2017愛媛/2022栃木/2023鹿児島) の 2016/2017 だけ検証
        # 第71回2016岩手 = 開催地敗北の総合的な話。サッカーは別優勝
        r71 = df[df.kai_num == 71]
        assert len(r71) == 1
        assert r71.iloc[0].year == 2016
        assert r71.iloc[0].host_raw == "岩手県"


class TestJihfHockey:
    @pytest.fixture(scope="class")
    def df(self):
        return load_jihf_hockey()

    def test_columns(self, df):
        assert list(df.columns) == [
            "kai_num", "year", "venue_raw",
            "adult_1st", "adult_2nd", "adult_3rd",
            "youth_1st", "youth_2nd", "youth_3rd",
            "tennou_score_1st",
        ]

    def test_kai_range_1_to_67(self, df):
        # 第1回1947 (八戸) 〜 第67回2012 (名古屋他)
        assert df.kai_num.min() == 1
        assert df.kai_num.max() == 67

    def test_first_record_1947(self, df):
        r = df[df.kai_num == 1].iloc[0]
        assert r.year == 1947
        assert r.venue_raw == "八戸"
        assert r.adult_1st == "北海道"

    def test_67th_2012_last(self, df):
        # 2012年で更新停止確認
        r = df[df.kai_num == 67].iloc[0]
        assert r.year == 2012
        assert r.adult_1st == "東京"
        assert r.youth_1st == "北海道"

    def test_kai_2_missing(self, df):
        # 第2回1946 (国体開催なし) は JIHF データにも無し
        assert 2 not in set(df.kai_num.tolist())

    def test_hyphen_normalized(self, df):
        # "-" は None (pandas NaN) に正規化されているか
        r64 = df[df.kai_num == 64].iloc[0]
        assert pd.isna(r64.tennou_score_1st)


class TestJspoKaiPdf:
    def test_60_tennou_okayama_host_win(self):
        # 第60回2005岡山 = ふるさと選手制度導入年・岡山 host 優勝 (2842点)
        df = load_jspo_kai_pdf(60, "tennou")
        assert df.shape == (47, 5)
        row = df[df.pref_name == "岡山"].iloc[0]
        assert row["rank"] == 1
        assert row["score"] == 2842.0

    def test_60_tennou_all_47_prefs(self):
        df = load_jspo_kai_pdf(60, "tennou")
        prefs = set(df.pref_name.tolist())
        assert len(prefs) == 47

    def test_58_tennou_shizuoka_host_win(self):
        # 第58回2003静岡・舟橋2016 パネル起点
        df = load_jspo_kai_pdf(58, "tennou")
        assert df.shape == (47, 5)
        # host = 静岡・舟橋2016 論文で host 優勝と確認済み
        row = df[df.pref_name == "静岡"].iloc[0]
        assert row["rank"] == 1

    def test_66_tennou_yamaguchi_host_win(self):
        # 第66回2011山口
        df = load_jspo_kai_pdf(66, "tennou")
        row = df[df.pref_name == "山口"].iloc[0]
        assert row["rank"] == 1
        assert row["score"] == 2220.5

    def test_64_tennou_niigata_host_win(self):
        # 第64回2009新潟 (小サイズPDFでも正常抽出できるかの検証)
        df = load_jspo_kai_pdf(64, "tennou")
        assert df.shape == (47, 5)
        row = df[df.pref_name == "新潟"].iloc[0]
        assert row["rank"] == 1
        assert row["score"] == 2426.0

    def test_67_kougou_gifu_host_win(self):
        # 第67回2012岐阜・皇后杯 (host が皇后杯も1位取ってるかは実データ次第)
        df = load_jspo_kai_pdf(67, "kougou")
        assert df.shape == (47, 5)
        # 存在確認だけ
        assert "岐阜" in set(df.pref_name.tolist())

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="58-67"):
            load_jspo_kai_pdf(68)
        with pytest.raises(ValueError, match="58-67"):
            load_jspo_kai_pdf(57)

    def test_invalid_cup_raises(self):
        with pytest.raises(ValueError, match="tennou or kougou"):
            load_jspo_kai_pdf(60, "invalid")

    def test_ranks_in_valid_range(self):
        # 47 prefectures, ranks 1-47 (ただし同点で欠番/重複あり得る)
        df = load_jspo_kai_pdf(60, "tennou")
        assert df["rank"].min() >= 1
        assert df["rank"].max() <= 47


class TestListAvailableJspoPdfs:
    def test_58_67_all_present(self):
        avail = list_available_jspo_pdfs()
        for kai in range(58, 68):
            assert kai in avail, f"kai {kai} missing"
            assert len(avail[kai]) == 2  # tennou + kougou


class TestListAvailableXls:
    def test_78_79_75_present(self):
        avail = list_available_xls()
        assert 78 in avail
        assert 79 in avail
        assert 75 in avail

    def test_78_has_two(self):
        avail = list_available_xls()
        assert len(avail[78]) == 2

    def test_79_has_two(self):
        avail = list_available_xls()
        assert len(avail[79]) == 2


class TestEsriSoukatu:
    def test_soukatu1_shape_47_by_12(self):
        df = load_esri_soukatu(ESRI_DIR / "soukatu1.xlsx")
        assert df.shape == (564, 4)  # 47県×12年
        assert set(df.columns) == {"pref_code", "pref_name", "year", "value"}

    def test_pref_codes_are_1_to_47(self):
        df = load_esri_soukatu(ESRI_DIR / "soukatu1.xlsx")
        assert sorted(df.pref_code.unique().tolist()) == list(range(1, 48))

    def test_years_are_2011_to_2022(self):
        df = load_esri_soukatu(ESRI_DIR / "soukatu1.xlsx")
        assert sorted(df.year.unique().tolist()) == list(range(2011, 2023))

    def test_no_summary_rows_included(self):
        df = load_esri_soukatu(ESRI_DIR / "soukatu1.xlsx")
        assert "全県計" not in df.pref_name.values
        assert "札幌市" not in df.pref_name.values
        assert "北海道・東北" not in df.pref_name.values

    def test_values_are_numeric_and_positive(self):
        df = load_esri_soukatu(ESRI_DIR / "soukatu1.xlsx")
        assert df.value.notna().all()
        assert (df.value > 0).all()


class TestEsriPopulation:
    def test_column_named_population(self):
        df = load_esri_population()
        assert "population" in df.columns
        assert df.shape == (564, 4)

    def test_hokkaido_2011(self):
        df = load_esri_population()
        val = df[(df.pref_code == 1) & (df.year == 2011)].population.iloc[0]
        assert val == 5488473  # ESRI 令和4年度版・北海道 2011年度総人口

    def test_okinawa_2022(self):
        df = load_esri_population()
        val = df[(df.pref_code == 47) & (df.year == 2022)].population.iloc[0]
        assert val == 1468318  # ESRI 令和4年度版・沖縄県 2022年度総人口


class TestEsriGdpNominal:
    def test_column_named_gdp_nominal_mil_yen(self):
        df = load_esri_gdp_nominal()
        assert "gdp_nominal_mil_yen" in df.columns
        assert df.shape == (564, 4)

    def test_hokkaido_2011_matches_esri(self):
        df = load_esri_gdp_nominal()
        val = df[(df.pref_code == 1) & (df.year == 2011)].gdp_nominal_mil_yen.iloc[0]
        assert val == 18527065  # 単位: 100万円 (=約18.5兆円)

    def test_tokyo_2022_largest(self):
        df = load_esri_gdp_nominal()
        by_pref_2022 = df[df.year == 2022].sort_values("gdp_nominal_mil_yen", ascending=False)
        assert by_pref_2022.iloc[0].pref_code == 13  # 東京都が最大
