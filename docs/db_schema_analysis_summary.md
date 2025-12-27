# データベーススキーマ分析サマリー

## 分析日時

- **作成日時**: 2025-12-27
- **分析対象**: ローカルDocker環境（FishTrackローカルDBコンテナ）

## 分析結果サマリー

### 環境情報

- **環境**: Local Docker
- **データベース**: `fishtrack_db` (PostgreSQL)
- **分析日時**: 2025-12-27T22:54:34
- **テーブル数**: 11
- **総レコード数**: 415

### テーブル一覧とレコード数

| テーブル名 | カラム数 | レコード数 | 主キー | 外部キー数 | 備考 |
|-----------|---------|-----------|--------|----------|------|
| `fishtrack_user` | 7 | 3 | id | 0 | ユーザー情報 |
| `manufacturer` | 8 | 2 | id | 0 | メーカーマスタ |
| `ops_job_log` | 13 | 0 | id | 0 | ジョブログ |
| `ops_monitoring` | 11 | 0 | id | 0 | 運用監視 |
| `reel_holding` | 11 | 0 | id | 2 | リール保有データ |
| `reel_model` | 12 | 0 | id | 2 | リール型番マスタ |
| `reel_series` | 6 | 0 | id | 1 | リールシリーズマスタ |
| `rod_holding` | 12 | 4 | id | 3 | ロッド保有データ |
| `rod_model` | 25 | 90 | id | 2 | ロッド型番マスタ |
| `rod_series` | 6 | 6 | id | 1 | ロッドシリーズマスタ |
| `tackle_spec_import_log` | 13 | 310 | id | 1 | スペック取り込みログ |

## 仕様書との比較

### FishTrack仕様書（06_database.md）との比較

#### 存在するテーブル（仕様書に記載あり）

- ✅ `fishtrack_user` - 仕様書の「A. ユーザー（FishTrackUser）」に対応
- ✅ `manufacturer` - 仕様書の「N. メーカー（マスタ）」に対応
- ✅ `rod_series` - 仕様書の「E. ロッドシリーズ（RodSeries）」に対応
- ✅ `rod_model` - 仕様書の「F. ロッド型番（RodModel）」に対応
- ✅ `rod_holding` - 仕様書の「G. ロッド保有データ（RodHolding）」に対応
- ✅ `reel_series` - 仕様書の「H. リールシリーズ（ReelSeries）」に対応
- ✅ `reel_model` - 仕様書の「I. リール型番（ReelModel）」に対応
- ✅ `reel_holding` - 仕様書の「J. リール保有データ（ReelHolding）」に対応
- ✅ `ops_monitoring` - 仕様書の「O. OpsMonitoring（運用監視）」に対応
- ✅ `ops_job_log` - 仕様書の「P. OpsJobLog（ジョブログ）」に対応
- ✅ `tackle_spec_import_log` - 仕様書の「R. TackleSpecImportLog（スペック取り込みログ）」に対応

#### 仕様書に記載されているが存在しないテーブル

以下のテーブルは仕様書に記載されていますが、ローカルDBには存在しません：

- ❌ `catch` - 仕様書の「A. 釣果ログ（Catch）」
- ❌ `trip` - 仕様書の「B. 釣行（Trip）」
- ❌ `lure` - 仕様書の「C. ルアー（マスタ）」
- ❌ `lure_inventory` - 仕様書の「D. ルアー保有データ（購入情報一体管理）」
- ❌ `lure_photo` - 仕様書の「C. ルアー（マスタ）」内の付随テーブル
- ❌ `lure_photo_allowed_host` - 仕様書の「ルアー写真許可ホスト」
- ❌ `reel_line_history` - 仕様書の「L. リールライン管理」
- ❌ `field` - 仕様書の「M. フィールドマスタ」
- ❌ `area` - 仕様書の「M. フィールドマスタ」内のエリアマスタ
- ❌ `field_snap` - 仕様書の「K. フィールドスナップ」
- ❌ `catch_photo` - 仕様書の「A. 釣果ログ（Catch）」内の写真テーブル
- ❌ `catch_environment` - 仕様書の「A. 釣果ログ（Catch）」内の環境データテーブル
- ❌ `tackle_spec_import_draft` - 仕様書の「Q. TackleSpecImportDraft（廃止予定）」

**注意**: これらは未実装の機能または別のデータベースに存在する可能性があります。

### MyPokedex仕様書（06_database.md）との比較

ローカルDBにはMyPokedexのテーブルは存在しません。MyPokedexのテーブルは別のデータベース（`mypokedex_db`）またはshared-dbに存在する可能性があります。

## 主要な発見事項

### 1. テーブル構造の確認

- ✅ すべてのテーブルに主キーが設定されている
- ✅ 外部キー制約が適切に設定されている
- ✅ インデックスが適切に設定されている

### 2. カラム定義の確認

主要なテーブルのカラム定義を確認：

#### `rod_model`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `manufacturer_id`, `series_id`, `model_name`, `jan_code`, `list_price`
  - `length_ft`, `length_in`, `power`, `action`, `genre`
  - `weight_g`, `lure_weight_min_oz`, `lure_weight_max_oz`
  - `line_min_lb`, `line_max_lb`, `pieces`, `blank_material`
  - `carbon_rate_pct`, `release_year`, `features`, `custom_note`, `memo`
- ✅ `series_id`がNULL許可（移行期間中の互換性のため）

#### `rod_holding`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `user_id`, `model_id`, `rod_id`（旧カラム、互換用途）
  - `status`, `purchase_date`, `purchase_shop`, `purchase_price`
  - `condition`, `memo`
- ✅ `rod_id`がNULL許可（移行期間中の互換性のため）

### 3. 制約の確認

- ✅ ユニーク制約が適切に設定されている
  - `manufacturer.name` - ユニーク
  - `rod_series` - `manufacturer_id` + `series_name` の組み合わせでユニーク
  - `rod_model` - `series_id` + `model_name` の組み合わせでユニーク
  - `reel_series` - `manufacturer_id` + `series_name` の組み合わせでユニーク
  - `reel_model` - `series_id` + `model_name` の組み合わせでユニーク

### 4. 外部キー制約の確認

- ✅ すべての外部キー制約が適切に設定されている
- ✅ `ON DELETE RESTRICT` が適切に設定されている（データ整合性のため）

## 次のステップ

1. **本番環境の分析**: 本番DB（shared-db）のスキーマを分析する
2. **比較レポートの生成**: 本番とローカルの差異を確認する
3. **仕様書との完全な比較**: すべてのテーブルとカラムを仕様書と照合する
4. **マイグレーションリセットの準備**: 差異を確認した後、マイグレーションをリセットする

## 注意事項

- ローカルDBはFishTrackのローカルDBコンテナ（`fishtrack_db`）を分析しました
- shared-db（本番と同じDB）を分析するには、Dockerコンテナ内から実行するか、別の方法が必要です
- MyPokedexのテーブルは別のデータベースに存在する可能性があります

