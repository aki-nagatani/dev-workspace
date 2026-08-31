# cursor-ide-browser-position

Always respond in Japanese when applying this skill.

## 発火条件

- Cursor 内蔵ブラウザ（`cursor-ide-browser` MCP）でページを開くとき
- `browser_navigate` / `browser_tabs` に `position` を付けようとするとき

## 要点

- **ブラウザはサイドで開かないこと**（`position: "side"` 禁止）
- 既定は `position` 省略。見せるときだけ `"active"`
- 手順の正本は **`SKILL.md`**
