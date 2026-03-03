# Claude Code Custom Extensions

> Claude Code hooks + MCP + Atomic Memory V2 = 自動化工作流監督 & 跨 session 知識管理（含向量語意搜尋）

---

## Overview

這是一套 Claude Code 的自訂擴充系統，核心解決兩個問題：

1. **工作流監督** — Claude 容易忘記同步（git commit、更新文件），這套系統自動追蹤修改、提醒同步、阻止未完成就結束
2. **跨 session 記憶** — Claude 每次新對話都是白紙一張，原子記憶 V2 讓知識在 sessions 之間延續

**技術架構**：
- **Hooks**（Python）— 6 個生命週期事件的統一處理器
- **MCP Server**（Node.js）— JSON-RPC stdio + HTTP Dashboard
- **Atomic Memory V2** — Hybrid RECALL：Keyword Trigger + Vector Semantic Search + Local LLM

---

## 7-Phase Workflow Lifecycle

每個 Claude Code session 的完整生命週期：

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  Phase 1: BOOT（啟動初始化）                                          │
│  Trigger: SessionStart hook                                          │
│  ├─ 新 session → 建立 state, 解析全域+專案 MEMORY.md atom index       │
│  ├─ resume/compact → 恢復 state, 清空 injected_atoms, 注入摘要       │
│  └─ 自動啟動 Memory Vector Service daemon（若未運行）                  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 2: RECALL（記憶召回）★ V2 Hybrid                              │
│  Trigger: UserPromptSubmit hook（每輪）                               │
│  ├─ [1] Keyword match: prompt vs atom Trigger 關鍵詞（~10ms）        │
│  ├─ [2] Semantic search: HTTP → Vector Service（~200-400ms）         │
│  ├─ [3] Merge: keyword + semantic results（去重）                     │
│  ├─ [4] 在 token budget 內載入 atom 全文或摘要                        │
│  └─ 自動更新被載入 atom 的 Last-used 日期                             │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 3: TRACK（修改追蹤）                                           │
│  Trigger: PostToolUse hook（Edit|Write）                              │
│  ├─ 靜默記錄 file_path + tool + timestamp                            │
│  ├─ 設定 sync_pending = true                                         │
│  └─ ★ 若修改的是 atom 檔 → 觸發增量向量索引                          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 4: REMIND（同步提醒）                                          │
│  Trigger: UserPromptSubmit hook（週期性）                              │
│  ├─ 每 N 輪提醒一次未同步修改（max_reminders 上限）                    │
│  └─ 偵測 sync 關鍵詞時顯示完整 sync context                          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 5: COMPACT（壓縮保護）                                         │
│  Trigger: PreCompact hook                                             │
│  ├─ 快照 state（timestamp）                                          │
│  └─ Resume 時由 Phase 1 恢復 context + 重新注入 atoms                 │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 6: GATE（結束閘門）                                            │
│  Trigger: Stop hook                                                   │
│  ├─ 修改 ≥ min_files_to_block → BLOCK（最多 N 次）                   │
│  ├─ phase=done/muted → ALLOW                                         │
│  └─ 阻止 N 次後強制放行（anti-loop）                                  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 7: SYNC（同步執行）                                            │
│  Trigger: 手動（Claude + 使用者確認）                                 │
│  ├─ 更新 _AIDocs/_CHANGELOG.md                                       │
│  ├─ 更新 atom 檔（知識段落 + Last-used）                              │
│  ├─ workflow_signal("sync_completed") → 清空 queue + phase=done       │
│  └─ git commit + push                                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

### Workflow Guardian
- **自動追蹤修改** — Edit/Write 操作靜默記錄，不干擾工作
- **Stop 閘門** — 有未同步修改時阻止 Claude 結束，防止遺忘
- **Anti-loop 保護** — 最多阻止 N 次後強制放行，不會卡死
- **Mute 靜音** — 不想被打擾時可以靜音提醒
- **Dashboard** — `http://127.0.0.1:3848` 即時監控所有 sessions
- **多實例 Heartbeat** — 多個 VS Code 視窗時自動接管 Dashboard port
- **Session ID Prefix Match** — 用截短 ID（前 8 碼）即可操作

### Atomic Memory V2
- **兩層架構** — 全域 atoms（跨專案）+ 專案 atoms（專案綁定）
- **Hybrid RECALL** — Keyword Trigger + Vector Semantic Search 並行
- **Vector Service** — LanceDB + Ollama qwen3-embedding，常駐 HTTP daemon @ port 3849
- **Embedding 雙軌** — Ollama qwen3-embedding（主力）/ sentence-transformers bge-m3（fallback）
- **本地 LLM** — qwen3:1.7b via Ollama：查詢改寫、Re-ranking、知識萃取
- **段落級索引** — atom 中每個知識點獨立向量化，搜尋精度高於整檔比對
- **增量索引** — atom 修改時自動觸發，只重建變動的檔案（hash 比對）
- **Graceful fallback** — daemon/Ollama 未啟動時自動退化為純 keyword 模式
- **Token Budget** — 根據 prompt 複雜度自動調整載入量（4.5~15KB）
- **三級分類** — `[固]` 確認長期有效、`[觀]` 可能演化、`[臨]` 單次決策
- **Last-used 自動刷新** — Atom 被載入時自動更新使用日期
- **Compact 恢復** — Context 壓縮後自動重新注入 atoms

