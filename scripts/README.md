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

`.github/workflows/cost_monitoring.yml` が毎月1日・15日 22:00 JSTに実行する。
AWS と OpenAI API の集計は別ジョブで並列に動作し、Slack `#コスト監視` へ投稿する。

運用フロー:

1. 月2回 Slack にレポートが届く（先頭行が作業指示）
2. `【貼るだけ】`（判定 `要注意` / `要確認`）なら本文全文をそのまま Cursor に貼る
   （考えなくてよい・追記不要。末尾の `#cost-monitoring-handoff` が依頼の正本）
3. `【対応不要】`（判定 `正常`）なら閲覧のみ

通知内容の要点:

- 先頭行: `【貼るだけ】` または `【対応不要】`
- 判定: 正常／要注意／要確認
- 毎月1日: 完了月確定レビュー（上位・意味のある増減・直近3完了月推移）
- 毎月15日: 当月累計・月末予測中心（正常時は詳細を省略）
- 共通: 同期間前月比、前月完了月合計、日次異常（異常時のみ詳細）
- AWS: サービス上位（構成比）。増減は閾値超えのみ
- AWSの日次異常判定は、TaxとRoute 53のHostedZone（月次固定計上）を運用費から分離する。
  固定費は総額には含め、通知本文にも「日次固定費（異常判定から除外）」として表示する。
- 異常時: Cursor依頼ブロック（SKILL・対象・調査観点・成果物）を本文に含める

GitHub リポジトリ Secrets には、次を設定する。

- `COST_MONITORING_SLACK_WEBHOOK_URL`: `#コスト監視` 向け Incoming Webhook URL
- `AWS_ACCESS_KEY_ID`: Cost Explorer を読み取れる IAM アクセスキー ID
- `AWS_SECRET_ACCESS_KEY`: 上記 IAM アクセスキーのシークレット
- `OPENAI_ADMIN_API_KEY`: Organization Costs API を読める OpenAI 管理者 API キー

`report_aws_cost_to_slack.py` と `report_openai_cost_to_slack.py` は、Slack に送る本文を
標準出力へ書き出す。送信は `send_slack_notification.py` が担当する。

`.github/workflows/cost_monitoring.yml` は、各ジョブのレポート本文と実行メタデータを
`persist_cost_monitoring_history.py`でJSON化し、Artifact経由で
`cost-monitoring-history/{service}/YYYY/MM/DD/`へ統合する。
Artifact自体はジョブ間の受け渡し用で、期限なし保存の正本ではない。
履歴統合ジョブは新しい履歴をGitへ自動コミット・プッシュする。
同じ実行IDと試行回数の履歴は上書きされるため、再実行しても重複しない。

履歴にはSlack本文の原文、判定、期間、合計、月末予測または日次平均、
日次異常などの抽出値を保存する。AWS／OpenAIのAPIキーやSlack Webhookは
保存しない。

OpenAI Costs API は、429・一時的な5xxに対して `Retry-After` 優先の指数バックオフを行う。
月中のレポートでは未使用の直近完了月推移を取得せず、API呼出しを最小限にする。

Cursor個人契約のUsage監視はGHAで実額を取得せず、
`cursor-cost-monitoring` SKILLをCursor内ブラウザから明示的に呼び出す。
GHAの `cursor_usage_reminder.yml` は、約5日ごとにSKILL呼び出しをSlackへ促すだけである。
確認結果はObsidianの `Notes/コスト監視履歴.md`へ追記し、Cursorの認証情報や
Cookieは保存しない。
