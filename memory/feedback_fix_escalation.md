# 精確修正升級協議

- Scope: global
- Confidence: [固]
- Trigger: 重試, retry, escalation, 精確修正, fix-escalation, 修不好, 又壞了, 失敗
- Last-used: 2026-03-17
- Confirmations: 5

## 知識

- [固] 同一問題修正超過 1 次（第 2 次起），暫停直接修復，啟動精確修正會議
- [固] Guardian hook 自動偵測 `wisdom_retry_count >= 2` → 注入 `[Guardian:FixEscalation]`
- [固] 收到信號或自我察覺時，執行 `/fix-escalation` skill
- [固] 6 Agent 編制：外部搜索 + 專案調查 + 正向策略 + 反向策略 + 落地分析 + 垃圾回收
- [固] 5 Phase：暫停 → 蒐集 → 辯論 → 深度挑戰 → 決策執行 → 驗證
- [固] 自我驗證：成功主動回報成效；連續 3 次未解決強制暫停
- [固] 豁免：typo/語法錯誤不計；使用者說「直接改」可跳過

## 行動

- 收到 `[Guardian:FixEscalation]` 或自我察覺重試 → 立即執行 `/fix-escalation`
- 連續 3 次未解決 → 強制暫停，向使用者報告

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-17 | 初始建立：6 Agent 會議制 + Guardian hook 自動偵測 + /fix-escalation skill | 使用者明確要求 |
| 2026-03-24 | 格式轉換：claude-native → 原子記憶標準格式 | memory-health 診斷 |
