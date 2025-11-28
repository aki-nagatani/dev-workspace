# archive/migration-complete テンプレート（2025-11-28作成）

以下は MyHobbySite 統合リポジトリをアーカイブする際に作成するタグ／リリースノートの雛形です。タグ名は `archive/migration-complete` を推奨し、内容は実際の作業結果で必ず更新してください。

## 1. サマリー

- **目的**: 例）MyHobbySite 統合リポジトリを履歴参照専用としてアーカイブ
- **実施日**: YYYY-MM-DD
- **担当**: （GitHubアカウント名）
- **対象リポジトリ**: MyHobbySite

## 2. 分割完了ステータス

| 項目 | FishTrack | MyPokedex | 備考 |
| --- | --- | --- | --- |
| 本番systemdサービス | `fishtrack.service` | `mypokedex.service` | 稼働中/停止中 |
| CI/CD deploy/rollback | ✅ | ✅ | `.github/workflows/ci.yml` |
| テストカバレッジ | 99.xx% | 99.xx% | `pytest -n auto --cov` |
| ドキュメント同期 | ✅ | ✅ | `dev-workspace` 参照 |

## 3. 実施内容

1. `dev-workspace/docs/plans/MyPokedexとFishTrack分割計画.md` の Phase 5 を完了
2. MyHobbySite README / docs/README をアーカイブ表記へ更新
3. GitHub Settings → Archive this repository を実行
4. `git bundle` で最終バックアップを取得（保存パスを記載）

## 4. 参照リンク

- FishTrack リポジトリ: https://github.com/aki-nagatani/FishTrack
- MyPokedex リポジトリ: https://github.com/aki-nagatani/MyPokedex
- dev-workspace（共通ドキュメント）: https://github.com/aki-nagatani/dev-workspace
- 分割計画書: `dev-workspace/docs/plans/MyPokedexとFishTrack分割計画.md`
- 本番移行ガイド: `dev-workspace/docs/plans/completed/production_migration_guide.md`

## 5. 追加メモ

- 例）Raspberry Pi 上の `/home/pi/MyHobbySite` を削除済み（バックアップ: s3://backup/...）
- 例）Cloudflare 側の設定に統合パスは残っていないことを確認

