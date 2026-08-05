"""新人OJT月報Excelの読取・Markdown整形を検証する。"""

from __future__ import annotations

import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as element_tree
from pathlib import Path
from subprocess import run
from sys import executable

from scripts.read_ojt_monthly_report_xlsx import (
    _text_without_phonetics,
    format_note_section,
    read_monthly_report,
)


def _write_monthly_report_xlsx(path: Path) -> None:
    """固定様式で参照するセルだけを含む最小のxlsxファイルを作成する。"""
    strings = [
        "実績\n・原文の箇条書き",
        "次月の予定",
        "意見",
        "トレーナーコメント",
        "上長フォローコメント",
    ]
    shared_strings = "".join(f"<si><t>{text}</t></si>" for text in strings)
    cells = """
        <c r="C9"><v>2026</v></c>
        <c r="H9"><v>7</v></c>
        <c r="B12" t="s"><v>0</v></c>
        <c r="L12" t="s"><v>1</v></c>
        <c r="B14" t="s"><v>2</v></c>
        <c r="L14" t="s"><v>3</v></c>
        <c r="B17" t="s"><v>4</v></c>
    """
    with zipfile.ZipFile(path, "w") as workbook:
        workbook.writestr(
            "xl/sharedStrings.xml",
            f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"{shared_strings}</sst>",
        )
        workbook.writestr(
            "xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"<sheetData><row>{cells}</row></sheetData></worksheet>",
        )


class TestReadOjtMonthlyReportXlsx(unittest.TestCase):
    """新人OJT月報Excelの読取とMarkdown整形を検証する。"""

    def test_text_without_phonetics_excludes_excel_ruby(self) -> None:
        """Excelのふりがな要素は転記本文へ含めない。"""
        node = element_tree.fromstring(
            '<si xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<t>上長コメント</t><rPh sb=\"0\" eb=\"2\"><t>ジョウチョウ</t></rPh></si>",
        )

        self.assertEqual(_text_without_phonetics(node), "上長コメント")

    def test_read_monthly_report_extracts_fixed_template_cells(self) -> None:
        """固定様式のセルから月報に必要な項目をすべて取得する。"""
        with tempfile.TemporaryDirectory() as directory:
            workbook = Path(directory) / "monthly_report.xlsx"
            _write_monthly_report_xlsx(workbook)

            report = read_monthly_report(workbook)

        self.assertEqual(
            report,
            {
                "year": "2026",
                "month": "7",
                "duty_status": "実績\n・原文の箇条書き",
                "next_month_plan": "次月の予定",
                "opinion": "意見",
                "trainer_comment": "トレーナーコメント",
                "manager_comment": "上長フォローコメント",
            },
        )

    def test_format_note_section_marks_blank_cells_as_unrecorded(self) -> None:
        """Excelで空欄の項目は管理ノートで未記載と分かるように出力する。"""
        markdown = format_note_section(
            {
                "year": "2026",
                "month": "7",
                "duty_status": "実績",
                "next_month_plan": "予定",
                "opinion": "",
                "trainer_comment": "所見",
                "manager_comment": "",
            },
        )

        self.assertTrue(markdown.startswith("## 2026年7月\n"))
        self.assertIn("### 意見または所感\n\n（未記載）", markdown)
        self.assertIn("### 上長フォローコメント\n\n（未記載）", markdown)
        self.assertIn("### 執務状況（実績と反省）\n\n実績", markdown)

    def test_read_monthly_report_rejects_non_xlsx_files(self) -> None:
        """xlsx以外の入力を明示的に拒否し、誤った帳票を取り込ませない。"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "monthly_report.xls"
            source.write_text("not an Excel workbook", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, r"\.xlsx ファイルのみ対応"):
                read_monthly_report(source)

    def test_cli_outputs_utf8_for_excel_text(self) -> None:
        """コンソールの既定文字コードにかかわらず、Excel本文をUTF-8で出力する。"""
        with tempfile.TemporaryDirectory() as directory:
            workbook = Path(directory) / "monthly_report.xlsx"
            _write_monthly_report_xlsx(workbook)
            script = Path(__file__).parents[1] / "scripts" / "read_ojt_monthly_report_xlsx.py"

            result = run(
                [executable, str(script), str(workbook)],
                check=True,
                capture_output=True,
                encoding="utf-8",
            )

        self.assertIn("・原文の箇条書き", result.stdout)
