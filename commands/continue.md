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

用 **Read tool**（不是 Glob）直接讀取以下絕對路徑：

```
~/.claude/projects/MEMORY.md
```

從 MEMORY.md 所在目錄推算 staging 路徑，然後用 Read tool 讀取：

```
{MEMORY.md 所在目錄}/_staging/next-phase.md
```

> 例：如果 MEMORY.md 在 `~/.claude/projects/c--Projects/memory/MEMORY.md`，
> 則讀 `~/.claude/projects/c--Projects/memory/_staging/next-phase.md`

**重要**：不要用 Glob 搜尋。直接用 Read tool 讀絕對路徑。路徑在系統 context 的 "Additional working directories" 中可以找到 memory 目錄的位置。

**每個專案有獨立的 staging 區**，確保不同專案的續接互不干擾。

### 分流

- **讀取成功** → 繼續 Step 2
- **檔案不存在（Read 報錯）** → 回覆「沒有待續任務。`_staging/` 目錄下無 `next-phase.md` 檔案。使用 `/resume` 可從 atoms/git/todo 推斷續接工作。」→ 結束

## Step 2: 讀取並刪除

1. 讀取 `next-phase.md` 全部內容，記住內容
2. **立即刪除**該檔案（防止重複執行）

## Step 3: 執行

將讀取到的內容視為**任務 prompt**，立即開始執行。不需要使用者確認，直接動工。

**注意**：如果任務的完成條件中包含「產出下一階段續接 prompt」，在任務完成時寫入新的 `next-phase.md`。
