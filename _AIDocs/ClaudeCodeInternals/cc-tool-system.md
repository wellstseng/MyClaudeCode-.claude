# Claude Code Tool System

## 知識

### Tool 型別結構
- [固] 泛型介面：name, aliases, searchHint, call(), description(), checkPermissions()
- [固] 安全元資料（接受 input 參數）：isConcurrencySafe(input), isReadOnly(input), isDestructive(input)
- [固] 同一工具不同輸入可有不同安全行為（如 BashTool `ls` vs `rm`）
- [固] 雙軌驗證：JSON Schema（給 LLM 合約）+ Zod Schema（harness runtime 防線）
- [固] Zod 驗證失敗 → InputValidationError → LLM 可重試

### Fail-Closed 設計
- [固] buildTool() 保守預設：isConcurrencySafe=false, isReadOnly=false
- [固] 未聲明 → 系統採最安全行為（寧可犧牲效能不冒正確性風險）

### 執行狀態機（StreamingToolExecutor）
- [固] 4 狀態：Queued → Executing → Completed → Yielded
- [固] 非 concurrency-safe 工具結果必須按序交付（防亂序到達 LLM）

### runToolUse 序列
- [固] 工具名稱查找（含 alias）→ 中止檢查 → 權限檢查 → 執行+進度回報 → 結果驗證+交付

### lazySchema（打破循環依賴）
- [固] AgentTool schema 需要工具列表 ↔ 工具列表包含 AgentTool → 循環
- [固] 解法：推遲 schema 建構到首次使用。代價：首次存取較慢，錯誤延後到 runtime

### Progress Callback
- [固] 路徑：BashTool stdout → onProgress → checkPermissionsAndCallTool → StreamingToolExecutor.pendingProgress → yield → React/Ink render
- [固] 工具不決定輸出目標，只報告進度。上層決定如何處理

### 工具清單分類
- [固] 檔案：FileReadTool, FileEditTool, FileWriteTool
- [固] 搜尋：GlobTool, GrepTool
- [固] 執行：BashTool
- [固] 代理：AgentTool, SendMessageTool
- [固] 任務：TaskCreateTool, TaskUpdateTool
- [固] 其他：SkillTool, MCPTool

## 行動

- 自製工具時必須宣告 isConcurrencySafe/isReadOnly（否則 fail-closed 預設會阻止並行）
- MCP 第三方工具永遠 isConcurrencySafe=false（副作用未知）
- 來源：https://claude-code-harness-blog.vercel.app/chapters/02-tool-system/
