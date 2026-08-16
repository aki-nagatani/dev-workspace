"""コスト監視レポートを実行単位のJSON履歴として保存する。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")
SUPPORTED_SERVICES = frozenset({"aws", "openai"})
SCHEMA_VERSION = 1


def _parse_arguments() -> argparse.Namespace:
    """履歴作成またはArtifact統合の引数を解析する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="1ジョブ分のArtifact JSONを作成する")
    create.add_argument("--service", required=True, choices=sorted(SUPPORTED_SERVICES))
    create.add_argument("--status", required=True)
    create.add_argument("--report-path", type=Path)
    create.add_argument("--output", type=Path, required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--run-attempt", required=True)
    create.add_argument("--workflow", required=True)
    create.add_argument("--ref", required=True)
    create.add_argument("--sha", required=True)
    create.add_argument("--observed-at", help="テスト用のUTC ISO 8601日時")

    merge = subparsers.add_parser("merge", help="Artifact JSONをGit管理履歴へ統合する")
    merge.add_argument("--artifact-dir", type=Path, required=True)
    merge.add_argument("--history-dir", type=Path, required=True)
    return parser.parse_args()


def _now_utc(observed_at: str | None) -> datetime:
    """保存に使うUTC日時を返す。"""
    if observed_at is None:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("--observed-atはタイムゾーン付きで指定してください")
    return parsed.astimezone(timezone.utc)


def _parse_report_summary(report: str) -> dict[str, Any]:
    """Slack本文から比較に使える主要な表示値を抽出する。"""
    summary: dict[str, Any] = {}
    for line in report.splitlines():
        if line.startswith("判定: "):
            summary["judgment"] = line.removeprefix("判定: ").split("（", 1)[0]
        elif line.startswith("期間: "):
            summary["period"] = line.removeprefix("期間: ")
        elif line.startswith("合計: "):
            summary["total"] = line.removeprefix("合計: ")
        elif line.startswith("前月の完了月合計: "):
            summary["previous_full_month_total"] = line.removeprefix(
                "前月の完了月合計: "
            )
        elif line.startswith("月末予測: "):
            summary["projected_month_total"] = line.removeprefix("月末予測: ")
        elif line.startswith("日次平均: "):
            summary["daily_average"] = line.removeprefix("日次平均: ")
        elif line.startswith("日次異常: "):
            summary["daily_anomaly"] = line.removeprefix("日次異常: ")
    return summary


def _validate_path_component(value: str, name: str) -> str:
    """履歴ファイル名へ使う値がパス区切りを含まないことを確認する。"""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise ValueError(f"{name}に使用できない文字が含まれています")
    return value


def build_snapshot(
    *,
    service: str,
    status: str,
    report: str,
    run_id: str,
    run_attempt: str,
    workflow: str,
    ref: str,
    sha: str,
    observed_at: str | None = None,
) -> dict[str, Any]:
    """1回分の監視結果をJSONへ保存する辞書に変換する。"""
    if service not in SUPPORTED_SERVICES:
        raise ValueError(f"未対応のサービスです: {service}")
    _validate_path_component(run_id, "run_id")
    _validate_path_component(run_attempt, "run_attempt")
    observed = _now_utc(observed_at)
    return {
        "schema_version": SCHEMA_VERSION,
        "service": service,
        "status": status,
        "observed_at_utc": observed.isoformat().replace("+00:00", "Z"),
        "observed_at_jst": observed.astimezone(JST).isoformat(),
        "workflow": workflow,
        "ref": ref,
        "sha": sha,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "summary": _parse_report_summary(report),
        "report": report,
    }


def _read_report(report_path: Path | None) -> str:
    """レポートファイルを読み、存在しない場合は空文字を返す。"""
    if report_path is None or not report_path.is_file():
        return ""
    return report_path.read_text(encoding="utf-8")


def write_snapshot(snapshot: dict[str, Any], output_path: Path) -> None:
    """JSONスナップショットを指定先へ書き出す。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_snapshot(
    *,
    service: str,
    status: str,
    report_path: Path | None,
    output_path: Path,
    run_id: str,
    run_attempt: str,
    workflow: str,
    ref: str,
    sha: str,
    observed_at: str | None = None,
) -> None:
    """監視ジョブの出力をArtifact用JSONへ変換する。"""
    snapshot = build_snapshot(
        service=service,
        status=status,
        report=_read_report(report_path),
        run_id=run_id,
        run_attempt=run_attempt,
        workflow=workflow,
        ref=ref,
        sha=sha,
        observed_at=observed_at,
    )
    write_snapshot(snapshot, output_path)


def _snapshot_path(snapshot: dict[str, Any], history_dir: Path) -> Path:
    """スナップショットの一意なGit管理パスを返す。"""
    service = snapshot["service"]
    observed_at = datetime.fromisoformat(
        snapshot["observed_at_utc"].replace("Z", "+00:00")
    )
    filename = (
        f"run-{snapshot['run_id']}-attempt-{snapshot['run_attempt']}.json"
    )
    return (
        history_dir
        / service
        / f"{observed_at.year:04d}"
        / f"{observed_at.month:02d}"
        / f"{observed_at.day:02d}"
        / filename
    )


def _load_snapshots(artifact_dir: Path) -> Iterable[dict[str, Any]]:
    """Artifactディレクトリ以下のJSONスナップショットを読み込む。"""
    for path in sorted(artifact_dir.rglob("*.json")):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        if snapshot.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"未対応のスキーマです: {path}")
        if snapshot.get("service") not in SUPPORTED_SERVICES:
            raise ValueError(f"未対応のサービスです: {path}")
        yield snapshot


def merge_snapshots(artifact_dir: Path, history_dir: Path) -> list[Path]:
    """ArtifactのスナップショットをGit管理履歴へ統合する。"""
    written: list[Path] = []
    for snapshot in _load_snapshots(artifact_dir):
        destination = _snapshot_path(snapshot, history_dir)
        write_snapshot(snapshot, destination)
        written.append(destination)
    return written


def main() -> None:
    """コマンドラインから履歴保存処理を実行する。"""
    arguments = _parse_arguments()
    if arguments.command == "create":
        create_snapshot(
            service=arguments.service,
            status=arguments.status,
            report_path=arguments.report_path,
            output_path=arguments.output,
            run_id=arguments.run_id,
            run_attempt=arguments.run_attempt,
            workflow=arguments.workflow,
            ref=arguments.ref,
            sha=arguments.sha,
            observed_at=arguments.observed_at,
        )
        return
    merge_snapshots(arguments.artifact_dir, arguments.history_dir)


if __name__ == "__main__":
    main()
