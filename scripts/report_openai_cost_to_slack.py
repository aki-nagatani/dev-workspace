"""OpenAI Organization Costs API の定期サマリを Slack 向けに出力する。"""

from __future__ import annotations

import json
import os
from datetime import datetime, time
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.cost_monitoring import (
    CostPeriod,
    MonitoringWindows,
    TOKYO,
    daily_average,
    format_usd,
    month_trend_lines,
    monitoring_windows,
    percent_change,
    projected_month_total,
)


COSTS_URL = "https://api.openai.com/v1/organization/costs"


def _timestamp(value: datetime) -> int:
    """JST の日付境界を Unix 時刻へ変換する。"""
    return int(value.timestamp())


def fetch_costs(api_key: str, period: CostPeriod) -> list[dict[str, Any]]:
    """Organization Costs API から全ページのバケットを取得する。"""
    page: str | None = None
    buckets: list[dict[str, Any]] = []
    while True:
        start = datetime.combine(period.start, time.min, tzinfo=TOKYO)
        end = datetime.combine(period.end, time.min, tzinfo=TOKYO)
        query: dict[str, str | int] = {
            "start_time": _timestamp(start),
            "end_time": _timestamp(end),
            "bucket_width": "1d",
        }
        if page:
            query["page"] = page
        request = Request(
            f"{COSTS_URL}?{urlencode(query)}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310
            payload = json.load(response)
        buckets.extend(payload.get("data", []))
        page = payload.get("next_page")
        if not page:
            return buckets


def total_cost(buckets: list[dict[str, Any]]) -> Decimal:
    """Costs API のバケットから USD 合計を集計する。"""
    return sum(
        (
            Decimal(str(result["amount"]["value"]))
            for bucket in buckets
            for result in bucket.get("results", [])
        ),
        Decimal(),
    )


def daily_cost_series(buckets: list[dict[str, Any]]) -> list[tuple[str, Decimal]]:
    """日次バケットを日付と合計額の系列へ変換する。"""
    series: list[tuple[str, Decimal]] = []
    for bucket in buckets:
        start_time = bucket.get("start_time")
        if start_time is None:
            continue
        day = datetime.fromtimestamp(int(start_time), tz=TOKYO).date().isoformat()
        amount = sum(
            (Decimal(str(result["amount"]["value"])) for result in bucket.get("results", [])),
            Decimal(),
        )
        series.append((day, amount))
    return series


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
    current_total: Decimal,
    previous_total: Decimal,
    previous_full_month_total: Decimal,
    recent_month_totals: list[tuple[CostPeriod, Decimal]],
    current_daily_costs: list[tuple[str, Decimal]],
) -> str:
    """Slack へ投稿する OpenAI コストサマリを生成する。"""
    avg_daily = daily_average(current_total, windows.focus.days)
    lines = [
        f"*OpenAI API コスト監視（{windows.mode_label}）*",
        f"期間: {windows.focus.label()}",
        (
            f"合計: {format_usd(current_total)}"
            f"（同期間前月比 {percent_change(current_total, previous_total)}）"
        ),
        f"日次平均: {format_usd(avg_daily)}",
        (
            f"前月の完了月合計: {format_usd(previous_full_month_total)}"
            f"（{windows.previous_full_month.label()}）"
        ),
    ]
    if not windows.is_complete_month:
        projected = projected_month_total(
            current_total,
            windows.focus.days,
            windows.focus.start,
        )
        lines.append(
            f"月末予測: {format_usd(projected)}"
            f"（前月完了月比 {percent_change(projected, previous_full_month_total)}）"
        )

    lines.extend(
        [
            "直近完了月の推移:",
            *month_trend_lines(recent_month_totals),
            anomaly_summary(current_daily_costs),
            f"比較期間: {windows.previous_comparable.label()}",
            "内訳確認: FishTrack 管理者の OpenAI 利用量画面",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    """OpenAI の請求コストを取得して Slack 向けテキストを標準出力へ書き出す。"""
    api_key = os.environ["OPENAI_ADMIN_API_KEY"]
    windows = monitoring_windows()
    current_buckets = fetch_costs(api_key, windows.focus)
    recent_month_totals = [
        (period, total_cost(fetch_costs(api_key, period)))
        for period in windows.recent_full_months
    ]
    print(
        build_report(
            windows,
            total_cost(current_buckets),
            total_cost(fetch_costs(api_key, windows.previous_comparable)),
            total_cost(fetch_costs(api_key, windows.previous_full_month)),
            recent_month_totals,
            daily_cost_series(current_buckets),
        )
    )


if __name__ == "__main__":
    main()
