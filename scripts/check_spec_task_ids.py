#!/usr/bin/env python3
# Why: 仕様書に計画用タスク ID が混入していないかを機械検出する（specification-update SKILL 準拠）。

from __future__ import annotations

import re
import sys
from pathlib import Path

# ゲーム略号 FRLG は \bF[0-9] にマッチしない。OCR は \bO[0-9] にマッチしない。
_PAT_TASK_F = re.compile(r"\bF[0-9]{1,3}\b")
_PAT_TASK_O = re.compile(r"\bO[0-9]{1,3}\b")
_PAT_TASK_P_LAYER = re.compile(r"P[0-9]{1,2}-[0-9A-Za-z-]+")  # P1-4-T17
_PAT_SCHED_ANCHOR = re.compile(r"統合作業スケジュール#P[0-9]")
_PAT_BOLD_P = re.compile(r"\*\*P[0-9]{1,2}\*\*")
_PAT_BOLD_F = re.compile(r"\*\*F[0-9]{1,3}\*\*")
_PAT_BOLD_O = re.compile(r"\*\*O[0-9]{1,3}\*\*")
_PAT_PAREN_F = re.compile(r"（F[0-9]{1,3}）")
_PAT_PAREN_O = re.compile(r"（O[0-9]{1,3}）")
_PAT_PAREN_P = re.compile(r"（P[0-9]{1,2}）")
_PAT_HEADING_F = re.compile(r"^####\s+F[0-9]{1,3}\s")

PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (_PAT_TASK_F, "Fxx タスク ID"),
    (_PAT_TASK_O, "Oxx タスク ID"),
    (_PAT_TASK_P_LAYER, "P 階層タスク ID（例: P1-4-T17）"),
    (_PAT_SCHED_ANCHOR, "統合作業スケジュールのアンカーに P 番号"),
    (_PAT_BOLD_P, "**Pxx** 形式"),
    (_PAT_BOLD_F, "**Fxx** 形式"),
    (_PAT_BOLD_O, "**Oxx** 形式"),
    (_PAT_PAREN_F, "（Fxx）形式"),
    (_PAT_PAREN_O, "（Oxx）形式"),
    (_PAT_PAREN_P, "（Pxx）形式"),
    (_PAT_HEADING_F, "見出し Fxx"),
]


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [(0, "", f"{path}: read error {e}")]
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pat, label in PATTERNS:
            if pat.search(line):
                hits.append((lineno, label, line.rstrip()[:200]))
                break
    return hits


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: check_spec_task_ids.py <specifications_root_dir>",
            file=sys.stderr,
        )
        return 2
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    md_files = sorted(root.rglob("*.md"))
    total = 0
    for f in md_files:
        if ".git" in f.parts:
            continue
        hits = scan_file(f)
        if hits:
            total += len(hits)
            for lineno, label, snippet in hits:
                print(f"{f}:{lineno}: [{label}] {snippet}")
    if total:
        print(f"\nTotal lines with suspected task IDs: {total}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
