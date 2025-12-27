# データベーススキーマ分析レポート

## 環境情報

- **環境**: Local Docker (MyPokedex)
- **分析日時**: 2025-12-27T23:07:21.570386
- **テーブル数**: 11
- **総レコード数**: 404

## テーブル一覧

| テーブル名 | カラム数 | レコード数 | 主キー | 外部キー数 |
|-----------|---------|-----------|--------|----------|
| `Contact` | 8 | 1 | userId, createdAt | 1 |
| `DexEntry` | 3 | 285 | nationalNo, dexType | 0 |
| `GameTitle` | 4 | 4 | id | 0 |
| `Pokemon` | 11 | 35 | nationalNo | 0 |
| `Regist` | 3 | 37 | userId, nationalNo, dexType | 2 |
| `User` | 3 | 9 | id | 0 |
| `UserGameSetting` | 3 | 10 | userId, gameId | 2 |
| `box_members` | 4 | 10 | userId, gameId, nationalNo, createdAt | 2 |
| `evolution` | 3 | 10 | fromNationalNo, toNationalNo | 0 |
| `party_members` | 5 | 3 | userId, gameId, slot | 2 |
| `placement` | 5 | 0 | userId, slot, location | 1 |

## テーブル詳細

### Contact

**レコード数**: 1

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `category` | `VARCHAR(20)` | ✗ | - | ✗ |
| `message` | `TEXT` | ✗ | - | ✗ |
| `email` | `VARCHAR(255)` | ✓ | - | ✗ |
| `screenName` | `VARCHAR(50)` | ✓ | - | ✗ |
| `status` | `VARCHAR(20)` | ✗ | 'pending'::character varying | ✗ |
| `createdAt` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updatedAt` | `TIMESTAMP` | ✓ | - | ✗ |

#### 主キー

- `userId`, `createdAt`

#### 外部キー

- **Contact_userId_fkey**: `userId` → `User`(`id`)

#### インデックス

- **ix_contact_created_at**: `createdAt`
- **ix_contact_user_id**: `userId`

---

### DexEntry

**レコード数**: 285

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `nationalNo` | `INTEGER` | ✗ | - | ✗ |
| `dexType` | `VARCHAR(20)` | ✗ | - | ✗ |
| `dexNo` | `INTEGER` | ✗ | - | ✗ |

#### 主キー

- `nationalNo`, `dexType`

#### インデックス

- **ix_DexEntry_dexType_dexNo**: `dexType`, `dexNo`
- **ix_DexEntry_nationalNo**: `nationalNo`

---

### GameTitle

**レコード数**: 4

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('"GameTitle_id_seq"'::regclass) | ✓ |
| `key` | `VARCHAR(16)` | ✗ | - | ✗ |
| `nameJa` | `VARCHAR(50)` | ✗ | - | ✗ |
| `sortOrder` | `INTEGER` | ✗ | 1 | ✗ |

#### 主キー

- `id`

#### インデックス

- **GameTitle_key_key**: `key` (UNIQUE)

#### ユニーク制約

- **GameTitle_key_key**: `key`

---

### Pokemon

**レコード数**: 35

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `nationalNo` | `INTEGER` | ✗ | nextval('"Pokemon_nationalNo_seq"'::regclass) | ✓ |
| `nameJa` | `VARCHAR(100)` | ✗ | - | ✗ |
| `type1` | `VARCHAR(20)` | ✗ | - | ✗ |
| `type2` | `VARCHAR(20)` | ✓ | - | ✗ |
| `hp` | `INTEGER` | ✗ | - | ✗ |
| `attack` | `INTEGER` | ✗ | - | ✗ |
| `defense` | `INTEGER` | ✗ | - | ✗ |
| `spAtk` | `INTEGER` | ✗ | - | ✗ |
| `spDef` | `INTEGER` | ✗ | - | ✗ |
| `speed` | `INTEGER` | ✗ | - | ✗ |
| `total` | `INTEGER` | ✗ | - | ✗ |

#### 主キー

- `nationalNo`

#### インデックス

- **ixPokemonNameJa**: `nameJa`

---

### Regist

**レコード数**: 37

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `nationalNo` | `INTEGER` | ✗ | - | ✗ |
| `dexType` | `VARCHAR(9)` | ✗ | - | ✗ |

#### 主キー

- `userId`, `nationalNo`, `dexType`

#### 外部キー

- **Regist_nationalNo_fkey**: `nationalNo` → `Pokemon`(`nationalNo`)
- **Regist_userId_fkey**: `userId` → `User`(`id`)

#### インデックス

- **ixRegistNational**: `nationalNo`
- **ixRegistUserDex**: `userId`, `dexType`

---

### User

**レコード数**: 9

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('"User_id_seq"'::regclass) | ✓ |
| `username` | `VARCHAR(50)` | ✗ | - | ✗ |
| `passwordHash` | `VARCHAR(200)` | ✗ | - | ✗ |

#### 主キー

- `id`

#### インデックス

- **uxUserName**: `username` (UNIQUE)

#### ユニーク制約

- **uxUserName**: `username`

---

### UserGameSetting

**レコード数**: 10

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `gameId` | `INTEGER` | ✗ | - | ✗ |
| `isEnabled` | `BOOLEAN` | ✗ | - | ✗ |

#### 主キー

- `userId`, `gameId`

#### 外部キー

- **UserGameSetting_gameId_fkey**: `gameId` → `GameTitle`(`id`)
- **UserGameSetting_userId_fkey**: `userId` → `User`(`id`)

---

### box_members

**レコード数**: 10

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `gameId` | `INTEGER` | ✗ | - | ✗ |
| `nationalNo` | `INTEGER` | ✗ | - | ✗ |
| `createdAt` | `TIMESTAMP` | ✗ | - | ✗ |

#### 主キー

- `userId`, `gameId`, `nationalNo`, `createdAt`

#### 外部キー

- **box_members_gameId_fkey**: `gameId` → `GameTitle`(`id`)
- **fk_box_members_user**: `userId` → `User`(`id`)

#### インデックス

- **ix_box_members_nationalNo**: `nationalNo`
- **ix_box_members_userId**: `userId`
- **ix_box_user_game**: `userId`, `gameId`
- **ix_box_user_game_nat_created**: `userId`, `gameId`, `nationalNo`, `createdAt`

---

### evolution

**レコード数**: 10

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `fromNationalNo` | `INTEGER` | ✗ | - | ✗ |
| `toNationalNo` | `INTEGER` | ✗ | - | ✗ |
| `conditionText` | `VARCHAR(200)` | ✗ | - | ✗ |

#### 主キー

- `fromNationalNo`, `toNationalNo`

#### インデックス

- **ix_evolution_fromNationalNo**: `fromNationalNo`
- **ix_evolution_toNationalNo**: `toNationalNo`

---

### party_members

**レコード数**: 3

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `gameId` | `INTEGER` | ✗ | - | ✗ |
| `nationalNo` | `INTEGER` | ✗ | - | ✗ |
| `slot` | `INTEGER` | ✗ | - | ✗ |
| `createdAt` | `TIMESTAMP` | ✗ | - | ✗ |

#### 主キー

- `userId`, `gameId`, `slot`

#### 外部キー

- **fk_party_members_user**: `userId` → `User`(`id`)
- **party_members_gameId_fkey**: `gameId` → `GameTitle`(`id`)

#### インデックス

- **ix_party_members_userId**: `userId`
- **ix_party_user_game**: `userId`, `gameId`
- **ix_party_user_game_slot**: `userId`, `gameId`, `slot`
- **ix_party_user_poke**: `userId`, `nationalNo`

---

### placement

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `userId` | `INTEGER` | ✗ | - | ✗ |
| `nationalNo` | `INTEGER` | ✗ | - | ✗ |
| `location` | `VARCHAR(10)` | ✗ | - | ✗ |
| `slot` | `INTEGER` | ✗ | - | ✗ |
| `createdAt` | `TIMESTAMP` | ✗ | - | ✗ |

#### 主キー

- `userId`, `slot`, `location`

#### 外部キー

- **fk_placement_user**: `userId` → `User`(`id`)

#### インデックス

- **ix_placement_nationalNo**: `nationalNo`
- **ix_placement_userId**: `userId`

---

