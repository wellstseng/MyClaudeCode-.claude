# Claude Code Prompt Engineering

- Scope: global
- Confidence: [固]
- Trigger: prompt engineering, system prompt, prompt section, DYNAMIC_BOUNDARY, prompt cache, 提示詞設計, prompt 分層, prompt 覆蓋, section system, NO_TOOLS, compact prompt, BashTool prompt, AgentTool prompt, coordinator prompt, tool description
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-context-management, cc-agent-orchestration, cc-design-patterns

## 知識

### 5 層優先順序
- [固] Layer 0 Override（完全替換）→ Layer 1 Coordinator → Layer 2 Agent → Layer 3 Custom（--system-prompt）→ Layer 4 Default
- [固] appendSystemPrompt 在所有模式下附加（除 Layer 0）

### 17 個 Section 組裝架構
- [固] 靜態 Sections 1-7（scope: global，跨使用者共享快取）：身份+安全、系統行為、任務執行、謹慎操作、工具使用、語調、輸出效率
- [固] DYNAMIC_BOUNDARY 分界
- [固] 動態 Sections 8-17（Session 專屬）：Session Guidance、Memory、Model Override、Env Info、Language、Output Style、MCP Instructions（DANGEROUS_uncached）、Scratchpad、FRC、Summarize Tool Results

### Section 快取機制
- [固] systemPromptSection(name, compute)：快取型，直到 /clear 或 /compact 重新計算
- [固] DANGEROUS_uncachedSystemPromptSection(name, compute, reason)：揮發型，每輪重新計算（破壞 Prompt Cache）
- [固] 目前唯一揮發型：mcp_instructions（MCP 伺服器可能 mid-session 連接/斷開）
- [固] DANGEROUS_ 前綴強化約束：命名本身就在 code review 時警示

### Prompt Cache Boundary 工程
- [固] 靜態前綴必須在動態 sections 之前（prefix match 物理約束）
- [固] 反例：Git status 放邊界前 = 每次 commit bust 整個 50k token 快取
- [固] 50k token system prompt：cache hit 時只付 $0.075（vs $0.75 無 cache），10 輪節省 81%

### 多模式 Prompt 變體
- [固] CLI Mode：標準互動式，完整工具指引+安全準則
- [固] Proactive Mode：自主代理，含 Tick 機制+Sleep 管理+行動優先
- [固] Coordinator Mode：純協調器，不直接執行任務
- [固] Simple Mode（CLAUDE_CODE_SIMPLE=1）：3 行最小化 prompt
- [固] Mode 切換需重新啟動 session（prompt cache 完全失效）

### 防禦性 Prompt 模式
- [固] 反過度工程："Don't add features beyond what was asked"、"Three similar lines > premature abstraction"
- [固] 可逆性評估：分類高風險操作（破壞性/難復原/影響他人）
- [固] 反幻覺："Never claim 'all tests pass' when output shows failures"
- [固] 工具優先級："Do NOT use Bash when dedicated tool exists"（Read>cat, Edit>sed, Glob>find, Grep>grep）

### BashTool Prompt 三層約束
- [固] Layer 1：工具迴避（禁 bash 執行 find/grep/cat）→ Layer 2：操作安全（並行/sleep/路徑）→ Layer 3：Git Safety Protocol（禁 force push/reset hard，HEREDOC 強制格式）

### Compact Prompt 設計
- [固] NO_TOOLS 三明治結構（前後雙框架強化限制，防壓縮時呼叫工具）
- [固] formatCompactSummary() 移除 `<analysis>` 標籤

### 跨 Prompt 設計模式
- [固]「When NOT to use」清單：防 LLM 過度使用新工具
- [固] NO_TOOLS 強制邊界：前後雙框架
- [固] XML 結構化通訊：強制性結構化場景
- [固] 絕對命令 vs 相對指引：區分嚴格程度

## 行動

- 開發 system prompt section 時，確認放在 DYNAMIC_BOUNDARY 前（靜態）或後（動態）
- 新增揮發型 section 必須有充分理由（每次都破壞 cache）
- 來源：Ch.11 + Ch.13 + Ch.14 https://claude-code-harness-blog.vercel.app/
