---
name: test-code-generator
description: Generate comprehensive test code for Python (pytest) and JavaScript (Jest) projects to achieve 99% test coverage. Use when users request test generation, test coverage improvement, or adding tests for specific functions, classes, or modules. Continuously generates tests until 99% coverage is achieved. Supports unit tests, integration tests, edge cases, error handling, and mocking patterns. NEVER modifies source code - only generates test code. If source code issues are found, proposes fixes but never modifies code without permission.
---

# Test Code Generator

## Overview

このスキルは、Python（pytest）とJavaScript（Jest）の包括的なテストコードを生成し、**テストカバレッジ99%以上を達成するまで継続してテストコードを生成します**。既存のコードベースを分析し、適切なテストパターン、モック、フィクスチャを使用して高品質なテストコードを作成します。

**重要**: テストカバレッジ方針については、[テストカバレッジ方針.md](../../docs/guidelines/テストカバレッジ方針.md) を参照してください。

## 基本原則

### 1. カバレッジ目標

- **目標カバレッジ**: 99%以上（Python、JavaScript共通）
- **継続的な生成**: カバレッジ99%を達成するまで、継続してテストコードを生成する
- **カバレッジ指標**: 
  - Python: ブランチ、関数、行、ステートメントすべて99%以上
  - JavaScript: branches, functions, lines, statements すべて99%以上

### 2. ソースコードの改変禁止

**絶対に禁止事項**:
- ❌ ソースコードの修正・変更
- ❌ ソースコードの削除
- ❌ ソースコードへのコメント追加（テスト除外用の`# pragma: no cover`など）
- ❌ ソースコードのリファクタリング

**許可されること**:
- ✅ テストコードの生成のみ
- ✅ テストファイルの作成・更新
- ✅ カバレッジレポートの確認と分析

### 3. ソースコードに不備がある場合の対応

ソースコードに不備や問題を発見した場合：

1. **修正案を提案する**: 問題点と修正案を明確に説明する
2. **無断で修正しない**: ユーザーの承認なしにソースコードを修正しない
3. **テストは生成する**: 不備があっても、可能な範囲でテストコードは生成する
4. **問題点を記録する**: 発見した問題点を明確に文書化する

### 4. テスト除外の禁止

テストカバレッジ方針に従い、以下は禁止です：

- ❌ ファイル単位の除外（`omit`設定の使用）
- ❌ 行単位の除外（`# pragma: no cover`の安易な使用）
- ❌ テスト実行時のスキップ（`pytest.skip()`、`test.skip()`の安易な使用）

**認められる例外**（例外的な場合のみ）:
- 型チェック専用コード（`if TYPE_CHECKING:`ブロック）
- 開発環境専用コード（本番環境では絶対に実行されない）
- 実装上どうしても再現できない安全弁（理由を明確に文書化）

## ワークフロー

### 1. カバレッジレポートの確認

まず、現在のカバレッジ状況を確認します：

- **Python**: `pytest --cov=src --cov-branch --cov-report=term-missing` を実行してカバレッジを確認
- **JavaScript**: `npm run test:coverage` を実行してカバレッジを確認
- **未カバー部分の特定**: カバレッジレポートから未カバーの行、ブランチ、関数を特定

### 2. 対象コードの分析

テストを生成する前に、以下を確認します：

- **ソースコードの構造**: 関数、クラス、モジュールの依存関係
- **既存のテストパターン**: プロジェクト内の既存テストファイルの構造とスタイル
- **テスト設定**: `pyproject.toml`、`package.json`、`conftest.py`、`setup.js`などの設定ファイル
- **依存関係**: データベース、外部API、モックが必要な依存関係
- **未カバー部分**: カバレッジレポートで特定した未カバーの部分

### 3. テストタイプの決定

生成するテストの種類を決定します：

- **ユニットテスト**: 単一の関数やメソッドのテスト
- **統合テスト**: 複数のコンポーネント間の相互作用のテスト
- **エッジケース**: 境界値、異常系、エラーハンドリングのテスト
- **モックテスト**: 外部依存関係をモックしたテスト
- **未カバー部分のテスト**: カバレッジレポートで特定した未カバー部分のテスト

### 4. テストコードの生成

既存のパターンに従ってテストコードを生成します。詳細なパターンは [references/test_patterns.md](references/test_patterns.md) を参照してください。

**重要**: ソースコードは一切変更しません。テストコードのみを生成します。

### 5. カバレッジの再確認と継続

テストコード生成後：

1. カバレッジを再確認する
2. 99%未満の場合は、未カバー部分を特定して追加のテストを生成する
3. 99%以上になるまで、ステップ1-4を繰り返す
4. ソースコードに不備を発見した場合は、修正案を提案する（修正はしない）

## Python (pytest) テスト生成

### 基本パターン

```python
"""Module description.

This module tests [target module/function].
システムの品質を確保する
"""

from __future__ import annotations

# 必要なインポート
from mypokedex.models.user import User
from mypokedex.extensions import db


def test_function_name_normal_case(app, client):
    """Test description for normal case."""
    with app.app_context():
        db.create_all()
        # テストデータの準備
        user = User(email="test@example.com")
        db.session.add(user)
        db.session.commit()
    
    # テスト実行
    response = client.get("/endpoint")
    
    # アサーション
    assert response.status_code == 200
```

### 重要なポイント

- **docstring**: 各テスト関数に明確な説明を追加
- **fixtureの使用**: `app`、`client`などの既存fixtureを活用
- **データベース操作**: `app.app_context()`内で実行
- **エラーハンドリング**: try-finallyでクリーンアップを確実に実行
- **モック**: 外部依存関係は適切にモック

