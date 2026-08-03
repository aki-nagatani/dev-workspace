"""定期 AWS・OpenAI コスト監視のサマリ生成を検証する。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from scripts.cost_monitoring import (
    CostPeriod,
    anomaly_summary,
    comparison_periods,
    cost_deltas,
    daily_average,
    evaluate_judgment,
    is_meaningful_delta,
    monitoring_windows,
    percent_change,
    projected_month_total,
    share_percent,
    significant_increases,
)
from scripts.report_aws_cost_to_slack import build_report as build_aws_report
from scripts.report_openai_cost_to_slack import (
    build_report as build_openai_report,
    daily_cost_series,
    total_cost,
)


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


def test_monitoring_windows_includes_full_month_and_recent_trend() -> None:
    """月中監視では完了月と直近3か月の推移期間も持つ。"""
    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))

    assert windows.is_complete_month is False
    assert windows.mode_label == "当月累計"
    assert windows.previous_full_month.start.isoformat() == "2026-07-01"
    assert windows.previous_full_month.end.isoformat() == "2026-08-01"
    assert [period.start.isoformat() for period in windows.recent_full_months] == [
        "2026-05-01",
        "2026-06-01",
        "2026-07-01",
    ]


def test_percent_change_handles_zero_baseline() -> None:
    """比較対象がゼロのときは比率ではなく比較不可として表示する。"""
    assert percent_change(Decimal("3"), Decimal()) == "比較対象なし"


def test_daily_average_and_month_end_projection() -> None:
    """日次平均と月末予測を月日数から算出する。"""
    assert daily_average(Decimal("14"), 14) == Decimal("1")
    assert projected_month_total(Decimal("14"), 14, datetime(2026, 8, 15).date()) == Decimal(
        "31"
    )


def test_cost_deltas_and_share_percent() -> None:
    """サービス増減と構成比を計算する。"""
    deltas = cost_deltas(
        {"Amazon RDS": Decimal("12"), "Amazon EC2": Decimal("3")},
        {"Amazon RDS": Decimal("10"), "Amazon S3": Decimal("2")},
    )

    assert deltas[0][0] == "Amazon EC2"
    assert deltas[0][3] == Decimal("3")
    assert deltas[1][0] == "Amazon RDS"
    assert deltas[1][3] == Decimal("2")
    assert share_percent(Decimal("3"), Decimal("15")) == "20.0%"


def test_meaningful_delta_and_significant_increases() -> None:
    """小さい増減は捨て、意味のある増加だけ残す。"""
    assert is_meaningful_delta(Decimal("0.2"), Decimal("10")) is False
    assert is_meaningful_delta(Decimal("1.2"), Decimal("10")) is True
    increases = significant_increases(
        {"Amazon RDS": Decimal("12"), "Amazon EC2": Decimal("3.1")},
        {"Amazon RDS": Decimal("11.9"), "Amazon EC2": Decimal("2")},
    )
    assert [row[0] for row in increases] == ["Amazon EC2"]


def test_judgment_escalates_for_mom_and_projection() -> None:
    """前月比と月末予測で要注意／要確認に上げる。"""
    warn = evaluate_judgment(
        current_total=Decimal("13"),
        previous_total=Decimal("10"),
        previous_full_month_total=Decimal("20"),
        projected_total=None,
        has_daily_anomaly=False,
    )
    investigate = evaluate_judgment(
        current_total=Decimal("13"),
        previous_total=Decimal("10"),
        previous_full_month_total=Decimal("20"),
        projected_total=Decimal("30"),
        has_daily_anomaly=False,
    )

    assert warn.level == "要注意"
    assert warn.needs_cursor_paste is True
    assert warn.user_action_line().startswith("【貼るだけ】")
    assert investigate.level == "要確認"
    assert investigate.needs_cursor_paste is True


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
    assert anomaly_summary([("2026-08-01", Decimal("1")), ("2026-08-02", Decimal("1"))]) == (
        "日次異常なし"
    )


def test_aws_mid_month_normal_report_is_compact() -> None:
    """当月累計で正常なら増減詳細と月次推移を省略する。"""
    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))
    report = build_aws_report(
        windows,
        {"Amazon RDS": Decimal("10.00"), "Amazon EC2": Decimal("1.00")},
        {"Amazon RDS": Decimal("10.00"), "Amazon EC2": Decimal("1.00")},
        Decimal("31.00"),
        [
            (CostPeriod(datetime(2026, 7, 1).date(), datetime(2026, 8, 1).date()), Decimal("31")),
        ],
        [("2026-08-01", Decimal("1")), ("2026-08-02", Decimal("1"))],
    )

    assert "判定: 正常" in report
    assert "【対応不要】" in report
    assert "月末予測" in report
    assert "増加上位" not in report
    assert "直近完了月の推移" not in report
    assert "#cost-monitoring-handoff" not in report


def test_aws_complete_month_report_includes_trend_and_movers() -> None:
    """完了月レビューでは推移と意味のある増加を出す。"""
    windows = monitoring_windows(datetime(2026, 8, 1, 9, tzinfo=JST))
    report = build_aws_report(
        windows,
        {"Amazon RDS": Decimal("20.00"), "Amazon EC2": Decimal("5.00")},
        {"Amazon RDS": Decimal("10.00"), "Amazon EC2": Decimal("4.00")},
        Decimal("14.00"),
        [
            (CostPeriod(datetime(2026, 5, 1).date(), datetime(2026, 6, 1).date()), Decimal("12")),
            (CostPeriod(datetime(2026, 6, 1).date(), datetime(2026, 7, 1).date()), Decimal("14")),
            (CostPeriod(datetime(2026, 7, 1).date(), datetime(2026, 8, 1).date()), Decimal("25")),
        ],
        [("2026-07-01", Decimal("1")), ("2026-07-02", Decimal("1"))],
    )

    assert "完了月" in report
    assert "判定: 要注意" in report or "判定: 要確認" in report
    assert "【貼るだけ】" in report
    assert "直近完了月の推移" in report
    assert "増加上位" in report
    assert "Amazon RDS" in report
    assert "#cost-monitoring-handoff" in report
    assert "SKILL: aws-cost-monitoring" in report
    assert "追加質問はせず" in report
    assert "ユーザー作業は貼り付けのみ完了" in report


def test_openai_cost_report_sums_api_buckets_and_daily_series() -> None:
    """OpenAI Costs API の複数バケットを合計し判定付きで通知する。"""
    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))
    buckets = [
        {
            "start_time": int(datetime(2026, 8, 1, tzinfo=JST).timestamp()),
            "results": [{"amount": {"value": "1.25"}}],
        },
        {
            "start_time": int(datetime(2026, 8, 2, tzinfo=JST).timestamp()),
            "results": [{"amount": {"value": "2.75"}}],
        },
    ]
    total = total_cost(buckets)
    report = build_openai_report(
        windows,
        total,
        Decimal("2.00"),
        Decimal("8.00"),
        [
            (CostPeriod(datetime(2026, 7, 1).date(), datetime(2026, 8, 1).date()), Decimal("8.00")),
        ],
        daily_cost_series(buckets),
    )

    assert total == Decimal("4.00")
    assert "OpenAI API コスト監視（当月累計）" in report
    assert "判定:" in report
    assert "【貼るだけ】" in report
    assert "$4.00" in report
    assert "+100.0%" in report
    assert "月末予測" in report
    assert "直近完了月の推移" not in report
    assert "#cost-monitoring-handoff" in report
    assert "対象: OpenAI API" in report