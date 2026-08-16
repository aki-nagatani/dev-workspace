"""OpenAI Organization Costs API の定期サマリを Slack 向けに出力する。"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, time as datetime_time
from decimal import Decimal
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.cost_monitoring import (
    CostPeriod,
    MonitoringWindows,
    TOKYO,
    anomaly_summary,
    cursor_handoff_lines,
    daily_average,
    detect_daily_anomaly,
    evaluate_judgment,
    format_usd,
    month_trend_lines,
    monitoring_windows,
    percent_change,
    projected_month_total,
)


COSTS_URL = "https://api.openai.com/v1/organization/costs"
RETRYABLE_HTTP_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
MAX_REQUEST_ATTEMPTS = 4
DEFAULT_RETRY_DELAY_SECONDS = 1.0


def _timestamp(value: datetime) -> int:
    """JST の日付境界を Unix 時刻へ変換する。"""
    return int(value.timestamp())


def _retry_delay_seconds(error: HTTPError, retry_number: int) -> float:
    """Retry-After を優先し、なければ指数バックオフの待機秒数を返す。"""
    retry_after = error.headers.get("Retry-After") if error.headers else None
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            pass
    return DEFAULT_RETRY_DELAY_SECONDS * (2**retry_number)


def fetch_costs(api_key: str, period: CostPeriod) -> list[dict[str, Any]]:
    """Organization Costs API から全ページのバケットを取得する。429・一時5xxは再試行する。"""
    page: str | None = None
    buckets: list[dict[str, Any]] = []
    while True:
        start = datetime.combine(period.start, datetime_time.min, tzinfo=TOKYO)
        end = datetime.combine(period.end, datetime_time.min, tzinfo=TOKYO)
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
        for retry_number in range(MAX_REQUEST_ATTEMPTS):
            try:
                with urlopen(request, timeout=30) as response:  # noqa: S310
                    payload = json.load(response)
                break
            except HTTPError as error:
                is_last_attempt = retry_number == MAX_REQUEST_ATTEMPTS - 1
                if error.code not in RETRYABLE_HTTP_STATUS_CODES or is_last_attempt:
                    raise
                time.sleep(_retry_delay_seconds(error, retry_number))
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


def build_report(
    windows: MonitoringWindows,
    current_total: Decimal,
    previous_total: Decimal,
    previous_full_month_total: Decimal,
    recent_month_totals: list[tuple[CostPeriod, Decimal]],
    current_daily_costs: list[tuple[str, Decimal]],
) -> str:
    """Slack へ投稿する OpenAI コストサマリを生成する。"""
    projected = None
    if not windows.is_complete_month:
        projected = projected_month_total(
            current_total,
            windows.focus.days,
            windows.focus.start,
        )

    has_anomaly = detect_daily_anomaly(current_daily_costs) is not None
    judgment = evaluate_judgment(
        current_total=current_total,
        previous_total=previous_total,
        previous_full_month_total=previous_full_month_total,
        projected_total=projected,
        has_daily_anomaly=has_anomaly,
    )

    lines = [
        judgment.user_action_line(),
        f"*OpenAI API コスト監視（{windows.mode_label}）*",
        judgment.line(),
        (
            f"期間: {windows.focus.label()}"
            f"（比較: {windows.previous_comparable.label()}）"
        ),
        (
            f"合計: {format_usd(current_total)}"
            f"（同期間前月比 {percent_change(current_total, previous_total)}）"
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
        lines.append(f"日次平均: {format_usd(daily_average(current_total, windows.focus.days))}")

    if windows.is_complete_month:
        lines.extend(["直近完了月の推移:", *month_trend_lines(recent_month_totals)])

    lines.append(anomaly_summary(current_daily_costs))
    if judgment.needs_cursor_paste:
        focus_points = [
            "判定理由: " + (" / ".join(judgment.reasons) if judgment.reasons else "前月比増加"),
            "Organization Costs の合計増がどの用途か切り分ける",
            "FishTrack 管理者の OpenAI 利用量画面でプロダクト内訳を確認する",
            "AI補助スペック取込など短期間の集中利用がないか確認する",
        ]
        lines.extend(
            cursor_handoff_lines(
                target="OpenAI API",
                judgment=judgment,
                focus_points=focus_points,
            )
        )
    else:
        lines.append("内訳確認: FishTrack 管理者の OpenAI 利用量画面")
    return "\n".join(lines)


def main() -> None:
    """OpenAI の請求コストを取得して Slack 向けテキストを標準出力へ書き出す。"""
    api_key = os.environ["OPENAI_ADMIN_API_KEY"]
    windows = monitoring_windows()
    current_buckets = fetch_costs(api_key, windows.focus)
    recent_month_totals: list[tuple[CostPeriod, Decimal]] = []
    if windows.is_complete_month:
        recent_month_totals = [
            (period, total_cost(fetch_costs(api_key, period)))
            for period in windows.recent_full_months
        ]
    previous_total = total_cost(fetch_costs(api_key, windows.previous_comparable))
    previous_full_month_total = total_cost(fetch_costs(api_key, windows.previous_full_month))
    print(
        build_report(
            windows,
            total_cost(current_buckets),
            previous_total,
            previous_full_month_total,
            recent_month_totals,
            daily_cost_series(current_buckets),
        )
    )


if __name__ == "__main__":
    main()
