# Install-forAI — Claude Code 自訂擴充快速安裝指南

> **讀者：另一台電腦上的 Claude Code AI 助手**
> 此文件設計為 AI 可讀格式。請逐步執行以下操作，將本 repo 的自訂擴充合併到目標機器的 `~/.claude/` 中。

---

## 前置條件

### 必要（基本功能）
- Claude Code 已安裝且可正常運作
- Python 3.8+（hooks 需要）
- Node.js 18+（MCP server 需要）
- `~/.claude/` 目錄已存在（Claude Code 首次啟動會自動建立）

### 必要（V2 向量搜尋）
- Python 3.10+（LanceDB 需要）
- Ollama 已安裝（embedding + local LLM）
- NVIDIA GPU with CUDA（推薦，CPU 也可但較慢）

---

## 安裝步驟

### Step 1: 複製自訂檔案

將以下檔案/目錄從 repo 複製到 `~/.claude/`：

```
hooks/workflow-guardian.py            → ~/.claude/hooks/workflow-guardian.py
tools/workflow-guardian-mcp/          → ~/.claude/tools/workflow-guardian-mcp/
tools/memory-vector-service/          → ~/.claude/tools/memory-vector-service/
tools/rag-engine.py                   → ~/.claude/tools/rag-engine.py
workflow/config.json                  → ~/.claude/workflow/config.json
commands/init-project.md              → ~/.claude/commands/init-project.md
memory/SPEC_Atomic_Memory_System.md   → ~/.claude/memory/SPEC_Atomic_Memory_System.md
_AIDocs/                              → ~/.claude/_AIDocs/  (可選，僅作參考)
```

**不要覆蓋**：
- `memory/MEMORY.md` — 每台機器有自己的記憶索引
- `memory/decisions.md` — 包含機器特有的決策記錄
- `memory/preferences.md` — 可參考但應由使用者確認

### Step 2: 安裝 Python 依賴

```bash
# V2 向量搜尋依賴
python -m pip install lancedb sentence-transformers
```

> **注意**：在 Git Bash 中 `pip` 可能不在 PATH，請使用 `python -m pip install`。

### Step 3: 安裝 Ollama 及模型

```bash
# 1. 安裝 Ollama
#    Windows: https://ollama.com/download/windows
#    macOS: https://ollama.com/download/mac
#    Linux: curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型
ollama pull qwen3-embedding      # embedding 主力 (~1.2GB, MTEB 多語言 #1)
ollama pull qwen3:1.7b            # 本地 LLM for Phase 3 (~1.5GB)
```

> **GPU VRAM 需求**：
> - qwen3-embedding: ~1.5GB
> - qwen3:1.7b: ~2GB
> - 最低建議 4GB VRAM（分時使用，不會同時佔用）
> - 無 GPU 時自動 CPU fallback（速度慢 3-5x 但可用）

### Step 4: 合併 CLAUDE.md

讀取 repo 中的 `CLAUDE.md`，**合併**（非覆蓋）到目標機器的 `~/.claude/CLAUDE.md`：

- 第一～四區塊（_AIDocs 知識庫、原子記憶、工作結束同步、對話管理）→ 直接採用
- 第五區塊（使用者偏好）→ 應由使用者確認是否適用

### Step 5: 合併 settings.json — hooks 區段

讀取目標機器的 `~/.claude/settings.json`，在 JSON 中新增或合併 `hooks` 欄位：

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 3 }] }],
    "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 3 }] }],
    "PreCompact": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5 }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "python \"$HOME/.claude/hooks/workflow-guardian.py\"", "timeout": 5, "async": true }] }]
  }
}
```

**注意**：若目標機器已有 `hooks`，需手動合併而非覆蓋。

### Step 6: 合併 MCP server 註冊

在 `~/.claude.json`（注意：在 HOME 目錄，不在 `~/.claude/` 裡）的 `mcpServers` 中新增：

```json
{
  "workflow-guardian": {
    "type": "stdio",
    "command": "node",
    "args": ["{{HOME_PATH}}/.claude/tools/workflow-guardian-mcp/server.js"],
    "env": {}
  },
  "computer-use": {
    "type": "stdio",
    "command": "cmd",
    "args": ["/c", "npx", "-y", "computer-use-mcp"],
    "env": {}
  }
}
```

`{{HOME_PATH}}` 替換為目標機器的 HOME 絕對路徑（Windows: `C:\\Users\\USERNAME`，macOS/Linux: `/home/USERNAME`）。

> **MCP 傳輸格式警告**
>
> Claude Code v2.x 使用 **JSONL** 傳輸格式（每行一個完整 JSON，以 `\n` 分隔），而非 LSP 風格的 Content-Length header。自寫 MCP server 必須：
> - 以 JSONL 格式收發訊息（`{...}\n`）
> - `protocolVersion` 設為 `2025-11-25`
> - 違反上述格式將導致 30 秒超時 → `/mcp` 顯示 failed
>
> Windows 上使用 npx 的 MCP server 需加 `cmd /c` wrapper（如上方 computer-use 範例）。

### Step 7: 合併 settings.json — permissions 區段（可選）

以下權限與 Workflow Guardian 無直接關係，屬於使用者個人偏好。目標使用者可參考後自行決定：

```json
{
  "permissions": {
    "allow": [
      "Bash(svn status:*)", "Bash(svn diff:*)", "Bash(svn log:*)",
      "Bash(svn info:*)", "Bash(svn revert:*)",
      "Bash(git config:*)", "Bash(git commit:*)", "Bash(git push)",
      "Bash(git add:*)", "Bash(git init)", "Bash(git remote add:*)",
      "Bash(dotnet build:*)"
    ]
  }
}
```

### Step 8: 初始化記憶索引

若目標機器的 `~/.claude/memory/MEMORY.md` 尚未存在，建立最小版本：

```markdown
# Atom Index — Global

