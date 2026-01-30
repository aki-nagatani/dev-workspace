#!/usr/bin/env python3
"""Slack通知送信スクリプト

Slack Webhook URLを使用してメッセージを送信する。
環境変数 SLACK_WEBHOOK_URL からWebhook URLを取得する。

Usage:
    python send_slack_notification.py "メッセージ本文"
    python send_slack_notification.py --channel "#general" "メッセージ本文"
    python send_slack_notification.py --channel "@username" "メッセージ本文"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


class SlackNotificationError(RuntimeError):
    """Slack通知送信エラー。"""

    pass


def get_slack_webhook_url_from_mcp_config() -> str | None:
    """MCP設定ファイルからSlack Webhook URLを取得する。

    MCP設定ファイル（`~/.cursor/mcp.json` または `%APPDATA%\\Cursor\\User\\globalStorage\\saoudrizwan.claude-dev\\settings\\cline_mcp_settings.json`）
    から `text2slack` MCPサーバーの環境変数 `SLACK_WEBHOOK_URL` を読み取る。

    Returns:
        Slack Webhook URL（見つからない場合はNone）
    """
    # MCP設定ファイルの候補パス
    mcp_config_paths = [
        Path.home() / ".cursor" / "mcp.json",
        Path.home() / ".config" / "cursor" / "mcp.json",
        Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
    ]

    for config_path in mcp_config_paths:
        if not config_path.exists():
            continue

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # text2slack MCPサーバーの環境変数から取得
            mcp_servers = config.get("mcpServers", {})
            text2slack_config = mcp_servers.get("text2slack", {})
            env = text2slack_config.get("env", {})
            webhook_url = env.get("SLACK_WEBHOOK_URL")

            if webhook_url:
                return webhook_url
        except (json.JSONDecodeError, KeyError, OSError):
            # 設定ファイルの読み取りエラーは無視して次の候補を試す
            continue

    return None


def send_slack_message(
    webhook_url: str,
    text: str,
    channel: str | None = None,
    username: str | None = None,
    icon_emoji: str | None = None,
) -> None:
    """Slack Webhook URLを使用してメッセージを送信する。

    Args:
        webhook_url: Slack Webhook URL
        text: 送信するメッセージ本文
        channel: 送信先チャンネル（オプション、例: "#general", "@username"）
        username: ボット名（オプション）
        icon_emoji: アイコン絵文字（オプション、例: ":robot_face:"）

    Raises:
        SlackNotificationError: 送信に失敗した場合
    """
    payload: dict[str, Any] = {"text": text}

    if channel:
        payload["channel"] = channel
    if username:
        payload["username"] = username
    if icon_emoji:
        payload["icon_emoji"] = icon_emoji

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()

        # Slack Webhook APIは成功時に "ok" を返す
        if response.text != "ok":
            raise SlackNotificationError(
                f"Unexpected response from Slack: {response.text}"
            )
    except requests.exceptions.RequestException as exc:
        raise SlackNotificationError(f"Failed to send Slack message: {exc}") from exc


def main() -> int:
    """メイン処理。

    Returns:
        終了コード（0: 成功、1: エラー）
    """
    parser = argparse.ArgumentParser(
        description="Slack通知を送信する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "message",
        help="送信するメッセージ本文",
    )
    parser.add_argument(
        "--channel",
        help="送信先チャンネル（例: #general, @username）",
    )
    parser.add_argument(
        "--username",
        help="ボット名（デフォルト: Cursor AI Agent）",
        default="Cursor AI Agent",
    )
    parser.add_argument(
        "--icon-emoji",
        help="アイコン絵文字（例: :robot_face:）",
        default=":robot_face:",
    )
    parser.add_argument(
        "--webhook-url",
        help="Slack Webhook URL（デフォルト: 環境変数 SLACK_WEBHOOK_URL から取得）",
    )

    args = parser.parse_args()

    # Webhook URLの取得（優先順位: コマンドライン引数 > 環境変数 > MCP設定ファイル）
    webhook_url = args.webhook_url
    if not webhook_url:
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        webhook_url = get_slack_webhook_url_from_mcp_config()

    if not webhook_url:
        print(
            "Error: SLACK_WEBHOOK_URL is not set",
            file=sys.stderr,
        )
        print(
            "Please set SLACK_WEBHOOK_URL environment variable, configure it in MCP settings, or use --webhook-url option",
            file=sys.stderr,
        )
        return 1

    # メッセージ送信
    try:
        send_slack_message(
            webhook_url=webhook_url,
            text=args.message,
            channel=args.channel,
            username=args.username,
            icon_emoji=args.icon_emoji,
        )
        print("Slack notification sent successfully", file=sys.stderr)
        return 0
    except SlackNotificationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
