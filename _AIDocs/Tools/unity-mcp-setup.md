# Unity MCP 安裝與配置（全域）

- Scope: global
- Confidence: [固]
- Type: procedural
- Trigger: Unity MCP 安裝, mcp__unity-mcp, CoplayDev/unity-mcp, MCPForUnity, 8080, Unity Editor 自動化
- Created: 2026-04-23
- Confirmations: 1
- Tags: tool, unity, mcp, setup
- Related: unity-mcp-自動化工具鏈 (memory atom), toolchain

---

## 元件總覽

| 元件 | 角色 | 位置 |
|------|------|------|
| MCP for Unity (Coplay) | Unity Editor plugin，啟動 HTTP MCP server | UPM 套件 `com.coplaydev.unity-mcp` |
| Unity Editor | Host process（必須開著且載入專案） | port 8080 (HTTP) |
| Claude Code | MCP client | `~/.claude.json` 內 `mcpServers.unity-mcp` |

**架構**：Claude Code → HTTP `localhost:8080/mcp` → Unity Editor plugin → Unity Editor API。

---

## 安裝步驟

### 1. Unity 端（每個專案各自加）

修改 `Packages/manifest.json`，於 `dependencies` 加入：

```json
"com.coplaydev.unity-mcp": "https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#v9.6.6"
```

> 版本號 `v9.6.6` 為 2026-04 當時最新。後續可改 `#main` 拉最新。

開啟 Unity Editor，等套件還原完成。Plugin 自動啟動 HTTP server 於 `localhost:8080/mcp`。

### 2. Claude Code 端（一次設定，全機通用）

編輯 `C:\Users\wellstseng\.claude.json`（**注意是 `.claude.json` 檔案，不是 `.claude\` 資料夾**），於 `mcpServers` 加入：

```json
"unity-mcp": {
  "type": "http",
  "url": "http://localhost:8080/mcp"
}
```

**`type` 欄位必須有**（見[踩坑 1](#踩坑)）。

### 3. 重啟 Claude Code Session

設定變更後**必須重啟 session**，新的 MCP server 才會載入。重啟後執行檢查：
- 工具列表應出現 `mcp__unity-mcp__*` 系列（manage_gameobject、manage_scene、execute_code 等共 44+）
- ToolSearch 查詢 `unity` 應有結果

---

## 驗證

| 檢查 | 指令 / 動作 | 預期 |
|------|------------|------|
| Unity HTTP server 存活 | `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/mcp` | `406`（協定不對但 port 通） |
| Claude Code 載入 MCP | ToolSearch `unity` | 列出 `mcp__unity-mcp__*` |
| 連線到 Unity | 呼叫 `mcp__unity-mcp__read_console` | 回傳 console 輸出 |

---

## 踩坑

### 1. 漏 `type` 欄位 → server 不會載入（2026-04-23）

**症狀**：MCP server 條目寫在 `~/.claude.json` 內，但 Claude Code session 沒看到工具。

**根因**：`~/.claude.json` 內的全域條目只寫 `"url"` 沒寫 `"type"`，Claude Code 不知用什麼 transport，靜默忽略。

**正確**：
```json
"unity-mcp": { "type": "http", "url": "http://localhost:8080/mcp" }
```

### 2. Unity Editor 未開啟 → 連線失敗

Plugin 是 Editor extension，**Editor 關閉則 HTTP server 死**。Headless / batchmode 場景需另外處理（見 atom `unity-mcp-自動化工具鏈`）。

### 3. 多 Unity instance 並存 → 必須 set_active_instance

同時開多個 Unity 專案時，MCP server 要明確路由。先呼叫 `mcp__unity-mcp__set_active_instance` 指定 `Name@hash`，否則 tool call 會 error。

### 4. 設定檔位置易混淆

`~/.claude.json` 是**檔案**，位於 `C:\Users\wellstseng\.claude.json`；
`~/.claude\` 是**資料夾**，位於 `C:\Users\wellstseng\.claude\`。
MCP server 設定寫在前者，**不在 git repo 內**（git repo 在後者），無法直接版控設定本身——所以才需要這份 setup 文件作為設定範本。

### 5. ensure-mcp.py 不會碰 unity-mcp

[hooks/ensure-mcp.py](~/.claude/hooks/ensure-mcp.py) 只管理 `mcp-servers.template.json` 內列出的 stdio + npm 安裝的 server，且只 add 不 delete。手動加的 `unity-mcp`（HTTP type）安全，不會被覆寫或清除。

---

## 常用工具速查

完整工作流範例見 skill `unity-mcp-skill`（`SKILL.md`）。重點工具：

| 類別 | 工具 | 用途 |
|------|------|------|
| Resource (讀) | `mcpforunity://editor/state` | 編譯狀態、play mode |
| GameObject | `manage_gameobject` / `find_gameobjects` | CRUD GameObject |
| Scene | `manage_scene` | 載入/儲存/查詢場景 |
| Script | `create_script` / `script_apply_edits` / `validate_script` | C# 檔操作 |
| Asset | `manage_asset` / `manage_prefab` | Asset/Prefab |
| 編譯 | `read_console` | 編譯後檢查錯誤（必跑） |
| 批次 | `batch_execute` | 多操作 10-100x 加速 |
| 工具 | `execute_code` / `execute_menu_item` | 執行 C# 片段 / 觸發選單 |

**鐵則**：改完 script → 等 `is_compiling == false` → `read_console(types=["error"])` 確認再下一步。

---

## 跨機器還原 SOP

1. 複製這份文件到目標機器（或用同一個 ~/.claude git repo pull）
2. 編輯目標機器的 `~/.claude.json`，照「[安裝步驟 § 2](#2-claude-code-端一次設定全機通用)」貼設定
3. 各 Unity 專案的 `Packages/manifest.json` 加 dependency（每專案一次）
4. 重啟 Claude Code session

---

## 參考

- 上游：https://github.com/CoplayDev/unity-mcp
- Skill 操作指引：`~/.claude/skills/unity-mcp-skill/SKILL.md`
- 工作流 atom：`~/.claude/memory/unity-mcp-自動化工具鏈.md`
