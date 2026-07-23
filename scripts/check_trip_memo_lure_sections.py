#!/usr/bin/env python3
"""釣行メモの `### 使用ルアー` 節が FishTrack 向け体裁かを検査する。

正本ルール: Obsidian `Fishing/釣行メモ.md` 先頭「使用ルアー（FishTrack ルアー紐づけ）」。
発火: `obsidian-inbox-summarize`（釣行メモ追記後）・`trip-memo-import`（resolve/import 前）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_RESULT_TOKENS = (
    "キャッチ",
    "バイトのみ",
    "バイト・",
    "バラシ",
    "ヒット",
    "反応なし",
    "反応な",
    "ロスト",
    "不成立",
    "ワンバイト",
    "暴れ",
    "浮かせ",
    "サイトで",
    "見えたのみ",
    "釣れ",
    "食べ",
    "のみ（",
)

_SIZE_TOKENS = ("cm", "センチ", "mm", "尾")

_VALID_LINE_PATTERNS = (
    re.compile(r"^- \*\*[^*]+\*\*\s*$"),
    re.compile(r"^- \*\*[^*]+\*\* — \*\*[^*]+\*\*\s*$"),
    re.compile(r"^- \*\*[^*]+\*\*: \*\*[^*]+\*\*\s*$"),
    re.compile(r"^- \*\*[^*]+\*\*: \*\*[^*]+\*\* — \*\*[^*]+\*\*\s*$"),
    re.compile(r"^- \*\*[^*]+\*\*: \*\*[^*]+\*\* ＋ \*\*[^*]+\*\*"),
    re.compile(r"^- \*\*[^*]+\*\*: \*\*[^*]+\*\* \*\*[^*]+\*\*"),
)


def _is_valid_product_line(line: str) -> bool:
    stripped = line.strip()
    return any(pattern.match(stripped) for pattern in _VALID_LINE_PATTERNS)


def _line_issues(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("- "):
        return []

    issues: list[str] = []
    for token in _RESULT_TOKENS + _SIZE_TOKENS:
        if token in stripped:
            issues.append(f"結果・状況語「{token}」")

    colon_match = re.match(r"^- \*\*[^*]+\*\*:\s+(.+)$", stripped)
    if colon_match and "**" not in colon_match.group(1):
        issues.append("コロン後が製品名（太字）ではない")

    product_tail = re.match(r"^- \*\*[^*]+\*\*:\s+\*\*[^*]+\*\*\s+(.+)$", stripped)
    if product_tail and not product_tail.group(1).strip().startswith("—"):
        issues.append("製品名の後に結果・説明が続く")

    dash_tail = re.match(r"^- \*\*[^*]+\*\* — .+$", stripped)
    if dash_tail and not re.search(r"\*\*[^*]+\*\*\s*$", stripped):
        issues.append("カラー（太字）形式でないダッシュ以降")

    if not issues and not _is_valid_product_line(stripped):
        issues.append("製品行の形式が想定外（リグ＋製品＋カラーのみ）")

    return issues


def _iter_lure_sections(lines: list[str]) -> list[tuple[int, list[tuple[int, str]]]]:
    sections: list[tuple[int, list[tuple[int, str]]]] = []
    index = 0
    while index < len(lines):
        if re.match(r"^###\s+使用ルアー", lines[index]):
            section_start = index + 1
            items: list[tuple[int, str]] = []
            index += 1
            while index < len(lines) and not re.match(r"^#{2,3}\s+", lines[index]):
                if lines[index].strip().startswith("- "):
                    items.append((index + 1, lines[index]))
                index += 1
            sections.append((section_start, items))
            continue
        index += 1
    return sections


def check_file(path: Path, min_line: int | None = None, max_line: int | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    violations: list[str] = []

    for _section_start, items in _iter_lure_sections(lines):
        for line_no, line in items:
            if min_line is not None and line_no < min_line:
                continue
            if max_line is not None and line_no > max_line:
                continue
            for issue in _line_issues(line):
                violations.append(f"{path}:{line_no}: {issue}: {line.strip()}")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="釣行メモの使用ルアー節を検査する")
    parser.add_argument("path", type=Path, help="釣行メモ.md のパス")
    parser.add_argument("--min-line", type=int, default=None, help="検査対象の最小行番号")
    parser.add_argument("--max-line", type=int, default=None, help="検査対象の最大行番号")
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"ファイルが見つかりません: {args.path}", file=sys.stderr)
        return 2

    violations = check_file(args.path, args.min_line, args.max_line)
    if violations:
        print("使用ルアー節の体裁違反:", file=sys.stderr)
        for item in violations:
            print(item, file=sys.stderr)
        return 1

    print("OK: 使用ルアー節に体裁違反はありません")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
