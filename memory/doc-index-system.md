# 原子記憶系統 — 全檔案索引

- Scope: global
- Confidence: [臨]
- Type: semantic
- Trigger: 系統架構, 檔案結構, file tree, architecture, hook, skill, tool, 升級, upgrade, 迭代, self-understand
- Last-used: 2026-03-18
- Created: 2026-03-13
- Confirmations: 21
- Tags: doc-index, system-overview
- Related: decisions, toolchain

## 知識

### 啟動鏈（Session Lifecycle）

Claude Code 啟動時載入順序：
1. `settings.json` — 權限白名單 + 6 hook events 定義
2. `hooks/user-init.sh` — 從 USER.template.md 生成 USER-{username}.md → USER.md
3. `hooks/workflow-guardian.py:handle_session_start()` — 初始化 state、解析 atom 索引、載入 _AIDocs、check periodic review、Wisdom blind spots、啟動 vector service
4. `CLAUDE.md` @import → IDENTITY.md + USER.md + MEMORY.md + rules/*.md（4 模組）

### 設定檔（Config Layer）

- `CLAUDE.md` — 全域入口，@import 3 檔 + 引用 4 個 rules 模組
- `IDENTITY.md` — AI 人格（團隊共用）：直球精準、最小變動、懷疑就問
- `USER.md` — 使用者偏好（per-user，由 hook 從 template 生成，gitignore）
- `USER.template.md` — 多人使用模板（git 追蹤）
- `BOOTSTRAP.md` — 首次設定引導（IDENTITY/USER 為空時觸發）
- `settings.json` — Hook 事件綁定 + 權限 allowlist + MCP 設定
- `.mcp.json` — MCP server 定義（MCPControl = computer-use）
- `workflow/config.json` — Guardian/Vector/WriteGate/Decay/ResponseCapture 全參數

### 規則模組（rules/）

- `aidocs.md` — _AIDocs 知識庫維護（啟動檢查 + 工作中 4 規則）
- `memory-system.md` — 原子記憶分類/寫入/演進/引用原則
- `session-management.md` — 對話管理 + 續航 + 識流 + 自我迭代 V2.6
- `sync-workflow.md` — 工作結束同步 checklist + Guardian 閘門

### Hook 系統（hooks/）

- `workflow-guardian.py`（~2841 行）— 統一 hook dispatcher，6 event handlers：
  - SessionStart: 初始化 state + atom index + _AIDocs + Wisdom + long_die check
  - UserPromptSubmit: Phase0(episodic) → Phase0.5(_AIDocs match) → Phase1(atom injection, ACT-R ranking) → Phase2(sync remind)
  - PostToolUse: 追蹤 Edit/Write/Read + incremental vector index + Wisdom retry
  - PreCompact: snapshot timestamp
  - Stop: 未同步閘門（block/allow）
  - SessionEnd: spawn extract-worker → cross-session pattern → conflict detect → Wisdom reflect → episodic atom
- `extract-worker.py`（~463 行）— SessionEnd 子程序，LLM 萃取知識 + dedup + cross-session vector search
- `wisdom_engine.py`（~195 行）— 反思引擎：2 硬規則（plan/confirm）+ 3 反思指標（accuracy/over_engineering/silence）
- `user-init.sh`（~20 行）— 多人 USER.md 初始化

### Skills 系統（commands/）

| Skill | 用途 | 外部依賴 |
|-------|------|---------|
| `/atom-debug` | 原子記憶注入/萃取 debug log 開關 | 無 |
| `/consciousness-stream` | 高風險跨系統任務（唯識八識框架） | 無 |
| `/continue` | 讀取 _staging/next-phase.md 續接 | 無 |
| `/harvest` | Playwright 網頁收割 → Markdown | Playwright |
| `/init-project` | 專案 _AIDocs 知識庫初始化 | 無 |
| `/read-project` | 系統性讀取 → doc-index atom | 無 |
| `/resume` | 生成續接 prompt + 自動開新 session | MCPControl |
| `/svn-update` | SVN 更新 + 衝突處理 | TortoiseSVN/svn CLI |
| `/unity-yaml` | Unity YAML 解析/生成 | unity-yaml-tool.py |
| `/upgrade` | 環境升級（diff + merge + rebuild） | 無 |

### 工具鏈（tools/）

**向量服務（port 3849）：**
- `service.py` — HTTP daemon（search/ranked/episodic/index/health）
- `config.py` — config.json 讀寫
- `indexer.py` — atom 解析 → chunk → embed → LanceDB 寫入
- `searcher.py` — semantic + ranked search（5-factor scoring: 0.45 semantic + 0.15 recency + 0.20 intent + 0.10 confidence + 0.10 confirmations）
- `reranker.py` — LLM query rewrite + re-rank + knowledge extraction

**Ollama 雙 Backend：**
- `ollama_client.py` — singleton，generate()/chat()/embed()，rdchat(pri=1) → local(pri=2)，三階段退避，long_die marker + 使用者確認

**記憶品質工具：**
- `memory-audit.py` — atom 格式驗證 + staleness 檢查
- `memory-write-gate.py` — 寫入前品質閘門（6 規則 + 0.80 dedup）
- `memory-conflict-detector.py` — 向量衝突偵測 + LLM 分類（AGREE/CONTRADICT/EXTEND）
- `atom-health-check.py` — 參照完整性 + alias 驗證

**其他工具：**
- `read-excel.py` — Excel 讀取（openpyxl + xlrd）
- `unity-yaml-tool.py` — Unity YAML 解析/生成
- `rag-engine.py` — Vector Service CLI wrapper
- `eval-ranked-search.py` — 50 query 檢索品質 benchmark
- `test-memory-v21.py` — V2.1 feature E2E test
- `cleanup-old-files.py` — 舊 state/debug 檔清理
- `gdoc-harvester/` — Google Docs/Sheets 收割 + dashboard
- `workflow-guardian-mcp/server.js` — MCP stdio server + HTTP dashboard（port 3848）

### 記憶層（memory/）

**索引**：MEMORY.md — 9 atoms 觸發表 + 高頻事實（always loaded，≤30 行）

**Atoms**（9 個 [固]/[觀]）：preferences, decisions, excel-tools, workflow-rules, failures, toolchain, unity-yaml(+detail), gdoc-harvester, feedback-research

**參考文件**（_reference/，不自動注入）：SPEC(950行), self-iteration, v3-design, v3-research

**Wisdom Engine**：DESIGN.md(架構) + reflection_metrics.json(live 指標)

**運行時**（gitignore）：episodic/, _vectordb/, _staging/, _distant/

### 對外文件

- `README.md` — GitHub 入口：設計理念 + 7 階段流程 + Token 影響 + 安裝指引
- `Install-forAI.md` — 6 步安裝 SOP + FAQ
- `_AIDocs/` — 專案知識庫（Architecture, Project_File_Tree, CHANGELOG 等）
- `LICENSE` — GPLv3

## 行動

- 需要了解某模組細節時，直接 Read 對應檔案
- 升級/迭代時，從此索引定位影響範圍
- 新增檔案後更新此索引

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-13 | 初始建立：76 檔完整索引 | /read-project |
