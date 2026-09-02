"""定期 AWS・OpenAI コスト監視のサマリ生成を検証する。"""

from __future__ import annotations

import io
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import urllib.request
from urllib.error import HTTPError
from unittest.mock import MagicMock

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
    uses_previous_month_review,
)
from scripts.report_aws_cost_to_slack import build_report as build_aws_report
import scripts.report_aws_cost_to_slack as aws_report
from scripts.report_openai_cost_to_slack import (
    build_report as build_openai_report,
    daily_cost_series,
    total_cost,
)
import scripts.report_openai_cost_to_slack as openai_report


JST = timezone(timedelta(hours=9))


def test_comparison_periods_uses_complete_months_on_first_day() -> None:
    """1日は直前の完了月とその前月を比較対象にする。"""
    current, previous = comparison_periods(datetime(2026, 8, 1, 9, tzinfo=JST))

    assert current.start.isoformat() == "2026-07-01"
    assert current.end.isoformat() == "2026-08-01"
    assert previous.start.isoformat() == "2026-06-01"
    assert previous.end.isoformat() == "2026-07-01"


def test_uses_previous_month_review_until_tenth() -> None:
    """1日ジョブと遅延分は前月、10日以降は当月累計にする。"""
    assert uses_previous_month_review(datetime(2026, 9, 1, tzinfo=JST).date()) is True
    assert uses_previous_month_review(datetime(2026, 9, 2, 2, 15, tzinfo=JST).date()) is True
    assert uses_previous_month_review(datetime(2026, 9, 9, tzinfo=JST).date()) is True
    assert uses_previous_month_review(datetime(2026, 9, 10, tzinfo=JST).date()) is False
    assert uses_previous_month_review(datetime(2026, 9, 20, tzinfo=JST).date()) is False


def test_monitoring_windows_keeps_complete_month_when_first_job_is_delayed() -> None:
    """1日ジョブが2日未明に落ちても前月完了月を見る。"""
    windows = monitoring_windows(datetime(2026, 9, 2, 2, 15, tzinfo=JST))

    assert windows.is_complete_month is True
    assert windows.mode_label == "完了月"
    assert windows.focus.start.isoformat() == "2026-08-01"
    assert windows.focus.end.isoformat() == "2026-09-01"


def test_comparison_periods_uses_month_to_date_from_tenth() -> None:
    """10日以降は当月の前日までと前月の同日数を比較する。"""
    current, previous = comparison_periods(datetime(2026, 8, 10, 9, tzinfo=JST))

    assert current.start.isoformat() == "2026-08-01"
    assert current.end.isoformat() == "2026-08-10"
    assert previous.start.isoformat() == "2026-07-01"
    assert previous.end.isoformat() == "2026-07-10"


def test_comparison_periods_uses_month_to_date_on_twentieth() -> None:
    """20日も当月累計として前月同日数と比較する。"""
    current, previous = comparison_periods(datetime(2026, 8, 20, 9, tzinfo=JST))

    assert current.start.isoformat() == "2026-08-01"
    assert current.end.isoformat() == "2026-08-20"
    assert previous.start.isoformat() == "2026-07-01"
    assert previous.end.isoformat() == "2026-07-20"


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


def test_aws_daily_costs_separate_tax_and_hosted_zone_fixed_charges() -> None:
    """TaxとHostedZoneだけを固定費として分離し、DNSクエリ費用は残す。"""
    client = MagicMock()
    client.get_cost_and_usage.return_value = {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2026-08-01", "End": "2026-08-02"},
                "Groups": [
                    {
                        "Keys": ["Tax", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "3.33"}},
                    },
                    {
                        "Keys": ["Amazon Route 53", "HostedZone"],
                        "Metrics": {"UnblendedCost": {"Amount": "1.00"}},
                    },
                    {
                        "Keys": ["Amazon Route 53", "DNS-Queries"],
                        "Metrics": {"UnblendedCost": {"Amount": "0.20"}},
                    },
                    {
                        "Keys": ["Amazon RDS", "InstanceUsage:db.t3.micro"],
                        "Metrics": {"UnblendedCost": {"Amount": "0.86"}},
                    },
                ],
            }
        ]
    }

    operational, fixed = aws_report.daily_costs_excluding_fixed_charges(
        client,
        CostPeriod(datetime(2026, 8, 1).date(), datetime(2026, 8, 2).date()),
    )

    assert operational == [("2026-08-01", Decimal("1.06"))]
    assert fixed == [
        ("2026-08-01", "Tax", Decimal("3.33")),
        ("2026-08-01", "Amazon Route 53/HostedZone", Decimal("1.00")),
    ]
    request = client.get_cost_and_usage.call_args.kwargs
    assert request["GroupBy"] == [
        {"Type": "DIMENSION", "Key": "SERVICE"},
        {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
    ]


def test_aws_report_excludes_fixed_charges_from_daily_judgment() -> None:
    """月初固定費を除いた日次系列では誤警報せず、固定費だけを明示する。"""
    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))
    report = build_aws_report(
        windows,
        {"Amazon RDS": Decimal("13.43"), "Tax": Decimal("3.33")},
        {"Amazon RDS": Decimal("13.43"), "Tax": Decimal("6.47")},
        Decimal("31.00"),
        [],
        [("2026-08-01", Decimal("2.05")), ("2026-08-02", Decimal("2.05"))],
        fixed_daily_costs=[
            ("2026-08-01", "Tax", Decimal("3.33")),
            ("2026-08-01", "Amazon Route 53/HostedZone", Decimal("1.00")),
        ],
    )

    assert "判定: 正常" in report
    assert "日次異常:" not in report
    assert "日次固定費（異常判定から除外）" in report
    assert "$3.33" in report
    assert "$1.00" in report


