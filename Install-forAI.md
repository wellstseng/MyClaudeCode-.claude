# 原子記憶 V2.4 安裝指南 (Install for AI)

> 本文件供其他 Claude Code 實例安裝原子記憶系統。
> 設計為可由 AI 助手讀取並執行的安裝步驟。

---

## 前置需求

### 必要軟體

| 軟體 | 最低版本 | 用途 | 安裝方式 |
|------|---------|------|---------|
| Python | 3.8+ | Hook 腳本、工具鏈 | python.org 或系統內建 |
| Node.js | 18+ | Dashboard MCP server | nodejs.org |
| Ollama | 最新 | 本地 LLM + embedding | ollama.com |
| Claude Code | 最新 | 主程式 | `npm install -g @anthropic-ai/claude-code` |

### Ollama Models（必須預先下載）

```bash
ollama pull qwen3-embedding          # embedding 模型（完整版，需 AVX2 CPU）
# 或 qwen3-embedding:0.6b           # 小模型版（無 AVX2 限制，~400MB）
ollama pull qwen3:1.7b               # 語意處理 LLM (~1.2GB)
```

### Python 套件

```bash
pip install lancedb                  # Vector DB (需 AVX2 CPU)
# 或 pip install chromadb           # 替代方案 (無 AVX2 限制)
pip install sentence-transformers    # Fallback embedding (建議，Ollama 不可用時備援)
```

### 硬體注意事項

- **有 AVX2 的 CPU**（2013 年後多數 CPU）：LanceDB 和 ChromaDB 都可用
- **無 AVX2**（如 i7-3770）：必須用 ChromaDB，LanceDB 會 crash
- **GPU**：非必要，但有 NVIDIA GPU 可加速 Ollama 推論
- **RAM**：建議 8GB+（Ollama model 常駐約 1-2GB）

---

## 需複製的檔案

從來源機器複製以下結構到目標機器的 `~/.claude/`：

```
~/.claude/
├── CLAUDE.md                          [必要] 系統指令
├── settings.json                      [必要] Hook 註冊 + 權限
│
├── hooks/
│   └── workflow-guardian.py           [必要] 統一 Hook 入口
│
├── tools/
│   ├── memory-audit.py               [必要] 健檢工具
│   ├── memory-write-gate.py          [必要] 寫入品質閘門
│   ├── memory-conflict-detector.py   [建議] 衝突偵測
│   ├── rag-engine.py                [建議] RAG CLI
│   ├── memory-vector-service/        [必要] Vector 搜尋服務
│   │   ├── service.py
│   │   ├── indexer.py
│   │   ├── searcher.py
│   │   ├── reranker.py
│   │   ├── config.py
│   │   └── requirements.txt
│   └── workflow-guardian-mcp/        [建議] Dashboard MCP
│       └── server.js (+ package.json)
│
├── memory/                            [必要] 全域記憶
│   ├── MEMORY.md                     ← 需依目標機器重建
│   └── SPEC_Atomic_Memory_System.md  [參考] 規格文件
│
├── workflow/
│   └── config.json                   [必要] 需依目標機器調整
│
└── commands/                          [建議] Slash commands
    └── init-project.md
```

### 不需複製

```
workflow/state-*.json         # Session 狀態 (自動生成)
memory/_vectordb/             # 向量索引 (自動重建)
memory/episodic/              # Session 摘要 (自動生成)
memory/_distant/              # 遙遠記憶 (個人歷史)
memory/preferences.md         # 使用者偏好 (需自建)
memory/decisions.md           # 決策記錄 (需自建)
tools/__pycache__/            # Python 快取
todos/                        # Session todos
debug/                        # Debug logs
cache/                        # 快取
shell-snapshots/              # Shell 快照
telemetry/                    # 遙測數據
```

---

## 設定步驟

### Step 1: 調整 settings.json

確認 hooks 的 `command` 欄位中 Python 路徑正確：

```json
"hooks": {
    "SessionStart": [{
        "hooks": [{
            "type": "command",
            "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"",
            "timeout": 5
        }]
    }]
}
```

**注意**：若目標機器的 Python 指令是 `python3` 而非 `python`，需全部替換。

6 個 Hook event 都需檢查：
- `SessionStart` (timeout: 5)
- `UserPromptSubmit` (timeout: 3)
- `PostToolUse` (timeout: 3, matcher: "Edit|Write")
- `PreCompact` (timeout: 5)
- `Stop` (timeout: 5)
- `SessionEnd` (timeout: 30)  ← V2.4: transcript extraction + cross-session check 需更多時間

### Step 2: 調整 workflow/config.json

關鍵設定項需依目標環境調整：

```json
{
  "vector_search": {
    "embedding_model": "qwen3-embedding",
    "ollama_llm_model": "qwen3:1.7b",
    "search_min_score": 0.65,
    "additional_atom_dirs": []
  },
  "response_capture": {
    "enabled": true,
    "per_turn_enabled": true,
    "per_turn_max_chars": 3000,
    "per_turn_max_items": 2,
    "session_end_max_chars": 20000,
    "session_end_max_items": 5,
    "ollama_timeout_seconds": 3,
    "classification_default": "[臨]"
  },
  "cross_session": {
    "enabled": true,
    "min_score": 0.75,
    "promote_threshold": 2,
    "suggest_threshold": 4,
    "timeout_seconds": 5
  }
}
```

