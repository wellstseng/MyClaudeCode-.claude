# Hybrid RAG 架構設計

- Scope: global
- Confidence: [觀]
- Trigger: RAG, vector, 向量, embedding, 語意, semantic, ChromaDB, LanceDB, Ollama, 本地LLM, local LLM, sentence-transformers
- Last-used: 2026-03-03
- Confirmations: 1

## 知識

### 決策

- [觀] 採用 Hybrid 架構：keyword trigger（現有）優先 + vector semantic search 補充
- [觀] 現有 atom trigger 系統保留不動，RAG 作為 RECALL 階段的第二層
- [觀] 後端雙軌：sentence-transformers（快速 embedding ~150ms）+ Ollama（高品質 + LLM 推理）
- [觀] 向量 DB 選擇：ChromaDB（DX 好、社群大）或 LanceDB（更輕、Rust 核心）
- [觀] 使用者決定兩個都裝：Ollama + sentence-transformers

### 環境資訊

- GPU: NVIDIA GTX 1050 Ti (4GB VRAM, CUDA 可用)
- Python: 3.14.2
- Ollama: 未安裝（待安裝）
- Node: 24.12.0（主用）+ 22.14.0（computer-use-mcp 專用）
- Hook timeout: UserPromptSubmit = 3 秒（vector search 必須在 ~2s 內完成）

### 架構設計

```
UserPromptSubmit (3s timeout)
├─ [1] Keyword matching (existing, ~10ms)
├─ [2] HTTP → Vector Service @ localhost:3849 (~200-500ms)
│       GET /search?q=<prompt>&top_k=5
│       → 返回 ranked atom names + similarity scores
├─ [3] Merge: keyword + semantic results (deduplicate)
├─ [4] Load atoms within token budget (existing)
└─ Output context
```

### Memory Vector Service（新元件）

- 位置：`~/.claude/tools/memory-vector-service/`
- 類型：Python HTTP daemon（非 MCP），port 3849
- 啟動時載入 embedding model（一次載入，後續查詢 ~50-200ms）
- ChromaDB 持久化存儲：`~/.claude/memory/_vectordb/`
- API endpoints：GET /search、POST /index、GET /health
- 自動啟動：由 SessionStart hook 檢查並啟動

### 效能基準

| 後端 | Embedding | Search | 總計 | 狀態 |
|------|-----------|--------|------|------|
| sentence-transformers (GPU) | 50-100ms | 10-50ms | ~150ms | 最快 |
| Ollama nomic-embed-text | 200-300ms | 20-100ms | ~400ms | 品質好 |
| SQLite FTS5 | N/A | 5-20ms | ~20ms | 無語意 |

### 本地 LLM 應用場景（Ollama，未來）

1. **Reranking** — 向量搜尋候選 → LLM 判斷真正相關性
2. **摘要** — 長 atom 注入前先摘要，省 token
3. **知識萃取** — 從 session transcript 自動萃取事實寫入 atom
4. **Session transcript search** — 索引過去對話歷史，語意搜尋

### 為什麼不只用 RAG

- 目前只有 ~5 個 atoms，keyword matching 完美運作
- RAG 真正有價值的場景：50+ atoms、session transcript 搜尋、跨專案經驗遷移
- 3 秒 hook timeout 是硬限制，embedding service 必須是常駐 daemon

### 安裝需求

```bash
# Python packages
pip install sentence-transformers chromadb

# Ollama (Windows installer)
# https://ollama.com/download/windows
# 安裝後：
ollama pull nomic-embed-text    # embedding model (~274MB)
ollama pull qwen2.5:3b          # LLM for reranking/summary (~2GB)
```

## 行動

- 新 session 接手時，按 plans/compiled-coalescing-shore.md 的待實作步驟執行
- 先安裝 Ollama + sentence-transformers + chromadb
- 建立 memory-vector-service HTTP daemon
- 修改 workflow-guardian.py RECALL phase 整合 semantic search
- 測試 latency 必須在 3 秒內（目標 < 500ms）

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-03 | 研究完成，建立為 [觀] | session 研究分析 |
