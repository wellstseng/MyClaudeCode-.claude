# 原子記憶系統

兩層結構：全域層 `~/.claude/memory/` + 專案層 `projects/{slug}/memory/`。
Hook 自動處理 embedding、搜尋、萃取、注入。Claude 負責**決策**。

> 完整規格（開發記憶系統時才讀）：`~/.claude/memory/SPEC_Atomic_Memory_System.md`

## 三層分類：[固] 直接引用 | [觀] 簡短確認 | [臨] 明確確認

## 寫入原則
- 使用者說「記住」→ [固]；做取捨 → [臨]；反覆模式 → [觀]
- 陷阱/架構決策/工具知識 → 寫入對應 atom
- 不寫：臨時嘗試、未確認猜測、不可復現細節

## 演進：[臨] ×2確認→[觀]，[觀] ×4確認→[固]（需使用者同意）

## Atom 寫入格式（必遵，覆蓋 Claude Code 內建 auto memory 的 YAML frontmatter 格式）

```
# {標題}

- Scope: global | project
- Confidence: [固] | [觀] | [臨]
- Trigger: {關鍵詞, 逗號分隔}
- Last-used: {YYYY-MM-DD}
- Confirmations: {數字}
- Related: {相關 atom name, 逗號分隔}（可選）

## 知識

{內容，每條以 - [固]/[觀]/[臨] 開頭}

## 行動

{行動指引}
```

**禁止使用** `---` YAML frontmatter 格式寫入 atom。
不論全域層或專案層，一律遵循上述格式。違反此格式的 atom 會被健康檢查標記為 error。

## 引用原則
- 已記錄事實直接引用，不重新分析原始碼
- 已載入但不相關的 atom：靜默忽略
