from pathlib import Path

from scripts.check_spec_task_ids import scan_file


def test_scan_file_ignores_f_prefixed_product_model_codes(tmp_path: Path):
    """F数字から始まるロッド型番は、計画用タスクIDとして扱わない。"""
    spec = tmp_path / "spec.md"
    spec.write_text(
        "型番 `F0-68XSTZ` と `F2-66XTZSPARNA`、分類 `F7/F9` は製品コード。\n",
        encoding="utf-8",
    )

    assert scan_file(spec) == []


def test_scan_file_detects_plain_task_id(tmp_path: Path):
    """独立した Fxx は、従来どおり計画用タスクIDとして検出する。"""
    spec = tmp_path / "spec.md"
    spec.write_text("この仕様は F12 を参照しない。\n", encoding="utf-8")

    hits = scan_file(spec)
    assert len(hits) == 1
    assert hits[0][1] == "Fxx タスク ID"
