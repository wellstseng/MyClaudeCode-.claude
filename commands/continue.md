# /continue — 續接暫存任務

> 讀取 staging 區的續接 prompt 並立即執行。輕量版續接，適合已備好下一步的場景。
> 全域 Skill，適用任何專案。

---

## 使用方式

```
/continue
```

無參數。直接執行。

---

## Step 1: 檢查暫存區

檢查**專案層** `memory/_staging/next-phase.md` 是否存在。

路徑規則：
- 專案層 memory 目錄位於 `~/.claude/projects/{project-slug}/memory/`
- 完整路徑：`{專案層 memory}/_staging/next-phase.md`

### 分流

- **檔案存在** → 繼續 Step 2
- **檔案不存在** → 回覆「沒有待續任務。使用 `/resume` 可從 atoms/git/todo 推斷續接工作。」→ 結束

## Step 2: 讀取並刪除

1. 讀取 `next-phase.md` 全部內容，記住內容
2. **立即刪除**該檔案（防止重複執行）

## Step 3: 執行

將讀取到的內容視為**任務 prompt**，立即開始執行。不需要使用者確認，直接動工。

**注意**：如果任務的完成條件中包含「產出下一階段續接 prompt」，在任務完成時寫入新的 `next-phase.md`。