---

## Quick Start

詳細安裝指南見 [Install-forAI.md](Install-forAI.md)（為 AI 設計的安裝手冊）。

### 核心元件

```
~/.claude/
├── CLAUDE.md                      # 工作流引擎指令（Claude 自動載入）
├── hooks/
│   └── workflow-guardian.py        # 6 事件 hook 處理器（含 V2 semantic search 整合）
├── tools/
│   ├── workflow-guardian-mcp/
│   │   └── server.js              # MCP server + HTTP Dashboard
│   ├── memory-vector-service/     # ★ V2 向量搜尋服務
│   │   ├── service.py             # HTTP daemon (port 3849)
│   │   ├── indexer.py             # 段落級 chunking + embedding + LanceDB
│   │   ├── searcher.py            # 語意搜尋
│   │   ├── reranker.py            # LLM 查詢改寫 / re-ranking / 知識萃取
│   │   ├── config.py              # 設定管理
│   │   └── requirements.txt       # Python 依賴
│   └── rag-engine.py              # ★ V2 CLI 入口
├── workflow/
│   ├── config.json                # Guardian + Vector Search 設定
│   └── state-*.json               # Session state（自動產生，不 commit）
├── memory/
│   ├── MEMORY.md                  # 全域 Atom Index
│   ├── preferences.md             # 使用者偏好 atom
│   ├── decisions.md               # 全域決策 atom
│   ├── rag-vector-plan.md         # RAG 架構設計 atom
│   ├── _vectordb/                 # ★ LanceDB 向量資料庫（runtime data）
│   └── SPEC_Atomic_Memory_System.md  # 原子記憶 V2 規格書
├── commands/
│   └── init-project.md            # /init-project 自訂指令
├── _AIDocs/
│   ├── _INDEX.md                  # 文件索引
│   ├── Architecture.md            # 系統架構詳述
│   └── _CHANGELOG.md              # 變更記錄
└── settings.json                  # hooks 註冊 + 權限
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `workflow_status` | 查詢 session 狀態（省略 session_id → 列出全部） |
| `workflow_signal` | 發送信號：sync_started / sync_completed / reset / mute |
| `memory_queue_add` | 新增知識到 pending queue |
| `memory_queue_flush` | 標記 queue 已寫入 atom |

### RAG Engine CLI

```bash
# 全量建索引
python ~/.claude/tools/rag-engine.py index

# 語意搜尋
python ~/.claude/tools/rag-engine.py search "查詢關鍵字"

# 增強搜尋（LLM 查詢改寫）
python ~/.claude/tools/rag-engine.py search "查詢" --enhanced

# 服務管理
python ~/.claude/tools/rag-engine.py status
python ~/.claude/tools/rag-engine.py health
python ~/.claude/tools/rag-engine.py start
python ~/.claude/tools/rag-engine.py stop
```

---

## MCP Transport Format

Claude Code v2.x 使用 **JSONL** 傳輸格式（非 LSP Content-Length header）：

```
{"jsonrpc":"2.0","method":"initialize","params":{...}}\n
{"jsonrpc":"2.0","id":1,"result":{...}}\n
```

- protocolVersion: `2025-11-25`
- 自寫 MCP server 務必遵循此格式，否則 30 秒超時 failed

---

## Configuration

`~/.claude/workflow/config.json`:

```json
{
  "enabled": true,
  "dashboard_port": 3848,
  "stop_gate_max_blocks": 2,
  "min_files_to_block": 2,
  "remind_after_turns": 3,
  "max_reminders": 3,
  "sync_keywords": ["同步", "sync", "commit", "提交", "結束", "收工"],
  "vector_search": {
    "enabled": true,
    "service_port": 3849,
    "embedding_backend": "ollama",
    "embedding_model": "qwen3-embedding",
    "fallback_backend": "sentence-transformers",
    "fallback_model": "BAAI/bge-m3",
    "ollama_llm_model": "qwen3:1.7b",
    "search_top_k": 5,
    "search_min_score": 0.65,
    "search_timeout_ms": 2000,
    "auto_start_service": true,
    "auto_index_on_change": true
  }
}
```

---

## Hardware Requirements

### Minimum（純 keyword 模式，不需 GPU）
- Python 3.8+
- Node.js 18+

### Recommended（V2 Hybrid RECALL）
- Python 3.10+（3.14 已驗證）
- NVIDIA GPU with CUDA（embedding 加速）
- Ollama 已安裝 + `qwen3-embedding` 模型
- `pip install lancedb sentence-transformers`

### Tested On
- Windows 11 Pro, GTX 1050 Ti 4GB, Python 3.14.2
- Ollama: qwen3-embedding（embedding）+ qwen3:1.7b（LLM）
- 全量索引 18 atoms → 380 chunks in ~300s
- Warm search latency: ~386ms

---

## License

Personal use. Not published as a package.
