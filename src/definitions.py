"""国民体育大会 (国民スポーツ大会) 基本定義

真実源:
- 都道府県: JIS X0401 コード順 (01北海道 - 47沖縄)
- 開催地マッピング: JSPO tabid183 index から抽出した refs/host_mapping_raw.json
- 統計母集団: 第3回1948〜第79回2025 (計77大会) + 特別大会 2件 = 79大会

除外/フラグ:
- 第1回1946 = 「京阪神地域を中心に近畿地区」= 単一県帰属不可 → panel_included=False
- 第2回1947 = 石川 単独 (パネル母集団は PLAN L243 で第3回起点のため panel_included=False)
- 第7回1952 = 福島/宮城/山形 3県共催 → is_multi_pref=True
- 第8回1953 = 愛媛/香川/徳島/高知 4県共催 → is_multi_pref=True
- 第75回2020 = 鹿児島 (COVID中止・冬季のみ実施) → cancelled=True, is_winter_only_kai=True
- 第76回2021 = 三重 (COVID中止) → cancelled=True
- 特別大会2023 = 鹿児島 (COVID延期分・第20回鹿児島国体 令和特別大会) → is_special=True, kai_num=None → KOKUTAI_SPECIAL["special_2023"]
- 特別国体1973 = 沖縄 (若夏国体・沖縄本土復帰後初の国体・第28回本大会外の特別枠) → is_special=True, kai_num=None → KOKUTAI_SPECIAL["special_1973"]
  - ★注意: 長野県体協 high_rank.html には行なし・build_ranking_panel() から実質除外・順位ベース分析母集団には含まれない
- 第80回2026 = 未実施 → future=True
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFS_DIR = PROJECT_ROOT / "refs"

# JIS X0401 準拠 47都道府県
PREFECTURES: dict[int, str] = {
    1: "北海道", 2: "青森", 3: "岩手", 4: "宮城", 5: "秋田",
    6: "山形", 7: "福島", 8: "茨城", 9: "栃木", 10: "群馬",
    11: "埼玉", 12: "千葉", 13: "東京", 14: "神奈川", 15: "新潟",
    16: "富山", 17: "石川", 18: "福井", 19: "山梨", 20: "長野",
    21: "岐阜", 22: "静岡", 23: "愛知", 24: "三重", 25: "滋賀",
    26: "京都", 27: "大阪", 28: "兵庫", 29: "奈良", 30: "和歌山",
    31: "鳥取", 32: "島根", 33: "岡山", 34: "広島", 35: "山口",
    36: "徳島", 37: "香川", 38: "愛媛", 39: "高知", 40: "福岡",
    41: "佐賀", 42: "長崎", 43: "熊本", 44: "大分", 45: "宮崎",
    46: "鹿児島", 47: "沖縄",
}
PREFECTURE_TO_CODE: dict[str, int] = {name: code for code, name in PREFECTURES.items()}

# 東京は「東京都」表記もあり得るので alias 対応
_HOST_NAME_ALIASES: dict[str, str] = {
    "東京都": "東京",
    "北海道": "北海道",
    "京都府": "京都",
    "大阪府": "大阪",
}

# 手動 override (JSON パースだけでは判定できないフラグ)
_MANUAL_OVERRIDES: dict[int | str, dict] = {
    1: {"is_multi_pref": True, "panel_included": False, "note": "京阪神地域を中心に近畿地区・単一県帰属不可"},
    2: {"panel_included": False, "note": "PLAN L243 で母集団起点は第3回1948"},
    7: {"is_multi_pref": True, "note": "福島/宮城/山形 3県共催"},
    8: {"is_multi_pref": True, "note": "愛媛/香川/徳島/高知 4県共催"},
    75: {"is_winter_only_kai": True, "note": "本大会COVID中止・冬季のみ実施"},
}


def _parse_host_string(host_raw: str) -> tuple[list[str], bool]:
    """開催地 raw string をパース → (県名リスト, cancelled フラグ)

    - "滋賀県" → (["滋賀"], False)
    - "三重県※中止" → (["三重"], True)
    - "愛媛県 香川県 徳島県 高知県" → (["愛媛", "香川", "徳島", "高知"], False)
    - "京阪神地域を 中心に近畿地区" → ([], False) - 手動overrideで補完
    - "－" → ([], False) - 未実施 (第80回)
    """
    if not host_raw or host_raw.strip() in ("－", "-", ""):
        return [], False

    cancelled = "中止" in host_raw
    cleaned = host_raw.replace("※中止", "").replace("中止", "").strip()

    prefs: list[str] = []
    for token in cleaned.split():
        for suffix in ("県", "府", "都", "道"):
            if token.endswith(suffix):
                base = token[: -len(suffix)]
                # 北海道は「道」を含めて識別
                canonical = _HOST_NAME_ALIASES.get(token, base if suffix != "道" else token)
                if canonical in PREFECTURE_TO_CODE:
                    prefs.append(canonical)
                break
    return prefs, cancelled


def _load_kokutai_hosts() -> tuple[dict[int, dict], dict[str, dict]]:
    """host_mapping_raw.json (JSPO tabid183 抽出結果) から
    KOKUTAI_HOSTS (kai_num keyed) と KOKUTAI_SPECIAL (special_YYYY keyed) を生成
    """
    src_path = REFS_DIR / "host_mapping_raw.json"
    if not src_path.exists():
        raise FileNotFoundError(f"{src_path} not found. run scripts/refresh_host_mapping.py first.")

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    hosts: dict[int, dict] = {}
    specials: dict[str, dict] = {}

    for rec in raw:
        prefs, cancelled = _parse_host_string(rec["host_raw"])
        entry = {
            "year": rec["year"],
            "host_prefs": prefs,
            "host_raw": rec["host_raw"],
            "tabid": rec["tabid"],
            "cancelled": cancelled,
            "is_special": rec["kai_num"] is None,
            "is_multi_pref": len(prefs) > 1,
            "is_winter_only_kai": False,
            "future": len(prefs) == 0 and not cancelled,
            "panel_included": True,
            "note": None,
        }

        if rec["kai_num"] is None:
            key = f"special_{rec['year']}"
            override = _MANUAL_OVERRIDES.get(key, {})
            entry.update(override)
            specials[key] = entry
        else:
            kai = rec["kai_num"]
            override = _MANUAL_OVERRIDES.get(kai, {})
            entry.update(override)
            # future=True は panel_included=False にフォールバック
            if entry["future"]:
                entry["panel_included"] = False
            hosts[kai] = entry

    return hosts, specials


KOKUTAI_HOSTS, KOKUTAI_SPECIAL = _load_kokutai_hosts()


def get_panel_kai_list() -> list[int]:
    """統計母集団 (panel_included=True) の kai_num を昇順で返す"""
    return sorted(kai for kai, e in KOKUTAI_HOSTS.items() if e["panel_included"])


def get_host_code(kai_num: int) -> int | None:
    """kai_num の主開催都道府県コードを返す。複数県共催は先頭県のコード。特別大会は None を渡すな (KOKUTAI_SPECIAL 経由)。"""
    entry = KOKUTAI_HOSTS.get(kai_num)
    if not entry or not entry["host_prefs"]:
        return None
    return PREFECTURE_TO_CODE.get(entry["host_prefs"][0])


def get_all_host_codes(kai_num: int) -> list[int]:
    """kai_num の全開催県コードを返す (複数県共催時は複数)"""
    entry = KOKUTAI_HOSTS.get(kai_num)
    if not entry:
        return []
    return [PREFECTURE_TO_CODE[p] for p in entry["host_prefs"] if p in PREFECTURE_TO_CODE]


def is_host(pref_code: int, kai_num: int) -> bool:
    """pref_code が kai_num の開催県か (複数県共催時は該当県すべて True)"""
    return pref_code in get_all_host_codes(kai_num)