- **response_capture**：控制回應知識萃取（V2.4），需 Ollama qwen3:1.7b
- **cross_session**：控制跨 Session 鞏固（V2.4 Phase 3），依賴 Vector Service
- **search_min_score**：完整版 embedding 建議 0.60-0.65；小模型 (0.6b) 建議 0.40-0.50

### Step 3: 初始化全域記憶

建立 `~/.claude/memory/MEMORY.md`：

```markdown
# Atom Index — Global

> Session 啟動時先讀此索引。比對 Trigger → Read 對應 atom。

| Atom | Path | Trigger | Confidence |
|------|------|---------|------------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference | [固] |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, hooks | [固] |

---

## 高頻事實

- 使用者: {username} | {OS} | 回應語言: 繁體中文
- [固] 原子記憶 V2.4
```

### Step 4: 啟動 Vector Service 並建立索引

```bash
# 安裝 Python 依賴
cd ~/.claude/tools/memory-vector-service
pip install -r requirements.txt

# 啟動 Vector Service (背景)
python service.py &

# 確認健康
curl http://127.0.0.1:3849/health
# 預期: {"status":"ok",...}

# 觸發完整索引
curl http://127.0.0.1:3849/index/full
# 預期: {"indexed":N,"chunks":M}
```

### Step 5: 註冊 Dashboard MCP（可選）

若有 `workflow-guardian-mcp/`，在 `.mcp.json` 中加入：

```json
{
  "mcpServers": {
    "workflow-guardian": {
      "command": "node",
      "args": ["~/.claude/tools/workflow-guardian-mcp/server.js"],
      "disabled": false
    }
  }
}
```

Dashboard 可在 `http://127.0.0.1:3848` 查看 Guardian 狀態。

---

## 驗證清單

### 基礎驗證

```bash
# 1. Python 可執行
python --version                    # 需 3.8+

# 2. Ollama 模型就緒
ollama list                          # 應看到 qwen3-embedding 和 qwen3:1.7b

# 3. Hook 可執行 (模擬 SessionStart)
echo '{"hook_event_name":"SessionStart","session_id":"test-001","cwd":"/tmp"}' | \
  python ~/.claude/hooks/workflow-guardian.py
# 預期: JSON output 含 "additionalContext"

# 4. Vector Service 啟動
curl http://127.0.0.1:3849/health
# 預期: {"status":"ok","chunks":N,...}

# 5. 健檢工具
python ~/.claude/tools/memory-audit.py
# 預期: Markdown 格式報告，無 ERROR

# 6. 語意搜尋
curl "http://127.0.0.1:3849/search/ranked?q=test&top_k=3"
# 預期: JSON array with scored results
```

### 整合驗證

啟動 Claude Code，觀察：

1. **Session 開始**：應看到 `[Workflow Guardian] Active.` 訊息
2. **輸入含 trigger 關鍵字的 prompt**：應看到 atom 被載入
3. **Edit/Write 操作後嘗試結束**：應看到 Stop 閘門同步提醒
4. **Session 結束後**：檢查 `~/.claude/memory/` 是否有新的 `episodic-*.md`

---

## 常見問題

### Q: Vector Service 啟動失敗
**A**: 檢查 `pip install lancedb` 是否成功（需 AVX2 CPU）。無 AVX2 則改用 `pip install chromadb` 並修改 indexer.py。檢查 port 3849 是否被占用。

### Q: Ollama embedding timeout
**A**: 確認使用正確版本的 embedding model。小模型首次載入約 5-10 秒，之後常駐。

### Q: Hook 執行但沒有 atom 注入
**A**: 檢查 `MEMORY.md` 的 Trigger 欄位是否與 prompt 關鍵字匹配。檢查 atom 檔案路徑是否正確（相對於 `~/.claude/`）。

### Q: 無 GPU 能跑嗎
**A**: 可以。Ollama 自動 fallback 到 CPU。`qwen3-embedding` CPU 推論約 200-500ms，`qwen3:1.7b` CPU 約 1-3s。

### Q: 如何遷移已有 atom 到新機器
**A**: 複製整個 `~/.claude/memory/` 目錄，然後：
```bash
curl -X POST http://127.0.0.1:3849/index/full
```
即可重建向量索引。Atom 是純 Markdown 檔案，完全可攜。

---

## 升級路徑

安裝完成後，可根據硬體能力逐步啟用：

| 階段 | 條件 | 升級項目 |
|------|------|---------|
| **基礎** | 任何機器 | Keyword trigger + MEMORY.md 索引 |
| **+Vector** | Python + LanceDB/ChromaDB | Hybrid RECALL 語意搜尋 |
| **+本地 LLM** | Ollama + 4GB+ RAM | Intent 分類 + embedding + 回應知識萃取 (V2.4) |
| **+大模型** | 16GB+ VRAM GPU | qwen3:8b/14b 提升語意品質 |
