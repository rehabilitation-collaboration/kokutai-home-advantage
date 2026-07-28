"""definitions.py の contract テスト"""

import pytest
from src.definitions import (
    PREFECTURES,
    PREFECTURE_TO_CODE,
    KOKUTAI_HOSTS,
    KOKUTAI_SPECIAL,
    get_panel_kai_list,
    get_host_code,
    get_all_host_codes,
    is_host,
)


class TestPrefectures:
    def test_47_prefectures(self):
        assert len(PREFECTURES) == 47

    def test_jis_code_range(self):
        assert min(PREFECTURES) == 1
        assert max(PREFECTURES) == 47

    def test_bidirectional_mapping(self):
        for code, name in PREFECTURES.items():
            assert PREFECTURE_TO_CODE[name] == code

    def test_key_prefectures(self):
        assert PREFECTURES[1] == "北海道"
        assert PREFECTURES[13] == "東京"
        assert PREFECTURES[25] == "滋賀"
        assert PREFECTURES[41] == "佐賀"
        assert PREFECTURES[47] == "沖縄"


class TestKokutaiHosts:
    def test_at_least_80_kai(self):
        # 第1-80回大会が全部入ってる
        assert set(KOKUTAI_HOSTS.keys()) >= set(range(1, 81))

    def test_special_2023(self):
        assert "special_2023" in KOKUTAI_SPECIAL
        entry = KOKUTAI_SPECIAL["special_2023"]
        assert entry["year"] == 2023
        assert entry["host_prefs"] == ["鹿児島"]
        assert entry["is_special"] is True

    def test_79th_shiga_host_win(self):
        entry = KOKUTAI_HOSTS[79]
        assert entry["year"] == 2025
        assert entry["host_prefs"] == ["滋賀"]
        assert entry["cancelled"] is False
        assert entry["panel_included"] is True

    def test_78th_saga(self):
        entry = KOKUTAI_HOSTS[78]
        assert entry["year"] == 2024
        assert entry["host_prefs"] == ["佐賀"]

    def test_75th_kagoshima_cancelled(self):
        entry = KOKUTAI_HOSTS[75]
        assert entry["cancelled"] is True
        assert entry["is_winter_only_kai"] is True

    def test_76th_mie_cancelled(self):
        entry = KOKUTAI_HOSTS[76]
        assert entry["cancelled"] is True

    def test_80th_future(self):
        entry = KOKUTAI_HOSTS[80]
        assert entry["future"] is True
        assert entry["panel_included"] is False

    def test_7th_multi_pref_tohoku(self):
        entry = KOKUTAI_HOSTS[7]
        assert entry["is_multi_pref"] is True
        assert set(entry["host_prefs"]) == {"福島", "宮城", "山形"}

    def test_8th_multi_pref_shikoku(self):
        entry = KOKUTAI_HOSTS[8]
        assert entry["is_multi_pref"] is True
        assert set(entry["host_prefs"]) == {"愛媛", "香川", "徳島", "高知"}

    def test_1st_kinki_excluded(self):
        entry = KOKUTAI_HOSTS[1]
        assert entry["panel_included"] is False


class TestPanelKaiList:
    def test_starts_at_3(self):
        panel = get_panel_kai_list()
        assert panel[0] == 3

    def test_ends_at_79(self):
        panel = get_panel_kai_list()
        assert panel[-1] == 79

    def test_no_80(self):
        assert 80 not in get_panel_kai_list()

    def test_includes_cancelled(self):
        # 中止年 (75/76) もパネル母集団には含める (欠測扱いで別途処理)
        panel = get_panel_kai_list()
        assert 75 in panel
        assert 76 in panel


class TestHostAccessors:
    def test_79th_host_code_shiga(self):
        assert get_host_code(79) == 25

    def test_78th_host_code_saga(self):
        assert get_host_code(78) == 41

    def test_71st_host_code_iwate(self):
        assert get_host_code(71) == 3

    def test_multi_pref_returns_all(self):
        codes = get_all_host_codes(8)
        assert set(codes) == {38, 37, 36, 39}  # 愛媛/香川/徳島/高知

    def test_is_host_true(self):
        assert is_host(25, 79) is True  # 滋賀 in 第79回

    def test_is_host_false(self):
        assert is_host(13, 79) is False  # 東京 not in 第79回

    def test_is_host_multi_pref_all_true(self):
        assert is_host(38, 8) is True  # 愛媛
        assert is_host(37, 8) is True  # 香川
        assert is_host(1, 8) is False  # 北海道
