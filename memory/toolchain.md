# toolchain

- Scope: global
- Author: wellstseng
- Confidence: [固]
- Trigger: 工具鏈, 環境設定, MCPControl, MCP新增, npm全域, 螢幕截圖, Excel MCP, LanceDB, MSYS2, cp950, PowerShell截圖, 向量服務
- Created-at: 2026-06-12
- Related: toolchain-ollama, decisions, feedback-global-install, failures, hotfix-ilruntime-traps, obsidian-sync-hook-全域同步-stdin-json-測試陷阱, unity-mcp-自動化工具鏈, toolchain-batch-cmd-crlf-encoding, dotnet-inline-cant-cross-delegate, dotnet-mysqldata-collation-id-相容

## 知識

- ### Windows 環境差異
- [固] Claude Code 的 bash 環境是 MSYS2，路徑格式 `/c/Users/` 而非 `C:\Users\`，但 Python Path 物件自動轉換
- [固] Windows 上 bash 指令的 `/dev/null` 有效（MSYS2 模擬），不需改成 `NUL`
- [固] `timeout` 指令在 MSYS2 bash 不可用，需用 Python 的 subprocess timeout 或其他替代
- [固] Windows 環境變數用 `$env:VAR`（PowerShell）或 `$VAR`（bash），混用易出錯
- ### 已驗證的指令組合
- [固] Ollama 啟動: `ollama serve`（背景）→ `ollama list`（驗證模型可用）
- [固] 向量服務啟動: `python ~/.claude/tools/memory-vector-service/service.py`（port 3849）
- [固] 向量健康檢查: `curl http://127.0.0.1:3849/health`
- [固] 記憶格式檢查: `python ~/.claude/tools/memory-audit.py`
- ### 路徑與版本
- [固] Ollama models 位置: 預設 `~/.ollama/models/`
- [固] LanceDB 資料: `~/.claude/memory/_vectordb/`
- ### Ollama Dual-Backend → 詳見 `toolchain-ollama.md`
- ### 桌面操控 / 螢幕截圖（原 MCPControl，已移除）
- [固] **MCPControl 與 playwright MCP 已於 2026-06-12 移除**（node_modules 缺依賴失連 + 功能被內建工具覆蓋）；桌面操控改用 harness 內建 `mcp__computer-use__*`，瀏覽器自動化改用 Claude in Chrome（`mcp__Claude_in_Chrome__*`）
- [固] **使用者明確要求**：需要看畫面時優先用內建 computer-use 截圖，不要說「看不到」。若內建工具不可用，fallback 用 PowerShell 截圖：`CopyFromScreen` → 存 PNG → Read tool 讀取
- [固] PowerShell 截圖配方：`Add-Type System.Windows.Forms + System.Drawing` → `Bitmap` → `Graphics.CopyFromScreen` → `.Save()`；可 `Bitmap.Clone(Rectangle)` 裁切特定區域
- ### MCP Server：Excel（@negokaz/excel-mcp-server）
- [固] 全域安裝：`npm i -g @negokaz/excel-mcp-server`，目前版本 0.12.0
- [固] 功能：describe_sheets / read_sheet / write_to_sheet / create_table / format_range / screen_capture
- [固] 支援 xlsx/xlsm/xltx/xltm；**不支援舊版 .xls**（舊版用 `tools/read-excel.py` + xlrd）
- [固] 跨專案可用（`~/.claude.json` User scope）
- ### MCP 新增規則
- [固] **全域 MCP 設定位置**：`~/.claude.json`（注意不是 `~/.claude/.mcp.json`）的 `mcpServers` 欄位 → 所有專案顯示為 "User" scope
- [固] **`~/.claude/.mcp.json` 是專案層**：只在 `~/.claude` 作為工作目錄時生效，其他專案看不到
- [固] **一律全域安裝 + 絕對路徑**：`npm i -g {pkg}` → 用 `node.exe` + 絕對路徑指向 `AppData/Roaming/npm/node_modules/{pkg}/dist/{entry}.js`
- [固] **禁用 npx 啟動**：`cmd /c npx` 在 VSCode 擴充環境不穩定，MCP server 會無法啟動
- [固] 入口查找：`package.json` 的 `bin` 欄位確認 entry point
- [固] 範本：`"command": "C:\\Program Files\\nodejs\\node.exe", "args": ["C:\\Users\\holylight\\AppData\\Roaming\\npm\\node_modules\\{pkg}\\dist\\{entry}.js"]`
- ### 環境特殊配置
- [固] ChromaDB 已棄用，改用 LanceDB（i7-3770 不支援 AVX2）
- [固] workflow-guardian.py stdout/stderr 強制 UTF-8（Windows 預設 cp950 會導致中文亂碼）

## 行動

- build/setup/config intent 時自動載入
- 成功執行新工具指令後，評估是否值得記錄（跨 session 重用性 ≥ 2 次預期）
- 環境問題 debug 時，優先查此 atom 再嘗試盲目探索
- 版本資訊在確認後更新，不猜測
