# Claude Code State Management

- Scope: global
- Confidence: [固]
- Trigger: state management, AppState, AppStateStore, createStore, ToolUseContext, 狀態管理, DeepImmutable, 依賴注入, DI, 雙層快取
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-query-loop

## 知識

### AppState Store（自製極簡 Store）
- [固] 3 個公開方法：getState(), setState(updater), subscribe(listener)
- [固] 不用 Redux 的 4 個理由：Agent session 不可重現（時光旅行無用）、需 Snapshot 序列化、需 Diff 欄位差異、Ephemeral by design

### ToolUseContext 依賴注入
- [固] 傳播路徑：query → StreamingToolExecutor → runToolUse → checkPermissionsAndCallTool → tool.checkPermissions → tool.call
- [固] 核心欄位：options(tools/commands/verbose), abortController, getAppState, setAppState, messages, agentId
- [固] 子代理派生：setAppState→no-op, setAppStateForTasks→指向根store, abortController→子代理自有, tools→授權子集

### AppState 結構
- [固] settings, mainLoopModel, messages, mcp(clients/commands), tasks(Map), toolPermissionContext, classifierApprovals, denialTracking, expandedView

### DeepImmutable 型別級不可變
- [固] 純編譯期檢查（readonly recursive），無 runtime 開銷
- [固] 正確更新：setState(prev => ({...prev, field: newValue}))

### 雙層快取
- [固] L1：記憶體（AppState），即時存取，Session 生命週期
- [固] L2：磁碟檔案，毫秒存取，跨 Session
- [固] Cache key = session_id + tool_name + hash(input)
- [固] 失效策略：session 結束即失效（不追蹤細粒度工具依賴）

## 行動

- Agent 系統更像有狀態伺服器而非互動式 UI，簡單 pub/sub + immutable 更新已足夠
- 來源：https://claude-code-harness-blog.vercel.app/chapters/09-state-management/
