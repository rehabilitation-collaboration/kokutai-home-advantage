"""外部データソースからの読み込み層

対応データソース (Phase 1 前半):
- 長野県体協 high_rank.html: 第3-79回+特別大会の天皇杯/皇后杯 1-8位ランキング → load_nagano_high_rank()
- JSPO 78+79回 xls: 47県×競技クロス集計 (副次分析基盤) → load_jspo_kai_xls()

Phase 1 中盤で追加 (2026-07-28・全 5関数 + tests 40件):
- 剣道 old2 第71回岩手 (2016年主観判定副次データ・岩手 host 優勝144点) → load_kendo_2016_iwate()
- 長野県体協 game_score.html (2016年以降9年分・長野1県時系列・素点副次) → load_nagano_game_score()
- JFA サッカー歴代 (客観リファレンス・第1-76回) → load_jfa_soccer_history()
- JIHF アイスホッケー (客観リファレンス・第1-67回2012で更新停止) → load_jihf_hockey()
- JSPO 個別回 PDF (規則的パス `data0/kokutai/{kai}/{kai}_{cup}.pdf` の第58-67回×2杯=20 PDF・47県総合順位/得点) → load_jspo_kai_pdf()

Phase 1 中盤 未実装 (Limitations 明記に確定):
- 体操 jpn-gym.or.jp: サイト内 (トップ/event/) に国体データ非公開 (接続自体は復旧確認済)
- JSPO PDF 第68-77回: 規則的パス 404 (20 URL 全滅)+不規則URL (74茨城=画像PDFでtext抽出不能)→Phase 2 OCR 検討
- JFA 第77-78回 (2022-2023) 4部門化行: rowspan で構造変わり→Phase 2 個別対応
"""

import re
from pathlib import Path

import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
from python_calamine import CalamineWorkbook

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFS_DIR = PROJECT_ROOT / "refs"
JSPO_PDF_DIR = REFS_DIR / "jspo_pdf"

# JSPO 個別回 PDF 規則的パス対応範囲 (58-67回・2003-2012・舟橋2016期間+1年)
# 第68回2013 東京 以降は不規則 URL + 画像PDFで抽出困難 → Phase 2 個別対応
JSPO_PDF_RANGE = (58, 67)

# 年号 → 西暦オフセット (元号n年 = base + n)
_ERA_OFFSETS: dict[str, int] = {
    "S": 1925,  # 昭和1=1926
    "H": 1988,  # 平成1=1989
    "R": 2018,  # 令和1=2019
}


def parse_japanese_era(era_str: str) -> int | None:
    """"R7" → 2025, "S24" → 1949, "H30" → 2018 等を西暦に変換"""
    if not era_str:
        return None
    m = re.match(r"^([SHR])\s*(\d+)$", era_str.strip())
    if not m:
        return None
    era, n_str = m.group(1), m.group(2)
    return _ERA_OFFSETS[era] + int(n_str)


def _extract_rank_cells(cells: list[str], has_season_col: bool) -> list[str]:
    """順位セル (1位-8位) を抽出。「冬・夏・秋」列がある行は1つずらす。"""
    start = 5 if has_season_col else 4  # 天皇杯行の1位開始インデックス
    return [c.strip() for c in cells[start:start + 8]]