> 每個 session 啟動時，先讀此索引。
> 比對使用者訊息的 Trigger 欄，命中 → Read 對應 atom 檔。

| Atom | Path | Trigger |
|------|------|---------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, guardian, hooks |

---

## 高頻事實

- 使用者: {{USERNAME}} | 回應語言: 繁體中文
- [固] Workflow Guardian: hooks 驅動工作流監督 + Dashboard @ localhost:3848
- [固] 原子記憶 V2：Hybrid RECALL（keyword + vector semantic search）@ localhost:3849
```

### Step 9: 建立向量索引

```bash
# 確認 Ollama 正在運行
ollama list

# 啟動 Vector Service daemon
python ~/.claude/tools/rag-engine.py start

# 建立全量索引（首次需要幾分鐘，取決於 atom 數量和 GPU 速度）
python ~/.claude/tools/rag-engine.py index

# 驗證
python ~/.claude/tools/rag-engine.py status
python ~/.claude/tools/rag-engine.py search "test query"
```

### Step 10: 驗證

重啟 Claude Code（VS Code: `Ctrl+Shift+P` → `Reload Window`），然後：

1. 執行 `/mcp` — 確認 `workflow-guardian` 狀態為 **connected**
2. 開啟 `http://127.0.0.1:3848` — 應看到 Dashboard
3. 編輯任意檔案 → Dashboard 應出現新 session 卡片
4. 嘗試結束對話 → Guardian 應阻止並提醒同步
5. 確認 Vector Service 運行：`python ~/.claude/tools/rag-engine.py health`
6. 確認語意搜尋：`python ~/.claude/tools/rag-engine.py search "測試"`

---

## Placeholder 清單

安裝時需替換的佔位符：

| Placeholder | 說明 | 範例 |
|-------------|------|------|
| `{{HOME_PATH}}` | 使用者 HOME 絕對路徑 | `C:\\Users\\john` 或 `/home/john` |
| `{{USERNAME}}` | 使用者名稱 | `john` |

---

## Fallback 機制

V2 向量搜尋設計為 graceful degradation：

| 情境 | 行為 |
|------|------|
| Ollama 未安裝 | embedding fallback 到 sentence-transformers (bge-m3) |
| Ollama 未啟動 | 同上 |
| sentence-transformers 也沒裝 | 純 keyword 模式（V1 行為） |
| Vector Service daemon 未啟動 | 純 keyword 模式（V1 行為） |
| GPU 不可用 | CPU fallback（慢 3-5x 但可用） |

**任何環節故障都不會影響 Claude Code 正常運作**，只是語意搜尋功能不可用。

---

## 系統概述（供 AI 理解上下文）

本擴充包含兩個核心系統，透過 7 個階段（BOOT → RECALL → TRACK → REMIND → COMPACT → GATE → SYNC）管理 session 生命週期：

1. **原子記憶 V2**：跨 session 知識管理，兩層（全域/專案）、三級分類（[固]/[觀]/[臨]），Hybrid RECALL（keyword + vector semantic search），本地 LLM 增強（查詢改寫、re-ranking、知識萃取）
2. **Workflow Guardian**：hooks 事件驅動的工作流監督，自動追蹤修改、阻止未同步結束、提供 Dashboard 監控

MCP 傳輸格式：JSONL（`{...}\n`），protocolVersion `2025-11-25`。

詳見 `README.md`（運作流程圖）、`_AIDocs/Architecture.md` 和 `memory/SPEC_Atomic_Memory_System.md`。
