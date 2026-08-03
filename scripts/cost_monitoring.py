"""定期コスト監視ジョブで共通利用する期間計算と表示用の関数。"""

from __future__ import annotations

from calendar import monthrange
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

    @property
    def last_day(self) -> date:
        """表示用の最終日（終了日の前日）を返す。"""
        return self.end - timedelta(days=1)

    def label(self) -> str:
        """Slack 表示用の期間ラベルを返す。"""
        return f"{self.start}〜{self.last_day}"


@dataclass(frozen=True)
class MonitoringWindows:
    """月次コスト監視で使う期間セット。"""

    focus: CostPeriod
    previous_comparable: CostPeriod
    previous_full_month: CostPeriod
    recent_full_months: tuple[CostPeriod, ...]
    is_complete_month: bool

    @property
    def mode_label(self) -> str:
        """通知見出し用のモード名を返す。"""
        return "完了月" if self.is_complete_month else "当月累計"


def _month_start(value: date) -> date:
    """指定日が属する月の1日を返す。"""
    return value.replace(day=1)


def _shift_months(value: date, months: int) -> date:
    """月初日を月単位でずらす。"""
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    return date(year, month, 1)


def _full_month(month_start: date) -> CostPeriod:
    """月初日を含む暦月の半開区間を返す。"""
    return CostPeriod(month_start, _shift_months(month_start, 1))


def monitoring_windows(now: datetime | None = None) -> MonitoringWindows:
    """JST の実行日から月次監視用の期間セットを計算する。"""
    today = (now or datetime.now(TOKYO)).astimezone(TOKYO).date()
    this_month = _month_start(today)
    previous_month = _shift_months(this_month, -1)

    if today.day == 1:
        focus = _full_month(previous_month)
        previous_comparable = _full_month(_shift_months(previous_month, -1))
        is_complete_month = True
    else:
        focus = CostPeriod(this_month, today)
        previous_comparable = CostPeriod(
            previous_month,
            previous_month + timedelta(days=focus.days),
        )
        is_complete_month = False

    recent_months = tuple(
        _full_month(_shift_months(this_month, -offset)) for offset in (3, 2, 1)
    )
    return MonitoringWindows(
        focus=focus,
        previous_comparable=previous_comparable,
        previous_full_month=_full_month(previous_month),
        recent_full_months=recent_months,
        is_complete_month=is_complete_month,
    )


def comparison_periods(now: datetime | None = None) -> tuple[CostPeriod, CostPeriod]:
    """後方互換: 今回期間と比較対象期間だけを返す。"""
    windows = monitoring_windows(now)
    return windows.focus, windows.previous_comparable


def format_usd(amount: Decimal) -> str:
    """Slack 通知向けに米ドルを小数第2位まで整形する。"""
    return f"${amount.quantize(Decimal('0.01')):,.2f}"


def percent_change(current: Decimal, previous: Decimal) -> str:
    """比較期間の増減率を表示する。"""
    if previous == 0:
        return "比較対象なし"
    return f"{((current - previous) / previous * Decimal('100')):+.1f}%"


def share_percent(part: Decimal, total: Decimal) -> str:
    """合計に対する割合を表示する。"""
    if total == 0:
        return "—"
    return f"{(part / total * Decimal('100')).quantize(Decimal('0.1'))}%"


def daily_average(total: Decimal, days: int) -> Decimal:
    """期間合計から日次平均を求める。"""
    if days <= 0:
        return Decimal()
    return total / Decimal(days)


def projected_month_total(mtd_total: Decimal, days_elapsed: int, as_of: date) -> Decimal:
    """当月累計から月末予測額を求める。"""
    if days_elapsed <= 0:
        return Decimal()
    days_in_month = monthrange(as_of.year, as_of.month)[1]
    return daily_average(mtd_total, days_elapsed) * Decimal(days_in_month)


def cost_deltas(
    current: dict[str, Decimal],
    previous: dict[str, Decimal],
) -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """項目ごとの増減を差分の大きい順に返す。"""
    names = set(current) | set(previous)
    rows: list[tuple[str, Decimal, Decimal, Decimal]] = []
    for name in names:
        now_amount = current.get(name, Decimal())
        prev_amount = previous.get(name, Decimal())
        rows.append((name, now_amount, prev_amount, now_amount - prev_amount))
    rows.sort(key=lambda item: item[3], reverse=True)
    return rows


def top_cost_items(
    costs: dict[str, Decimal],
    *,
    limit: int = 5,
) -> list[tuple[str, Decimal]]:
    """金額の大きい順に上位項目を返す。"""
    return sorted(costs.items(), key=lambda item: item[1], reverse=True)[:limit]


def month_trend_lines(
    month_totals: list[tuple[CostPeriod, Decimal]],
) -> list[str]:
    """直近完了月の合計推移を Slack 行へ整形する。"""
    if not month_totals:
        return ["• 月次データなし"]
    lines: list[str] = []
    for index, (period, total) in enumerate(month_totals):
        label = f"{period.start.year}-{period.start.month:02d}"
        if index == 0:
            change = ""
        else:
            change = f"（前月比 {percent_change(total, month_totals[index - 1][1])}）"
        lines.append(f"• {label}: {format_usd(total)}{change}")
    return lines