def load_nagano_high_rank(html_path: Path | None = None) -> pd.DataFrame:
    """長野県体協 high_rank.html をパース

    Returns:
        DataFrame with columns:
        - kai_num: int or None (特別大会は None)
        - is_special: bool
        - era_raw: str ("R7", "S24" 等)
        - year: int (西暦)
        - host_raw: str ("滋賀県", "京阪神地方" 等)
        - cup: str ("tennou" or "kougou")
        - rank1 - rank8: str (都道府県名)
    """
    if html_path is None:
        html_path = REFS_DIR / "nagano_high_rank.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> in nagano_high_rank.html")

    records = []
    current_kai_ctx = None  # 天皇杯行から皇后杯行に継承する回情報

    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if not cells or cells[0] == "回":  # ヘッダ行 skip
            continue

        first = cells[0]
        # 天皇杯行 = 先頭が "回番号" or "特"
        if first == "皇后杯":
            if current_kai_ctx is None:
                continue
            # 皇后杯行は 1位-8位 (cells[1:9])
            ranks = [c.strip() for c in cells[1:9]]
            records.append({
                **current_kai_ctx,
                "cup": "kougou",
                **{f"rank{i+1}": ranks[i] if i < len(ranks) else None for i in range(8)},
            })
            continue

        # 天皇杯行 = 回番号 or "特"
        is_special = first == "特"
        kai_num: int | None = None if is_special else int(first) if first.isdigit() else None
        if kai_num is None and not is_special:
            continue  # 無効行

        era_raw = cells[1]
        year = parse_japanese_era(era_raw)
        host_raw = cells[2]

        # 「冬・夏・秋」列があるか (cells[4] = "冬・夏・秋" 等)
        has_season_col = len(cells) >= 5 and "・" in cells[4]

        ranks = _extract_rank_cells(cells, has_season_col)

        current_kai_ctx = {
            "kai_num": kai_num,
            "is_special": is_special,
            "era_raw": era_raw,
            "year": year,
            "host_raw": host_raw,
        }
        records.append({
            **current_kai_ctx,
            "cup": "tennou",
            **{f"rank{i+1}": ranks[i] if i < len(ranks) else None for i in range(8)},
        })

    return pd.DataFrame(records)


def load_jspo_kai_xls(kai_num: int, cup: str = "tennou") -> pd.DataFrame:
    """JSPO 第78回/第79回 xls (47県×競技クロス集計) をパース

    Args:
        kai_num: 78 or 79
        cup: "tennou" (天皇杯) or "kougou" (皇后杯)

    Returns:
        DataFrame (index=都道府県, columns=競技名+得点合計+順位等)
        列マッピングは xls 生 shape のまま返し、Phase 2 で正式マッピングを実装
    """
    if kai_num not in (78, 79):
        raise ValueError(f"kai_num must be 78 or 79 (xls 内訳公開年のみ), got {kai_num}")

    # ファイル名は kai によって異なる (79回 = deta typo, 78回 = data 正)
    fname = {
        79: "79_score_deta.xls",
        78: "78_score_data.xls",
    }[kai_num]
    path = REFS_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run Phase 1 冒頭タスクの xls DL 先に")

    sheet_name = {"tennou": "天皇杯都道府県順", "kougou": "皇后杯都道府県順"}[cup]

    df = pd.read_excel(path, sheet_name=sheet_name, engine="calamine", header=None)
    return df


# JSPO 78+79 xls の列マッピング (2026-07-28 実測)
# - 天皇杯: header row=5 (78) or 6 (79)・冬季3+本大会37 (79) or 38 (78=クレー射撃含む)
# - 皇后杯: header row=5 (78) or 6 (79)・冬季2+本大会32 (78) or 34 (79) (男子のみ = アイスホッケー/軟式野球/相撲/銃剣道 除外)
_XLS_HEADER_ROW: dict[int, int] = {78: 5, 79: 6}
_PREF_COL_HEADER = "都道府県名"
_NON_SPORT_HEADERS: frozenset[str] = frozenset({
    "", "都道府県名", "順位", "得点合計",
    "冬季小計", "冬季順位", "本大会小計", "本大会順位",
})
_WINTER_XLS_NAMES: frozenset[str] = frozenset({"スキー競技", "スケート競技", "アイスホッケー競技"})
_XLS_NAME_TO_CANONICAL: dict[str, str] = {
    "アイスホッケー競技": "アイスホッケー",
}