def test_aws_main_uses_operational_daily_costs_for_judgment(monkeypatch, capsys) -> None:
    """AWSメイン処理が固定費分離済みの日次系列でレポートを生成する。"""
    class FakeCostExplorer:
        def get_cost_and_usage(self, **request):
            if request["Granularity"] == "DAILY":
                return {
                    "ResultsByTime": [
                        {
                            "TimePeriod": {"Start": "2026-08-01", "End": "2026-08-02"},
                            "Groups": [
                                {
                                    "Keys": ["Tax", "NoUsageType"],
                                    "Metrics": {"UnblendedCost": {"Amount": "3.33"}},
                                },
                                {
                                    "Keys": ["Amazon Route 53", "HostedZone"],
                                    "Metrics": {"UnblendedCost": {"Amount": "1.00"}},
                                },
                                {
                                    "Keys": ["Amazon RDS", "InstanceUsage"],
                                    "Metrics": {"UnblendedCost": {"Amount": "2.05"}},
                                },
                            ],
                        }
                    ]
                }
            if request.get("GroupBy"):
                return {
                    "ResultsByTime": [
                        {
                            "Groups": [
                                {
                                    "Keys": ["Amazon RDS"],
                                    "Metrics": {"UnblendedCost": {"Amount": "1.00"}},
                                }
                            ]
                        }
                    ]
                }
            return {
                "ResultsByTime": [
                    {"Total": {"UnblendedCost": {"Amount": "1.00"}}}
                ]
            }

    class FakeBoto3:
        def client(self, service_name, region_name):
            assert service_name == "ce"
            assert region_name == "us-east-1"
            return FakeCostExplorer()

    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))
    monkeypatch.setattr(aws_report, "monitoring_windows", lambda: windows)
    monkeypatch.setitem(sys.modules, "boto3", FakeBoto3())

    aws_report.main()

    output = capsys.readouterr().out
    assert "日次異常:" not in output
    assert "日次固定費（異常判定から除外）" in output


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


def test_fetch_costs_retries_rate_limit_using_retry_after(monkeypatch) -> None:
    """OpenAI APIの429をRetry-After待機後に再試行し、取得を成功させる。"""
    rate_limit = HTTPError(
        openai_report.COSTS_URL,
        429,
        "Too Many Requests",
        {"Retry-After": "0"},
        None,
    )
    response = MagicMock()
    response.__enter__.return_value = io.StringIO('{"data": []}')
    response.__exit__.return_value = None
    urlopen = MagicMock(side_effect=[rate_limit, response])
    sleep = MagicMock()
    monkeypatch.setattr(openai_report, "urlopen", urlopen)
    monkeypatch.setattr(openai_report.time, "sleep", sleep)

    buckets = openai_report.fetch_costs(
        "test-key",
        CostPeriod(datetime(2026, 8, 1).date(), datetime(2026, 8, 2).date()),
    )

    assert buckets == []
    assert urlopen.call_count == 2
    sleep.assert_called_once_with(0.0)


def test_fetch_costs_does_not_retry_non_retryable_http_errors(monkeypatch) -> None:
    """認証エラーなど再試行対象外のHTTPエラーはそのまま呼び出し元へ返す。"""
    unauthorized = HTTPError(
        openai_report.COSTS_URL,
        401,
        "Unauthorized",
        {},
        None,
    )
    urlopen = MagicMock(side_effect=unauthorized)
    sleep = MagicMock()
    monkeypatch.setattr(openai_report, "urlopen", urlopen)
    monkeypatch.setattr(openai_report.time, "sleep", sleep)

    try:
        openai_report.fetch_costs(
            "test-key",
            CostPeriod(datetime(2026, 8, 1).date(), datetime(2026, 8, 2).date()),
        )
    except HTTPError as error:
        assert error.code == 401
    else:
        raise AssertionError("HTTPErrorが送出されていない")

    assert urlopen.call_count == 1
    sleep.assert_not_called()


