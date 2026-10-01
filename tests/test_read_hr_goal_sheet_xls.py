"""目標管理シートExcelの枝番セル読取を検証する。"""

from __future__ import annotations

from scripts.read_hr_goal_sheet_xls import _format_text, extract_branch


def test_extract_branch_reads_evaluation_columns() -> None:
    """枝番ごとのCH列・CJ列を本人評価・補助評価として取得する。"""
    values = {
        (18, "CH"): "○",
        (18, "CJ"): "△",
    }

    branch = extract_branch(lambda row, column: values.get((row, column), ""), 1)

    assert branch["evaluation_self_ch"] == "○"
    assert branch["evaluation_assist_cj"] == "△"


def test_format_text_displays_evaluation_columns() -> None:
    """テキスト出力にCH列・CJ列の評価値を含める。"""
    branch = extract_branch(
        lambda row, column: {
            (18, "CH"): "○",
            (18, "CJ"): "△",
        }.get((row, column), ""),
        1,
    )
    data = {"path": "sample.xlsx", "sheet": "目標管理シート", "backend": "test"}
    data["header"] = {
        "name_bh4": "",
        "grade_bs4": "",
        "staff_bf6_raw": "",
        "staff_number_6digits": "",
        "year_bi1": "",
        "half_bm1": "",
    }
    data["computed"] = {"period_from_bi1_rule": None}
    data["branches"] = [branch]

    formatted = _format_text(data)

    assert "本人評価 CH18: ○" in formatted
    assert "補助評価 CJ18: △" in formatted
