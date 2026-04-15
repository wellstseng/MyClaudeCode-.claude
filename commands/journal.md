# /journal — 工作日誌產出

> 從 episodic atoms + workflow state 自動彙整工作日誌（日報 / 週報）。
> 全域 Skill，適用任何專案。

---

## 使用方式

```
/journal                              # 今天的日報
/journal 2026-04-07                   # 指定日期的日報
/journal week                         # 本週週報
/journal week 2026-04-07              # 含該日期的那週週報
/journal range 2026-04-01 2026-04-15  # 任意日期區間
```

---

## Step 1: 執行聚合腳本

用 Bash tool 執行：

```bash
python ~/.claude/tools/journal-aggregate.py $ARGUMENTS
```

- 日報存檔至 `~/.claude/journals/YYYY-MM-DD.md`
- 週報存檔至 `~/.claude/journals/week-YYYY-WNN.md`
- 區間日誌存檔至 `~/.claude/journals/range-{start}_{end}.md`
- 腳本自動清理 >60 天的舊日誌

## Step 2: 檢視產出

1. 讀取腳本的 stdout 輸出
2. 如果內容為「無記錄」，告知使用者並結束
3. 否則將內容展示給使用者

## Step 3: 詢問是否調整

問使用者：

> 「日誌已產出。要調整內容嗎？例如：補充說明、改格式、匯出成其他形式。」

- 使用者要求修改 → 用 Edit tool 直接修改對應的 md 檔
- 使用者滿意 → 結束