def test_openai_main_skips_recent_month_requests_mid_month(monkeypatch, capsys) -> None:
    """月中実行では未使用の直近完了月取得を行わず、API呼出しを3回に抑える。"""
    windows = monitoring_windows(datetime(2026, 8, 15, 9, tzinfo=JST))
    requested_periods = []

    def fake_fetch_costs(_api_key, period):
        requested_periods.append(period)
        return []

    monkeypatch.setenv("OPENAI_ADMIN_API_KEY", "test-key")
    monkeypatch.setattr(openai_report, "monitoring_windows", lambda: windows)
    monkeypatch.setattr(openai_report, "fetch_costs", fake_fetch_costs)
    monkeypatch.setattr(openai_report, "build_report", lambda *args: "report")

    openai_report.main()

    assert capsys.readouterr().out == "report\n"
    assert requested_periods == [
        windows.focus,
        windows.previous_comparable,
        windows.previous_full_month,
    ]


def test_openai_main_keeps_recent_month_requests_on_first_day(monkeypatch, capsys) -> None:
    """月初の完了月レビューでは直近3か月の推移取得を維持する。"""
    windows = monitoring_windows(datetime(2026, 8, 1, 9, tzinfo=JST))
    requested_periods = []

    def fake_fetch_costs(_api_key, period):
        requested_periods.append(period)
        return []

    monkeypatch.setenv("OPENAI_ADMIN_API_KEY", "test-key")
    monkeypatch.setattr(openai_report, "monitoring_windows", lambda: windows)
    monkeypatch.setattr(openai_report, "fetch_costs", fake_fetch_costs)
    monkeypatch.setattr(openai_report, "build_report", lambda *args: "report")

    openai_report.main()

    assert capsys.readouterr().out == "report\n"
    assert requested_periods == [
        windows.focus,
        *windows.recent_full_months,
        windows.previous_comparable,
        windows.previous_full_month,
    ]


def test_retry_delay_uses_exponential_backoff_for_invalid_retry_after() -> None:
    """Retry-Afterが数値でない場合に指数バックオフへフォールバックする。"""
    error = HTTPError(openai_report.COSTS_URL, 503, "Unavailable", {"Retry-After": "later"}, None)

    assert openai_report._retry_delay_seconds(error, 2) == 4.0


def test_fetch_costs_follows_next_page(monkeypatch) -> None:
    """Costs APIのページングトークンを次のリクエストへ引き継ぐ。"""
    first_response = MagicMock()
    first_response.__enter__.return_value = io.StringIO(
        '{"data": [{"id": "first"}], "next_page": "next-page"}'
    )
    first_response.__exit__.return_value = None
    second_response = MagicMock()
    second_response.__enter__.return_value = io.StringIO('{"data": [{"id": "second"}]}')
    second_response.__exit__.return_value = None
    urlopen = MagicMock(side_effect=[first_response, second_response])
    monkeypatch.setattr(openai_report, "urlopen", urlopen)

    buckets = openai_report.fetch_costs(
        "test-key",
        CostPeriod(datetime(2026, 8, 1).date(), datetime(2026, 8, 2).date()),
    )

    assert buckets == [{"id": "first"}, {"id": "second"}]
    assert "page=next-page" in urlopen.call_args_list[1].args[0].full_url


def test_daily_cost_series_skips_bucket_without_start_time() -> None:
    """開始時刻のないバケットを日次系列へ混入させない。"""
    assert daily_cost_series([{"results": []}]) == []


def test_openai_complete_month_normal_report_includes_average_and_trend() -> None:
    """完了月の正常レポートでは日次平均と直近月推移を表示する。"""
    windows = monitoring_windows(datetime(2026, 8, 1, 9, tzinfo=JST))
    report = build_openai_report(
        windows,
        Decimal("3.00"),
        Decimal("4.00"),
        Decimal("5.00"),
        [
            (period, Decimal("2.00"))
            for period in windows.recent_full_months
        ],
        [("2026-07-01", Decimal("1")), ("2026-07-02", Decimal("1"))],
    )

    assert "OpenAI API コスト監視（完了月）" in report
    assert "日次平均" in report
    assert "直近完了月の推移:" in report
    assert "内訳確認: FishTrack 管理者の OpenAI 利用量画面" in report


def test_module_entrypoint_runs_without_external_network(monkeypatch, capsys) -> None:
    """モジュール実行時も外部API応答を処理してレポートを標準出力へ出す。"""

    def fake_urlopen(_request, timeout):
        response = MagicMock()
        response.__enter__.return_value = io.StringIO('{"data": []}')
        response.__exit__.return_value = None
        assert timeout == 30
        return response

    monkeypatch.setenv("OPENAI_ADMIN_API_KEY", "test-key")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    source_path = Path("scripts/report_openai_cost_to_slack.py").resolve()
    namespace = {"__name__": "__main__", "__file__": str(source_path)}
    exec(compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec"), namespace)

    assert "OpenAI API コスト監視" in capsys.readouterr().out
