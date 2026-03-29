---
name: python-code-error-fix
description: Python の構文エラー・型エラー・Lint エラー・インポート不整合など、コード修正案が要る問題の汎用手順。basedpyright 専用ではない。修正依頼時は先に本 SKILL を読む。
---

# Python コードエラー修正ガイド（汎用）

**basedpyright 専用ではない。** 次のような **Python ソースを直す作業**の共通入口とする。

| 区分 | 例 |
| --- | --- |
| **構文** | `SyntaxError`、`IndentationError`、不正な f-string、未閉じ括弧 |
| **静的解析** | basedpyright / Pyright / Pylance、mypy の指摘 |
| **Lint（エラー級）** | 未定義名、重複定義、不正な import（※スタイルのみはプロジェクト方針に従う） |
| **契約不一致** | ライブラリの `__init__` 引数型（例: `orig: BaseException` に `None` を渡さない） |

JavaScript / TypeScript / 他言語は **対象外**（各プロジェクトのツールに従う）。

---

## 汎用フロー（エラー種別の前に必ず踏む）

1. **メッセージと位置を読む**（ファイル・行番号・列・トレースの先頭付近）。
2. **分類する**: 構文 / 型 / 名前・import / 実行時の再現が必要か。
3. **根本原因を直す**（プロジェクトの「エラー対応規律」に従い、握りつぶし・安易な `ignore` は最終手段）。
4. **連鎖を見る**: 同ファイル・同ブロックに **同系統のエラーが残っていないか**。
5. **検証**:
   - 構文: `python -m py_compile path/to/file.py` 等でパース確認してもよい
   - 型・Lint: IDE / 相当コマンドで当該ファイルを再確認
   - 可能なら **pytest** や狭いスコープのテスト

---

## 構文エラー（Syntax / Indentation）

- **インデント**: ブロック単位で揃える（tab と space の混在に注意）。
- **括弧・引用符**: `()` `[]` `{}`、`"""` `'''` の対応を確認。
- **f-string**: 式内のクォート・**ネストした `f`** のルール（Python バージョン依存はプロジェクトの CI / `.python-version` に合わせる）。
- **新構文**: `match` や型パラメータ構文など、**ランタイムの Python バージョン**と一致しているか。

---

## 型チェッカー・オーバーロード

- **期待型と実際の型**をメッセージから特定する（代入元、戻り値、ジェネリック引数）。
- **スタブと実行時のギャップ**は、付録の典型パターンや公式シグネチャに合わせて直す（例: DB-API 例外の `orig` は `BaseException`）。
- **`type: ignore` / `cast`**: スタブ限界など **最後の手段**に限定。

---

## 検証チェックリスト

- [ ] 報告どおりのエラーが再現しない状態になった
- [ ] 同じファイルに **同类の残り**がない
- [ ] 必要なら **テスト**または **最小実行**で確認した

---

## 付録: SQLAlchemy / Flask-SQLAlchemy（列・クエリ）

`Model.col` だけでは `ColumnElement` にならず、次のような指摘が出ることがある。

- `指定された引数に一致する "query" のオーバーロードがありません`
- `クラス "str" の属性 "in_" にアクセスできません`

**Core 列**で組み立てる（単一テーブル想定）。

```python
from sqlalchemy import select
from sqlalchemy.orm import class_mapper

c = class_mapper(DexEntry).local_table.c
stmt = select(c.dexType).where(
    c.nationalNo == national_no,
    c.dexType.in_(value_list),
)
rows = db.session.scalars(stmt)
```

---

## 付録: 宣言モデルのコンストラクタ kwargs（型・スタブ）

スタブが `__init__` を知らない場合、**空インスタンス + 属性代入**。

```python
r = Regist()
r.userId = user_id
r.nationalNo = national_no
r.dexType = dex_type
db.session.add(r)
```

---

## 付録: `url_for` と動的クエリ

`**` で任意 dict を渡すと予約名衝突やオーバーロード誤解決がある。**`urllib.parse.urlencode`** でクエリを付けるか、`_` 始まりキーを除外。

---

## 付録: WTForms の `.data` と数値変換

`.data` は **`None` や空**があり得る。**`_coerce_int(value: object) -> int | None`** のようなヘルパで吸収し、`int(form.field.data)` を直接使わない。