def parse_jspo_xls_long_format(kai_num: int, cup: str = "tennou") -> pd.DataFrame:
    """JSPO 78/79 の xls を 47県×競技 の long format DataFrame に変換

    副次分析 (analysis_cross_section_2024_2025.py) の基盤データ。

    Args:
        kai_num: 78 (2024佐賀・host敗北) or 79 (2025滋賀・host優勝)
        cup: "tennou" or "kougou"

    Returns:
        DataFrame columns:
        - pref_code: int (1-47)
        - pref_name: str
        - kai_num: int
        - year: int
        - cup: str
        - sport: str (競技正式名称・SPORT_CATEGORIES キーに整合)
        - score: float (小数得点あり)
        - is_winter: bool (冬季3競技: スキー競技/スケート競技/アイスホッケー)

        競技セット (2026-07-28 実測):
        - 78-tennou: 冬季3 + 本大会37 = 40 sports (クレー射撃あり・ボクシングなし)
        - 78-kougou: 冬季2 + 本大会33 = 35 sports (ボクシングなし)
        - 79-tennou: 冬季3 + 本大会37 = 40 sports (ボクシングあり・クレー射撃廃止)
        - 79-kougou: 冬季2 + 本大会34 = 36 sports (ボクシング追加)
        78→79 の入れ替え: クレー射撃廃止 + ボクシング追加 (男女とも)
    """
    from src.definitions import KOKUTAI_HOSTS, PREFECTURE_TO_CODE

    if kai_num not in (78, 79):
        raise ValueError(f"kai_num must be 78 or 79, got {kai_num}")
    if cup not in ("tennou", "kougou"):
        raise ValueError(f"cup must be 'tennou' or 'kougou', got {cup!r}")

    fname = {79: "79_score_deta.xls", 78: "78_score_data.xls"}[kai_num]
    path = REFS_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    sheet_name = {"tennou": "天皇杯都道府県順", "kougou": "皇后杯都道府県順"}[cup]
    wb = CalamineWorkbook.from_path(str(path))
    sheet = wb.get_sheet_by_name(sheet_name).to_python()

    header_row_idx = _XLS_HEADER_ROW[kai_num]
    header = [str(c).strip() for c in sheet[header_row_idx]]

    if _PREF_COL_HEADER not in header:
        raise ValueError(f"'{_PREF_COL_HEADER}' not found in header row {header_row_idx} of {fname}")
    pref_col = header.index(_PREF_COL_HEADER)

    sport_cols: list[tuple[int, str]] = [
        (i, name) for i, name in enumerate(header)
        if name and name not in _NON_SPORT_HEADERS
    ]

    year = KOKUTAI_HOSTS[kai_num]["year"]
    records = []

    for row_offset in range(1, 48):
        row_idx = header_row_idx + row_offset
        if row_idx >= len(sheet):
            break
        row = sheet[row_idx]
        pref_name_raw = str(row[pref_col]).strip() if pref_col < len(row) else ""
        if not pref_name_raw or pref_name_raw not in PREFECTURE_TO_CODE:
            continue
        pref_code = PREFECTURE_TO_CODE[pref_name_raw]

        for col_idx, xls_sport_name in sport_cols:
            if col_idx >= len(row):
                continue
            score = _parse_score_cell(row[col_idx])
            if score is None:
                continue
            canonical_sport = _XLS_NAME_TO_CANONICAL.get(xls_sport_name, xls_sport_name)
            records.append({
                "pref_code": pref_code,
                "pref_name": pref_name_raw,
                "kai_num": kai_num,
                "year": year,
                "cup": cup,
                "sport": canonical_sport,
                "score": score,
                "is_winter": xls_sport_name in _WINTER_XLS_NAMES,
            })

    return pd.DataFrame(records)


