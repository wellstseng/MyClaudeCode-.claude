# Claude Code Harness Engineering 概論

## 知識

### 定義
- [固] Harness Engineering = 在 LLM 和真實世界之間建立安全、高效、可控的介面層
- [固] 5 核心原則：工具即一等公民、分層權限、可觀測性、容錯設計、成本意識（Prompt Cache）

### 架構元件責任矩陣
- [固] Query Loop 主迴圈 — `src/query.ts` / `src/QueryEngine.ts`（接收輸入→驅動 LLM API→協調工具執行）
- [固] Tool System — `src/Tool.ts` / `src/tools.ts`（定義介面→驗證 schema→執行→回傳）
- [固] Agent Orchestration — `src/tools/AgentTool/`（派遣子代理→管理生命週期→共享 prompt cache）
- [固] Permission System — `src/hooks/toolPermission/`（判斷是否需確認→ML 分類）
- [固] Hook System — `src/utils/hooks.ts`（前後觸發外部程序→Session 生命週期）
- [固] Context Management — `src/context.ts`（組裝 system prompt→注入 CLAUDE.md→壓縮管理）
- [固] Compaction — `src/context/compaction.ts`（偵測 context 接近上限→自動摘要）
- [固] State Management — `src/state/AppStateStore.ts`（維護 session 不可變狀態樹→驅動 UI）
- [固] Skills — `src/skills/`（使用者自定義 slash command）
- [固] Plugins/MCP — `src/services/mcp/client.ts`（MCP server 連接→工具發現→生命週期管理）

### 啟動序列（因果鏈，順序不可違反）
- [固] 階段一 Module Loading（同步）：`profileCheckpoint` → `startMdmRawRead()` → `startKeychainPrefetch()`，I/O 與 import 並行（省 ~135ms）
- [固] 階段二 init()（memoize 只執行一次）：enableConfigs → applySafeConfigEnvVars → applyExtraCACerts → setupGracefulShutdown → configureGlobalMTLS → configureGlobalAgents
- [固] 階段三 action handler：getTools → initBuiltinPlugins + initBundledSkills → setup() ‖ getCommands() → connectMcpBatch → queryLoop
- [固] Print mode（`-p`）在 connectMcpBatch 完成前阻塞（turn-1 工具完整）；interactive mode 允許 MCP 背景連線（turn-2 才保證）
- [固] setup.ts 嚴格順序：setCwd → captureHooksConfigSnapshot → initializeFileChangedWatcher → worktree 建立（可能 chdir）→ 背景工作 → Plugin 預取 → 安全驗證

### 端對端旅程（使用者輸入→回應）
- [固] 6 步驟：① 輸入進入 Query Loop → ② Context 組裝（CLAUDE.md 注入 + System Prompt）→ ③ LLM API Streaming → ④ 工具執行（權限檢查→pre hook→執行→post hook）→ ⑤ 子代理派遣（可選）→ ⑥ 工具結果注入→下一輪或終止
- [固] Prompt cache 命中節省 60-80% input token

## 行動

- 開發 hook/skill/tool 時，先對照架構責任矩陣確認修改落點
- 啟動順序問題導致靜默 bug → 注意 setup.ts 的因果鏈
- 來源：https://claude-code-harness-blog.vercel.app/chapters/01-introduction/
