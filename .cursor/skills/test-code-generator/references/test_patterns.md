# テスト生成パターン

## テスト生成の基本原則

### 重要: ソースコードの改変禁止

**絶対に禁止事項**:

- ❌ ソースコードの修正・変更
- ❌ ソースコードの削除
- ❌ ソースコードへのコメント追加（テスト除外用の`# pragma: no cover`など）
- ❌ ソースコードのリファクタリング

**許可されること**:

- ✅ テストコードの生成のみ
- ✅ テストファイルの作成・更新

### カバレッジ目標

- **目標カバレッジ**: 99%以上（Python、JavaScript共通）
- **継続的な生成**: カバレッジ99%を達成するまで、継続してテストコードを生成する
- **カバレッジ指標**:
  - Python: ブランチ、関数、行、ステートメントすべて99%以上
  - JavaScript: branches, functions, lines, statements すべて99%以上

### 1. テストの構造

すべてのテストは以下の構造に従います：

1. **準備（Arrange）**: テストデータと環境のセットアップ
2. **実行（Act）**: テスト対象のコードを実行
3. **検証（Assert）**: 期待される結果を検証

### 2. テストメソッドのコメント（必須）

各テストメソッドの冒頭に、なんのためのテストなのかを必ず記述する。

- **Python**: 各テスト関数に docstring を付与。例: `"""SECRET_KEY が未設定のとき EmailVerificationError を送出する。"""`
- **JavaScript**: `test()` / `it()` のテスト名で目的が伝わる文言にする。必要に応じて直前コメントで補足

### 3. テスト命名規則

- **Python**: `test_<function_name>_<scenario>`形式
  - 例: `test_login_post_with_invalid_password`
  - 例: `test_get_user_by_id_not_found`

- **JavaScript**: `should <expected behavior> when <condition>`形式
  - 例: `should return error when password is invalid`
  - 例: `should update user when valid data provided`

### 4. テストカテゴリ

#### 正常系テスト

- 期待される入力に対する正常な動作を検証
- 典型的なユースケースをカバー

#### 異常系テスト

- 無効な入力、エラー条件、例外処理を検証
- エッジケースと境界値をカバー

#### 統合テスト

- 複数のコンポーネント間の相互作用を検証
- データベース、API、外部サービスの統合

## Python (pytest) パターン

### 基本的なテスト構造（Python）

```python
def test_function_name_scenario(app, client):
    """Clear description of what this test verifies."""
    # Arrange
    with app.app_context():
        db.create_all()
        # テストデータの準備
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### エラーハンドリングテスト

```python
def test_function_name_with_exception(app, client):
    """Test error handling when exception occurs."""
    # Arrange
    original_func = module.target_function
    
    def mock_function():
        raise Exception("Test error")
    
    module.target_function = mock_function
    
    try:
        # Act
        result = function_under_test()
        
        # Assert
        assert result is None or result.status_code == 500
    finally:
        # Cleanup
        module.target_function = original_func
```

### データベーステスト

```python
def test_database_operation(app, client):
    """Test database operations."""
    with app.app_context():
        db.create_all()
        
        # テストデータの作成
        user = User(email="test@example.com")
        db.session.add(user)
        db.session.commit()
        
        # 検証
        found_user = User.query.filter_by(email="test@example.com").first()
        assert found_user is not None
        assert found_user.email == "test@example.com"
```

### モックテスト

```python
from unittest.mock import patch, MagicMock

def test_function_with_mock(app, client):
    """Test with mocked external dependency."""
    with patch('module.external_api') as mock_api:
        mock_api.return_value = {'status': 'success'}
        
        result = function_under_test()
        
        assert result == expected_value
        mock_api.assert_called_once()
