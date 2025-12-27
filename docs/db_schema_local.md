# データベーススキーマ分析レポート

## 環境情報

- **環境**: Local Docker
- **分析日時**: 2025-12-27T22:54:34.302746
- **テーブル数**: 11
- **総レコード数**: 415

## テーブル一覧

| テーブル名 | カラム数 | レコード数 | 主キー | 外部キー数 |
|-----------|---------|-----------|--------|----------|
| `fishtrack_user` | 7 | 3 | id | 0 |
| `manufacturer` | 8 | 2 | id | 0 |
| `ops_job_log` | 13 | 0 | id | 0 |
| `ops_monitoring` | 11 | 0 | id | 0 |
| `reel_holding` | 11 | 0 | id | 2 |
| `reel_model` | 12 | 0 | id | 2 |
| `reel_series` | 6 | 0 | id | 1 |
| `rod_holding` | 12 | 4 | id | 3 |
| `rod_model` | 25 | 90 | id | 2 |
| `rod_series` | 6 | 6 | id | 1 |
| `tackle_spec_import_log` | 13 | 310 | id | 1 |

## テーブル詳細

### fishtrack_user

**レコード数**: 3

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('fishtrack_user_id_seq'::regclass) | ✓ |
| `username` | `VARCHAR(64)` | ✗ | - | ✗ |
| `password_hash` | `VARCHAR(255)` | ✗ | - | ✗ |
| `is_active` | `BOOLEAN` | ✗ | - | ✗ |
| `is_admin` | `BOOLEAN` | ✗ | false | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### インデックス

- **ix_fishtrack_user_username**: `username` (UNIQUE)

---

### manufacturer

**レコード数**: 2

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('manufacturer_id_seq'::regclass) | ✓ |
| `name` | `VARCHAR(128)` | ✗ | - | ✗ |
| `name_kana` | `VARCHAR(128)` | ✓ | - | ✗ |
| `country` | `VARCHAR(2)` | ✓ | - | ✗ |
| `website_url` | `VARCHAR(255)` | ✓ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### インデックス

- **manufacturer_name_key**: `name` (UNIQUE)

#### ユニーク制約

- **manufacturer_name_key**: `name`

---

### ops_job_log

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('ops_job_log_id_seq'::regclass) | ✓ |
| `job_name` | `VARCHAR(64)` | ✗ | - | ✗ |
| `entity_type` | `VARCHAR(64)` | ✓ | - | ✗ |
| `entity_id` | `INTEGER` | ✓ | - | ✗ |
| `status` | `VARCHAR(32)` | ✗ | - | ✗ |
| `attempt` | `INTEGER` | ✗ | 1 | ✗ |
| `started_at` | `TIMESTAMP` | ✗ | - | ✗ |
| `finished_at` | `TIMESTAMP` | ✓ | - | ✗ |
| `duration_ms` | `INTEGER` | ✓ | - | ✗ |
| `error_code` | `VARCHAR(128)` | ✓ | - | ✗ |
| `error_detail` | `TEXT` | ✓ | - | ✗ |
| `payload` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | CURRENT_TIMESTAMP | ✗ |

#### 主キー

- `id`

#### インデックス

- **idx_ops_job_log_entity**: `entity_type`, `entity_id`
- **idx_ops_job_log_job**: `job_name`, `started_at`
- **idx_ops_job_log_status**: `status`, `started_at`

---

### ops_monitoring

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('ops_monitoring_id_seq'::regclass) | ✓ |
| `event_type` | `VARCHAR(64)` | ✗ | - | ✗ |
| `scope` | `VARCHAR(128)` | ✓ | - | ✗ |
| `occurrences` | `INTEGER` | ✗ | - | ✗ |
| `first_seen_at` | `TIMESTAMP` | ✗ | - | ✗ |
| `last_seen_at` | `TIMESTAMP` | ✗ | - | ✗ |
| `last_payload` | `TEXT` | ✓ | - | ✗ |
| `status` | `VARCHAR(32)` | ✗ | - | ✗ |
| `notes` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | - | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | - | ✗ |

#### 主キー

