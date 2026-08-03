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
| --- | --- | --- |
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

## 定期コスト監視

`.github/workflows/cost_monitoring.yml` が毎月1日・15日 09:00 JSTに実行する。
AWS と OpenAI API の集計は別ジョブで並列に動作し、Slack `#コスト監視` へ投稿する。

GitHub リポジトリ Secrets には、次を設定する。

- `COST_MONITORING_SLACK_WEBHOOK_URL`: `#コスト監視` 向け Incoming Webhook URL
- `AWS_ACCESS_KEY_ID`: Cost Explorer を読み取れる IAM アクセスキー ID
- `AWS_SECRET_ACCESS_KEY`: 上記 IAM アクセスキーのシークレット
- `OPENAI_ADMIN_API_KEY`: Organization Costs API を読める OpenAI 管理者 API キー

`report_aws_cost_to_slack.py` と `report_openai_cost_to_slack.py` は、Slack に送る本文を
標準出力へ書き出す。送信は `send_slack_notification.py` が担当する。
