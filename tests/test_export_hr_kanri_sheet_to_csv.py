"""人事考課管理シートのCSV出力を検証する。"""

from __future__ import annotations

from scripts.export_hr_kanri_sheet_to_csv import CSV_HEADER, parse_md, rows_to_csv


def test_parse_md_reads_half_year_evaluation_fields() -> None:
    """Markdownの半期別評価見出しを独立したCSV項目として読み取る。"""
    text = """\
## 55期

### 55期 寺崎　達也

- **メンバー**: 寺崎　達也 ／ **等級**: G3 ／ **社員番号**: 077981

#### 55期 寺崎　達也 1

- **目標ジャンル**: 案件管理

##### 上期本人評価 — 55期 寺崎　達也 1

△

##### 上期補助評価 — 55期 寺崎　達也 1

○

##### 下期本人評価 — 55期 寺崎　達也 1

×
"""

    rows = parse_md(text)

    assert rows[0]["上期本人評価"] == "△"
    assert rows[0]["上期補助評価"] == "○"
    assert rows[0]["下期本人評価"] == "×"
    assert rows[0]["下期補助評価"] == ""


def test_rows_to_csv_includes_half_year_evaluation_columns() -> None:
    """CSVヘッダーに半期別の本人評価・補助評価列を含める。"""
    assert "上期本人評価" in CSV_HEADER
    assert "上期補助評価" in CSV_HEADER
    assert "下期本人評価" in CSV_HEADER
    assert "下期補助評価" in CSV_HEADER

    csv_text = rows_to_csv(
        [
            {
                "期": "55",
                "メンバー": "寺崎　達也",
                "上期本人評価": "△",
                "上期補助評価": "○",
            }
        ]
    )

    assert "上期本人評価" in csv_text.splitlines()[0]
    assert "△" in csv_text
    assert "○" in csv_text
