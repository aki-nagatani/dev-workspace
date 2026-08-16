---
name: cursor-cost-monitoring
description: 個人契約のCursor Usage画面をCursor内ブラウザで確認し、表示された使用量・on-demand spend・請求サイクルをCursor LLMが整理してSlackへ通知する。ユーザーがCursor Usage監視、Cursorコスト監視、cursor-cost-monitoringを明示したときに使用する。
disable-model-invocation: true
---

# Cursorコスト監視

## 目的

個人契約で公式APIを使えないため、Cursor内ブラウザのUsage画面を読み取り、
表示された事実だけをSlack `#コスト監視`へ通知する。

このSKILLは、ユーザーが明示的に呼び出したときだけ実行する。
GitHub ActionsはSKILL呼び出しのリマインダーだけを担当し、ブラウザ操作や
Cursor LLMによるUsage取得は行わない。

## 必須手順

### 1. ブラウザの準備

1. `browser_tabs`で既存タブを確認する。
2. `https://cursor.com/dashboard/usage`が開いていれば、そのタブを使う。
3. 開いていなければ、Cursor内ブラウザで同URLを開く。
4. 既存タブを操作するときは、操作前に`browser_lock`でロックする。
5. `browser_snapshot`で画面の見出し・Usage値・請求サイクルを取得する。
   必要な場合だけ`browser_cdp`のDOM確認を使う。

### 2. 認証境界

次の場合は自動操作を止め、ユーザーにブラウザでの対応を依頼する。

- ログイン画面
- 2FA、CAPTCHA、本人確認
- 権限エラー
- Usage画面が表示されない状態

パスワード、Cookie、セッション情報、認証トークンを取得・保存・Slackへ送信しない。
ブラウザ操作が終わったら`browser_lock`を解除する。

### 3. 取得する値

画面に表示されている場合だけ、次の項目を記録する。

- プラン名
- 請求サイクルの開始日・リセット日
- Cursor Modelsの使用量・含まれる上限
- Other Modelsの使用量・含まれる上限
- on-demand spendとlimit
- 画面上の警告、超過、支払いに関する表示

画面に表示されない請求額、税額、為替額、残り使用量から推測した金額は記載しない。
取得できない値は「画面表示なし」とする。

### 4. 判定

表示値に基づき、次の基準で判定する。

- `要確認`: on-demand spendが0より大きい、超過表示がある、または画面取得に失敗した
- `要注意`: limitが表示され、on-demand spendがlimitの80%以上
- `正常`: 上記に該当せず、表示された使用量が含まれる範囲内
- on-demand spendまたはlimitが画面にない場合は、金額判定を行わず「表示値確認」とする

判定根拠が複数ある場合は、画面に表示された内容を優先して併記する。
不明な値を正常扱いにしてはいけない。

### 5. 契約プランの推奨

契約変更は単月の急増だけで決めず、可能なら直近2〜3請求サイクルのUsage履歴と
on-demand spendを比較して提案する。料金・含まれる利用枠は変更されるため、
公式の料金表も確認する。

現時点の利用前提はユーザー申告のUltra契約中とする。
Usage画面またはユーザーから最新情報が示された場合は、そちらを優先する。

必ず、現行プランだけでなく次の節約案も比較する。

1. 現行プランを維持する場合の月額
2. 一つ下のプランへ変更し、必要な分だけAPI単価のon-demandで追加する場合
3. さらに下のプランへ変更し、必要な分だけAPI単価のon-demandで追加する場合

比較式は「下位プランの月額＋表示されたon-demand費用」とする。
金額が画面に表示されない場合は試算せず、「金額比較不可」と明記する。
トークン数や使用率から請求額を推定してはいけない。

- Ultra維持: Ultraの利用枠を継続的に使う、またはUltra相当の利用量・機能が必要な場合
- Pro+＋on-demand検討: Ultraからの月額差額（現行目安$140/月）より
  追加費用が小さく、Ultra固有の利用量・機能も不要な場合
- Pro＋on-demand検討: Pro+からの月額差額（現行目安$40/月）より
  追加費用が小さく、Pro+固有の利用量・機能も不要な場合
- 上位プラン検討: 下位プラン＋on-demandの合計が現行プランを上回る場合

on-demandが無効な場合は自動で有効化せず、
「下位プラン＋API単価on-demand」を節約案として提示するだけに留める。
有効化する場合もdashboardのspend limitで月間上限を設定する。

現行の料金表では、Proは月額$20・Other Models枠$20、
Pro+は月額$60・同枠$70、Ultraは月額$200・同枠$400である。
この数値は判断時に公式ドキュメントで再確認する。

- 料金表: <https://cursor.com/docs/models-and-pricing>
- Usage制限: <https://cursor.com/help/models-and-usage/usage-limits>

利用実績が不足しているときは「次回も観測」とし、プラン変更を断定しない。

### 6. Slack通知

次の形式で日本語の本文を作成する。

```text
【対応不要】または【貼るだけ】Cursor Usage監視の確認結果
対象: Cursor個人契約
判定: 正常／要注意／要確認
プラン: [表示値]
請求サイクル: [表示値]
Cursor Models: [表示値]
Other Models: [表示値]
on-demand spend: [表示値]
limit: [表示値]
判定理由: [表示値に基づく理由]
契約プラン推奨: Ultra維持／Pro+変更検討／Pro変更検討／次回も観測
推奨根拠: [直近のUsageとon-demand spendの比較]
節約案: [一つ下のプラン＋API単価on-demand等。金額比較不可なら明記]
確認画面: <https://cursor.com/dashboard/usage>
確認日時: [JSTの実日時]
```

`要注意`または`要確認`の場合は、本文末尾に次を追加する。

```text
-----
#cursor-cost-monitoring-handoff
【Cursor依頼】
ユーザー作業は貼り付けのみ完了。以降はエージェントが自動継続する。
SKILL: cursor-cost-monitoring
SKILL path: dev-workspace/.agents/skills/cursor-cost-monitoring/SKILL.md
対象: Cursor個人契約
```

Slack送信は既存の`dev-workspace/scripts/send_slack_notification.py`を使う。
Webhook URLを本文、ログ、コマンド引数の表示へ直接書かない。
既存のWebhookが`#コスト監視`向けに設定されているため、送信先を勝手に変更しない。

通知に失敗した場合は成功扱いにせず、失敗理由をユーザーへ報告する。

### 7. 実行履歴の保存

Slack通知本文を作成した後、送信成否にかかわらず、同じ確認結果をObsidianの
`Notes/コスト監視履歴.md`へ1回分の記録として追記する。

記録項目は次のとおりとする。

- 確認日時（JST）
- プラン名と請求サイクル
- Cursor Models、Other Modelsの表示値
- on-demand spendとlimit
- 判定と判定理由
- 契約プラン推奨、節約案、推奨根拠
- Usage画面のURL

画面に表示されない値は「画面表示なし」と記載し、トークン数・使用率・
過去の断片的な表示から請求額を推測しない。認証情報、Cookie、Webhook URLは
履歴へ書き込まない。

履歴は次回のプラン比較に使う。直近2〜3請求サイクルがまだ蓄積されていない
場合は、プラン変更を断定せず「次回も観測」とする。

## 実行しないこと

- GitHub ActionsからCursorへログインすること
- Cookieや認証情報を使ったブラウザセッションの複製
- Usage画面のDOM構造だけを根拠に、表示されていない請求額を推測すること
- 固定月額や税額をUsage値として混同すること
- Loopを定期監視の正本にすること
- GHAのリマインダーを、Usage取得済みのレポートとして扱うこと
