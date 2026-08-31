"""AWS Cost Explorer の定期サマリを Slack 向け Markdown として出力する。"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from scripts.cost_monitoring import (
    CostPeriod,
    MonitoringWindows,
    anomaly_summary,
    cursor_handoff_lines,
    daily_average,
    delta_lines,
    detect_daily_anomaly,
    evaluate_judgment,
    format_usd,
    month_trend_lines,
    monitoring_windows,
    percent_change,
    projected_month_total,
    share_percent,
    significant_decreases,
    significant_increases,
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


def _is_monthly_fixed_charge(service: str, usage_type: str) -> bool:
    """日次異常判定から除外する月次固定計上かを判定する。"""
    return service == "Tax" or (
        service == "Amazon Route 53" and usage_type == "HostedZone"
    )


def daily_costs_excluding_fixed_charges(
    client: Any,
    period: CostPeriod,
) -> tuple[list[tuple[str, Decimal]], list[tuple[str, str, Decimal]]]:
    """月次固定計上を分離した日次コストと固定費内訳を返す。"""
    results = _cost_and_usage(
        client,
        period,
        granularity="DAILY",
        group_by=[
            {"Type": "DIMENSION", "Key": "SERVICE"},
            {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
        ],
    )
    operational_costs: list[tuple[str, Decimal]] = []
    fixed_charges: list[tuple[str, str, Decimal]] = []
    for result in results:
        day = result["TimePeriod"]["Start"]
        operational_total = Decimal()
        for group in result.get("Groups", []):
            keys = group.get("Keys", [])
            service = keys[0] if keys else ""
            usage_type = keys[1] if len(keys) > 1 else ""
            amount = Decimal(group["Metrics"]["UnblendedCost"]["Amount"])
            if _is_monthly_fixed_charge(service, usage_type):
                label = (
                    service
                    if service == "Tax" or not usage_type
                    else f"{service}/{usage_type}"
                )
                fixed_charges.append((day, label, amount))
            else:
                operational_total += amount
        operational_costs.append((day, operational_total))
    return operational_costs, fixed_charges


def _fixed_charge_summary(fixed_charges: list[tuple[str, str, Decimal]]) -> str:
    """固定費内訳をサービス・UsageType単位でSlack向けに整形する。"""
    totals: dict[str, Decimal] = {}
    for _day, label, amount in fixed_charges:
        totals[label] = totals.get(label, Decimal()) + amount
    return "、".join(f"{label} {format_usd(amount)}" for label, amount in totals.items())


def build_report(
    windows: MonitoringWindows,
    current_costs: dict[str, Decimal],
    previous_costs: dict[str, Decimal],
    previous_full_month_total: Decimal,
    recent_month_totals: list[tuple[CostPeriod, Decimal]],
    current_daily_costs: list[tuple[str, Decimal]],
    *,
    fixed_daily_costs: list[tuple[str, str, Decimal]] | None = None,
) -> str:
    """Slack へ投稿する AWS コストサマリを生成する。"""
    total_current = sum(current_costs.values(), Decimal())
    total_previous = sum(previous_costs.values(), Decimal())
    projected = None
    if not windows.is_complete_month:
        projected = projected_month_total(
            total_current,
            windows.focus.days,
            windows.focus.start,
        )

    has_anomaly = detect_daily_anomaly(current_daily_costs) is not None
    judgment = evaluate_judgment(
        current_total=total_current,
        previous_total=total_previous,
        previous_full_month_total=previous_full_month_total,
        projected_total=projected,
        has_daily_anomaly=has_anomaly,
    )
    show_details = windows.is_complete_month or judgment.needs_cursor_paste

    top_services = top_cost_items(current_costs, limit=5 if windows.is_complete_month else 3)
    service_lines = [
        (
            f"• {service}: {format_usd(cost)}"
            f"（構成比 {share_percent(cost, total_current)}）"
        )
        for service, cost in top_services
    ] or ["• コストデータなし"]

    lines = [
        judgment.user_action_line(),
        f"*AWS コスト監視（{windows.mode_label}）*",
        judgment.line(),
        (
            f"期間: {windows.focus.label()}"
            f"（比較: {windows.previous_comparable.label()}）"
        ),
        (
            f"合計: {format_usd(total_current)}"
            f"（同期間前月比 {percent_change(total_current, total_previous)}）"
        ),
        (
            f"前月の完了月合計: {format_usd(previous_full_month_total)}"
            f"（{windows.previous_full_month.label()}）"
        ),
    ]
    if projected is not None:
        lines.append(
            f"月末予測: {format_usd(projected)}"
            f"（前月完了月比 {percent_change(projected, previous_full_month_total)}）"
        )
    else:
        lines.append(f"日次平均: {format_usd(daily_average(total_current, windows.focus.days))}")

    lines.extend(["上位サービス:", *service_lines])

    if show_details:
        increases = significant_increases(current_costs, previous_costs)
        decreases = significant_decreases(current_costs, previous_costs)
        lines.extend(
            [
                "増加上位:",
                *delta_lines(increases, empty_label="意味のある増加なし"),
            ]
        )
        if decreases:
            lines.extend(
                [
                    "減少上位:",
                    *delta_lines(decreases, empty_label="意味のある減少なし"),
                ]
            )

    if windows.is_complete_month:
        lines.extend(["直近完了月の推移:", *month_trend_lines(recent_month_totals)])

    lines.append(anomaly_summary(current_daily_costs))
    if fixed_daily_costs:
        lines.append(
            "日次固定費（異常判定から除外）: "
            + _fixed_charge_summary(fixed_daily_costs)
        )
    if judgment.needs_cursor_paste:
        increases = significant_increases(current_costs, previous_costs)
        focus_points = [
            "上位サービスと増加上位の内訳を Cost Explorer で確認する",
            "日次異常がある場合はその日付のサービス別コストを特定する",
            "不要リソース・設定ミス・想定外トラフィックの有無を切り分ける",
        ]
        if increases:
            focus_points.insert(
                0,
                "増加サービス: "
                + ", ".join(name for name, *_rest in increases[:3]),
            )
        if judgment.reasons:
            focus_points.insert(0, "判定理由: " + " / ".join(judgment.reasons))
        lines.extend(
            cursor_handoff_lines(
                target="AWS",
                judgment=judgment,
                focus_points=focus_points,
            )
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
    current_daily_costs, fixed_daily_costs = daily_costs_excluding_fixed_charges(
        client,
        windows.focus,
    )
    print(
        build_report(
            windows,
            service_costs(client, windows.focus),
            service_costs(client, windows.previous_comparable),
            period_total(client, windows.previous_full_month),
            recent_month_totals,
            current_daily_costs,
            fixed_daily_costs=fixed_daily_costs,
        )
    )


if __name__ == "__main__":
    main()
