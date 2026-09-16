"""釣行メモの使用ルアー節検査が実釣行だけを対象にすることを検証する。"""

from __future__ import annotations

from pathlib import Path

from scripts.check_trip_memo_lure_sections import check_file


def test_check_file_ignores_preamble_and_fenced_examples(tmp_path: Path) -> None:
    """先頭の説明とコード例の悪い行は違反にしない。"""
    path = tmp_path / "memo.md"
    path.write_text(
        "\n".join(
            [
                "# 釣行メモ",
                "",
                "### 使用ルアー（FishTrack ルアー紐づけ）",
                "",
                "- **基本形**: `- **リグ種別（任意）**: **製品名** — カラー（任意）`",
                "",
                "```text",
                "### 使用ルアー",
                "- **ミミキング**: サイトで進行方向に浮かせて44cmをキャッチ",
                "```",
                "",
                "## 2026-09-01 — 三島湖（国民宿舎前）",
                "",
                "### 使用ルアー",
                "",
                "- **ワーム**: **ギミー** — **DARK KUWASE**",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert check_file(path) == []


def test_check_file_allows_unresolved_suffix(tmp_path: Path) -> None:
    """import 後の未突合印は体裁違反にしない。"""
    path = tmp_path / "memo.md"
    path.write_text(
        "\n".join(
            [
                "## 2026-09-01 — 三島湖（国民宿舎前）",
                "",
                "### 使用ルアー",
                "",
                "- **ワーム**: **ギミー** （未突合）",
                "- **トレーラー**: **ギミー** — **DARK KUWASE** （曖昧）",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert check_file(path) == []


def test_check_file_allows_inch_size_in_product_name(tmp_path: Path) -> None:
    """製品名のインチ表記は釣果サイズとみなさない。Gimmy の mm も誤検知しない。"""
    path = tmp_path / "memo.md"
    path.write_text(
        "\n".join(
            [
                "## 2026-06-06 — 戸面原ダム（バックウォーター）",
                "",
                "### 使用ルアー",
                "",
                "- **トレーラー**: **Gimmy 3.5インチ** （未突合）",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert check_file(path) == []


def test_check_file_flags_catch_size_units(tmp_path: Path) -> None:
    """釣果の cm/mm は使用ルアー節では違反にする。"""
    path = tmp_path / "memo.md"
    path.write_text(
        "\n".join(
            [
                "## 2026-09-01 — 三島湖（国民宿舎前）",
                "",
                "### 使用ルアー",
                "",
                "- **ワーム**: **ミミキング** 44cm",
                "- **ワーム**: **ミミキング** 10mm",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    violations = check_file(path)
    assert any("cm" in item for item in violations)
    assert any("mm" in item for item in violations)


def test_check_file_flags_result_text_in_trip_lure_section(tmp_path: Path) -> None:
    """実釣行の使用ルアー節に結果語があれば違反にする。"""
    path = tmp_path / "memo.md"
    path.write_text(
        "\n".join(
            [
                "## 2026-09-01 — 三島湖（国民宿舎前）",
                "",
                "### 使用ルアー",
                "",
                "- **ライトリグ**: 反応なし",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    violations = check_file(path)
    assert len(violations) >= 1
    assert "反応なし" in violations[0]