詳細は [references/python_patterns.md](references/python_patterns.md) を参照してください。

## JavaScript (Jest) テスト生成

### 基本パターン

```javascript
/**
 * Module description
 * 
 * Test description
 * システムの品質を確保する
 */

describe('Module Name', () => {
    let originalConsole;
    let originalWindow;

    beforeEach(() => {
        jest.resetModules();
        jest.clearAllMocks();

        // consoleのモック
        originalConsole = console.log;
        console.log = jest.fn();
        console.error = jest.fn();

        // window.locationのモック
        delete global.window;
        global.window = {
            location: {
                href: 'http://localhost',
                pathname: '/',
                origin: 'http://localhost',
                search: '',
                hash: ''
            },
            sessionStorage: {
                getItem: jest.fn(() => null),
                setItem: jest.fn(),
                removeItem: jest.fn(),
                clear: jest.fn()
            }
        };

        // DOMのモック
        global.document = {
            querySelector: jest.fn(() => null),
            querySelectorAll: jest.fn(() => []),
            getElementById: jest.fn(() => null)
        };
    });

    afterEach(() => {
        console.log = originalConsole;
    });

    test('should handle normal case', () => {
        // テスト実行
        const result = functionUnderTest();

        // アサーション
        expect(result).toBe(expectedValue);
    });
});
```

### 重要なポイント

- **describe/it構造**: 論理的なグループ化
- **beforeEach/afterEach**: テスト間の状態リセット
- **モックの適切な使用**: DOM、window、consoleなどのモック
- **非同期処理**: `async/await`または`Promise`の適切な処理

詳細は [references/javascript_patterns.md](references/javascript_patterns.md) を参照してください。

## テストカバレッジの達成

### カバレッジ目標

生成するテストコードは、以下のカバレッジ目標を達成することを目指します：

- **Python**: ブランチ、関数、行、ステートメントすべて99%以上
- **JavaScript**: branches, functions, lines, statements すべて99%以上

### カバレッジ達成プロセス

1. **カバレッジレポートの確認**: 
   - Python: `pytest --cov=src --cov-branch --cov-report=term-missing`
   - JavaScript: `npm run test:coverage`

2. **未カバー部分の特定**: 
   - カバレッジレポートから未カバーの行、ブランチ、関数を特定
   - 優先順位を決定（ビジネスロジック > ユーティリティ関数 > 単純なgetter/setter）

3. **テストコードの生成**: 
   - 未カバー部分に対してテストコードを生成
   - 既存のテストパターンに従う

4. **カバレッジの再確認**: 
   - テスト実行後、カバレッジを再確認
   - 99%未満の場合は、ステップ2-3を繰り返す

5. **継続的な生成**: 
   - カバレッジ99%以上を達成するまで、継続してテストコードを生成
   - 一度にすべてを生成する必要はなく、段階的に生成してもよい

### カバレッジ測定コマンド

**Python**:
```bash
pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html
```

**JavaScript**:
```bash
npm run test:coverage
```

カバレッジレポートは以下に出力されます：
- Python: `htmlcov/index.html`
- JavaScript: `htmlcov/js/index.html`

## ベストプラクティス

1. **既存パターンに従う**: プロジェクト内の既存テストファイルのスタイルと構造を維持
2. **明確なテスト名**: テストの目的が明確に分かる命名
3. **適切なアサーション**: 期待される動作を明確に検証
4. **エッジケースの網羅**: 正常系だけでなく異常系もテスト
5. **モックの適切な使用**: 外部依存関係を適切にモックし、テストの独立性を保つ
6. **ソースコードの改変禁止**: テストコードのみを生成し、ソースコードは一切変更しない
7. **カバレッジの継続的な確認**: テスト生成後は必ずカバレッジを確認し、99%未満の場合は追加のテストを生成
8. **問題点の明確な記録**: ソースコードに不備を発見した場合は、修正案を提案し、問題点を明確に記録

## ソースコードに不備がある場合の対応例

### 例1: 未実装のプレースホルダー関数

**発見した問題**:
```python
def process_data(data):
    # TODO: 実装予定
    pass
```

**対応**:
1. 問題点を記録: "`process_data`関数が未実装のプレースホルダーです"
2. 修正案を提案: "この関数を実装するか、使用されていない場合は削除することを推奨します"
3. テストは生成: 可能な範囲でテストコードを生成（`pass`の実行をテスト）

### 例2: エラーハンドリングの不備

**発見した問題**:
```python
def divide(a, b):
    return a / b  # ゼロ除算のエラーハンドリングなし
```

**対応**:
1. 問題点を記録: "`divide`関数にゼロ除算のエラーハンドリングがありません"
2. 修正案を提案: "`if b == 0: raise ValueError('Division by zero')` を追加することを推奨します"
3. テストは生成: ゼロ除算時の動作をテスト（現在の実装に基づいて）

### 例3: 型チェックの不備

**発見した問題**:
```javascript
function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
    // itemsがnull/undefinedの場合のチェックなし
}
```

**対応**:
1. 問題点を記録: "`calculateTotal`関数にnull/undefinedチェックがありません"
2. 修正案を提案: "`if (!items) return 0;` を追加することを推奨します"
3. テストは生成: null/undefinedの場合の動作をテスト（現在の実装に基づいて）

## Resources

### references/

テスト生成に必要な詳細なパターンとリファレンス情報を格納しています。

- **test_patterns.md**: テスト生成の全般的なパターンとガイドライン
- **python_patterns.md**: pytest固有のパターン、fixture、モック方法
- **javascript_patterns.md**: Jest固有のパターン、モック、非同期処理

これらのファイルは、特定のテストタイプやパターンが必要な場合に参照してください。
