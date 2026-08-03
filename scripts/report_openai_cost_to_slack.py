"""OpenAI Organization Costs API の定期サマリを Slack 向けに出力する。"""

from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.cost_monitoring import (
    CostPeriod,
    TOKYO,
    comparison_periods,
    format_usd,
    percent_change,
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


def build_report(
    current: CostPeriod,
    previous: CostPeriod,
    current_total: Decimal,
    previous_total: Decimal,
) -> str:
    """Slack へ投稿する OpenAI コストサマリを生成する。"""
    current_end = current.end - timedelta(days=1)
    previous_end = previous.end - timedelta(days=1)
    return "\n".join(
        [
            "*OpenAI API コスト監視*",
            f"期間: {current.start}〜{current_end}",
            f"合計: {format_usd(current_total)}（前回比較: {percent_change(current_total, previous_total)}）",
            f"比較期間: {previous.start}〜{previous_end}",
            "内訳確認: FishTrack 管理者の OpenAI 利用量画面",
        ]
    )


def main() -> None:
    """OpenAI の請求コストを取得して Slack 向けテキストを標準出力へ書き出す。"""
    api_key = os.environ["OPENAI_ADMIN_API_KEY"]
    current, previous = comparison_periods()
    print(
        build_report(
            current,
            previous,
            total_cost(fetch_costs(api_key, current)),
            total_cost(fetch_costs(api_key, previous)),
        )
    )


if __name__ == "__main__":
    main()
