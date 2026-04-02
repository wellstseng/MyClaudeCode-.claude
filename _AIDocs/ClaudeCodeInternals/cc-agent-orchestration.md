# Claude Code Agent Orchestration

## 知識

### 子代理生命週期 FSM
- [固] 狀態：Pending → Running → Completed/Failed/Killed
- [固] isTerminalTaskStatus() 識別終端狀態

### 三種執行模式
- [固] 同步（Sync/Inline）：子代理完成即返回，無 Task 物件
- [固] 非同步（Async/Background）：背景執行，父代理立即拿到 task ID
- [固] 遠端（Remote）：傳送到 Cloud Runner，不佔本地資源

### CacheSafeParams — 成本優化核心
- [固] 父子代理必須有完全相同的 system prompt + tools + model → 命中 prompt cache
- [固] Fork 模型 vs Naive Spawn：10 個子代理 $0.75 vs $7.50（90% 節省）
- [固] CacheSafeParams 欄位：systemPrompt, userContext, systemContext, toolUseContext, forkContextMessages
- [固] 任何欄位改變 → 全新 cache key → 前面所有快取寫入白費
- [固] 父代理每次 API 呼叫後儲存參數（saveCacheSafeParams），子代理取得（getLastCacheSafeParams）

### Prompt Cache 底層
- [固] 只快取前綴（prefix match），非 key-value store
- [固] cache_control: { type: "ephemeral" } 標記前的 tokens 進入 KV cache
- [固] 價格：正常 input $3/1M，cache_creation $3.75/1M（1.25×），cache_read $0.30/1M（10%）
- [固] 靜態 sections 必須在動態 sections 之前（SYSTEM_PROMPT_DYNAMIC_BOUNDARY）

### Agent Definition System
- [固] Markdown 格式定義子代理角色（name, description, model, tools）
- [固] 來源：內建（ONE_SHOT_BUILTIN_AGENT_TYPES）、使用者（.claude/agents/）、專案

### Worktree 隔離
- [固] git worktree：同一 repo 多個工作副本，共享 .git/objects（無磁碟浪費）
- [固] WorktreeSession 追蹤 originalHeadCommit（防靜默刪除未 merge 變更）
- [固] 大型目錄用 symlink 節省空間（settings.worktree.symlinkDirectories）

### Coordinator Mode 工具限制
- [固] Worker 允許：~30 個核心工具（ASYNC_AGENT_ALLOWED_TOOLS）
- [固] Worker 禁止：AgentTool（禁派生）、TaskStopTool、AskUserQuestionTool
- [固] Coordinator 專用：AgentTool, TaskStopTool, SendMessageTool, SyntheticOutputTool
- [固] Coordinator 不能編輯檔案/執行 Bash（強制分離規劃與執行）
- [固] 遞迴防護：Worker 無 AgentTool → 遞迴在工具層級被切斷

## 行動

- 開發多 Agent 工具時，確保 CacheSafeParams 一致以命中 prompt cache
- Worktree 隔離適合需要平行修改檔案的場景
- 來源：https://claude-code-harness-blog.vercel.app/chapters/03-agent-orchestration/
