# JavaScript (Jest) テストパターン

## 基本的なテスト構造

### describe/it の使用

```javascript
describe('Module Name', () => {
    describe('Function Group', () => {
        it('should handle specific case', () => {
            // テストコード
        });
    });
});
```

### beforeEach/afterEach

```javascript
describe('Module Name', () => {
    let originalConsole;
    let mockElement;

    beforeEach(() => {
        // 各テスト前のセットアップ
        jest.resetModules();
        jest.clearAllMocks();
        
        originalConsole = console.log;
        console.log = jest.fn();
    });

    afterEach(() => {
        // 各テスト後のクリーンアップ
        console.log = originalConsole;
    });
});
```

## モックの使用

### 関数のモック

```javascript
// モジュール全体をモック
jest.mock('module-name', () => ({
    functionName: jest.fn(() => 'mocked value')
}));

// 特定の関数をモック
const mockFunction = jest.fn();
mockFunction.mockReturnValue('return value');
mockFunction.mockResolvedValue(Promise.resolve('async value'));
```

### オブジェクトのモック

```javascript
const mockObject = {
    method1: jest.fn(),
    method2: jest.fn(() => 'return value'),
    property: 'value'
};

// 使用
mockObject.method1();
expect(mockObject.method1).toHaveBeenCalled();
```

### モジュールのモック

```javascript
// モジュールのモック
jest.mock('../module', () => ({
    exportedFunction: jest.fn(),
    exportedConstant: 'value'
}));

// 部分的なモック
jest.mock('../module', () => {
    const originalModule = jest.requireActual('../module');
    return {
        ...originalModule,
        specificFunction: jest.fn()
    };
});
```

## DOM 操作のテスト

### 要素のモック

```javascript
test('should manipulate DOM element', () => {
    // 要素のモック
    const mockElement = {
        id: 'test-id',
        textContent: '',
        innerHTML: '',
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn(() => false),
            toggle: jest.fn()
        },
        style: {
            display: '',
            visibility: ''
        },
        setAttribute: jest.fn(),
        getAttribute: jest.fn(() => null),
        removeAttribute: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        querySelector: jest.fn(() => null),
        querySelectorAll: jest.fn(() => [])
    };

    document.getElementById = jest.fn(() => mockElement);
    document.querySelector = jest.fn(() => mockElement);

    // テスト実行
    updateElement('test-id', 'new content');

    // 検証
    expect(mockElement.textContent).toBe('new content');
    expect(document.getElementById).toHaveBeenCalledWith('test-id');
});
```

### イベントのテスト

```javascript
test('should handle click event', () => {
    const mockHandler = jest.fn();
    const element = {
        addEventListener: jest.fn(),
        click: jest.fn()
    };

    document.querySelector = jest.fn(() => element);

    // イベントリスナーの設定
    setupClickHandler('button', mockHandler);

    // イベントハンドラーの取得と実行
    const clickHandler = element.addEventListener.mock.calls[0][1];
    clickHandler();

    expect(mockHandler).toHaveBeenCalled();
});
```

## 非同期処理のテスト

### Promise のテスト

```javascript
test('should handle Promise', () => {
    return asyncFunction().then(result => {
        expect(result).toBe(expectedValue);
    });
});
```

### async/await のテスト

```javascript
test('should handle async operation', async () => {
    const result = await asyncFunction();
    expect(result).toBe(expectedValue);
});
```

### fetch のモック

```javascript
test('should handle fetch request', async () => {
    global.fetch = jest.fn(() =>
        Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({ data: 'test' }),
            text: () => Promise.resolve('response text')
        })
    );

    const result = await fetchData('/api/endpoint');

    expect(result).toEqual({ data: 'test' });
    expect(fetch).toHaveBeenCalledWith('/api/endpoint');
});
```

### エラーハンドリング

```javascript
test('should handle fetch error', async () => {
    global.fetch = jest.fn(() =>
        Promise.reject(new Error('Network error'))
    );

    await expect(fetchData('/api/endpoint')).rejects.toThrow('Network error');
});
```

## グローバルオブジェクトのモック

### window オブジェクト

```javascript
beforeEach(() => {
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
        },
        localStorage: {
            getItem: jest.fn(() => null),
            setItem: jest.fn(),
            removeItem: jest.fn(),
            clear: jest.fn()
        }
    };
});
```

### document オブジェクト

```javascript
beforeEach(() => {
    global.document = {
        createElement: jest.fn((tagName) => ({
            tagName: tagName.toUpperCase(),
            id: '',
            className: '',
            classList: {
                add: jest.fn(),
                remove: jest.fn(),
                contains: jest.fn(() => false)
            },
            setAttribute: jest.fn(),
            getAttribute: jest.fn(() => null),
            addEventListener: jest.fn(),
            querySelector: jest.fn(() => null),
            querySelectorAll: jest.fn(() => [])
        })),
        querySelector: jest.fn(() => null),
        querySelectorAll: jest.fn(() => []),
        getElementById: jest.fn(() => null),
        body: {
            classList: {
                add: jest.fn(),
                remove: jest.fn()
            }
        }
    };
});
```

### console のモック

```javascript
beforeEach(() => {
    console.log = jest.fn();
    console.error = jest.fn();
    console.warn = jest.fn();
    console.debug = jest.fn();
});

afterEach(() => {
    console.log.mockClear();
    console.error.mockClear();
});
```

## アサーション

### 基本的なアサーション

```javascript
// 等価性
expect(result).toBe(expectedValue);
expect(result).toEqual({ key: 'value' });

// 真偽値
expect(result).toBeTruthy();
expect(result).toBeFalsy();
expect(result).toBe(true);

// null/undefined
expect(result).toBeNull();
expect(result).toBeUndefined();
expect(result).toBeDefined();

// 数値
expect(result).toBeGreaterThan(0);
expect(result).toBeLessThan(100);
expect(result).toBeCloseTo(3.14, 2);

// 文字列
expect(result).toContain('substring');
expect(result).toMatch(/regex/);

// 配列
expect(array).toContain(item);
expect(array).toHaveLength(3);

// オブジェクト
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('key', 'value');
```

### モックのアサーション

```javascript
// 呼び出し回数
expect(mockFunction).toHaveBeenCalled();
expect(mockFunction).toHaveBeenCalledTimes(2);
expect(mockFunction).not.toHaveBeenCalled();

// 引数
expect(mockFunction).toHaveBeenCalledWith(arg1, arg2);
expect(mockFunction).toHaveBeenLastCalledWith(arg1, arg2);
expect(mockFunction).toHaveBeenNthCalledWith(1, arg1, arg2);

// 戻り値
expect(mockFunction).toHaveReturned();
expect(mockFunction).toHaveReturnedWith(value);
```

## タイマーのテスト

### setTimeout/setInterval

```javascript
jest.useFakeTimers();

test('should handle timeout', () => {
    const callback = jest.fn();
    
    setTimeout(callback, 1000);
    
    expect(callback).not.toHaveBeenCalled();
    
    jest.advanceTimersByTime(1000);
    
    expect(callback).toHaveBeenCalled();
});

afterEach(() => {
    jest.useRealTimers();
});
```

## モジュールのリセット

```javascript
beforeEach(() => {
    jest.resetModules();
    jest.clearAllMocks();
});

// 特定のモジュールをリセット
jest.resetModules();
const module = require('./module');
```

## テストのスキップ

```javascript
// テストをスキップ
test.skip('should skip this test', () => {
    // テストコード
});

// 条件付きスキップ
test('should run conditionally', () => {
    if (someCondition) {
        return;
    }
    // テストコード
});
```
