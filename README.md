# dev-workspace

全プロジェクト共通の開発ドキュメント・ワークスペース管理リポジトリ

## 概要

本リポジトリは、MyHobbySiteプロジェクト群（FishTrack、MyPokedex等）で共通して使用する開発ドキュメントとワークスペースファイルを管理します。2025-11-28時点でMyHobbySite統合リポジトリはアーカイブフェーズにあり、以降の更新はすべて本リポジトリおよび各アプリ固有リポジトリで行います。

## MyHobbySiteアーカイブ状況（2025-11-28）

- 2025-11-27に統合サービス（`myhobbysite.service`）を停止し、FishTrack / MyPokedexを独立運用に移行済み。
- 本リポジトリには分割計画（`docs/plans/MyPokedexとFishTrack分割計画.md`）および本番移行手順を正本として保存。
- MyHobbySiteリポジトリは履歴参照のみとし、READMEにもアーカイブバッジと参照リンクを追加済み。
- 最新ドキュメント・CI/CD記録は `FishTrack`, `MyPokedex`, `dev-workspace` 各リポジトリを参照する運用に切り替え。

## 目的

1. **共通開発ガイドラインの参照**
   - ガイドラインは Obsidian `DevProject/guidelines/` に集約（コーディング規約、テストカバレッジ方針、WEB指針、MCPサーバー設定ガイド等）

2. **統合開発環境としての役割**
   - Cursorマルチルートワークスペースファイルの管理
   - 共通開発ツールの設定

3. **プロジェクト間の一貫性の維持**
   - 全プロジェクトで共通の開発ルールを適用
   - ドキュメントの一元管理

## 構成

```
dev-workspace/
├── README.md                    # このファイル
├── dev-workspace.code-workspace # マルチルートワークスペースファイル
├── migrations/                  # 共通DBマイグレーション
├── scripts/                     # 共通スクリプト
└── .cursor/                     # Cursor設定テンプレート
    ├── rules/
    │   └── myrules.mdc
    ├── mcp.json
    └── commands/
```

共通開発ガイドラインは Obsidian `DevProject/guidelines/` に集約しています。

## 使用方法

### 各プロジェクトでの参照

各プロジェクトの `README.md` に以下のような参照リンクを記載してください：

```markdown
## 共通開発ガイドライン

本プロジェクトは、以下の共通開発ガイドラインに従います（Obsidian `DevProject/guidelines/` に集約）：

- コーディング規約
- テストカバレッジ方針
- WEBログ指針
- WEBセキュリティ指針
- MCPサーバー設定ガイド

詳細は Obsidian の DevProject/guidelines を参照してください。
```

### ワークスペースファイルの使用

Cursorで `dev-workspace.code-workspace` を開くことで、MyHobbySite（アーカイブ）、FishTrack、MyPokedex、dev-workspaceの各リポジトリを同時に管理できます。

## 更新ルール

- 共通開発ガイドラインの更新は、すべてのプロジェクトに影響するため慎重に行う
- 更新後は、各プロジェクトの `README.md` の参照リンクが正しいことを確認する（特にアーカイブ状況の記述）
- ワークスペースファイルは、新しいリポジトリが追加・削除された際やアーカイブ状態の更新時に必ず見直す

## ライセンス

（ライセンス情報を記載）

