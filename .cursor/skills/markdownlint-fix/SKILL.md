---
name: markdownlint-fix
description: Fix markdownlint errors (MD013, MD032, MD036, MD040, MD060, etc.) in Markdown files. Use when user shows "For the code present, we get this error" with a markdownlint error (MD0xx), requests "Fix it verify", or specifies file/line with a markdownlint violation. Follows markdown-editing SKILL for correction rules. 周辺の同様エラーも併せて修正する。
---

# マークダウンリント修正作業

## 🚨 発火トリガー（この SKILL を適用すべき場合）

ユーザーメッセージに以下のいずれかが含まれる場合、**本 SKILL を必ず適用する**:

- 「For the code present, we get this error」+ MD0xx 系エラー
- 「Fix it verify」+ ファイル・行指定
- ファイル・行を指定した markdownlint エラー修正の依頼
- 「markdownlint の修正」「MD013 を直して」などの明示的依頼

## 概要

ユーザーが該当箇所を指示した markdownlint 修正作業を実施する際のワークフローと方針を定める。

## 作業フロー（必須）

### 1. 該当箇所の確認

- ユーザーが指定したファイルと行（または選択範囲）を確認する
- 指定された箇所の markdownlint エラーを特定する

### 2. 周辺の同様エラーを併せて修正

**重要**: 該当箇所の修正に留めず、**周辺の同様のエラーも併せて対応する**。

- 同一ファイル内の同じ種類のエラー（例：他のテーブル区切り行の MD060、他のリストの MD032 など）を探して修正する
- 同じテーブル内の他の行、同じセクション内の他のリストなど、文脈的にまとめて修正すべき範囲を判断する

### 3. 修正ルールの参照

- 修正は `markdown-editing` SKILL（`dev-workspace/.cursor/skills/markdown-editing/SKILL.md`）のルールに従う
- 該当するエラー種別（MD013, MD024, MD032, MD060 等）の対応策を SKILL で確認して適用する

### 4. SKILL に未記載のエラーの場合

**SKILL で対応策が書かれていないエラー種別に遭遇した場合は、markdown-editing SKILL を更新する。**

- 発生したエラー種別とその修正方法を調査する
- `markdown-editing` SKILL に該当エラー種別のセクションを追加し、対応策を記載する
- 例：MD041（先頭行H1）、MD047（末尾改行）、MD051（リンクフラグメント）など

## 修正時の心構え

- **該当箇所だけでなく、周辺の同様のエラーもまとめて修正する**
- 同一ファイル内で同じパターンの違反が複数ある場合は、一括で修正する
- **別パターンのエラーも修正すること**（MD013 と MD060 が同時に存在する場合など）
- 既存の Markdown 構造・見出し階層・箇条書きは維持する
- 文脈を壊さない最小限の編集で完結させる

## 検証

修正後は markdownlint で再チェックし、エラーが解消されていることを確認する：

```powershell
cd dev-workspace
npx markdownlint-cli -c .markdownlint.json "対象ファイル.md"
```

または一括チェック：

```powershell
.\scripts\markdownlint-all.ps1
```

## 関連 SKILL

- **markdown-editing**: 修正時に従う具体的なルール（MD012〜MD060 等）はこちらの SKILL を参照する
