# 對話管理

## 識流工作流

使用者說「**透過識流進行…**」或「**用識流處理…**」→ 執行 `/consciousness-stream` skill。高風險跨系統任務可建議使用（不強制）。

## 拆分指引

- 獨立子任務可新開對話（MEMORY.md 自動載入）
- 拆分前確保：新發現已寫入 _AIDocs、重要事實已存入 atom
- 有順序依賴的任務應在同一對話完成
- 所有執行階段只要內容、檔案、邏輯、流程皆不衝突的，就開啟多agents分頭進行

## 主動續航

1. **段落完成即存**：完成一段工作後立即將進度寫入 atom
2. **Token 上限預警**：快碰上限時優先存檔工作狀態
3. **重試追蹤**：反覆修正 → 記錄重試次數+成敗原因，避免跨 session 重走錯路
4. **自動續接**：`/resume` 寫入 → `/continue` 讀取，路徑 `projects/{slug}/memory/_staging/`

## 自我迭代

記憶系統隨使用演進。核心：收斂優先、證據門檻（≥2 session）、淘汰勇氣、震盪偵測。
**適用範圍：規則管理。不適用於回答使用者問題。**
定期檢閱：收到提醒時掃描 episodic atoms，收攏重複，完成後寫入 `workflow/last_review_marker.json`。

> 完整 3 條核心原則：`memory/_reference/self-iteration.md`

## 提醒開新 Session

Context 被壓縮、任務告一段落、回應明顯變慢 → 提醒使用者開新 session（確保新知識已存入 atom）。
