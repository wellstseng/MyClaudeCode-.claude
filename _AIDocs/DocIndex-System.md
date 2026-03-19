# 原子記憶系統 — 全檔案索引（76 files）

> 由 `/read-project` 於 2026-03-13 系統性閱讀產出。
> 目標：讓 Claude Code AI 能了解自己，以利後續升級、迭代、進化。

---

## 1. 啟動鏈（Session Lifecycle）

```
Claude Code 啟動
  ↓
settings.json（權限 + hooks 定義）
  ↓
[SessionStart hooks]
  ├─ user-init.sh → USER.template.md → USER-{username}.md → USER.md
  └─ workflow-guardian.py:handle_session_start()
       ├─ 解析 MEMORY.md atom 索引
       ├─ 掃描 _AIDocs/_INDEX.md
       ├─ Wisdom Engine blind spots
       ├─ Long DIE check（Dual-Backend）
       └─ 啟動 Vector Service（port 3849）
  ↓
CLAUDE.md @import
  ├─ IDENTITY.md（AI 人格）
  ├─ USER.md（使用者偏好）
  ├─ MEMORY.md（atom 索引 + 高頻事實）
  └─ rules/*.md（4 模組自動載入）
  ↓
Session Ready
  ↓
[UserPromptSubmit] ×N → atom injection + sync remind
[PostToolUse] ×N → file tracking + vector index
[Stop] → sync gate
[SessionEnd] → LLM extraction + episodic + Wisdom reflect
```

## 2. 設定檔層

| 檔案 | 用途 | 載入方式 | 多人 |
|------|------|---------|------|
| CLAUDE.md | 全域入口，@import 3 檔 + 4 rules | 自動 | 共用 |
| IDENTITY.md | AI 人格（直球精準、最小變動） | @import | 共用 |
| USER.md | 使用者偏好（繁中、極簡） | @import（hook 生成，gitignore） | per-user |
| USER.template.md | 多人模板 | user-init.sh 複製 | 共用 |
| BOOTSTRAP.md | 首次設定引導 | 條件觸發 | 共用 |
| settings.json | Hook 事件 + 權限白名單 | Claude Code 讀取 | 共用 |
| .mcp.json | MCP server 定義 | Claude Code 讀取 | 共用 |
| workflow/config.json | Guardian/Vector/Decay/Capture 全參數 | Hook 每次讀取 | 共用 |

## 3. 規則模組（rules/）

| 模組 | 職責 |
|------|------|
| aidocs.md | _AIDocs 知識庫維護（啟動檢查 + 工作中 4 規則） |
| memory-system.md | 原子記憶：[固]/[觀]/[臨] 分類 + 寫入原則 + 演進規則 |
| session-management.md | 對話管理 + 續航 + 識流 + 自我迭代 |
| sync-workflow.md | 工作結束同步 + Workflow Guardian 閘門 |

## 4. Hook 系統

| 檔案 | 行數 | 事件 | 職責 |
|------|------|------|------|
| workflow-guardian.py | ~2841 | 6 events | 統一 dispatcher：state 管理、atom injection、sync gate、extraction |
| extract-worker.py | ~463 | SessionEnd子程序 | LLM 知識萃取 + dedup + cross-session vector search |
| wisdom_engine.py | ~195 | 被 guardian 呼叫 | 2 硬規則 + 3 反思指標 + Bayesian arch sensitivity |
| user-init.sh | ~20 | SessionStart | 多人 USER.md 初始化 |

## 5. Skills（commands/）

| 指令 | 用途 | 依賴 |
|------|------|------|
| /consciousness-stream | 高風險跨系統（唯識八識） | 無 |
| /continue | 讀 _staging/next-phase.md 續接 | 無 |
| /harvest | Playwright 網頁收割→Markdown | Playwright |
| /init-project | 專案 _AIDocs 初始化 | 無 |
| /read-project | 系統性閱讀→doc-index atom | 無 |
| /resume | 續接 prompt + 自動開新 session | MCPControl |
| /svn-update | SVN 更新 + 衝突處理 | TortoiseSVN |
| /unity-yaml | Unity YAML 解析/生成 | unity-yaml-tool.py |
| /upgrade | 環境升級（diff+merge+rebuild） | 無 |

## 6. 工具鏈（tools/）

### 向量服務（port 3849）
- service.py — HTTP daemon
- config.py — config.json 讀寫
- indexer.py — atom→chunk→embed→LanceDB
- searcher.py — semantic + ranked（5-factor: semantic 0.45 + recency 0.15 + intent 0.20 + confidence 0.10 + confirmations 0.10）
- reranker.py — LLM query rewrite + re-rank

### Ollama 雙 Backend
- ollama_client.py — singleton，generate()/chat()/embed()
  - rdchat: qwen3.5:latest + qwen3-embedding:latest（RTX 3090，pri=1）
  - local: qwen3:1.7b + qwen3-embedding（GTX 1050 Ti，pri=2）
  - 三階段退避：normal → short_die(60s) → long_die(6h boundary)
  - Long DIE → workflow-guardian SessionStart 提示使用者確認停用/保持

### 記憶品質
- memory-audit.py — 格式驗證 + staleness
- memory-write-gate.py — 寫入閘門（6 規則 + 0.80 dedup）
- memory-conflict-detector.py — 向量衝突 + LLM 分類
- atom-health-check.py — 參照完整性

### 其他
- read-excel.py（openpyxl+xlrd）| unity-yaml-tool.py | rag-engine.py（CLI wrapper）
- eval-ranked-search.py（50 query benchmark）| test-memory-v21.py（E2E）| cleanup-old-files.py
- gdoc-harvester/（Playwright 網頁收割 + dashboard）
- workflow-guardian-mcp/server.js（MCP stdio + dashboard port 3848）

## 7. 記憶層

- **MEMORY.md**（always loaded）— 10 atoms 觸發表 + 高頻事實
- **Atoms**（9+1 個）— preferences, decisions, excel-tools, workflow-rules, failures, toolchain, unity-yaml(+detail), gdoc-harvester, feedback-research, doc-index-system
- **_reference/**（手動讀取）— SPEC(950行), self-iteration, v3-design, v3-research
- **wisdom/**（live state）— DESIGN.md + reflection_metrics.json + causal_graph.json(stub)
- **Runtime**（gitignore）— episodic/, _vectordb/, _staging/, _distant/, state-*.json

## 8. 對外文件

- README.md — GitHub 入口（設計理念 + 架構 + Token 影響 + 安裝）
- Install-forAI.md — 6 步安裝 SOP + FAQ
- _AIDocs/ — 專案知識庫（6+1 文件）
- LICENSE — GPLv3

---

## 速查

| 問題 | 去看 |
|------|------|
| 啟動時載入了什麼？ | CLAUDE.md → settings.json → workflow-guardian.py:handle_session_start |
| Atom 怎麼被注入的？ | workflow-guardian.py Phase 1（trigger match + semantic search + ACT-R rank） |
| 記憶怎麼寫入？ | memory-write-gate.py → extract-worker.py → cross-session promote |
| 向量搜尋怎麼運作？ | indexer.py → searcher.py → reranker.py（via service.py） |
| Ollama 雙 Backend？ | ollama_client.py + workflow/config.json ollama_backends |
| 怎麼升級環境？ | /upgrade skill（diff + merge + rebuild vector） |
