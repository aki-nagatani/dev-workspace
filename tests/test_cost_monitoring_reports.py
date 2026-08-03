"""定期 AWS・OpenAI コスト監視のサマリ生成を検証する。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from scripts.cost_monitoring import comparison_periods, percent_change
from scripts.report_aws_cost_to_slack import anomaly_summary, build_report as build_aws_report
from scripts.report_openai_cost_to_slack import build_report as build_openai_report, total_cost


JST = timezone(timedelta(hours=9))


def test_comparison_periods_uses_complete_months_on_first_day() -> None:
    """月初は直前の完了月とその前月を比較対象にする。"""
    current, previous = comparison_periods(datetime(2026, 8, 1, 9, tzinfo=JST))

    assert current.start.isoformat() == "2026-07-01"
    assert current.end.isoformat() == "2026-08-01"
    assert previous.start.isoformat() == "2026-06-01"
    assert previous.end.isoformat() == "2026-07-01"


def test_comparison_periods_uses_month_to_date_after_first_day() -> None:
    """月中は当月の前日までと前月の同日数を比較する。"""
    current, previous = comparison_periods(datetime(2026, 8, 15, 9, tzinfo=JST))

    assert current.start.isoformat() == "2026-08-01"
    assert current.end.isoformat() == "2026-08-15"
    assert previous.start.isoformat() == "2026-07-01"
    assert previous.end.isoformat() == "2026-07-15"


def test_percent_change_handles_zero_baseline() -> None:
    """比較対象がゼロのときは比率ではなく比較不可として表示する。"""
    assert percent_change(Decimal("3"), Decimal()) == "比較対象なし"


def test_anomaly_summary_detects_latest_daily_spike() -> None:
    """最新日が過去平均の1.5倍超なら警告を返す。"""
    summary = anomaly_summary(
        [
            ("2026-08-01", Decimal("1")),
            ("2026-08-02", Decimal("1")),
            ("2026-08-03", Decimal("2")),
        ]
    )

    assert "日次異常" in summary
    assert "2026-08-03" in summary


def test_aws_report_includes_totals_top_service_and_no_anomaly() -> None:
    """AWS サマリに比較額、上位サービス、異常なしを含める。"""
    current, previous = comparison_periods(datetime(2026, 8, 15, 9, tzinfo=JST))
    report = build_aws_report(
        current,
        previous,
        {"Amazon RDS": Decimal("12.50"), "Amazon EC2": Decimal("3.00")},
        {"Amazon RDS": Decimal("10.00")},
        [("2026-08-01", Decimal("1")), ("2026-08-02", Decimal("1"))],
    )

    assert "AWS コスト監視" in report
    assert "$15.50" in report
    assert "Amazon RDS" in report
    assert "日次異常: 検知なし" in report


def test_openai_cost_report_sums_api_buckets() -> None:
    """OpenAI Costs API の複数バケットを合計して通知へ表示する。"""
    current, previous = comparison_periods(datetime(2026, 8, 15, 9, tzinfo=JST))
    total = total_cost(
        [
            {"results": [{"amount": {"value": "1.25"}}]},
            {"results": [{"amount": {"value": "2.75"}}]},
        ]
    )
    report = build_openai_report(current, previous, total, Decimal("2.00"))

    assert total == Decimal("4.00")
    assert "OpenAI API コスト監視" in report
    assert "$4.00" in report
    assert "+100.0%" in report
