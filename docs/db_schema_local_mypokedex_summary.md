# MyPokedexローカルDB分析サマリー

## 分析日時

- **作成日時**: 2025-12-27
- **分析対象**: ローカルDocker環境（MyPokedexローカルDBコンテナ）

## 分析結果サマリー

### 環境情報

- **環境**: Local Docker (MyPokedex)
- **データベース**: `mypokedex_db` (PostgreSQL)
- **分析日時**: 2025-12-27T23:07:21
- **テーブル数**: 11
- **総レコード数**: 404

### テーブル一覧とレコード数

| テーブル名 | カラム数 | レコード数 | 主キー | 外部キー数 | 備考 |
|-----------|---------|-----------|--------|----------|------|
| `DexEntry` | 3 | 285 | nationalNo, dexType | 0 | 図鑑種別ごとの番号正規化 |
| `Pokemon` | 11 | 35 | nationalNo | 0 | 全国図鑑マスター |
| `Regist` | 3 | 37 | userId, nationalNo, dexType | 2 | ユーザーの図鑑登録状況 |
| `User` | 3 | 9 | id | 0 | 認証ユーザー情報 |
| `UserGameSetting` | 3 | 10 | userId, gameId | 2 | ユーザーごとのゲーム有効フラグ |
| `box_members` | 4 | 10 | userId, gameId, nationalNo, createdAt | 2 | ボックス内の所持個体履歴 |
| `evolution` | 3 | 10 | fromNationalNo, toNationalNo | 0 | 進化関係 |
| `party_members` | 5 | 3 | userId, gameId, slot | 2 | パーティ編成 |
| `GameTitle` | 4 | 4 | id | 0 | 対応ゲームタイトル一覧 |
| `Contact` | 8 | 1 | userId, createdAt | 1 | お問い合わせ情報 |
| `placement` | 5 | 0 | userId, slot, location | 1 | 移行期間用の配置共存テーブル |

## 仕様書との比較

### MyPokedex仕様書（06_database.md）との比較

#### 存在するテーブル（仕様書に記載あり）

- ✅ `Pokemon` - 仕様書の「A. Pokemon」に対応
- ✅ `DexEntry` - 仕様書の「DexEntry」に対応
- ✅ `Regist` - 仕様書の「Regist」に対応
- ✅ `Evolution` (`evolution`) - 仕様書の「Evolution」に対応
- ✅ `GameTitle` - 仕様書の「GameTitle」に対応
- ✅ `UserGameSetting` - 仕様書の「UserGameSetting」に対応
- ✅ `BoxMember` (`box_members`) - 仕様書の「BoxMember」に対応
- ✅ `PartyMember` (`party_members`) - 仕様書の「PartyMember」に対応
- ✅ `Placement` (`placement`) - 仕様書の「Placement」に対応
- ✅ `User` - 仕様書の「User」に対応
- ✅ `Contact` - 仕様書の「Contact」に対応

#### 仕様書に記載されているが存在しないテーブル

- ❌ `alembic_version` - マイグレーション管理テーブル（分析対象外の可能性）

**注意**: `alembic_version`はマイグレーション管理用のテーブルで、通常は分析対象に含めない場合があります。

## 主要な発見事項

### 1. テーブル構造の確認

- ✅ すべてのテーブルに主キーが設定されている
- ✅ 複合主キーを持つテーブルが多数存在（仕様書通り）
- ✅ 外部キー制約が適切に設定されている
- ✅ インデックスが適切に設定されている

### 2. 命名規則の確認

- ✅ テーブル名はPascalCaseとsnake_caseが混在（仕様書通り）
  - PascalCase: `Pokemon`, `Regist`, `DexEntry`, `GameTitle`, `UserGameSetting`, `User`, `Contact`
  - snake_case: `box_members`, `party_members`, `evolution`, `placement`
- ✅ 列名はcamelCase（仕様書通り）
  - `nationalNo`, `dexNo`, `type1`, `type2`, `spAtk`, `spDef`, `createdAt`, `updatedAt` など

### 3. カラム定義の確認

#### `Pokemon`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `nationalNo`, `nameJa`, `type1`, `type2`
  - `hp`, `attack`, `defense`, `spAtk`, `spDef`, `speed`, `total`
- ✅ 主キーは`nationalNo`（意味のあるキー）

#### `Regist`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `userId`, `nationalNo`, `dexType`
- ✅ 複合主キー: `userId`, `nationalNo`, `dexType`
- ✅ 外部キー: `userId` → `User.id`, `nationalNo` → `Pokemon.nationalNo`

#### `box_members`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `userId`, `gameId`, `nationalNo`, `createdAt`
- ✅ 複合主キー: `userId`, `gameId`, `nationalNo`, `createdAt`
- ✅ 外部キー: `userId` → `User.id`, `gameId` → `GameTitle.id`

#### `party_members`テーブル

- ✅ 仕様書に記載されている主要カラムが存在
  - `userId`, `gameId`, `nationalNo`, `slot`, `createdAt`
- ✅ 複合主キー: `userId`, `gameId`, `slot`
- ✅ 外部キー: `userId` → `User.id`, `gameId` → `GameTitle.id`

### 4. 制約の確認

- ✅ ユニーク制約が適切に設定されている
  - `User.username` - ユニーク
  - `GameTitle.key` - ユニーク
- ✅ 複合主キーが一意性を保証している
- ✅ 外部キー制約が適切に設定されている

### 5. インデックスの確認

- ✅ 仕様書に記載されているインデックスが存在
  - `ixRegistNational`: `nationalNo`
  - `ixRegistUserDex`: `userId`, `dexType`
  - `ix_box_user_game`: `userId`, `gameId`
  - `ix_box_user_game_nat_created`: `userId`, `gameId`, `nationalNo`, `createdAt`
  - `ix_party_user_game`: `userId`, `gameId`
  - `ix_party_user_game_slot`: `userId`, `gameId`, `slot`

## データ分布

### レコード数の多いテーブル

1. **`DexEntry`**: 285レコード - 図鑑種別ごとの番号正規化データ
2. **`Regist`**: 37レコード - ユーザーの図鑑登録状況
3. **`Pokemon`**: 35レコード - 全国図鑑マスター（一部のみ）

### レコード数の少ないテーブル

- **`placement`**: 0レコード - 移行期間用の配置共存テーブル（使用されていない可能性）
- **`Contact`**: 1レコード - お問い合わせ情報
- **`party_members`**: 3レコード - パーティ編成

## 次のステップ

1. **本番環境（shared-db）の分析**: 統合データベースのスキーマを分析する
2. **比較レポートの生成**: 
   - ローカル（FishTrack） vs 本番（shared-db）
   - ローカル（MyPokedex） vs 本番（shared-db）
   - 本番（shared-db）の完全なスキーマ
3. **仕様書との完全な比較**: すべてのテーブルとカラムを仕様書と照合する

## 注意事項

- ローカルDBはMyPokedexのローカルDBコンテナ（`mypokedex_db`）を分析しました
- 本番環境ではshared-db（統合データベース）を使用しているため、FishTrackとMyPokedexのテーブルが同じデータベースに存在します
- マイグレーションは統合管理されているため、本番環境のスキーマを確認することが重要です

