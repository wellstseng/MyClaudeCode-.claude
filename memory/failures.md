# 失敗模式記憶

- Scope: global
- Confidence: [觀]
- Trigger: 失敗, 錯誤, debug, 踩坑, pitfall, crash, 重試, retry, workaround
- Last-used: 2026-03-10
- Confirmations: 0
- Type: procedural
- Tags: failure, pitfall, debug, quality-feedback
- Related: decisions, toolchain

## 知識

### 環境踩坑（Environment Trap）

（記錄格式：{觸發條件} → {錯誤行為} → {正確做法}（根因: {root cause}））

- [固] Windows bash 的 `find` 輸出路徑含反斜線 → 管道到其他工具時路徑解析失敗 → 改用 Glob/Grep 工具或 `//` 正斜線（根因: MSYS2 路徑轉換不一致）
- [固] ChromaDB 在 i7-3770 上 import 失敗 → 誤以為安裝問題反覆重裝 → 確認 CPU 不支援 AVX2 後改用 SQLite backend（根因: LanceDB/ChromaDB 預設需要 AVX2 指令集）

### 假設錯誤（Wrong Assumption）

（記錄格式：{假設內容} → {實際情況}（發現於: {context}））

（尚無記錄，使用中累積）

### 模式誤用（Pattern Misapplication）

（記錄格式：{套用的模式} → {為什麼不適用}（應改用: {correct approach}））

（尚無記錄，使用中累積）

### 生成品質回饋（Output Quality Feedback）

（記錄格式：{生成內容描述} → {被重寫/修正的部分} → {重寫原因}（品質訊號: −））

（尚無記錄，使用中累積）

## 行動

- debug 超過 5 分鐘時，先檢查此 atom 是否有已知模式匹配，避免重複踩坑
- 使用者糾正行為時，記錄到對應分類（環境踩坑 / 假設錯誤 / 模式誤用）
- 工具呼叫失敗後重試成功時，評估是否值得記錄（可重現性 + 影響面）
- 發現正在大幅修改前 session 生成的程式碼（>30% 變動）時，記錄到「生成品質回饋」
- 新增記錄前，先向量搜尋是否有相似的既有記錄（dedup）
- 遇到相似情境時，回應中簡短提醒已知陷阱
- 每條記錄初始為 [臨]，跨 2+ sessions 確認後晉升 [觀]

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-10 | 初始建立：四大分類（環境踩坑/假設錯誤/模式誤用/品質回饋）+ 2 條已知踩坑 | manual |
