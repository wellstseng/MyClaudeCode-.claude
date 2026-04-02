# Claude Code Query Loop 與並行控制

## 知識

### Master Query 狀態機
- [固] PreCompaction（BudgetTrim → Snip → Microcompact → Autocompact）→ ApiStream（Streaming → ToolExec → stop_reason）→ Decision（DrainTools → PostHooks → StopHooks → BudgetCheck）→ 回到 PreCompaction
- [固] 核心：Decision → PreCompaction 回頭箭頭 = agentic loop 的核心

### 為什麼用 Generator
- [固] async generator（function*）逐步 yield 訊息和事件，讓 UI 即時顯示
- [固] 4 大優勢：背壓控制、yield* 委派組合、return() 外部取消、TypeScript 型別安全
- [固] Pull 語義：消費者控制消費速度，防事件無界累積

### State 型別（每次 continue 寫新物件，非 mutation）
- [固] messages, toolUseContext, autoCompactTracking, maxOutputTokensRecoveryCount（上限 3）, hasAttemptedReactiveCompact, pendingToolUseSummary, stopHookActive, turnCount, transition

### Batch Partitioning（安全並行）
- [固] isConcurrencySafe 分類：FileReadTool/GlobTool/GrepTool=true（靜態）, BashTool=動態（分析命令）, FileEditTool/WriteFileTool/MCP=false（預設）
- [固] 連續相同類型才合併的貪婪策略（不重排序，優先正確性）
- [固] [ReadFile, ReadFile, WriteFile, BashTool("git status")] → 3 個 batch：並行→串行→串行

### Sibling Abort Controller
- [固] 批次中 Bash 失敗 → siblingAbortController.abort() → 取消所有兄弟工具

### Terminal Conditions（10 種）
- [固] completed（正常結束）、max_turns、blocking_limit、prompt_too_long（413）、model_error、image_error、aborted_streaming、aborted_tools、stop_hook_prevented、hook_stopped

### Continue Transitions（7 種）
- [固] next_turn、collapse_drain_retry、reactive_compact_retry、max_output_tokens_escalate（首次→64k）、max_output_tokens_recovery（最多 3 次）、stop_hook_blocking、token_budget_continuation

### StreamingToolExecutor
- [固] addTool() 在串流中即時加入工具 → processQueue() 排程
- [固] canExecuteTool()：無工具執行中 或 全部都是 concurrency-safe 時才並行
- [固] getRemainingResults()：Promise.race（工具完成 vs 進度更新），完成一個就交出一個

## 行動

- 開發新工具時定義 isConcurrencySafe → 影響並行排程效能
- Context modifier 模式：工具修改檔案系統後，批次結束順序應用 contextModifiers
- 來源：https://claude-code-harness-blog.vercel.app/chapters/07-coordinator-concurrency/