- `id`

---

### reel_holding

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('reel_holding_id_seq'::regclass) | ✓ |
| `model_id` | `INTEGER` | ✗ | - | ✗ |
| `status` | `VARCHAR(16)` | ✗ | - | ✗ |
| `purchase_date` | `DATE` | ✓ | - | ✗ |
| `purchase_shop` | `VARCHAR(128)` | ✓ | - | ✗ |
| `purchase_price` | `INTEGER` | ✓ | - | ✗ |
| `condition` | `VARCHAR(16)` | ✗ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `user_id` | `INTEGER` | ✗ | - | ✗ |

#### 主キー

- `id`

#### 外部キー

- **fk_reel_holding_user_id**: `user_id` → `fishtrack_user`(`id`)
- **reel_holding_model_id_fkey**: `model_id` → `reel_model`(`id`)

#### インデックス

- **idx_reel_holding_user_id**: `user_id`

---

### reel_model

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('reel_model_id_seq'::regclass) | ✓ |
| `manufacturer_id` | `INTEGER` | ✗ | - | ✗ |
| `series_id` | `INTEGER` | ✗ | - | ✗ |
| `model_name` | `VARCHAR(128)` | ✗ | - | ✗ |
| `jan_code` | `VARCHAR(16)` | ✓ | - | ✗ |
| `gear_ratio` | `VARCHAR(32)` | ✓ | - | ✗ |
| `list_price` | `INTEGER` | ✓ | - | ✗ |
| `weight_g` | `INTEGER` | ✓ | - | ✗ |
| `reel_type` | `VARCHAR(16)` | ✗ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### 外部キー

- **reel_model_manufacturer_id_fkey**: `manufacturer_id` → `manufacturer`(`id`)
- **reel_model_series_id_fkey**: `series_id` → `reel_series`(`id`)

#### インデックス

- **uq_reel_model_name_per_series**: `series_id`, `model_name` (UNIQUE)

#### ユニーク制約

- **uq_reel_model_name_per_series**: `series_id`, `model_name`

---

### reel_series

**レコード数**: 0

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('reel_series_id_seq'::regclass) | ✓ |
| `manufacturer_id` | `INTEGER` | ✗ | - | ✗ |
| `series_name` | `VARCHAR(128)` | ✗ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### 外部キー

- **reel_series_manufacturer_id_fkey**: `manufacturer_id` → `manufacturer`(`id`)

#### インデックス

- **uq_reel_series_name_per_manufacturer**: `manufacturer_id`, `series_name` (UNIQUE)

#### ユニーク制約

- **uq_reel_series_name_per_manufacturer**: `manufacturer_id`, `series_name`

---

### rod_holding

**レコード数**: 4

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('rod_holding_id_seq'::regclass) | ✓ |
| `rod_id` | `INTEGER` | ✓ | - | ✗ |
| `model_id` | `INTEGER` | ✗ | - | ✗ |
| `status` | `VARCHAR(16)` | ✗ | - | ✗ |
| `purchase_date` | `DATE` | ✗ | - | ✗ |
| `purchase_shop` | `VARCHAR(128)` | ✓ | - | ✗ |
| `purchase_price` | `INTEGER` | ✓ | - | ✗ |
| `condition` | `VARCHAR(16)` | ✗ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `user_id` | `INTEGER` | ✗ | - | ✗ |

#### 主キー

- `id`

#### 外部キー

- **fk_rod_holding_user_id**: `user_id` → `fishtrack_user`(`id`)
- **rod_holding_model_id_fkey**: `model_id` → `rod_model`(`id`)
- **rod_holding_rod_id_fkey**: `rod_id` → `rod_model`(`id`)

#### インデックス

- **idx_rod_holding_user_id**: `user_id`

---

### rod_model

