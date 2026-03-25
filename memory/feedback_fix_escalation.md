---
name: fix-escalation
description: 同一問題修正第 2 次起，強制啟動 6 Agent 精確修正會議（蒐集→辯論 2 輪→決策→驗證）
type: feedback
---

同一問題的修正嘗試超過 1 次（第 2 次起），必須暫停直接修復，啟動精確修正會議。

**Why:** 使用者明確要求。防止 AI 盲目重試、反覆試錯，確保每次修正都經過充分研究和多角度辯論。

**How to apply:**
- Guardian hook 自動偵測 `wisdom_retry_count >= 2` → 注入 `[Guardian:FixEscalation]`
- 收到信號或自我察覺時，執行 `/fix-escalation` skill
- 6 Agent 編制：外部搜索 + 專案調查 + 正向策略 + 反向策略 + 落地分析 + 垃圾回收
- 5 Phase：暫停 → 蒐集 → 辯論 → 深度挑戰 → 決策執行 → 驗證
- 自我驗證：成功主動回報成效；連續 3 次未解決強制暫停
- 豁免：typo/語法錯誤不計；使用者說「直接改」可跳過

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-17 | 初始建立：6 Agent 會議制 + Guardian hook 自動偵測 + /fix-escalation skill | 使用者明確要求 |
