# Claude Code Skills & Plugin System

## 知識

### Skill 系統
- [固] Skill = Markdown 檔案 + frontmatter（name, description, model, shell, env）
- [固] 發現來源（優先序）：`.claude/skills/` → `~/.claude/skills/` → managed → bundled → mcp://prompts
- [固] 執行流程：解析技能名 → 讀 markdown → 注入為新對話訊息 → 遞迴呼叫 query()
- [固] Inline 執行：展開 skill 提示注入父對話，contextModifier 修改 ToolUseContext
- [固] Fork 執行：啟動獨立子代理，透過 runAgent 傳遞父代理 context
- [固] 繼承：toolPermissionContext + 父工具清單 + getAppState；不繼承：model（可覆寫）
- [固] 安全：skill 無法取得不應有的權限

### MCP（Model Context Protocol）
- [固] Transport 類型：Stdio（本地 CLI）、SSE（遠端 HTTP）、WebSocket（即時雙向）、InProcess（內建）
- [固] 連線 memoization：同一 (name, config) 只建立一次
- [固] URL Elicitation：-32042 錯誤碼，最多重試 3 次

### MCP 工具包裝（MCPTool）
- [固] 雙軌 schema：inputSchema 用 Zod passthrough（不限型別），inputJSONSchema 直送 API
- [固] 代價：無法客戶端預先驗證 MCP 工具輸入
- [固] 大型結果寫入磁碟避免上下文溢出

### MCP Sampling Protocol（伺服器反向呼叫 LLM）
- [固] 流程：Claude → MCP 工具 → sampling/createMessage → Claude Code 呼叫 Anthropic API → 結果回傳
- [固] 代價：每次 MCP 伺服器請求消耗 session token 預算

### Plugin 系統
- [固] 來源：bundled / marketplace（npm）/ local（.claude/plugins/）
- [固] 生命週期：發現 → 載入 → 驗證 → Hook 註冊 → 活躍
- [固] 錯誤隔離：Promise.allSettled（單一 plugin 失敗不影響其他）
- [固] 安全：Plugin 工具進入與內建工具相同的 checkPermissionsAndCallTool 管道
- [固] 管理階層：policySettings > 使用者設定 > 專案設定

## 行動

- 自製 Skill：存為 `.claude/skills/{name}.md`，輸入 `/{name}` 即可用
- MCP 伺服器開發：用 JSON Schema 定義工具，Claude Code 自動包裝
- 來源：https://claude-code-harness-blog.vercel.app/chapters/08-skills-plugins/