def _parse_score_cell(cell) -> float | None:
    """xls セルから float 得点を取り出す (trailing space + 小数対応)。値なしは None"""
    if cell is None:
        return None
    if isinstance(cell, (int, float)):
        return float(cell)
    s = str(cell).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_kendo_2016_iwate(html_path: Path | None = None) -> pd.DataFrame:
    """剣道 old2 第71回岩手 (2016) 総合得点表をパース

    Source: https://old2.kendo.or.jp/competition/kokutai/71st/result/
    主観判定副次データ = 剣道単一種目での host effect 検出用 (本論 novelty コア)。
    第71回2016年は全体総合では開催地敗北 (6ショック年の1つ) だが、
    剣道単体では岩手が 1位 (144点) 取得 = 主観判定競技での host effect 残存の実データ。

    Returns:
        DataFrame with columns:
        - rank: int (1-7・7位が3県同点)
        - pref_name: str ("岩手県" 等・英字/空白除去済み)
        - competition_score: float (競技得点・小数あり例: Ehime 62.5)
        - participation_score: float (参加得点)
        - total_score: float (合計得点)
    """
    if html_path is None:
        html_path = REFS_DIR / "kendo_2016_iwate_71st.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    tables = soup.find_all("table")
    # Table 1 が総合得点表 (10 rows: header + 10 順位)
    if len(tables) < 2:
        raise ValueError("Expected >= 2 tables in kendo HTML")

    target = tables[1]
    rows = target.find_all("tr")
    if len(rows) < 2:
        raise ValueError("Expected total-score table with header + rank rows")

    records = []
    for tr in rows[1:]:  # skip header
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 5:
            continue
        rank_m = re.match(r"^(\d+)\s*位", cells[0])
        if not rank_m:
            continue
        rank = int(rank_m.group(1))
        # 都道府県名から英字部分除去 ("岩手県　Iwate" → "岩手県")
        pref_raw = cells[1]
        pref_name = re.sub(r"[\sA-Za-z　]+$", "", pref_raw).strip()
        try:
            comp = float(cells[2])
            part = float(cells[3])
            total = float(cells[4])
        except ValueError:
            continue
        records.append({
            "rank": rank,
            "pref_name": pref_name,
            "competition_score": comp,
            "participation_score": part,
            "total_score": total,
        })

    return pd.DataFrame(records)


def load_nagano_game_score(html_path: Path | None = None) -> pd.DataFrame:
    """長野県体協 game_score.html 競技別得点表 (長野1県時系列) をパース

    Source: https://www.nagano-sports.or.jp/kokutai/record/game_score.html
    第71回2016〜第79回2025 + 特別大会2023 = 計10大会 × 41競技 (冬季3+本大会38) の
    長野1県 素点ベース副次比較用データ。

    集計行 (冬季計/本大会計/合計/ヘッダ再掲) は除外。空セルは NaN。

    Returns:
        DataFrame (long format):
        - competition_no: int (1-41)
        - competition_name: str
        - kai_label: str ("71"〜"79" or "special_2023")
        - year: int
        - score: float (NaN 可・長野無得点は NaN)
    """
    # 遅延 import (definitions は panel_builder でも import 済み・循環回避)
    from src.definitions import KOKUTAI_HOSTS, KOKUTAI_SPECIAL

    if html_path is None:
        html_path = REFS_DIR / "nagano_game_score.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> in nagano_game_score.html")

    rows = table.find_all("tr")
    if len(rows) < 2:
        raise ValueError("Expected header + data rows")

    # ヘッダ行から列 → (kai_label, year) マッピングを構築
    header_cells = [c.get_text(" ", strip=True) for c in rows[0].find_all(["td", "th"])]
    if header_cells[:2] != ["No", "競技名"]:
        raise ValueError(f"Unexpected header: {header_cells[:2]}")

    kai_cols: list[tuple[int, str, int]] = []  # (col_index, kai_label, year)
    for idx, h in enumerate(header_cells[2:], start=2):
        h_stripped = h.strip()
        if h_stripped == "特別":
            # 特別大会は 2023 鹿児島確定 (game_score.html 掲載は 2016年以降なので特別=2023 一択)
            year = KOKUTAI_SPECIAL["special_2023"]["year"]
            kai_cols.append((idx, "special_2023", year))
        else:
            m = re.match(r"^(\d+)回?$", h_stripped)
            if not m:
                continue
            kai_num = int(m.group(1))
            year = KOKUTAI_HOSTS[kai_num]["year"]
            kai_cols.append((idx, str(kai_num), year))

    records = []
    for tr in rows[1:]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 3:
            continue
        # No 列が整数の行のみ拾う (集計行/ヘッダ再掲を除外)
        no_str = cells[0].strip()
        if not no_str.isdigit():
            continue
        competition_no = int(no_str)
        competition_name = cells[1].strip()

        for col_idx, kai_label, year in kai_cols:
            if col_idx >= len(cells):
                continue
            raw = cells[col_idx].strip()
            if not raw:
                score = float("nan")
            else:
                try:
                    score = float(raw)
                except ValueError:
                    score = float("nan")
            records.append({
                "competition_no": competition_no,
                "competition_name": competition_name,
                "kai_label": kai_label,
                "year": year,
                "score": score,
            })

    return pd.DataFrame(records)


