# error-handling-policy

Always respond in Japanese when applying this skill.

## 発火条件

- エラー・テスト失敗・CI/Lint 失敗の**修正**に着手する前
- バグ・誤判定・UI・レポート等、**問題の修正**に着手する前（表面上の対症療法を避ける）
- **回避策**（skip・閾値引き下げ・握りつぶし・type ignore・表示／手動フラグだけ）を検討するとき
- 手順の正本は **`SKILL.md`**（myrules「根本原因からの解決」と一体）

## 併用

- **Python ソース**の構文・型・import: 先に **`python-code-error-fix`** SKILL を Read
