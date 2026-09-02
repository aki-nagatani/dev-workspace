"""Slack 通知スクリプトの本文読込と Webhook 解決を検証する。"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.send_slack_notification import (
    load_notification_text,
    read_env_file_value,
    resolve_webhook_url,
)


def test_load_notification_text_from_file_keeps_dollar_amounts(tmp_path: Path) -> None:
    """ファイル経由の本文は $200 などの金額記号を維持する。"""
    path = tmp_path / "msg.txt"
    path.write_text("プラン: Ultra（$200/月） on-demand $0.00\n", encoding="utf-8")

    text = load_notification_text(None, str(path))

    assert "$200" in text
    assert "$0.00" in text


def test_load_notification_text_requires_exactly_one_source() -> None:
    """本文の位置引数とファイルはどちらか一方だけを受け付ける。"""
    with pytest.raises(ValueError):
        load_notification_text(None, None)


def test_read_env_file_value_returns_named_key(tmp_path: Path) -> None:
    """指定キーだけを読み、他キーは返さない。"""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SLACK_WEBHOOK_URL=https://hooks.example/generic\n"
        "CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL=https://hooks.example/cursor\n",
        encoding="utf-8",
    )

    assert read_env_file_value(env_file, "CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL") == (
        "https://hooks.example/cursor"
    )
    assert read_env_file_value(env_file, "MISSING") is None


def test_resolve_webhook_url_dedicated_key_does_not_fallback(tmp_path: Path) -> None:
    """専用キー未設定なら汎用 SLACK_WEBHOOK_URL へフォールバックしない。"""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SLACK_WEBHOOK_URL=https://hooks.example/generic\n",
        encoding="utf-8",
    )

    found = resolve_webhook_url(
        cli_webhook_url=None,
        webhook_env_key="CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL",
        environ={},
        env_file=env_file,
    )

    assert found is None


def test_resolve_webhook_url_dedicated_from_environ(tmp_path: Path) -> None:
    """専用キーはプロセス環境変数を .env より先に使う。"""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL=https://hooks.example/file\n",
        encoding="utf-8",
    )

    found = resolve_webhook_url(
        cli_webhook_url=None,
        webhook_env_key="CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL",
        environ={"CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL": "https://hooks.example/env"},
        env_file=env_file,
    )

    assert found == "https://hooks.example/env"


def test_resolve_webhook_url_cli_overrides_dedicated_key(tmp_path: Path) -> None:
    """CLI の URL は専用キーより優先する。"""
    found = resolve_webhook_url(
        cli_webhook_url="https://hooks.example/cli",
        webhook_env_key="CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL",
        environ={},
        env_file=tmp_path / ".env",
    )

    assert found == "https://hooks.example/cli"


def test_load_notification_text_from_positional_argument() -> None:
    """位置引数の本文もそのまま返す。"""
    assert load_notification_text("hello", None) == "hello"


def test_resolve_webhook_url_dedicated_key_from_env_file(tmp_path: Path) -> None:
    """専用キーは .env の該当行だけを使う。"""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SLACK_WEBHOOK_URL=https://hooks.example/generic\n"
        "CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL=https://hooks.example/cursor\n",
        encoding="utf-8",
    )

    found = resolve_webhook_url(
        cli_webhook_url=None,
        webhook_env_key="CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL",
        environ={},
        env_file=env_file,
    )

    assert found == "https://hooks.example/cursor"
