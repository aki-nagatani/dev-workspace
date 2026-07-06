---
name: ec2-rds-connection
description: 本番AWSのEC2およびRDSへ、AI（Cursorエージェント）が接続する方法を提供する。Session Manager（start-session / send-command）とSSHの選択肢をまとめ、RDSはEC2経由で接続する手順を記載。EC2/RDS接続・本番確認・SSM・Session Managerの依頼時に使用する。
---

# EC2・RDS接続SKILL（AI用）

## 概要

本番AWSのEC2とRDSに、**AIエージェント（Cursor等）がターミナル経由で接続する**ための手順です。
人間向けの詳細手順は **Obsidian「DevProject/guidelines/EC2_SSH接続手順.md」** を参照してください。

## 接続方式の選択（AI向け）

| 目的 | 方式 | コマンド例 |
| --- | --- | --- |
| EC2で単発コマンド実行し結果を取得 | **Session Manager send-command** | 下記「send-command」参照 |
| EC2で対話的に複数コマンド | **Session Manager start-session** | `aws ssm start-session --target <id> --region ap-northeast-1` |
| EC2で単発コマンド（SSH鍵あり） | **SSH リモート** | `ssh -i <key> ec2-user@<ip> "command"` |
| RDSへクエリ実行 | **EC2経由で send-command 内で psql** | EC2上で psql を実行するコマンドを send-command で送る |

## 本番インスタンス（要確認）

- **おたよりナビ EC2**: `i-001cd3b0db58d9f78`（IP: 18.178.163.222、プライベート: 10.0.2.151）。アプリパス `/home/ec2-user/otayori-navi`。Amazon Linux 2。
- **FishTrack EC2**: `i-0cc5625e58feb39b8`（IP: 52.197.69.195）。※本番は `i-05e573f245ca9e2d1` の可能性あり。要確認。
- **MyPokedex EC2**: `i-0b2e6876c16609083`（IP: 13.158.196.131、プライベート: 10.1.1.230。※i-023a1623e48cabf1d は旧インスタンス）
- **リージョン**: `ap-northeast-1`
- 接続前に GitHub Secrets（`*_EC2_HOST`）または AWSコンソールで現行のインスタンスID・IPを確認すること。

## Session Manager send-command（推奨・単発コマンド）

AIがEC2上で1本コマンドを実行し、標準出力・標準エラーを取得する。

```powershell
# 1. 送信
$result = aws ssm send-command --instance-ids i-023a1623e48cabf1d --region ap-northeast-1 `
  --document-name "AWS-RunShellScript" `
  --parameters '{"commands":["cd /home/ec2-user && uname -a"]}' `
  --output json | ConvertFrom-Json
$commandId = $result.Command.CommandId

# 2. 待機後、結果取得
Start-Sleep -Seconds 5
aws ssm get-command-invocation --command-id $commandId --instance-id i-023a1623e48cabf1d --region ap-northeast-1 --output json
```

- 出力は `StandardOutputContent` / `StandardErrorContent`。成否は `Status` で判定。
- 複数行コマンドは `commands` に配列で複数指定可能（例: `["cd /home/ec2-user", "docker ps"]`）。

## Session Manager start-session（対話型）

同じターミナルでEC2のシェルに入り、続けてコマンドを送る場合。

```powershell
aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1
```

## SSH 単発コマンド（鍵がある場合）

```powershell
# FishTrack
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "uname -a"

# MyPokedex（IPは要確認）
ssh -i "$env:USERPROFILE\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@54.249.50.253 "uname -a"
```

## RDSへの接続（必ずEC2経由）

RDSはSSH不可。EC2に接続した上で、EC2上で `psql` を実行する。

- **send-command で実行**: EC2インスタンスIDを指定し、`commands` に `psql -h <RDSエンドポイント> -U <user> -d <db> -c "SELECT ..."` などを指定。パスワードは環境変数やSecrets Managerから取得し、平文でスクリプトに書かないこと。
- **ポートフォワーディング**: `AWS-StartPortForwardingSessionToRemoteHost` でRDSの5432をローカルにフォワードし、別ターミナルで `psql -h localhost -p <localPort> ...` で接続可能。

## 前提条件（AIが実行する環境）

- AWS CLI がインストール済み
- Session Manager 利用時: Session Manager プラグインがインストール済み（`session-manager-plugin --version`）
- 実行環境（Cursorのターミナル）に、ssm:StartSession / ssm:SendCommand 等の権限を持つAWS認証が設定済み（プロファイルまたは環境変数）

## 参照

- **詳細手順**: Obsidian `DevProject/guidelines/EC2_SSH接続手順.md`
- **本番インスタンス一覧・DB操作**: `dev-workspace/.agents/skills/production-db-access/SKILL.md`
