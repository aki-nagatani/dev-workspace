"""定期コスト監視ジョブで共通利用する期間計算と表示用の関数。"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")

# 判定・詳細表示の初期閾値（少額運用向け）
# 毎月1日は前月完了月（当月は実績不足で予測しない）。
# GHA遅延で2日未明に落ちても、10日未満なら前月のまま。10日・20日は当月累計。
CURRENT_MONTH_REVIEW_FROM_DAY = 10
WARN_MOM_RATIO = Decimal("0.20")
WARN_ABSOLUTE_USD = Decimal("5")
INVESTIGATE_PROJECTION_RATIO = Decimal("0.20")
DAILY_ANOMALY_RATIO = Decimal("1.5")
MEANINGFUL_DELTA_USD = Decimal("1")
MEANINGFUL_DELTA_RATIO = Decimal("0.15")
MEANINGFUL_DELTA_MIN_USD = Decimal("0.5")


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


@dataclass(frozen=True)
class Judgment:
    """コスト監視の判定結果。"""

    level: str
    reasons: tuple[str, ...]

    @property
    def needs_cursor_paste(self) -> bool:
        """ユーザーが Slack 本文を Cursor へ貼るべき判定か。"""
        return self.level in {"要注意", "要確認"}

    def line(self) -> str:
        """Slack 先頭の判定行を返す。"""
        if not self.reasons:
            return f"判定: {self.level}"
        return f"判定: {self.level}（{' / '.join(self.reasons)}）"

    def user_action_line(self) -> str:
        """ユーザー向けの作業指示（貼る／何もしない）を返す。"""
        if self.needs_cursor_paste:
            return "【貼るだけ】このメッセージ全文を Cursor に貼る（考えなくてよい・追記不要）"
        return "【対応不要】判定が正常のため、貼り付けも不要"


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


def uses_previous_month_review(today: date) -> bool:
    """1日ジョブ相当なら前月完了月を見る。

    当月予測は10日未満だと実績不足。定期実行が遅れて2日になっても
    1日ジョブとして前月レビューを維持する。
    """
    return today.day < CURRENT_MONTH_REVIEW_FROM_DAY


def monitoring_windows(now: datetime | None = None) -> MonitoringWindows:
    """JST の実行日から月次監視用の期間セットを計算する。"""
    today = (now or datetime.now(TOKYO)).astimezone(TOKYO).date()
    this_month = _month_start(today)
    previous_month = _shift_months(this_month, -1)

    if uses_previous_month_review(today):
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


def is_meaningful_delta(delta: Decimal, previous: Decimal) -> bool:
    """増減が監視上意味のある大きさかを判定する。"""
    absolute = abs(delta)
    if absolute >= MEANINGFUL_DELTA_USD:
        return True
    if previous <= 0:
        return absolute >= MEANINGFUL_DELTA_MIN_USD
    ratio = absolute / previous
    return ratio >= MEANINGFUL_DELTA_RATIO and absolute >= MEANINGFUL_DELTA_MIN_USD


def significant_increases(
    current: dict[str, Decimal],
    previous: dict[str, Decimal],
    *,
    limit: int = 3,
) -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """意味のある増加だけを差分の大きい順に返す。"""
    rows = [
        row
        for row in cost_deltas(current, previous)
        if row[3] > 0 and is_meaningful_delta(row[3], row[2])
    ]
    return rows[:limit]


def significant_decreases(
    current: dict[str, Decimal],
    previous: dict[str, Decimal],
    *,
    limit: int = 3,
) -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """意味のある減少だけを差分の大きい順（減り幅大）に返す。"""
    rows = [
        row
        for row in reversed(cost_deltas(current, previous))
        if row[3] < 0 and is_meaningful_delta(row[3], row[2])
    ]
    return rows[:limit]


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


def detect_daily_anomaly(
    costs: list[tuple[str, Decimal]],
) -> tuple[str, Decimal] | None:
    """他日平均の1.5倍を超える日があればその日付と金額を返す。"""
    if len(costs) < 2:
        return None
    highest_date, highest_cost = max(costs, key=lambda item: item[1])
    other_costs = [cost for day, cost in costs if day != highest_date]
    average = sum(other_costs, Decimal()) / len(other_costs)
    if average > 0 and highest_cost > average * DAILY_ANOMALY_RATIO:
        return highest_date, highest_cost
    return None


def anomaly_summary(costs: list[tuple[str, Decimal]]) -> str:
    """日次異常の表示行を返す（正常時は短い文言）。"""
    if len(costs) < 2:
        return "日次異常なし（判定対象データ不足）"
    detected = detect_daily_anomaly(costs)
    if detected is None:
        return "日次異常なし"
    highest_date, highest_cost = detected
    other_costs = [cost for day, cost in costs if day != highest_date]
    average = sum(other_costs, Decimal()) / len(other_costs)
    return (
        f"日次異常: {highest_date} が他日の平均の"
        f"{(highest_cost / average):.1f}倍（{format_usd(highest_cost)}）"
    )


def evaluate_judgment(
    *,
    current_total: Decimal,
    previous_total: Decimal,
    previous_full_month_total: Decimal,
    projected_total: Decimal | None,
    has_daily_anomaly: bool,
) -> Judgment:
    """合計・予測・日次異常から監視判定を作る。"""
    investigate_reasons: list[str] = []
    warn_reasons: list[str] = []

    if has_daily_anomaly:
        investigate_reasons.append("日次異常あり")

    if projected_total is not None and previous_full_month_total > 0:
        projection_ratio = (
            projected_total - previous_full_month_total
        ) / previous_full_month_total
        if projection_ratio > INVESTIGATE_PROJECTION_RATIO:
            investigate_reasons.append(
                f"月末予測が前月比 {percent_change(projected_total, previous_full_month_total)}"
            )

    absolute_delta = current_total - previous_total
    if previous_total > 0:
        mom_ratio = absolute_delta / previous_total
        if mom_ratio > WARN_MOM_RATIO or absolute_delta > WARN_ABSOLUTE_USD:
            warn_reasons.append(f"同期間前月比 {percent_change(current_total, previous_total)}")
    elif absolute_delta > WARN_ABSOLUTE_USD:
        warn_reasons.append(f"同期間増分 {format_usd(absolute_delta)}")

    if investigate_reasons:
        return Judgment("要確認", tuple(investigate_reasons))
    if warn_reasons:
        return Judgment("要注意", tuple(warn_reasons))
    return Judgment("正常", ())


def delta_lines(
    rows: list[tuple[str, Decimal, Decimal, Decimal]],
    *,
    empty_label: str,
) -> list[str]:
    """増減行を Slack 表示用に整形する。"""
    if not rows:
        return [f"• {empty_label}"]
    return [
        f"• {name}: {format_usd(delta)}（{format_usd(prev)} → {format_usd(now)}）"
        for name, now, prev, delta in rows
    ]


def cursor_handoff_lines(
    *,
    target: str,
    judgment: Judgment,
    focus_points: list[str],
) -> list[str]:
    """Slack本文だけで Cursor が深掘りを開始できる依頼ブロックを返す。"""
    focus = focus_points or ["レポート記載の判定理由と増減要因を確認する"]
    return [
        "-----",
        "#cost-monitoring-handoff",
        "【Cursor依頼】",
        "ユーザー作業は貼り付けのみ完了。以降はエージェントが自動継続する。",
        "SKILL: aws-cost-monitoring",
        "SKILL path: dev-workspace/.agents/skills/aws-cost-monitoring/SKILL.md",
        f"対象: {target}",
        f"判定: {judgment.level}",
        (
            "依頼: このSlack通知本文だけを入力として深掘りを開始する。"
            "追加質問はせず、SKILLの実行フローに従い原因候補と改善案を日本語で返す。"
        ),
        "調査観点:",
        *[f"- {point}" for point in focus],
        "成果物:",
        "- 判定の妥当性（正常に戻せるか／要継続監視か）",
        "- 原因仮説（確度つき）",
        "- 優先度付き改善案（実施手順・注意点・概算効果）",
        "- 次にユーザーが取るべきこと（多くて3件）",
    ]
