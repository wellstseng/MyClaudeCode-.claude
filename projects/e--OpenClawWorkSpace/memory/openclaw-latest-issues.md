# Atom: OpenClaw 官方文件與最新版本問題

- Scope: project
- Confidence: [觀]
- Source: 2026-03-05 官方文件 docs.openclaw.ai + GitHub releases 掃描
- Last-used: 2026-03-05
- Confirmations: 0
- Type: reference
- Tags: openclaw, 官方文件, 版本, issues, troubleshooting
- Trigger: OpenClaw 官方文件, 最新版本, breaking changes, 升級問題, 已知問題, 故障排除, openclaw doctor, 版本差異, release notes
- Related: openclaw-self-iteration.md, openclaw-architecture.md, pitfalls.md
- Privacy: public

## 知識

### 版本時間線（2026.2-3 月）

| 版本 | 日期 | 重點 |
|------|------|------|
| 2026.2.23 | 2026-02 | — |
| 2026.2.26 | 2026-02-27 | 外部密鑰管理、ACP 線程代理、Codex WebSocket 傳輸 |
| 2026.3.1 | 2026-03-02 | Android 節點擴展、Discord 執行緒綁定、Telegram DM 主題、Web UI i18n |
| 2026.3.2 | 2026-03-03 | Secrets/SecretRef 覆蓋、PDF 分析工具、CLI 設定驗證 |
| 2026.3.3 | (main) | 開發中 |

**本地安裝版本**: 2026.3.2（確認於 MEMORY.md）

### v2026.3.2 Breaking Changes

1. **tools.profile 預設改為 `messaging`**（新安裝）— 非編碼工具預設不開
2. **ACP dispatch 預設啟用** — 可能影響 agent routing 行為
3. **Plugin SDK 移除 `api.registerHttpHandler()`** — 自訂 HTTP handler 需遷移
4. **Zalo Personal 外掛不再依賴外部 CLI** — 簡化部署

### 官方故障排除重點（本地未記錄過的）

| 問題 | 原因 | 解法 |
|------|------|------|
| Anthropic 429 錯誤 | context1m flag 或帳單未設定 | 停用 `context1m`，加 billing |
| 長 context 被拒 | credential 不支援 1M token beta | 確認 API key 等級 |
| 非 loopback 綁定需認證 | 3.x 安全強化 | 遠端存取需加 auth |
| Dashboard 設備身份缺失 | 未 pair 的裝置 | `openclaw pairing` 重新配對 |
| Discord 語音解密失敗 | discord.js 上游問題 | `daveEncryption=true` + 重新加入 |
| Discord bot 迴圈 | `allowBots=true` 觸發 | 嚴格 mention 規則或移除 allowBots |
| Discord 事件逾時 | listenerTimeout 太短 | `eventQueue.listenerTimeout=120000` |
| LINE markdown 被移除 | LINE 平台限制 | 無法解決，僅傳純文字 |
| LINE 5000 字元上限 | 平台限制 | 自動分塊傳送 |
| 類型指示符卡住 | 已知 bug（3.1 修復） | 升級到 3.2 |
| Telegram 傳送失敗重試迴圈 | 3.1 已知 bug | 升級到 3.2 |
| 暫存目錄權限 | umask 不相容 | 3.2 已修復 |

### 官方 Memory 系統（非我們的自訂版本）

官方內建 Memory 使用 SQLite + 向量搜尋：
- **預設後端**: `~/.openclaw/memory/<agentId>.sqlite`
- **混合搜尋**: 70% vector + 30% BM25（可配置）
- **時間衰減**: 半衰期 30 天（可配置）
- **MMR 去重**: 降低冗餘結果
- **QMD 實驗**: Bun sidecar，不需 Ollama

**與我們的差異**: 我們用自訂 preprocessor + LanceDB + 18 演算法，比官方系統複雜得多。官方系統是 agent 直接呼叫 `memory_search` / `memory_get` 工具。

### 官方 Hooks vs 我們的 Hooks

| 項目 | 官方 Hooks | 我們的自訂 Hooks |
|------|-----------|----------------|
| 格式 | HOOK.md + handler.ts | preprocessor/lib/*.js |
| 事件 | message:received/preprocessed/sent | message:before（自訂事件） |
| 發現 | workspace/hooks/ + ~/.openclaw/hooks/ | .openclaw/workspace/preprocessor/ |
| 註冊 | openclaw.json hooks.internal.entries | preprocessor/config.json algorithms |

兩套共存：官方 hooks 在 Gateway 層，我們的在 workspace preprocessor 層。

### 官方 Workspace 結構（供對照）

```
~/.openclaw/workspace/
├── AGENTS.md      — 行為指令（= 我們的 AGENTS.md）
├── SOUL.md        — 人格定義
├── USER.md        — 使用者身份
├── IDENTITY.md    — agent 名稱
├── TOOLS.md       — 工具說明
├── HEARTBEAT.md   — 心跳 checklist
├── BOOT.md        — 啟動 checklist
├── memory/        — 日誌 + MEMORY.md
├── hooks/         — 自訂 hooks
└── skills/        — 技能覆寫
```

### 官方文件結構（400+ 頁）

- **核心概念**: architecture, agent-loop, agent-workspace, memory, messages, session
- **通道**: 28+ 平台（WhatsApp, Telegram, Discord, Slack, Signal, iMessage, LINE, Matrix...）
- **自動化**: hooks, cron-jobs, webhooks, polls, heartbeat
- **Provider**: 30+ 模型提供商（OpenAI, Anthropic, Ollama, Mistral, OpenRouter...）
- **部署**: Docker, Fly.io, GCP, Ansible, Nix, Node.js
- **CLI**: 50+ 命令

### 升級安全流程（官方建議）

```bash
# 升級
curl -fsSL https://openclaw.ai/install.sh | bash  # 或 npm i -g openclaw@latest

# 驗證
openclaw doctor     # 修復 + 遷移 + 健檢
openclaw gateway restart
openclaw health

# 回滾
npm i -g openclaw@<舊版本>
openclaw doctor
openclaw gateway restart
```

### 社群資源

- 官方文件: https://docs.openclaw.ai
- LLM 友好文件: https://docs.openclaw.ai/llms.txt
- Discord 社群: https://discord.gg/clawd
- GitHub: https://github.com/openclaw/openclaw

## 行動

- 升級前：查本 atom 的 breaking changes 列表，確認是否影響我們的自訂設定
- 故障排除時：先跑 `openclaw doctor` + `openclaw channels status --probe`
- 我們的自訂系統（preprocessor/hooks）與官方系統獨立，升級通常不影響
- 但 Gateway 核心升級可能改變事件格式 — 測試 message:before hook 是否正常
- 版本資訊過時時：重新掃描 https://github.com/openclaw/openclaw/releases 更新本 atom

## 演化日誌

| 日期 | 動作 |
|------|------|
| 2026-03-05 | 初建：掃描 docs.openclaw.ai + GitHub releases v2026.2.23~3.2 |