def load_jfa_soccer_history(html_path: Path | None = None) -> pd.DataFrame:
    """JFA サッカー歴代優勝チーム一覧をパース (客観記録競技リファレンス)

    Source: https://www.jfa.jp/match/nationalsportsfestival_2024/history.html
    第1-74回 (1946-2019) は「回・年・開催地・成年男子・少年男子」の5列一貫。
    第75回2020=[延期]/第76回2021=[中止] は cancelled 情報として winner=None で保持。
    第77回2022以降は 4部門化+rowspan で行構造が変わるため Phase 2 個別対応 (現段階では skip)。

    Returns:
        DataFrame with columns:
        - kai_num: int
        - year: int
        - host_raw: str
        - adult_male_winner: str or None ([延期]/[中止] 時は None)
        - youth_male_winner: str or None
        - status: str ("normal"/"postponed"/"cancelled")
    """
    if html_path is None:
        html_path = REFS_DIR / "jfa_soccer_history.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> in JFA HTML")

    records = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 3:
            continue
        # 回列が整数の行のみ (rowspan による欠落行 + ヘッダ再掲行を除外)
        if not cells[0].strip().isdigit():
            continue
        kai_num = int(cells[0])
        # 年列 "1946 (昭和21年)" → 1946 を抽出
        year_m = re.match(r"^(\d{4})", cells[1].strip())
        if not year_m:
            continue
        year = int(year_m.group(1))
        host_raw = cells[2].strip()

        # 第75/76回の [延期]/[中止] は cells[3] に該当キーワード
        adult = cells[3].strip() if len(cells) > 3 else ""
        youth = cells[4].strip() if len(cells) > 4 else ""

        if "延期" in adult:
            status = "postponed"
            adult_val: str | None = None
            youth_val: str | None = None
        elif "中止" in adult:
            status = "cancelled"
            adult_val = None
            youth_val = None
        elif adult == "成年男子":
            # 第77回以降の4部門化ヘッダ再掲行 → skip (Phase 2 個別対応)
            continue
        else:
            status = "normal"
            adult_val = adult if adult else None
            youth_val = youth if youth else None

        records.append({
            "kai_num": kai_num,
            "year": year,
            "host_raw": host_raw,
            "adult_male_winner": adult_val,
            "youth_male_winner": youth_val,
            "status": status,
        })

    return pd.DataFrame(records)


def load_jihf_hockey(html_path: Path | None = None) -> pd.DataFrame:
    """JIHF アイスホッケー歴代成績をパース (客観記録競技リファレンス)

    Source: https://www.jihf.or.jp/watching_games/tournament/detail.php?meet_id=6
    第1回1947 (八戸) 〜 第67回2012 (名古屋他) までカバー・2012年で更新停止。
    ヘッダ2行 (メイン+サブ「優勝/2位/3位」) + データ66行の10列構造。

    Returns:
        DataFrame with columns:
        - kai_num: int
        - year: int
        - venue_raw: str (アイスホッケー会場地名・国体全体開催地とは別)
        - adult_1st, adult_2nd, adult_3rd: str (一般/成年カテゴリ)
        - youth_1st, youth_2nd, youth_3rd: str (高校/少年カテゴリ)
        - tennou_score_1st: str (天皇杯 得点1位・"-" は None)
    """
    if html_path is None:
        html_path = REFS_DIR / "jihf_hockey_meet6.html"
    if not html_path.exists():
        raise FileNotFoundError(f"{html_path} not found")

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> in JIHF HTML")

    records = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 10:
            continue
        # 「回」列が「N回」パターンの行のみ
        m = re.match(r"^(\d+)回$", cells[0].strip())
        if not m:
            continue
        kai_num = int(m.group(1))
        # 「年」列 "1947年" → 1947
        ym = re.match(r"^(\d{4})", cells[1].strip())
        if not ym:
            continue
        year = int(ym.group(1))

        def _clean(s: str) -> str | None:
            s = s.strip()
            if s in ("－", "-", ""):
                return None
            return s

        records.append({
            "kai_num": kai_num,
            "year": year,
            "venue_raw": cells[2].strip(),
            "adult_1st": _clean(cells[3]),
            "adult_2nd": _clean(cells[4]),
            "adult_3rd": _clean(cells[5]),
            "youth_1st": _clean(cells[6]),
            "youth_2nd": _clean(cells[7]),
            "youth_3rd": _clean(cells[8]),
            "tennou_score_1st": _clean(cells[9]),
        })

    return pd.DataFrame(records)


