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

用 **Read tool** 讀取以下路徑取得 staging 根目錄：

```
~/.claude/projects/MEMORY.md
```

從 MEMORY.md 所在目錄推算 staging 路徑：`{MEMORY.md 所在目錄}/_staging/`

> 例：如果 MEMORY.md 在 `~/.claude/projects/c--Projects/memory/MEMORY.md`，
> 則 staging 在 `~/.claude/projects/c--Projects/memory/_staging/`

**每個專案有獨立的 staging 區**，確保不同專案的續接互不干擾。

### 讀取順序（容錯掃描）

1. **優先**：直接 Read `_staging/next-phase.md`
2. **Fallback**：若 Read 報錯（檔案不存在），用 Glob 掃描 `_staging/*.md`，取**最新的**（按修改時間）
3. **都沒有** → 回覆「沒有待續任務。`_staging/` 目錄下無 `.md` 檔案。使用 `/resume` 可從 atoms/git/todo 推斷續接工作。」→ 結束

**重要**：路徑在系統 context 的 "Additional working directories" 中可以找到 memory 目錄的位置。

## Step 2: 讀取並刪除

1. 讀取找到的 `.md` 檔案全部內容，記住內容
2. **立即刪除**該檔案（防止重複執行）

## Step 3: 執行

將讀取到的內容視為**任務 prompt**，立即開始執行。不需要使用者確認，直接動工。

**注意**：如果任務的完成條件中包含「產出下一階段續接 prompt」，在任務完成時寫入新的 `next-phase.md`。
