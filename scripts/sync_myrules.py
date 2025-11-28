#!/usr/bin/env python3
"""Synchronize .cursor/rules/myrules.mdc across project repositories."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy dev-workspace/.cursor/rules/myrules.mdc to each project."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    parser.add_argument(
        "--targets",
        nargs="*",
        default=None,
        metavar="NAME",
        help="Optional list of repository names to sync "
        "(defaults to all known repositories).",
    )
    return parser.parse_args()


def resolve_targets(dev_workspace: Path) -> Dict[str, Path]:
    workspace_root = dev_workspace.parent
    return {
        "FishTrack": workspace_root / "FishTrack/.cursor/rules/myrules.mdc",
        "MyPokedex": workspace_root / "MyPokedex/.cursor/rules/myrules.mdc",
    }


def copy_if_changed(src_bytes: bytes, dst_path: Path, dry_run: bool) -> bool:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists() and dst_path.read_bytes() == src_bytes:
        return False
    if dry_run:
        return True
    dst_path.write_bytes(src_bytes)
    return True


def select_targets(
    all_targets: Dict[str, Path], requested: Iterable[str] | None
) -> Tuple[Dict[str, Path], Tuple[str, ...]]:
    if not requested:
        return all_targets, ()
    missing = tuple(name for name in requested if name not in all_targets)
    selected = {name: all_targets[name] for name in requested if name in all_targets}
    return selected, missing


def main() -> int:
    args = parse_args()
    script_path = Path(__file__).resolve()
    dev_workspace = script_path.parents[1]
    canonical = dev_workspace / ".cursor/rules/myrules.mdc"

    if not canonical.exists():
        print(f"[error] canonical file not found: {canonical}", file=sys.stderr)
        return 1

    targets_all = resolve_targets(dev_workspace)
    targets, missing = select_targets(targets_all, args.targets)

    if missing:
        print(
            "[warn] unknown repository names were ignored: "
            + ", ".join(sorted(missing)),
            file=sys.stderr,
        )

    canonical_bytes = canonical.read_bytes()
    changed = []

    for name, dst in targets.items():
        updated = copy_if_changed(canonical_bytes, dst, args.dry_run)
        status = "would update" if args.dry_run else "updated"
        if updated:
            changed.append(name)
            print(f"[sync] {status}: {dst}")
        else:
            print(f"[sync] already up-to-date: {dst}")

    if not changed:
        if args.dry_run:
            print("[sync] no repositories would change")
        else:
            print("[sync] all repositories already match canonical file")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

