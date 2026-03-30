# 精確修正升級（Fix Escalation Protocol）

- Scope: global
- Confidence: [固]
- Trigger: 修正, 重試, 第二次, 升級, escalation, 精確修正, fix, retry
- Last-used: 2026-03-27
- Confirmations: 22
- Related: failures, decisions

## 知識

- [固] 同一問題修正第 2 次起，必須暫停直接修復，啟動精確修正會議
- [固] Guardian hook 自動偵測 `wisdom_retry_count >= 2` → 注入 `[Guardian:FixEscalation]`
- [固] 6 Agent 編制：外部搜索 + 專案調查 + 正向策略 + 反向策略 + 落地分析 + 垃圾回收
- [固] 5 Phase：暫停 → 蒐集 → 辯論 → 深度挑戰 → 決策執行 → 驗證
- [固] 自我驗證：成功主動回報成效；連續 3 次未解決強制暫停
- [固] 豁免：typo/語法錯誤不計；使用者說「直接改」可跳過

## 行動

- 收到 `[Guardian:FixEscalation]` 信號或自我察覺重試時，執行 `/fix-escalation` skill
- 防止盲目重試、反覆試錯，確保每次修正都經過充分研究和多角度辯論

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-17 | 初始建立：6 Agent 會議制 + Guardian hook 自動偵測 | 使用者明確要求 |
| 2026-03-25 | 格式修正：YAML frontmatter → 標準 atom 格式 | 系統維護 |
