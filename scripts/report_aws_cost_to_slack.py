"""AWS Cost Explorer の定期サマリを Slack 向け Markdown として出力する。"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from scripts.cost_monitoring import (
    CostPeriod,
    MonitoringWindows,
    cost_deltas,
    daily_average,
    format_usd,
    month_trend_lines,
    monitoring_windows,
    percent_change,
    projected_month_total,
    share_percent,
    top_cost_items,
)


def _cost_and_usage(
    client: Any,
    period: CostPeriod,
    *,
    granularity: str,
    group_by: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """指定期間の Unblended Cost を Cost Explorer から取得する。"""
    request: dict[str, Any] = {
        "TimePeriod": {"Start": period.start.isoformat(), "End": period.end.isoformat()},
        "Granularity": granularity,
        "Metrics": ["UnblendedCost"],
    }
    if group_by:
        request["GroupBy"] = group_by

    results: list[dict[str, Any]] = []
    while True:
        response = client.get_cost_and_usage(**request)
        results.extend(response.get("ResultsByTime", []))
        next_page = response.get("NextPageToken")
        if not next_page:
            return results
        request["NextPageToken"] = next_page


def service_costs(client: Any, period: CostPeriod) -> dict[str, Decimal]:
    """サービス別コストを集計する。"""
    results = _cost_and_usage(
        client,
        period,
        granularity="MONTHLY",
        group_by=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    costs: dict[str, Decimal] = {}
    for result in results:
        for group in result.get("Groups", []):
            service = group["Keys"][0]
            amount = Decimal(group["Metrics"]["UnblendedCost"]["Amount"])
            costs[service] = costs.get(service, Decimal()) + amount
    return costs


def period_total(client: Any, period: CostPeriod) -> Decimal:
    """期間合計コストを取得する。"""
    results = _cost_and_usage(client, period, granularity="MONTHLY")
    total = Decimal()
    for result in results:
        total += Decimal(result["Total"]["UnblendedCost"]["Amount"])
    return total


def daily_costs(client: Any, period: CostPeriod) -> list[tuple[str, Decimal]]:
    """日次コストを取得し、急増判定に使う。"""
    results = _cost_and_usage(client, period, granularity="DAILY")
    return [
        (
            result["TimePeriod"]["Start"],
            Decimal(result["Total"]["UnblendedCost"]["Amount"]),
        )
        for result in results
    ]


def anomaly_summary(costs: list[tuple[str, Decimal]]) -> str:
    """平均の1.5倍を超える日次コストがあるときだけ警告を返す。"""
    if len(costs) < 2:
        return "日次異常: 判定対象データ不足"

    highest_date, highest_cost = max(costs, key=lambda item: item[1])
    other_costs = [cost for day, cost in costs if day != highest_date]
    average = sum(other_costs, Decimal()) / len(other_costs)
    if average > 0 and highest_cost > average * Decimal("1.5"):
        return (
            f"日次異常: {highest_date} が他日の平均の"
            f"{(highest_cost / average):.1f}倍（{format_usd(highest_cost)}）"
        )
    return "日次異常: 検知なし"


def build_report(
    windows: MonitoringWindows,
    current_costs: dict[str, Decimal],
    previous_costs: dict[str, Decimal],
    previous_full_month_total: Decimal,
    recent_month_totals: list[tuple[CostPeriod, Decimal]],
    current_daily_costs: list[tuple[str, Decimal]],
) -> str:
    """Slack へ投稿する AWS コストサマリを生成する。"""
    total_current = sum(current_costs.values(), Decimal())
    total_previous = sum(previous_costs.values(), Decimal())
    avg_daily = daily_average(total_current, windows.focus.days)
    top_services = top_cost_items(current_costs, limit=5)
    service_lines = [
        (
            f"• {service}: {format_usd(cost)}"
            f"（構成比 {share_percent(cost, total_current)}）"
        )
        for service, cost in top_services
    ] or ["• コストデータなし"]

    deltas = cost_deltas(current_costs, previous_costs)
    increases = [row for row in deltas if row[3] > 0][:3]
    decreases = [row for row in reversed(deltas) if row[3] < 0][:3]
    increase_lines = [
        f"• {name}: {format_usd(delta)}（{format_usd(prev)} → {format_usd(now)}）"
        for name, now, prev, delta in increases
    ] or ["• 増加サービスなし"]
    decrease_lines = [
        f"• {name}: {format_usd(delta)}（{format_usd(prev)} → {format_usd(now)}）"
        for name, now, prev, delta in decreases
    ] or ["• 減少サービスなし"]

    lines = [
        f"*AWS コスト監視（{windows.mode_label}）*",
        f"期間: {windows.focus.label()}",
        (
            f"合計: {format_usd(total_current)}"
            f"（同期間前月比 {percent_change(total_current, total_previous)}）"
        ),
        f"日次平均: {format_usd(avg_daily)}",
        (
            f"前月の完了月合計: {format_usd(previous_full_month_total)}"
            f"（{windows.previous_full_month.label()}）"
        ),
    ]
    if not windows.is_complete_month:
        projected = projected_month_total(
            total_current,
            windows.focus.days,
            windows.focus.start,
        )
        lines.append(
            f"月末予測: {format_usd(projected)}"
            f"（前月完了月比 {percent_change(projected, previous_full_month_total)}）"
        )

    lines.extend(
        [
            "上位サービス:",
            *service_lines,
            "増加上位:",
            *increase_lines,
            "減少上位:",
            *decrease_lines,
            "直近完了月の推移:",
            *month_trend_lines(recent_month_totals),
            anomaly_summary(current_daily_costs),
            f"比較期間: {windows.previous_comparable.label()}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    """AWS Cost Explorer からサマリを作成して標準出力へ書き出す。"""
    import boto3

    windows = monitoring_windows()
    client = boto3.client("ce", region_name="us-east-1")
    recent_month_totals = [
        (period, period_total(client, period)) for period in windows.recent_full_months
    ]
    print(
        build_report(
            windows,
            service_costs(client, windows.focus),
            service_costs(client, windows.previous_comparable),
            period_total(client, windows.previous_full_month),
            recent_month_totals,
            daily_costs(client, windows.focus),
        )
    )


if __name__ == "__main__":
    main()
