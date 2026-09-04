# /clear-session — 清除 tmux session

> 對指定的 tmux session 送出 `/clear`，清除 Claude Code CLI 的對話。
> 全域 Skill，適用任何專案。

---

## 使用方式

```
/clear-session              # 預設清 session "judy"
/clear-session <name>       # 清指定 session
```

---

## 執行流程

1. 從 `$ARGUMENTS` 取得 session 名稱（預設 `judy`）
2. 用 Bash tool 執行：

```bash
bash ~/.claude/scripts/reset-judy.sh <session-name>
```

3. 回報結果給使用者（成功或失敗原因）
4. 如果是從 Discord 觸發，用 reply tool 回覆結果