def load_jspo_kai_pdf(kai_num: int, cup: str = "tennou") -> pd.DataFrame:
    """JSPO 個別回 PDF から総合成績 (47県 順位/得点) を抽出

    Scope: 規則的パス `data0/kokutai/{kai}/{kai}_{cup}.pdf` 対応の第58-67回 (2003-2012)。
    第68回2013 東京 以降は不規則 URL + 画像PDFで抽出困難 → Phase 2 個別対応。

    PDF フォーマット:
    - 6列レイアウト (都道府県順3列 + 成績順3列)
    - 各行: 「県名 N位 得点」× 2セット
    - 都道府県順 (左3列) から 47県分の (順位, 得点) を抽出

    Args:
        kai_num: 58-67
        cup: "tennou" (天皇杯) or "kougou" (皇后杯)

    Returns:
        DataFrame with columns:
        - kai_num: int
        - cup: str
        - pref_name: str (canonical 47県名)
        - rank: int (1-47)
        - score: float (小数対応)
    """
    if not (JSPO_PDF_RANGE[0] <= kai_num <= JSPO_PDF_RANGE[1]):
        raise ValueError(
            f"kai_num must be in {JSPO_PDF_RANGE[0]}-{JSPO_PDF_RANGE[1]} "
            f"(Phase 1 中盤 規則的パス対応範囲), got {kai_num}"
        )
    if cup not in ("tennou", "kougou"):
        raise ValueError(f"cup must be tennou or kougou, got {cup}")

    path = JSPO_PDF_DIR / f"{kai_num}_{cup}.pdf"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    # 都道府県 canonical マッピング (definitions への循環回避のため lazy import)
    from src.definitions import PREFECTURE_TO_CODE

    with pdfplumber.open(path) as pdf:
        text = "\n".join(
            (page.extract_text() or "") for page in pdf.pages
        )

    records = []
    seen: set[str] = set()
    line_re = re.compile(r"^(\S+)\s+(\d+)位\s+([\d.]+)")

    for line in text.split("\n"):
        m = line_re.match(line.strip())
        if not m:
            continue
        pref_raw = m.group(1).strip()
        # 47県名に正規化 (「北海道」はそのまま JIS 001)
        pref_name = pref_raw if pref_raw in PREFECTURE_TO_CODE else None
        if not pref_name or pref_name in seen:
            continue
        seen.add(pref_name)
        rank = int(m.group(2))
        score = float(m.group(3))
        records.append({
            "kai_num": kai_num,
            "cup": cup,
            "pref_name": pref_name,
            "rank": rank,
            "score": score,
        })

    df = pd.DataFrame(records)
    if len(df) != 47:
        raise ValueError(
            f"Expected 47 prefectures in {path.name}, got {len(df)}. "
            f"PDF format may have changed."
        )
    return df


