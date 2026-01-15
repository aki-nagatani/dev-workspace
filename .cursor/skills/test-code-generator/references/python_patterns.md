# Python (pytest) テストパターン

## Fixture の使用

### 既存のFixture

プロジェクトでよく使用されるfixture：

- `app`: Flaskアプリケーションインスタンス
- `client`: テストクライアント
- `db`: データベースセッション

### カスタムFixtureの作成

```python
import pytest
from mypokedex.extensions import db
from mypokedex.models.user import User

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        db.create_all()
        user = User(email="test@example.com", passwordHash="hash")
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()
```

## データベース操作

### 基本的なパターン

```python
def test_database_operation(app, client):
    """Test database operations."""
    with app.app_context():
        db.create_all()
        
        # データの作成
        user = User(email="test@example.com")
        db.session.add(user)
        db.session.commit()
        
        # データの検証
        found_user = User.query.filter_by(email="test@example.com").first()
        assert found_user is not None
```

### トランザクションのロールバック

```python
def test_with_rollback(app, client):
    """Test with transaction rollback."""
    with app.app_context():
        db.create_all()
        
        try:
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()
            
            # テスト実行
            result = function_under_test()
            
            # 検証
            assert result is not None
        finally:
            db.session.rollback()
```

## モックとパッチ

### unittest.mock の使用

```python
from unittest.mock import patch, MagicMock, Mock

def test_with_mock(app, client):
    """Test with mocked dependency."""
    with patch('module.external_service') as mock_service:
        mock_service.return_value = {'status': 'success'}
        
        result = function_under_test()
        
        assert result == expected_value
        mock_service.assert_called_once()
```

### 関数のモック

```python
def test_with_function_mock(app, client):
    """Test with function mock."""
    import module.target_module as target
    
    original_func = target.target_function
    
    def mock_function(*args, **kwargs):
        return 'mocked_result'
    
    target.target_function = mock_function
    
    try:
        result = function_under_test()
        assert result == 'mocked_result'
    finally:
        target.target_function = original_func
```

### 例外のモック

```python
def test_with_exception_mock(app, client):
    """Test exception handling."""
    with patch('module.external_service') as mock_service:
        mock_service.side_effect = Exception("Test error")
        
        result = function_under_test()
        
        # エラーハンドリングの検証
        assert result is None or result.status_code == 500
```

## HTTP リクエストのテスト

### GET リクエスト

```python
def test_get_endpoint(app, client):
    """Test GET endpoint."""
    response = client.get('/endpoint')
    
    assert response.status_code == 200
    assert 'expected_content' in response.data.decode()
```

### POST リクエスト

```python
def test_post_endpoint(app, client):
    """Test POST endpoint."""
    response = client.post(
        '/endpoint',
        data={'key': 'value'},
        follow_redirects=False
    )
    
    assert response.status_code in (200, 302)
```

### JSON リクエスト

```python
def test_json_endpoint(app, client):
    """Test JSON endpoint."""
    response = client.post(
        '/api/endpoint',
        json={'key': 'value'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert response.json == {'status': 'success'}
```

## 認証とセッション

### ログイン状態のテスト

```python
def test_authenticated_endpoint(app, client):
    """Test authenticated endpoint."""
    with app.app_context():
        db.create_all()
        
        # ユーザーの作成とログイン
        user = User(email="test@example.com", passwordHash="hash")
        db.session.add(user)
        db.session.commit()
        
        # ログイン
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password'
        })
        
        # 認証が必要なエンドポイントのテスト
        response = client.get('/protected')
        assert response.status_code == 200
```

## エラーハンドリングのテスト

### 例外処理

```python
def test_exception_handling(app, client):
    """Test exception handling."""
    original_func = module.target_function
    
    def mock_function():
        raise ValueError("Test error")
    
    module.target_function = mock_function
    
    try:
        result = function_under_test()
        
        # エラーが適切に処理されることを検証
        assert result is None or result.status_code == 500
    finally:
        module.target_function = original_func
```

### バリデーションエラー

```python
def test_validation_error(app, client):
    """Test validation error handling."""
    response = client.post(
        '/endpoint',
        data={'invalid': 'data'}
    )
    
    assert response.status_code == 400
    assert 'error' in response.json or 'validation' in response.data.decode()
```

## アサーション

### 基本的なアサーション

```python
# 等価性
assert result == expected_value

# None チェック
assert result is not None
assert result is None

# 真偽値
assert result is True
assert result is False

# 含まれるか
assert 'substring' in result
assert item in list_result

# 型チェック
assert isinstance(result, ExpectedType)
```

### コレクションのアサーション

```python
# リストの長さ
assert len(result_list) == expected_length

# リストの内容
assert expected_item in result_list
assert result_list == [item1, item2, item3]

# 辞書のキー
assert 'key' in result_dict
assert result_dict['key'] == expected_value
```

## テストマーカーの使用

```python
import pytest

@pytest.mark.slow
def test_slow_operation(app, client):
    """Slow test that should be marked."""
    # 時間のかかるテスト
    pass

@pytest.mark.integration
def test_integration(app, client):
    """Integration test."""
    # 統合テスト
    pass

@pytest.mark.unit
def test_unit(app, client):
    """Unit test."""
    # ユニットテスト
    pass
```
