"""sport_classifier.py の contract テスト"""

import pytest
from src.sport_classifier import (
    SPORT_CATEGORIES,
    SPORT_ALIASES,
    WINTER_SPORTS,
    get_category,
    is_winter,
    get_sports_by_category,
    count_by_category,
)


class TestCategoryCounts:
    def test_total_41_sports(self):
        # 冬季3 + 本大会38 = 41 (78佐賀時点の最大セット・クレー射撃を含む・Deviation #5)
        assert len(SPORT_CATEGORIES) == 41

    def test_17_objective(self):
        assert count_by_category()["objective"] == 17

    def test_11_subjective(self):
        assert count_by_category()["subjective"] == 11

    def test_13_semi_subjective(self):
        assert count_by_category()["semi_subjective"] == 13


class TestSubjectiveSports:
    """審判減点/加点方式の主観判定競技"""

    @pytest.mark.parametrize("sport", [
        "剣道", "柔道", "体操", "空手道", "銃剣道", "なぎなた",
        "ボクシング", "フェンシング", "レスリング", "相撲", "馬術",
    ])
    def test_is_subjective(self, sport):
        assert get_category(sport) == "subjective"


class TestObjectiveSports:
    """計測系の客観記録競技"""

    @pytest.mark.parametrize("sport", [
        "陸上競技", "水泳", "自転車", "ローイング", "カヌー",
        "ウエイトリフティング", "セーリング", "スキー競技", "スケート競技",
        "アーチェリー", "弓道", "ライフル射撃", "クレー射撃", "ゴルフ", "ボウリング",
        "トライアスロン", "スポーツクライミング",
    ])
    def test_is_objective(self, sport):
        assert get_category(sport) == "objective"


class TestSemiSubjectiveSports:
    """団体競技の準主観 (審判判定影響あり)"""

    @pytest.mark.parametrize("sport", [
        "サッカー", "バスケットボール", "バレーボール", "ハンドボール",
        "ホッケー", "ラグビーフットボール", "軟式野球", "ソフトボール",
        "バドミントン", "卓球", "ソフトテニス", "テニス", "アイスホッケー",
    ])
    def test_is_semi(self, sport):
        assert get_category(sport) == "semi_subjective"


class TestAliases:
    def test_short_names_resolve(self):
        assert get_category("陸上") == "objective"
        assert get_category("スキー") == "objective"
        assert get_category("スケート") == "objective"
        assert get_category("ラグビー") == "semi_subjective"
        assert get_category("クライミング") == "objective"

    def test_unknown_returns_none(self):
        assert get_category("野球") is None  # 硬式野球は国体になし
        assert get_category("架空競技") is None


class TestWinter:
    def test_winter_sports_set(self):
        assert WINTER_SPORTS == {"スキー競技", "スケート競技", "アイスホッケー"}

    def test_is_winter_true(self):
        assert is_winter("スキー競技") is True
        assert is_winter("アイスホッケー") is True

    def test_is_winter_via_alias(self):
        assert is_winter("スキー") is True
        assert is_winter("スケート") is True

    def test_is_winter_false(self):
        assert is_winter("陸上競技") is False
        assert is_winter("剣道") is False
