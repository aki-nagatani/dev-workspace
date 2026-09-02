#!/usr/bin/env python3
"""Slack通知送信スクリプト

Slack Webhook URLを使用してメッセージを送信する。
環境変数 SLACK_WEBHOOK_URL からWebhook URLを取得する。

Usage:
    python send_slack_notification.py "メッセージ本文"
    python send_slack_notification.py --message-file temp/message.txt
    python send_slack_notification.py --channel "#general" "メッセージ本文"
    python send_slack_notification.py --channel "@username" "メッセージ本文"
    python send_slack_notification.py --message-file temp/message.txt \\
        --webhook-env-key CURSOR_COST_MONITORING_SLACK_WEBHOOK_URL
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


def project_env_file() -> Path:
    """スクリプト基準のプロジェクトルート `.env` パスを返す。"""
    return Path(__file__).resolve().parent.parent / ".env"


def read_env_file_value(env_file: Path, key: str) -> str | None:
    """`.env` から指定キーの値を読む。見つからなければ None。"""
    if not env_file.exists():
        return None

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                env_key, value = line.split("=", 1)
                if env_key.strip() == key:
                    parsed = value.strip().strip('"').strip("'")
                    if parsed:
                        return parsed
    except OSError:
        pass

    return None


def get_slack_webhook_url_from_env_file() -> str | None:
    """プロジェクトルートの.envファイルから汎用 Slack Webhook URLを取得する。"""
    return read_env_file_value(project_env_file(), "SLACK_WEBHOOK_URL")


def load_notification_text(message: str | None, message_file: str | None) -> str:
    """位置引数または UTF-8 ファイルから通知本文を読む。

    PowerShell は二重引用符内の `$200` 等を変数展開するため、
    金額を含む本文はファイル経由にする。
    """
    if message_file:
        return Path(message_file).read_text(encoding="utf-8")
    if message:
        return message
    raise ValueError("message or --message-file is required")


def resolve_webhook_url(
    *,
    cli_webhook_url: str | None,
    webhook_env_key: str | None,
    environ: dict[str, str] | None = None,
    env_file: Path | None = None,
) -> str | None:
    """Webhook URL を解決する。専用キー指定時は汎用キーへフォールバックしない。"""
    if cli_webhook_url:
        return cli_webhook_url

    env = environ if environ is not None else os.environ
    env_path = env_file if env_file is not None else project_env_file()

    if webhook_env_key:
        from_env = env.get(webhook_env_key)
        if from_env:
            return from_env
        return read_env_file_value(env_path, webhook_env_key)

    webhook_url = env.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        return webhook_url
    webhook_url = read_env_file_value(env_path, "SLACK_WEBHOOK_URL")
    if webhook_url:
        return webhook_url
    webhook_url = get_slack_webhook_url_from_mcp_config()
    if webhook_url:
        return webhook_url
    return get_slack_webhook_url_from_local_config()


def get_slack_webhook_url_from_local_config() -> str | None:
    """プロジェクトルートのconfig.local.jsonファイルからSlack Webhook URLを取得する。

    Returns:
        Slack Webhook URL（見つからない場合はNone）
    """
    # スクリプトの場所からプロジェクトルートを推定
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_file = project_root / "config.local.json"

    if not config_file.exists():
        return None

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            webhook_url = config.get("SLACK_WEBHOOK_URL")
            if webhook_url:
                return webhook_url
    except (json.JSONDecodeError, KeyError, OSError):
        # 設定ファイルの読み取りエラーは無視
        pass

    return None


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
        nargs="?",
        help="送信するメッセージ本文（金額の $ を含む場合は --message-file を使う）",
    )
    parser.add_argument(
        "--message-file",
        help="UTF-8 の本文ファイル（PowerShell の $ 展開を避ける）",
    )
    parser.add_argument(
        "--webhook-env-key",
        help=".env の Webhook キー名。指定時は SLACK_WEBHOOK_URL へフォールバックしない",
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

    if bool(args.message) == bool(args.message_file):
        print(
            "Error: specify exactly one of positional message or --message-file",
            file=sys.stderr,
        )
        return 1

    try:
        text = load_notification_text(args.message, args.message_file)
    except OSError as exc:
        print(f"Error: failed to read --message-file: {exc}", file=sys.stderr)
        return 1

    webhook_url = resolve_webhook_url(
        cli_webhook_url=args.webhook_url,
        webhook_env_key=args.webhook_env_key,
    )

    if not webhook_url:
        if args.webhook_env_key:
            print(
                f"Error: {args.webhook_env_key} is not set",
                file=sys.stderr,
            )
            print(
                "Dedicated webhook has no generic SLACK_WEBHOOK_URL fallback.",
                file=sys.stderr,
            )
            return 1
        print(
            "Error: SLACK_WEBHOOK_URL is not set",
            file=sys.stderr,
        )
        print(
            "Please set SLACK_WEBHOOK_URL using one of the following methods:",
            file=sys.stderr,
        )
        print("  1. Command line: --webhook-url option", file=sys.stderr)
        print("  2. Environment variable: SLACK_WEBHOOK_URL", file=sys.stderr)
        print("  3. .env file: Create .env file in project root with SLACK_WEBHOOK_URL=...", file=sys.stderr)
        print("  4. MCP settings: Configure in ~/.cursor/mcp.json", file=sys.stderr)
        print("  5. Local config: Create config.local.json in project root with SLACK_WEBHOOK_URL", file=sys.stderr)
        return 1

    try:
        send_slack_message(
            webhook_url=webhook_url,
            text=text,
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
