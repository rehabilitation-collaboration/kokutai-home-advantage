"""国民体育大会 競技を Balmer2003 準拠で3分類

分類定義 (Balmer, Nevill & Williams 2003 J Sports Sci 21(6):469-478):
- **objective** (客観記録): time/distance/weight/points 等の client-independent measurement で決まる
- **subjective** (主観判定): 審判員の減点/加点方式による主観判断
- **semi_subjective** (準主観): 団体競技・勝敗自体は明確だが審判判定 (ファウル/PK等) が影響

国体41競技 (冬季3 + 本大会38) の内訳 (78佐賀時点の最大セット):
- objective  = 17 (陸上/水泳/自転車/ローイング/カヌー/ウエイトリフティング/セーリング/スキー/スケート/アーチェリー/弓道/ライフル射撃/クレー射撃/ゴルフ/ボウリング/トライアスロン/スポーツクライミング)
- subjective = 11 (剣道/柔道/体操/空手道/銃剣道/なぎなた/ボクシング/フェンシング/レスリング/相撲/馬術)
- semi       = 13 (サッカー/バスケットボール/バレーボール/ハンドボール/ホッケー/ラグビーフットボール/軟式野球/ソフトボール/バドミントン/卓球/ソフトテニス/テニス/アイスホッケー)

★注記1: PHASE9-SUPPLEMENT.md L48-72 の暫定推定表 (「客観(団体)」「準主観=馬術」等) は本ファイルで正式に上書き。
Balmer2003 の semi_subjective 定義は「team sports」なので馬術は subjective (審判員採点競技)、ラグビー等の団体競技は semi_subjective に確定。

★注記2 (Deviation #5・2026-07-28): クレー射撃は 78佐賀の本大会競技セットに存在 (col45) するが 79滋賀では廃止。
Balmer2003 準拠でトラップ/スキート等の的中率計測 = client-independent measurement のため objective に分類。
"""

from typing import Literal

Category = Literal["objective", "subjective", "semi_subjective"]

# 競技名 → カテゴリ (JSPO xls の正式名称ベース・alias は SPORT_ALIASES で吸収)
SPORT_CATEGORIES: dict[str, Category] = {
    # === objective (客観記録・16競技) ===
    "陸上競技": "objective",
    "水泳": "objective",
    "自転車": "objective",
    "ローイング": "objective",
    "カヌー": "objective",
    "ウエイトリフティング": "objective",
    "セーリング": "objective",
    "スキー競技": "objective",
    "スケート競技": "objective",
    "アーチェリー": "objective",
    "弓道": "objective",
    "ライフル射撃": "objective",
    "クレー射撃": "objective",
    "ゴルフ": "objective",
    "ボウリング": "objective",
    "トライアスロン": "objective",
    "スポーツクライミング": "objective",

    # === subjective (主観判定・11競技) ===
    "剣道": "subjective",
    "柔道": "subjective",
    "体操": "subjective",
    "空手道": "subjective",
    "銃剣道": "subjective",
    "なぎなた": "subjective",
    "ボクシング": "subjective",
    "フェンシング": "subjective",
    "レスリング": "subjective",
    "相撲": "subjective",
    "馬術": "subjective",

    # === semi_subjective (準主観・団体競技・13競技) ===
    "サッカー": "semi_subjective",
    "バスケットボール": "semi_subjective",
    "バレーボール": "semi_subjective",
    "ハンドボール": "semi_subjective",
    "ホッケー": "semi_subjective",
    "ラグビーフットボール": "semi_subjective",
    "軟式野球": "semi_subjective",
    "ソフトボール": "semi_subjective",
    "バドミントン": "semi_subjective",
    "卓球": "semi_subjective",
    "ソフトテニス": "semi_subjective",
    "テニス": "semi_subjective",
    "アイスホッケー": "semi_subjective",
}

# xls 列名の表記揺れを正式名称に吸収 (発見次第追加)
SPORT_ALIASES: dict[str, str] = {
    "陸上": "陸上競技",
    "スキー": "スキー競技",
    "スケート": "スケート競技",
    "ラグビー": "ラグビーフットボール",
    "クライミング": "スポーツクライミング",
    "水泳競技": "水泳",
}

# 冬季3競技 (別集計・冬季小計/冬季順位を持つ)
WINTER_SPORTS: frozenset[str] = frozenset({"スキー競技", "スケート競技", "アイスホッケー"})


def get_category(sport_name: str) -> Category | None:
    """競技名 → カテゴリ (alias 経由で解決)。未登録は None を返す"""
    canonical = SPORT_ALIASES.get(sport_name, sport_name)
    return SPORT_CATEGORIES.get(canonical)


def is_winter(sport_name: str) -> bool:
    canonical = SPORT_ALIASES.get(sport_name, sport_name)
    return canonical in WINTER_SPORTS


def get_sports_by_category(category: Category) -> list[str]:
    """指定カテゴリに属する競技名を返す"""
    return sorted(s for s, c in SPORT_CATEGORIES.items() if c == category)


def count_by_category() -> dict[Category, int]:
    """カテゴリ別競技数の集計 (テスト用)"""
    counts: dict[Category, int] = {"objective": 0, "subjective": 0, "semi_subjective": 0}
    for c in SPORT_CATEGORIES.values():
        counts[c] += 1
    return counts
