# claude -p 精簡模式偵測-init 事件工具只剩 Bash Edit Read 三支-正常約四十支-隔離模式不會誤判

- Scope: global
- Author: wellstseng
- Source: session 6fb15a66 2026-11-06 探針實跑
- Quote: 「全部都做 目標讓某專案的代理品質更好 測試也請確實 要重啟要跟我確認」
- Confidence: [臨]
- Trigger: --bare, CLAUDE_CODE_SIMPLE, claude -p, stream-json, system/init, 精簡模式, 無頭, headless, --mcp-config
- Created-at: 2026-11-06

## 知識

- [臨] 官方預告 `claude -p` 將來預設改成 `--bare`：不載 hook、CLAUDE.md、skills、自動載入的 MCP、原子記憶，也不讀 OAuth 登入（要 API key）。只傳 `-p` 的程式到時會悄悄失去記憶或登入失敗
- [臨] 實測 claude 2.1.318 `-p --output-format stream-json --verbose`：正常 init 的 tools 40 支、mcp_servers 2、skills 85，init 前先出 hook_started／hook_response；`CLAUDE_CODE_SIMPLE=1`（等同 --bare）時內建工具剛好 Bash、Edit、Read 三支、skills 19、沒有 hook 事件
- [臨] `--bare` 加 `--mcp-config` 時明確給的 MCP 照樣載入：tools 是 Bash／Edit／Read＋一串 `mcp__*`。偵測要先濾掉 `mcp__*` 只看內建工具⊆{Bash,Edit,Read}；用「全部工具 ≤3 支」會在帶 MCP 的包裝程式上漏報
- [臨] 不要用 hook 有無判：`--setting-sources project,local` 這種隔離模式也沒有 hook，但內建工具照常
- [臨] 在 Claude 桌面 app 的 session 裡巢狀跑 `claude -p` 會因 OAuth 刷新失敗回 synthetic 錯誤訊息，但 init 事件照樣先吐，拿來看載入狀態夠用

## 行動

- 包 claude -p 的程式：init 時濾掉 mcp__* 再檢查內建工具，縮成三支就告警
- 做偵測的探針要帶上正式呼叫點的全部旗標（特別是 --mcp-config），不然範本會測錯情境
- 官方出關閉精簡模式的旗標後，在呼叫點明帶
