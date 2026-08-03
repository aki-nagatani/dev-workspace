"""AWS Cost Explorer の定期サマリを Slack 向け Markdown として出力する。"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any

from scripts.cost_monitoring import (
    CostPeriod,
    comparison_periods,
    format_usd,
    percent_change,
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
    current: CostPeriod,
    previous: CostPeriod,
    current_costs: dict[str, Decimal],
    previous_costs: dict[str, Decimal],
    current_daily_costs: list[tuple[str, Decimal]],
) -> str:
    """Slack へ投稿する AWS コストサマリを生成する。"""
    total_current = sum(current_costs.values(), Decimal())
    total_previous = sum(previous_costs.values(), Decimal())
    current_end = current.end - timedelta(days=1)
    previous_end = previous.end - timedelta(days=1)
    top_services = sorted(current_costs.items(), key=lambda item: item[1], reverse=True)[:3]
    service_lines = [
        f"• {service}: {format_usd(cost)}"
        for service, cost in top_services
    ] or ["• コストデータなし"]

    return "\n".join(
        [
            "*AWS コスト監視*",
            f"期間: {current.start}〜{current_end}",
            f"合計: {format_usd(total_current)}（前回比較: {percent_change(total_current, total_previous)}）",
            "上位サービス:",
            *service_lines,
            anomaly_summary(current_daily_costs),
            f"比較期間: {previous.start}〜{previous_end}",
        ]
    )


def main() -> None:
    """AWS Cost Explorer からサマリを作成して標準出力へ書き出す。"""
    import boto3

    current, previous = comparison_periods()
    client = boto3.client("ce", region_name="us-east-1")
    print(
        build_report(
            current,
            previous,
            service_costs(client, current),
            service_costs(client, previous),
            daily_costs(client, current),
        )
    )


if __name__ == "__main__":
    main()
