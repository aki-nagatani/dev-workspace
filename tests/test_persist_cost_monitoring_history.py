"""コスト監視履歴保存スクリプトを検証する。"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from scripts.persist_cost_monitoring_history import (
    build_snapshot,
    create_snapshot,
    main,
    merge_snapshots,
)


def test_build_snapshot_keeps_report_and_extracts_comparison_values() -> None:
    """成功レポートを再比較できる主要項目と本文付きのJSONへ変換する。"""
    snapshot = build_snapshot(
        service="aws",
        status="success",
        report=(
            "判定: 要確認（日次異常あり）\n"
            "期間: 2026-08-01〜2026-08-14（比較: 2026-07-01〜2026-07-14）\n"
            "合計: $31.98（同期間前月比 -11.6%）\n"
            "日次異常: 2026-08-01 が他日の平均の3.0倍（$5.96）"
        ),
        run_id="123",
        run_attempt="1",
        workflow="Cost Monitoring",
        ref="main",
        sha="abc123",
        observed_at="2026-08-16T00:00:00Z",
    )

    assert snapshot["service"] == "aws"
    assert snapshot["status"] == "success"
    assert snapshot["observed_at_jst"] == "2026-08-16T09:00:00+09:00"
    assert snapshot["summary"] == {
        "judgment": "要確認",
        "period": "2026-08-01〜2026-08-14（比較: 2026-07-01〜2026-07-14）",
        "total": "$31.98（同期間前月比 -11.6%）",
        "daily_anomaly": "2026-08-01 が他日の平均の3.0倍（$5.96）",
    }
    assert snapshot["report"].startswith("判定: 要確認")


def test_build_snapshot_extracts_complete_month_values_with_current_time() -> None:
    """完了月レポートの前月合計・予測・日次平均も履歴へ抽出する。"""
    snapshot = build_snapshot(
        service="openai",
        status="success",
        report=(
            "前月の完了月合計: $5.00（2026-07-01〜2026-08-01）\n"
            "月末予測: $6.00（前月完了月比 +20.0%）\n"
            "日次平均: $0.20"
        ),
        run_id="124",
        run_attempt="1",
        workflow="Cost Monitoring",
        ref="main",
        sha="abc123",
    )

    assert snapshot["summary"] == {
        "previous_full_month_total": "$5.00（2026-07-01〜2026-08-01）",
        "projected_month_total": "$6.00（前月完了月比 +20.0%）",
        "daily_average": "$0.20",
    }
    assert snapshot["observed_at_utc"].endswith("Z")


def test_build_snapshot_rejects_unsupported_service() -> None:
    """履歴の保存先を限定し、未知のサービス名を受け付けない。"""
    with pytest.raises(ValueError, match="未対応のサービス"):
        build_snapshot(
            service="cursor",
            status="success",
            report="",
            run_id="1",
            run_attempt="1",
            workflow="Cost Monitoring",
            ref="main",
            sha="abc",
            observed_at="2026-08-16T00:00:00Z",
        )


def test_create_snapshot_records_failed_job_without_report(tmp_path: Path) -> None:
    """レポート生成に失敗したジョブも失敗状態の履歴として保存する。"""
    output_path = tmp_path / "artifact" / "aws.json"

    create_snapshot(
        service="aws",
        status="failure",
        report_path=tmp_path / "missing.txt",
        output_path=output_path,
        run_id="456",
        run_attempt="2",
        workflow="Cost Monitoring",
        ref="main",
        sha="def456",
        observed_at="2026-08-16T00:00:00Z",
    )

    snapshot = json.loads(output_path.read_text(encoding="utf-8"))
    assert snapshot["status"] == "failure"
    assert snapshot["report"] == ""
    assert snapshot["summary"] == {}


def test_merge_snapshots_writes_idempotent_service_date_paths(tmp_path: Path) -> None:
    """複数Artifactをサービス・日付別に統合し、同じ実行は上書き可能にする。"""
    artifact_dir = tmp_path / "artifacts"
    history_dir = tmp_path / "history"
    first = artifact_dir / "aws" / "aws.json"
    second = artifact_dir / "openai" / "openai.json"

    for path, service, run_id in (
        (first, "aws", "100"),
        (second, "openai", "101"),
    ):
        report_path = tmp_path / f"{service}.txt"
        report_path.write_text(f"{service} report", encoding="utf-8")
        create_snapshot(
            service=service,
            status="success",
            report_path=report_path,
            output_path=path,
            run_id=run_id,
            run_attempt="1",
            workflow="Cost Monitoring",
            ref="main",
            sha="abc",
            observed_at="2026-08-16T00:00:00Z",
        )

    written = merge_snapshots(artifact_dir, history_dir)

    assert len(written) == 2
    aws_history = (
        history_dir / "aws" / "2026" / "08" / "16" / "run-100-attempt-1.json"
    )
    openai_history = (
        history_dir / "openai" / "2026" / "08" / "16" / "run-101-attempt-1.json"
    )
    assert aws_history.is_file()
    assert openai_history.is_file()
    assert json.loads(aws_history.read_text(encoding="utf-8"))["report"] == "aws report"

    merge_snapshots(artifact_dir, history_dir)
    assert len(list(history_dir.rglob("*.json"))) == 2


def test_build_snapshot_rejects_naive_observed_at() -> None:
    """履歴時刻にタイムゾーンがない入力を受け付けず、日付ずれを防ぐ。"""
    with pytest.raises(ValueError, match="タイムゾーン付き"):
        build_snapshot(
            service="openai",
            status="success",
            report="",
            run_id="1",
            run_attempt="1",
            workflow="Cost Monitoring",
            ref="main",
            sha="abc",
            observed_at="2026-08-16T00:00:00",
        )


def test_build_snapshot_rejects_path_separator_in_run_id() -> None:
    """実行IDを履歴パスへ展開するときのパス逸脱を拒否する。"""
    with pytest.raises(ValueError, match="run_id"):
        build_snapshot(
            service="openai",
            status="success",
            report="",
            run_id="../outside",
            run_attempt="1",
            workflow="Cost Monitoring",
            ref="main",
            sha="abc",
            observed_at="2026-08-16T00:00:00Z",
        )


def test_main_create_command_writes_snapshot(tmp_path: Path, monkeypatch) -> None:
    """CLIのcreateサブコマンドが指定先へ履歴Artifactを作成する。"""
    output_path = tmp_path / "artifact.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_cost_monitoring_history.py",
            "create",
            "--service",
            "aws",
            "--status",
            "success",
            "--output",
            str(output_path),
            "--run-id",
            "200",
            "--run-attempt",
            "1",
            "--workflow",
            "Cost Monitoring",
            "--ref",
            "main",
            "--sha",
            "abc",
            "--observed-at",
            "2026-08-16T00:00:00Z",
        ],
    )

    main()

    assert json.loads(output_path.read_text(encoding="utf-8"))["service"] == "aws"


def test_main_merge_command_writes_history(tmp_path: Path, monkeypatch) -> None:
    """CLIのmergeサブコマンドがArtifactをGit管理履歴へ取り込む。"""
    artifact_dir = tmp_path / "artifacts"
    history_dir = tmp_path / "history"
    artifact_path = artifact_dir / "aws.json"
    create_snapshot(
        service="aws",
        status="success",
        report_path=None,
        output_path=artifact_path,
        run_id="201",
        run_attempt="1",
        workflow="Cost Monitoring",
        ref="main",
        sha="abc",
        observed_at="2026-08-16T00:00:00Z",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_cost_monitoring_history.py",
            "merge",
            "--artifact-dir",
            str(artifact_dir),
            "--history-dir",
            str(history_dir),
        ],
    )

    main()

    assert len(list(history_dir.rglob("*.json"))) == 1


def test_merge_snapshots_rejects_unknown_schema(tmp_path: Path) -> None:
    """将来形式のJSONを黙って履歴へ混在させない。"""
    artifact_path = tmp_path / "artifacts" / "unknown.json"
    artifact_path.parent.mkdir()
    artifact_path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")

    with pytest.raises(ValueError, match="未対応のスキーマ"):
        merge_snapshots(tmp_path / "artifacts", tmp_path / "history")


def test_merge_snapshots_rejects_unknown_service(tmp_path: Path) -> None:
    """Artifactに未知のサービスが含まれる場合は統合を止める。"""
    artifact_path = tmp_path / "artifacts" / "unknown.json"
    artifact_path.parent.mkdir()
    artifact_path.write_text(
        json.dumps({"schema_version": 1, "service": "cursor"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="未対応のサービス"):
        merge_snapshots(tmp_path / "artifacts", tmp_path / "history")


def test_module_entrypoint_executes_main(tmp_path: Path, monkeypatch) -> None:
    """モジュールを直接実行した場合もCLIのcreate処理を呼び出す。"""
    source_path = Path("scripts/persist_cost_monitoring_history.py").resolve()
    output_path = tmp_path / "entrypoint.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(source_path),
            "create",
            "--service",
            "aws",
            "--status",
            "success",
            "--output",
            str(output_path),
            "--run-id",
            "202",
            "--run-attempt",
            "1",
            "--workflow",
            "Cost Monitoring",
            "--ref",
            "main",
            "--sha",
            "abc",
            "--observed-at",
            "2026-08-16T00:00:00Z",
        ],
    )

    namespace = {"__name__": "__main__", "__file__": str(source_path)}
    exec(compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec"), namespace)

    assert output_path.is_file()
