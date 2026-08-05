#!/usr/bin/env python3
"""新人OJT月報Excelを読み取り、管理ノート用の転記ブロックをstdoutへ出力する。

このツールは月報Excelを正本として扱い、Markdownファイルを直接更新しない。
Excelセルの本文は、改行・箇条書き記号を含めて変換せずに出力する。
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import xml.etree.ElementTree as element_tree
import zipfile
from pathlib import Path
from typing import Final
from uuid import uuid4


WORKSHEET_PATH: Final = "xl/worksheets/sheet1.xml"
SHARED_STRINGS_PATH: Final = "xl/sharedStrings.xml"
SPREADSHEET_NAMESPACE: Final = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NAMESPACE: Final = {"sheet": SPREADSHEET_NAMESPACE}
REPORT_CELLS: Final = {
    "year": "C9",
    "month": "H9",
    "duty_status": "B12",
    "next_month_plan": "L12",
    "opinion": "B14",
    "trainer_comment": "L14",
    "manager_comment": "B17",
}
TEMP_DIR: Final = Path(__file__).resolve().parents[1] / "temp"


def _text_without_phonetics(node: element_tree.Element) -> str:
    """セル本文だけを結合し、Excelのふりがな要素は除外する。"""
    text_tag = f"{{{SPREADSHEET_NAMESPACE}}}t"
    rich_text_tag = f"{{{SPREADSHEET_NAMESPACE}}}r"
    parts: list[str] = []
    for child in node:
        if child.tag == text_tag:
            parts.append(child.text or "")
        elif child.tag == rich_text_tag:
            text = child.find("sheet:t", NAMESPACE)
            if text is not None:
                parts.append(text.text or "")
    return "".join(parts)


def _shared_strings(workbook: zipfile.ZipFile) -> list[str]:
    """共有文字列テーブルを読み、セルの文字列インデックスを復元する。"""
    if SHARED_STRINGS_PATH not in workbook.namelist():
        return []

    root = element_tree.fromstring(workbook.read(SHARED_STRINGS_PATH))
    return [_text_without_phonetics(node) for node in root.findall("sheet:si", NAMESPACE)]


def _cell_text(cell: element_tree.Element, shared_strings: list[str]) -> str:
    """Excelセルを表示用テキストへ変換し、空欄は空文字列として扱う。"""
    cell_type = cell.get("t")
    value = cell.find("sheet:v", NAMESPACE)
    if cell_type == "inlineStr":
        inline = cell.find("sheet:is", NAMESPACE)
        return _text_without_phonetics(inline) if inline is not None else ""
    if value is None:
        return ""
    if cell_type == "s":
        return shared_strings[int(value.text)]
    return value.text or ""


def _read_cells(path: Path) -> dict[str, str]:
    """xlsxを開き、固定様式の月報で参照するセルをアドレス別に返す。"""
    with zipfile.ZipFile(path) as workbook:
        if WORKSHEET_PATH not in workbook.namelist():
            msg = f"月報の先頭シートが見つかりません: {path}"
            raise ValueError(msg)
        shared_strings = _shared_strings(workbook)
        worksheet = element_tree.fromstring(workbook.read(WORKSHEET_PATH))

    cells = {
        cell.get("r", ""): _cell_text(cell, shared_strings)
        for cell in worksheet.findall(".//sheet:c", NAMESPACE)
    }
    return {name: cells.get(address, "") for name, address in REPORT_CELLS.items()}


def _read_via_temp_copy(path: Path) -> dict[str, str]:
    """OneDriveの排他ロックを避け、リポジトリ内tempコピーを読んで即時削除する。"""
    TEMP_DIR.mkdir(exist_ok=True)
    staged_path = TEMP_DIR / f"ojt-monthly-report-{uuid4().hex}.xlsx"
    try:
        shutil.copy2(path, staged_path)
        return _read_cells(staged_path)
    finally:
        staged_path.unlink(missing_ok=True)


def read_monthly_report(path: Path) -> dict[str, str]:
    """固定様式の月報Excelから、管理ノートに必要な7項目だけを取得する。"""
    if path.suffix.lower() != ".xlsx":
        msg = f".xlsx ファイルのみ対応しています: {path}"
        raise ValueError(msg)

    return _read_via_temp_copy(path)


def _display_text(value: str) -> str:
    """Excelの未入力セルを管理ノートで判別可能な表記へ変換する。"""
    return value if value.strip() else "（未記載）"


def format_note_section(report: dict[str, str]) -> str:
    """セル本文を変換せず、管理ノートの月別節として配置する。"""
    try:
        year = int(report["year"].strip())
        month = int(report["month"].strip())
    except (KeyError, ValueError) as error:
        msg = "報告対象の年または月がExcelから取得できません。"
        raise ValueError(msg) from error

    sections = (
        ("執務状況（実績と反省）", report.get("duty_status", "")),
        ("次月目標および予定", report.get("next_month_plan", "")),
        ("意見または所感", report.get("opinion", "")),
        ("OJTトレーナーより", report.get("trainer_comment", "")),
        ("上長フォローコメント", report.get("manager_comment", "")),
    )
    lines = [f"## {year}年{month}月"]
    for heading, content in sections:
        lines.extend(("", f"### {heading}", "", _display_text(content)))
    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI入力を検証し、JSONまたはセル本文を保持した転記ブロックを標準出力へ送る。"""
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="新人OJT月報Excelを読み、セル本文を変換せずstdoutへ出力します。",
    )
    parser.add_argument("path", type=Path, help="月報の .xlsx ファイル")
    parser.add_argument(
        "--format",
        choices=("note", "json"),
        default="note",
        help="出力形式（既定: note）",
    )
    args = parser.parse_args()

    if not args.path.is_file():
        parser.error(f"ファイルが見つかりません: {args.path}")

    try:
        report = read_monthly_report(args.path)
        output = (
            format_note_section(report)
            if args.format == "note"
            else json.dumps(report, ensure_ascii=False, indent=2)
        )
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))

    print(output)


if __name__ == "__main__":
    main()