def list_available_jspo_pdfs() -> dict[int, list[str]]:
    """refs/jspo_pdf/ に保存済み PDF を回番号でグルーピング"""
    result: dict[int, list[str]] = {}
    if not JSPO_PDF_DIR.exists():
        return result
    for f in sorted(JSPO_PDF_DIR.glob("*.pdf")):
        m = re.match(r"^(\d+)_(tennou|kougou)\.pdf$", f.name)
        if m:
            kai = int(m.group(1))
            result.setdefault(kai, []).append(f.name)
    return result


# ============================================================
# ESRI 県民経済計算 (Phase 1 後半・Deviation #3)
# ============================================================
# ソース: 内閣府 経済社会総合研究所 (ESRI) 県民経済計算 令和4年度版
# URL: https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/files/contents/main_2022.html
# カバー: 平成23年度 (2011) 〜 令和4年度 (2022) の 12年分・47都道府県
# 基準: 2008SNA・平成27年基準
# フォーマット: soukatu*.xlsx (79行×16列・47県=行6-52・年=列3-14・sheet="実数")
#
# 提供ラッパ:
# - load_esri_population()   = soukatu9 (総人口・単位 人)
# - load_esri_gdp_nominal()  = soukatu1 (名目県内総生産・単位 100万円)

ESRI_DIR = REFS_DIR / "esri" / "main_2022"


def load_esri_soukatu(file_path: Path, sheet: str = "実数") -> pd.DataFrame:
    """ESRI 県民経済計算 総括表 (soukatu*.xlsx) の汎用パーサ

    共通フォーマット:
    - 79行×16列・sheet=['実数', '増加率']
    - 行6-52 = 47都道府県 (JIS X0401 コード col=0 / 名 col=1)
    - 列3-14 = 12年分 (平成23年度=2011 〜 令和4年度=2022)
    - 行53以降 = 全県計/地域ブロック/政令指定都市 (除外)

    Returns:
        long DataFrame: [pref_code (int), pref_name (str), year (int), value (float)]
        47県 × 12年 = 564 レコード
    """
    df = pd.read_excel(file_path, sheet_name=sheet, engine="calamine", header=None)

    pref_block = df.iloc[6:53, [0, 1]].copy()
    pref_block.columns = ["pref_code", "pref_name"]
    pref_block["pref_code"] = pref_block["pref_code"].astype(int)
    pref_block.reset_index(drop=True, inplace=True)

    year_row = df.iloc[4, 3:15].astype(int).tolist()

    values = df.iloc[6:53, 3:15].copy()
    values.columns = year_row
    values.reset_index(drop=True, inplace=True)

    wide = pd.concat([pref_block, values], axis=1)
    long = wide.melt(
        id_vars=["pref_code", "pref_name"],
        var_name="year",
        value_name="value",
    )
    long["year"] = long["year"].astype(int)
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    return long.reset_index(drop=True)


def load_esri_population(refs_dir: Path | None = None) -> pd.DataFrame:
    """ESRI soukatu9 = 47県 総人口 (2011-2022 の 12年) を long format で返却

    Returns:
        DataFrame [pref_code, pref_name, year, population] (単位: 人・47県×12年=564行)
    """
    base = refs_dir or ESRI_DIR
    return load_esri_soukatu(base / "soukatu9.xlsx").rename(columns={"value": "population"})


def load_esri_gdp_nominal(refs_dir: Path | None = None) -> pd.DataFrame:
    """ESRI soukatu1 = 47県 名目県内総生産 (2011-2022 の 12年) を long format で返却

    Returns:
        DataFrame [pref_code, pref_name, year, gdp_nominal_mil_yen] (単位: 100万円・47県×12年=564行)
    """
    base = refs_dir or ESRI_DIR
    return load_esri_soukatu(base / "soukatu1.xlsx").rename(columns={"value": "gdp_nominal_mil_yen"})


def list_available_xls() -> dict[int, list[str]]:
    """refs/ ディレクトリに保存済みの xls ファイルを回番号でグルーピング"""
    result: dict[int, list[str]] = {}
    for f in sorted(REFS_DIR.glob("*.xls*")):
        m = re.match(r"^(\d+)", f.name)
        if m:
            kai = int(m.group(1))
            result.setdefault(kai, []).append(f.name)
    return result