**レコード数**: 90

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('rod_model_id_seq'::regclass) | ✓ |
| `manufacturer_id` | `INTEGER` | ✗ | - | ✗ |
| `series_id` | `INTEGER` | ✓ | - | ✗ |
| `model_name` | `VARCHAR(128)` | ✗ | - | ✗ |
| `jan_code` | `VARCHAR(16)` | ✓ | - | ✗ |
| `list_price` | `INTEGER` | ✓ | - | ✗ |
| `length_ft` | `INTEGER` | ✗ | - | ✗ |
| `length_in` | `INTEGER` | ✗ | - | ✗ |
| `power` | `VARCHAR(64)` | ✗ | - | ✗ |
| `action` | `VARCHAR(64)` | ✗ | - | ✗ |
| `genre` | `VARCHAR(16)` | ✗ | - | ✗ |
| `weight_g` | `INTEGER` | ✓ | - | ✗ |
| `lure_weight_min_oz` | `NUMERIC(10, 6)` | ✓ | - | ✗ |
| `lure_weight_max_oz` | `NUMERIC(10, 6)` | ✓ | - | ✗ |
| `line_min_lb` | `NUMERIC(5, 2)` | ✓ | - | ✗ |
| `line_max_lb` | `NUMERIC(5, 2)` | ✓ | - | ✗ |
| `pieces` | `VARCHAR(32)` | ✓ | - | ✗ |
| `blank_material` | `VARCHAR(128)` | ✓ | - | ✗ |
| `carbon_rate_pct` | `NUMERIC(4, 1)` | ✓ | - | ✗ |
| `release_year` | `INTEGER` | ✓ | - | ✗ |
| `features` | `TEXT` | ✓ | - | ✗ |
| `custom_note` | `TEXT` | ✓ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### 外部キー

- **rod_model_manufacturer_id_fkey**: `manufacturer_id` → `manufacturer`(`id`)
- **rod_model_series_id_fkey**: `series_id` → `rod_series`(`id`)

#### インデックス

- **uq_rod_model_series_name**: `series_id`, `model_name` (UNIQUE)

#### ユニーク制約

- **uq_rod_model_series_name**: `series_id`, `model_name`

---

### rod_series

**レコード数**: 6

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('rod_series_id_seq'::regclass) | ✓ |
| `manufacturer_id` | `INTEGER` | ✗ | - | ✗ |
| `series_name` | `VARCHAR(128)` | ✗ | - | ✗ |
| `memo` | `TEXT` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### 外部キー

- **rod_series_manufacturer_id_fkey**: `manufacturer_id` → `manufacturer`(`id`)

#### インデックス

- **uq_rod_series_name_per_manufacturer**: `manufacturer_id`, `series_name` (UNIQUE)

#### ユニーク制約

- **uq_rod_series_name_per_manufacturer**: `manufacturer_id`, `series_name`

---

### tackle_spec_import_log

**レコード数**: 310

#### カラム定義

| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |
|---------|-----|---------|-----------|---------|
| `id` | `INTEGER` | ✗ | nextval('tackle_spec_import_log_id_seq'::regclass) | ✓ |
| `category` | `VARCHAR(32)` | ✗ | - | ✗ |
| `intent` | `VARCHAR(16)` | ✗ | - | ✗ |
| `mode` | `VARCHAR(16)` | ✗ | - | ✗ |
| `result` | `VARCHAR(16)` | ✗ | - | ✗ |
| `target_master_id` | `INTEGER` | ✓ | - | ✗ |
| `operator_user_id` | `INTEGER` | ✗ | - | ✗ |
| `source_url` | `TEXT` | ✗ | 'unknown'::text | ✗ |
| `summary` | `TEXT` | ✓ | - | ✗ |
| `error_detail` | `TEXT` | ✓ | - | ✗ |
| `committed_at` | `TIMESTAMP` | ✓ | - | ✗ |
| `created_at` | `TIMESTAMP` | ✗ | now() | ✗ |
| `updated_at` | `TIMESTAMP` | ✗ | now() | ✗ |

#### 主キー

- `id`

#### 外部キー

- **tackle_spec_import_log_operator_user_id_fkey**: `operator_user_id` → `fishtrack_user`(`id`)

#### インデックス

- **idx_tsi_log_category**: `category`, `result`
- **idx_tsi_log_created**: `created_at`
- **idx_tsi_log_operator**: `operator_user_id`, `created_at`

---

