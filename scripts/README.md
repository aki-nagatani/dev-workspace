# scripts

dev-workspace 用のユーティリティスクリプト。

## extract_pdf_text.py

PDF からテキストを抽出する（obsidian-inbox-summarize SKILL 用）。

### 使用方法

```bash
python extract_pdf_text.py <PDFファイルパス>
```

- **成功時**: 抽出したテキストを stdout に出力し、終了コード 0
- **失敗時**: 空文字を出力し、終了コード 1

### フォールバックの優先順

テキストが 50 文字未満の場合、以下の順でフォールバックを試行する。

1. **pypdf**（必須・常に試行）: 埋め込みテキストを抽出
2. **おたよりナビ OCR API**（オプション）: `http://localhost:5003` 固定。
   otayori-navi がローカル Docker で稼働している場合に検索可能 PDF を取得し、pypdf で再抽出
3. **Azure Document Intelligence**（オプション）: Read モデルで OCR。環境変数が設定されている場合のみ試行

### 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `OTAYORI_OCR_API_KEY` | 任意 | おたよりナビ OCR API の認証キー。otayori-navi が `api_key` 設定で稼働している場合のみ必要。未設定時は認証なしで呼び出す |
| `OTAYORI_OCR_TIMEOUT` | 任意 | OCR API のタイムアウト秒数。デフォルト 120 |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | 任意 | Azure リソースのエンドポイント URL（フォールバック b 用） |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | 任意 | Azure API キー（フォールバック b 用） |

### 依存

- **pypdf**（必須）: `pip install pypdf`
- **requests**（おたよりナビ API フォールバック用・オプション）: `pip install requests`
- **azure-ai-documentintelligence**（Azure フォールバック用・オプション）: `pip install azure-ai-documentintelligence`

### 前提条件（おたよりナビ OCR API フォールバック）

- otayori-navi がローカル Docker で `http://localhost:5003` に稼働していること
- otayori-navi の config で `ocr.api_enabled: true` が設定されていること
