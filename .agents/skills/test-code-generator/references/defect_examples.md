# ソースコードに不備がある場合の対応例

SKILL.md「3. ソースコードに不備がある場合の対応」の具体例。判断に迷うときに読む。

## 例1: 未実装のプレースホルダー関数

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

## 例2: エラーハンドリングの不備

**発見した問題**:

```python
def divide(a, b):
    return a / b  # ゼロ除算のエラーハンドリングなし
```

**対応**:

1. 問題点を記録: "`divide`関数にゼロ除算のエラーハンドリングがありません"
2. 修正案を提案: "`if b == 0: raise ValueError('Division by zero')` を追加することを推奨します"
3. テストは生成: ゼロ除算時の動作をテスト（現在の実装に基づいて）

## 例3: 型チェックの不備

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
