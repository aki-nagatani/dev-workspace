---
name: markdownlint-fix
description: markdownlint エラー（MD013/MD036/MD040等）の修正作業。Fix it verify、MD013 line-length、For the code present we get this error、該当行指定でのエラー修正依頼時に使用。
---

# マークダウンリント修正作業

## 概要

ユーザーが該当箇所を指示した markdownlint 修正作業を実施する際のワークフローと方針を定める。

## 発火条件（この SKILL を適用するタイミング）

以下のいずれかに該当する場合、**本 SKILL を必ず読み、手順に従って修正を行う**：

1. **「For the code present, we get this error:」** で始まるメッセージで markdownlint 系エラー（MD013, MD036, MD040 等）が示されている
2. ユーザーが「Fix it, verify」や「修正して」と依頼し、MD013 / line-length / markdownlint などのエラーが添付されている
3. ユーザーが該当ファイル・行を指定して markdownlint エラーの修正を依頼している
4. ユーザーが「markdownlint の修正」「MD013 を直して」などと明示的に依頼している

## 使用タイミング

以下の場合にこの SKILL を使用する：

- ユーザーが「markdownlint の修正作業をしてほしい」と依頼した場合
- ユーザーが該当ファイル・該当行を指定して markdownlint エラーの修正を依頼した場合
- **「For the code present, we get this error:」** で始まるメッセージ（IDE の linter エラー貼り付け等）で markdownlint エラー（MD013, MD060 等）が示されている場合

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
