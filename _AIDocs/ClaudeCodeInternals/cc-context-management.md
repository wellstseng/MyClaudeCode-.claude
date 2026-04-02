# Claude Code Context Management

- Scope: global
- Confidence: [固]
- Trigger: context management, 上下文管理, compaction, 壓縮策略, autocompact, microcompact, context collapse, CLAUDE.md loading, system context, user context, context window, memoize, 快取失效
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-prompt-engineering, cc-query-loop

## 知識

### System Context vs User Context
- [固] System Context：Git 狀態 + system prompt 注入
- [固] User Context：CLAUDE.md 記憶內容 + 持久資訊
- [固] 兩者皆 memoize，唯一失效點 setSystemPromptInjection() 同時清除兩個快取（一致性單元）

### CLAUDE.md 載入階層（後層覆蓋前層）
- [固] `~/.claude/CLAUDE.md` → `<project>/.claude/CLAUDE.md` → `<project>/CLAUDE.md` → `<cwd>/CLAUDE.md`

### 四層壓縮機制（代價遞增）
- [固] Snip：tool result 超 budget → 截斷最大結果（零 API 呼叫）
- [固] Microcompact：快取可用 → 複用舊摘要剪接訊息（極低代價）
- [固] Autocompact：tokens ≥ threshold → LLM 產生摘要（1 次 API ~50k input）
- [固] Reactive Compact：API 413 error → 收到錯誤後壓縮（同 autocompact 代價）

### Microcompact 雙軌
- [固] Cached microcompact：不修改本地 messages，透過 API cache editing 在伺服器端刪除（零 LLM 呼叫）
- [固] Time-based microcompact：快取冷時後備，直接修改本地 messages 替換為清除訊息

### contextCollapse（主動壓縮）
- [固] 與 autocompact 互斥：shouldAutoCompact() 在 contextCollapse 啟用時返回 false
- [固] 90% context 開始提交 span → ctx-agent 摘要 → committed → 漸進替換原始訊息
- [固] 95% 停止接受新輸入（blocking spawn）

### Memoization 策略
- [固] Git 狀態：Session 級 memoize（無失效）
- [固] CLAUDE.md：Session 級 memoize（setSystemPromptInjection 失效）
- [固] Hook 設定：File watcher 失效
- [固] 工具定義：永久快取（重啟失效）
- [固] MCP 連線：連線級（斷線失效）

### 壓縮後恢復
- [固] postCompactCleanup.ts 嘗試恢復最多 5 個最近編輯的檔案

### 認知科學對應（Baddeley Working Memory）
- [固] 上下文窗口 ≈ 工作記憶（有限容量）、CLAUDE.md ≈ 長期記憶、壓縮摘要 ≈ 情節記憶
- [固] 更大 context window 不能解決一切：self-attention 複雜度與序列長度平方成正比

## 行動

- Hook（pre_compact/post_compact）可在壓縮前後介入（如存檔工作狀態）
- 開發長 session 工具時注意 context 消耗，善用 Snip 避免大型 tool result
- 來源：https://claude-code-harness-blog.vercel.app/chapters/06-context-management/
