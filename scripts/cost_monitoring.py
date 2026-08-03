"""定期コスト監視ジョブで共通利用する期間計算と表示用の関数。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")


@dataclass(frozen=True)
class CostPeriod:
    """Cost Explorer と OpenAI Costs API に渡す比較期間。"""

    start: date
    end: date

    @property
    def days(self) -> int:
        """終了日を含まない期間の日数を返す。"""
        return (self.end - self.start).days


def comparison_periods(now: datetime | None = None) -> tuple[CostPeriod, CostPeriod]:
    """JST の実行日から今回と比較対象の期間を計算する。"""
    today = (now or datetime.now(TOKYO)).astimezone(TOKYO).date()
    month_start = today.replace(day=1)

    if today.day == 1:
        previous_month_end = month_start
        previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
        baseline_start = (previous_month_start - timedelta(days=1)).replace(day=1)
        return (
            CostPeriod(previous_month_start, previous_month_end),
            CostPeriod(baseline_start, previous_month_start),
        )

    current = CostPeriod(month_start, today)
    previous_month_end = month_start
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    return (
        current,
        CostPeriod(
            previous_month_start,
            previous_month_start + timedelta(days=current.days),
        ),
    )


def format_usd(amount: Decimal) -> str:
    """Slack 通知向けに米ドルを小数第2位まで整形する。"""
    return f"${amount.quantize(Decimal('0.01')):,.2f}"


def percent_change(current: Decimal, previous: Decimal) -> str:
    """比較期間の増減率を表示する。"""
    if previous == 0:
        return "比較対象なし"
    return f"{((current - previous) / previous * Decimal('100')):+.1f}%"
