# dev-workspace

全プロジェクト共通の開発ドキュメント・ワークスペース管理リポジトリ

## 概要

本リポジトリは、MyHobbySiteプロジェクト群（FishTrack、MyPokedex等）で共通して使用する開発ドキュメントとワークスペースファイルを管理します。

## 目的

1. **共通開発ガイドラインの管理**
   - コーディング規約
   - テストカバレッジ方針
   - MCPサーバー設定ガイド

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
├── guidelines/                  # 共通開発ガイドライン
│   ├── コーディング規約.md
│   ├── テストカバレッジ方針.md
│   └── MCP_SERVERS.md
└── .cursor/                     # Cursor設定テンプレート（将来追加予定）
    ├── rules/
    │   └── myrules.mdc
    ├── mcp.json
    └── commands/
```

## 使用方法

### 各プロジェクトでの参照

各プロジェクトの `README.md` に以下のような参照リンクを記載してください：

```markdown
## 共通開発ガイドライン

本プロジェクトは、以下の共通開発ガイドラインに従います：

- [コーディング規約](https://github.com/aki-nagatani/dev-workspace/blob/main/guidelines/コーディング規約.md)
- [テストカバレッジ方針](https://github.com/aki-nagatani/dev-workspace/blob/main/guidelines/テストカバレッジ方針.md)
- [MCPサーバー設定ガイド](https://github.com/aki-nagatani/dev-workspace/blob/main/guidelines/MCP_SERVERS.md)

詳細は [共通開発ガイドライン](https://github.com/aki-nagatani/dev-workspace) を参照してください。
```

### ワークスペースファイルの使用

Cursorで `MyHobbySite.code-workspace` を開くことで、複数のリポジトリを同時に管理できます。

## 更新ルール

- 共通開発ガイドラインの更新は、すべてのプロジェクトに影響するため慎重に行う
- 更新後は、各プロジェクトの `README.md` の参照リンクが正しいことを確認する
- ワークスペースファイルは、新しいリポジトリが追加された際に更新する

## ライセンス

（ライセンス情報を記載）

