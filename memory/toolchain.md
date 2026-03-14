# 工具鏈實戰記憶

- Scope: global
- Confidence: [固]
- Trigger: 工具, 環境, 指令, command, path, 路徑, bash, git, python, npm, ollama
- Last-used: 2026-03-14
- Confirmations: 25
- Type: procedural
- Tags: toolchain, environment, commands
- Related: failures

## 知識

### Windows 環境差異

- [固] Claude Code 的 bash 環境是 MSYS2，路徑格式 `/c/Users/` 而非 `C:\Users\`，但 Python Path 物件自動轉換
- [固] Windows 上 bash 指令的 `/dev/null` 有效（MSYS2 模擬），不需改成 `NUL`
- [固] `timeout` 指令在 MSYS2 bash 不可用，需用 Python 的 subprocess timeout 或其他替代
- [觀] Windows 環境變數用 `$env:VAR`（PowerShell）或 `$VAR`（bash），混用易出錯

### 已驗證的指令組合

- [固] Ollama 啟動: `ollama serve`（背景）→ `ollama list`（驗證模型可用）
- [固] 向量服務啟動: `python ~/.claude/tools/memory-vector-service/service.py`（port 3849）
- [固] 向量健康檢查: `curl http://127.0.0.1:3849/health`
- [固] 記憶格式檢查: `python ~/.claude/tools/memory-audit.py`

### 路徑與版本

- [觀] Python: Windows 預設路徑 — 需確認具體 session 中的 `which python` 結果
- [觀] Node.js: 用於 inbox-check.js hook — 需確認版本
- [固] Ollama models 位置: 預設 `~/.ollama/models/`
- [固] ChromaDB 資料: `~/.claude/memory/_vectordb/`

### Ollama Dual-Backend 知識（辦公室環境）

> 家用環境僅有 local backend，以下為跨環境參考知識。

- [觀] ollama_client.py: singleton pattern，generate()/chat()/embed() 三個 API，自動 primary→fallback
- [觀] generate() 支援 think 參數（預設 False）。chat() 固定 think:false（reranker/conflict-detector 用短 prompt，不需 thinking）
- [觀] Open WebUI proxy 不轉發 Ollama 原生 /api/embed — 改走 OpenAI-compatible /api/v1/embeddings（在根路徑，非 /ollama/ 下）
- [觀] failover 時 model 名稱要跟著切換（rdchat 用 qwen3.5:latest，local 用 qwen3:1.7b）

### Dual-Backend 萃取品質實測（2026-03-13）

A/B 對比：2 段真實 transcript（Redmine debug + NuGet build），各 4000 字送入萃取 prompt。

| 維度 | rdchat qwen3.5 (think=T, 8192) | local qwen3:1.7b (think=F, 2048) |
|------|------|------|
| JSON 格式 | OK | OK |
| 回應時間 | 38-43s | 6-13s |
| 萃取項目數 | 2-4 項（精簡） | 4-6 項（較多但淺） |
| 平均 content 長度 | 83-89 字 | 38-49 字 |
| type 多樣性 | factual+architectural+decision+procedural | 幾乎全 factual |

**關鍵發現**：
- [觀] qwen3.5 + think=false + 長 prompt → 秒回空 `[]`（退化），必須 think=true 才能正確萃取
- [觀] qwen3:1.7b 不支援 think 參數（自動忽略），think=false 正常運作
- [觀] 結論：extract-worker 統一用 think=true + num_predict=8192，rdchat 品質高但慢，local 品質中但快

### 環境特殊配置

- [固] ChromaDB 用 SQLite backend（i7-3770 不支援 AVX2，預設 HNSW backend 會 crash）
- [固] Ollama 同時只能跑一個模型（GTX 1650 4GB VRAM 限制），embedding 和推論模型需輪替
- [固] workflow-guardian.py stdout/stderr 強制 UTF-8（Windows 預設 cp950 會導致中文亂碼）

## 行動

- build/setup/config intent 時自動載入
- 成功執行新工具指令後，評估是否值得記錄（跨 session 重用性 ≥ 2 次預期）
- 環境問題 debug 時，優先查此 atom 再嘗試盲目探索
- 版本資訊在確認後更新，不猜測

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-10 | 初始建立：從 hardware.md + decisions.md 整理已知工具鏈知識，4 大分類 | manual |
| 2026-03-10 | [觀]→[固] 定期檢閱晉升，Confirmations=4 | periodic-review |
| 2026-03-13 | Dual-Backend A/B 萃取品質實測 + generate() think 參數 + extract-worker think=true | ab-extract-test |
| 2026-03-14 | 合併辦公室 V2.11 — 保留家用 ChromaDB/GTX1650 環境 | merge-office-v2.11 |
