# feedback-knowledge-doc-iteration

- Scope: global
- Author: judy
- Confidence: [觀]
- Trigger: same_file_3x, retry_escalation, knowledge_doc, 規劃文件, 補章節, WellsDB, 知識庫
- Last-used: 2026-05-03
- Confirmations: 2
- Created-at: 2026-05-03
- Related: workflow-rules, decisions-architecture

## 知識

- [觀] 連續多次 Edit 同一份知識庫 .md 文件補**不同章節 / 不同項目**，**不是** retry_escalation（重複修同一 bug），是 knowledge_doc_iteration（規劃文件分段補完整）
- [觀] Guardian 的 `same_file_3x` 偵測對 src/ 程式碼正確（重複改同一檔可能在表面修復），但對 `.md` 規劃 / 報告類文件誤觸——這類文件本來就分段寫成
- [觀] 已跨 session 出現第 2 次：4-22 寫初版 + 5-3 補進度章節 + 補項目 12/13；兩次都被 Guardian 報「retry / 覆轍」，實際無重複修復行為
- [觀] 對話實例：5-3 16:34 與 17:54 兩次 SessionStart 都帶 `[Guardian:覆轍] same_file_3x:CatClaw 整合 Hermes 優化計畫.md, retry_escalation`，導致使用者要花時間判讀 Guardian 訊號真偽

## 行動

- Why：Guardian 規則無法區分「同檔 src/ 程式碼反覆修補同一 bug」vs「同檔規劃文件補不同章節」；後者誤觸會打斷規劃節奏，使用者要在每個 session 重新解釋
- How to apply（寫入端 / AI）：
  - 開始連續編輯 .md 知識庫文件前，先在回覆中聲明「knowledge_doc_iteration 模式：補不同章節 ≠ retry」，給 Guardian 留紀錄
  - 一個 session 內補完所有規劃章節，避免跨 session 多次回頭改同檔
  - 若需跨 session 接力（如 4-22 寫初版 → 5-3 補進度），明確記錄「補章節 X / Y / Z」差異
- How to apply（規則端 / Guardian 設計）：
  - `same_file_3x` 偵測排除路徑：`~/WellsDB/`、`*/_AIDocs/`、`*.md` 結尾的非 src/ 路徑
  - 或加白名單：規劃 / 報告 / 知識庫文件路徑前綴
  - 或新增分類：`knowledge_doc_iteration` 與 `retry_escalation` 並列，前者不觸發 fix-escalation
- 自查：每次連續 Edit 同檔超過 3 次，先檢查「是不同章節 / 不同項目嗎？」是 → 屬 knowledge_doc_iteration，不是 retry