```

## JavaScript (Jest) パターン

### 基本的なテスト構造（JavaScript）

```javascript
describe('Module Name', () => {
    beforeEach(() => {
        // セットアップ
        jest.resetModules();
        jest.clearAllMocks();
    });

    test('should handle normal case', () => {
        // Arrange
        const input = 'test';
        
        // Act
        const result = functionUnderTest(input);
        
        // Assert
        expect(result).toBe(expectedValue);
    });
});
```

### DOM操作のテスト

```javascript
test('should update DOM element', () => {
    // Arrange
    const mockElement = {
        textContent: '',
        classList: {
            add: jest.fn(),
            remove: jest.fn()
        }
    };
    document.getElementById = jest.fn(() => mockElement);
    
    // Act
    updateElement('test-id', 'new content');
    
    // Assert
    expect(mockElement.textContent).toBe('new content');
    expect(document.getElementById).toHaveBeenCalledWith('test-id');
});
```

### 非同期処理のテスト

```javascript
test('should handle async operation', async () => {
    // Arrange
    global.fetch = jest.fn(() =>
        Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ data: 'test' })
        })
    );
    
    // Act
    const result = await asyncFunction();
    
    // Assert
    expect(result).toEqual({ data: 'test' });
    expect(fetch).toHaveBeenCalledTimes(1);
});
```

### イベントハンドラのテスト

```javascript
test('should handle click event', () => {
    // Arrange
    const mockHandler = jest.fn();
    const element = {
        addEventListener: jest.fn(),
        click: jest.fn()
    };
    document.querySelector = jest.fn(() => element);
    
    // Act
    setupClickHandler('button', mockHandler);
    
    // Assert
    expect(element.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    
    // イベントのシミュレーション
    const clickHandler = element.addEventListener.mock.calls[0][1];
    clickHandler();
    expect(mockHandler).toHaveBeenCalled();
});
```

## エッジケースのテスト

### 境界値テスト

```python
# Python
def test_boundary_values(app, client):
    """Test boundary values."""
    # 最小値
    assert function_under_test(0) == expected_min
    
    # 最大値
    assert function_under_test(MAX_VALUE) == expected_max
    
    # 境界値の前後
    assert function_under_test(MAX_VALUE - 1) == expected_near_max
```

```javascript
// JavaScript
test('should handle boundary values', () => {
    expect(functionUnderTest(0)).toBe(expectedMin);
    expect(functionUnderTest(MAX_VALUE)).toBe(expectedMax);
    expect(functionUnderTest(MAX_VALUE - 1)).toBe(expectedNearMax);
});
```

### null/undefined テスト

```python
# Python
def test_null_values(app, client):
    """Test null/None handling."""
    assert function_under_test(None) is None
    assert function_under_test("") == expected_empty
```

```javascript
// JavaScript
test('should handle null/undefined', () => {
    expect(functionUnderTest(null)).toBeNull();
    expect(functionUnderTest(undefined)).toBeUndefined();
    expect(functionUnderTest('')).toBe(expectedEmpty);
});
```

## テストカバレッジの最大化

### カバレッジ目標（必須）

- **目標カバレッジ**: 99%以上（Python、JavaScript共通）
- **行カバレッジ**: すべてのコード行を実行（99%以上）
- **ブランチカバレッジ**: すべての条件分岐をテスト（99%以上）
- **関数カバレッジ**: すべての関数を呼び出し（99%以上）
- **ステートメントカバレッジ**: すべてのステートメントを実行（99%以上）

### カバレッジ達成プロセス

1. **カバレッジレポートの確認**:
   - Python: `pytest --cov=src --cov-branch --cov-report=term-missing`
   - JavaScript: `npm run test:coverage`

2. **未カバー部分の特定**:
   - カバレッジレポートから未カバーの行、ブランチ、関数を特定
   - 優先順位を決定

3. **テストコードの生成**:
   - 未カバー部分に対してテストコードを生成
   - **重要**: ソースコードは一切変更しない

4. **カバレッジの再確認**:
   - テスト実行後、カバレッジを再確認
   - 99%未満の場合は、ステップ2-3を繰り返す

5. **継続的な生成**:
   - カバレッジ99%以上を達成するまで、継続してテストコードを生成

### 未カバー部分の特定方法

1. **カバレッジレポートの確認**:
   - ターミナル出力で未カバー行を確認
   - HTMLレポートで詳細を確認（`htmlcov/index.html`、`htmlcov/js/index.html`）

2. **未カバーの行、ブランチ、関数を特定**:
   - カバレッジレポートの`Missing`セクションを確認
   - 各未カバー部分の理由を分析

3. **各未カバー部分に対してテストを追加**:
   - 既存のテストパターンに従ってテストを生成
   - ソースコードは変更しない

### テストの優先順位

1. **高優先度**: ビジネスロジック、エラーハンドリング
2. **中優先度**: ユーティリティ関数、ヘルパー関数
3. **低優先度**: 単純なgetter/setter、定数定義

### テスト除外の禁止

テストカバレッジ方針に従い、以下は禁止です：

- ❌ ファイル単位の除外（`omit`設定の使用）
- ❌ 行単位の除外（`# pragma: no cover`の安易な使用）
- ❌ テスト実行時のスキップ（`pytest.skip()`、`test.skip()`の安易な使用）

**認められる例外**（例外的な場合のみ）:

- 型チェック専用コード（`if TYPE_CHECKING:`ブロック）
- 開発環境専用コード（本番環境では絶対に実行されない）
- 実装上どうしても再現できない安全弁（理由を明確に文書化）
