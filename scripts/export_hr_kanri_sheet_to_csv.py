#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人事考課_管理シート.md を読み取り、Excel 作業用 CSV を stdout に出力する（書き込みは行わない）。

- 1 行 = 1 枝番（#### ブロック）。列は期・メンバー・等級・社員番号・枝番・目標ジャンル + 17 項目。
- <改善案> ブロックは CSV に含めない（校閲メタは Markdown のみ）。
- mokuhyo-kanri-sheet-csv SKILL の全量再生成に使用。

使用例:
  python scripts/export_hr_kanri_sheet_to_csv.py
  python scripts/export_hr_kanri_sheet_to_csv.py --md "D:/.../人事考課_管理シート.md"
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

DEFAULT_MD = Path(
    "D:/OneDrive/アプリ/remotely-save/Obsidian/Work/社内業務/人事考課/人事考課_管理シート.md"
)

FIELD_NAMES: tuple[str, ...] = (
    "通期目標",
    "上期目標",
    "下期目標",
    "通期達成基準（ターゲット）",
    "通期達成基準（ミニマム）",
    "上期達成基準（ターゲット）",
    "上期達成基準（ミニマム）",
    "下期達成基準（ターゲット）",
    "下期達成基準（ミニマム）",
    "チャレンジ度",
    "ウェイト",
    "設定理由（本人）",
    "設定時コメント(補助・１次調整者)",
    "上期達成状況コメント(本人)",
    "上期達成状況コメント(補助・１次評価者)",
    "下期達成状況コメント(本人)",
    "下期達成状況コメント(補助・１次評価者)",
)

CSV_HEADER: tuple[str, ...] = (
    "期",
    "メンバー",
    "等級",
    "社員番号",
    "枝番",
    "目標ジャンル",
) + FIELD_NAMES

RE_PERIOD = re.compile(r"^##\s+(\d+)期\s*$")
RE_MEMBER = re.compile(r"^###\s+(\d+)期\s+(.+?)\s*$")
RE_BRANCH = re.compile(r"^####\s+(\d+)期\s+(.+?)\s+(\d+)\s*$")
RE_FIELD = re.compile(r"^#####\s+(.+?)\s+—\s+")
RE_MEMBER_LINE = re.compile(
    r"^\-\s+\*\*メンバー\*\*:\s*(.+?)\s+／\s+\*\*等級\*\*:\s*(.+?)\s+／\s+\*\*社員番号\*\*:\s*(\d+)\s*$"
)
RE_GENRE = re.compile(r"^\-\s+\*\*目標ジャンル\*\*:\s*(.+?)\s*$")


def _is_section_boundary(line: str) -> bool:
    s = line.strip()
    return s.startswith("## ") or s.startswith("### ") or s.startswith("#### ") or s.startswith("##### ")


def _skip_kaizen(lines: list[str], start: int) -> int:
    """<改善案> … </改善案> をスキップし、次のインデックスを返す。"""
    i = start
    while i < len(lines):
        if lines[i].strip() == "<改善案>":
            i += 1
            while i < len(lines) and lines[i].strip() != "</改善案>":
                i += 1
            if i < len(lines):
                i += 1
            continue
        if _is_section_boundary(lines[i]):
            break
        i += 1
    return i


def _extract_body(lines: list[str], start: int) -> tuple[str, int]:
    """##### 直下の本文（<改善案> 除外）と次インデックス。"""
    body_lines: list[str] = []
    i = start
    while i < len(lines):
        if lines[i].strip() == "<改善案>":
            i = _skip_kaizen(lines, i)
            continue
        if _is_section_boundary(lines[i]):
            break
        body_lines.append(lines[i])
        i += 1
    body = "\n".join(body_lines).strip("\n")
    return body, i


def parse_md(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    rows: list[dict[str, str]] = []
    i = 0
    current_period = ""
    member_name = ""
    grade = ""
    employee_id = ""

    while i < len(lines):
        line = lines[i]

        m_period = RE_PERIOD.match(line)
        if m_period:
            current_period = m_period.group(1)
            i += 1
            continue

        m_member = RE_MEMBER.match(line)
        if m_member:
            member_name = m_member.group(2).strip()
            grade = ""
            employee_id = ""
            i += 1
            if i < len(lines):
                m_info = RE_MEMBER_LINE.match(lines[i].strip())
                if m_info:
                    member_name = m_info.group(1).strip()
                    grade = m_info.group(2).strip()
                    employee_id = m_info.group(3).strip()
                    i += 1
            continue

        m_branch = RE_BRANCH.match(line)
        if m_branch:
            branch_num = m_branch.group(3)
            genre = ""
            fields: dict[str, str] = {name: "" for name in FIELD_NAMES}
            i += 1
            while i < len(lines) and not RE_BRANCH.match(lines[i]) and not RE_MEMBER.match(lines[i]) and not RE_PERIOD.match(lines[i]):
                if lines[i].strip() == "<改善案>":
                    i = _skip_kaizen(lines, i)
                    continue
                m_genre = RE_GENRE.match(lines[i].strip())
                if m_genre:
                    genre = m_genre.group(1).strip()
                    i += 1
                    continue
                m_field = RE_FIELD.match(lines[i])
                if m_field:
                    field_name = m_field.group(1).strip()
                    i += 1
                    body, i = _extract_body(lines, i)
                    if field_name in fields:
                        fields[field_name] = body
                    continue
                i += 1

            row: dict[str, str] = {
                "期": current_period,
                "メンバー": member_name,
                "等級": grade,
                "社員番号": employee_id,
                "枝番": branch_num,
                "目標ジャンル": genre,
            }
            row.update(fields)
            rows.append(row)
            continue

        i += 1

    return rows


def rows_to_csv(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(CSV_HEADER), lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in CSV_HEADER})
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description="人事考課_管理シート.md → CSV（stdout）")
    parser.add_argument(
        "--md",
        type=Path,
        default=DEFAULT_MD,
        help=f"管理シート Markdown（既定: {DEFAULT_MD}）",
    )
    args = parser.parse_args()
    md_path: Path = args.md
    if not md_path.is_file():
        print(f"error: file not found: {md_path}", file=sys.stderr)
        return 1
    text = md_path.read_text(encoding="utf-8")
    rows = parse_md(text)
    # Excel（Windows）での文字化け防止のため BOM 付き UTF-8
    sys.stdout.buffer.write(rows_to_csv(rows).encode("utf-8-sig"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
