# Claude Code Feature Inventory

- Scope: global
- Confidence: [固]
- Trigger: feature flag, feature gate, GrowthBook, hidden feature, 隱藏功能, coordinator mode, KAIROS, daemon mode, bridge mode, BUDDY, ULTRAPLAN, agent triggers, cron, team memory, hidden CLI, 環境變數, claude server, 未公開功能
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-agent-orchestration, cc-prompt-engineering

## 知識

### 三層隱藏機制
- [固] 編譯時 feature flags（bun:bundle → 死碼消除）
- [固] Runtime GrowthBook feature gates（15+ 使用者維度）
- [固] Commander.js .hideHelp()（CLI 隱藏參數）
- [固] checkStatsigFeatureGate_CACHED_MAY_BE_STALE()：磁碟快取讀取，零啟動延遲

### 主要未公開功能
- [固] Coordinator Mode：主 session 變純協調器，Worker agents 執行（CLAUDE_CODE_COORDINATOR_MODE=1）
- [固] KAIROS（Daemon Mode）：Claude Code 從互動 REPL 變事件驅動背景服務
- [固] Bridge Mode（Remote Control）：透過 CloudControl Relay 遠端控制，需 claude.ai OAuth
- [固] BUDDY：終端 UI 角色系統，RPG 稀有度，seeded PRNG（同 userId+SALT 跨 session 一致）
- [固] ULTRAPLAN/ULTRATHINK：遠端 Anthropic 基礎設施規劃，用 Opus 模型，30 分鐘 timeout
- [固] Agent Triggers（Cron）：cron 排程自動任務，.claude/scheduled_tasks.json，避免 :00/:30（流量分散）
- [固] Workflow Scripts：宣告式多步驟工作流（類 GitHub Actions）
- [固] Team Memory：雙向同步跨團隊知識，scanForSecrets() 防洩漏，刪除不傳播

### 隱藏 CLI 參數（30+）
- [固] 多 Agent：--advisor, --worktree, --tmux, --agent-teams, --teammate-mode, --agent-id/name/color
- [固] 除錯：--plan-mode-required, --rewind-files, --resume-session-at, --include-hook-events, --parent-session-id
- [固] 模型控制：--effort, --thinking, --max-turns, --max-budget-usd
- [固] 認證：--system-prompt-file, --permission-prompt-tool, --enable-auto-mode

### 環境變數
- [固] Feature Toggles：CLAUDE_CODE_COORDINATOR_MODE, CLAUDE_CODE_SIMPLE, CLAUDE_CODE_REMOTE, CLAUDE_CODE_ENABLE_TASKS
- [固] Disable Flags：CLAUDE_CODE_DISABLE_FAST_MODE, CLAUDE_CODE_DISABLE_THINKING, CLAUDE_CODE_DISABLE_CRON
- [固] Debug：CLAUDE_CODE_DUMP_SYSTEM_PROMPT, CLAUDE_CODE_PROFILE_STARTUP, VCR_RECORD
- [固] Model Overrides：ANTHROPIC_DEFAULT_OPUS_MODEL, ANTHROPIC_DEFAULT_SONNET_MODEL, CLAUDE_CODE_API_BASE_URL

### 隱藏 Server Commands
- [固] `claude server`：REST API 管理多個平行 session（--port, --host, --auth-token, --unix, --max-sessions）
- [固] `claude ssh`：SSH 遠端執行，I/O bridge 到本地終端
- [固] `claude remote-control`/`claude rc`：Bridge Mode 客戶端

## 行動

- 開發進階工具時可利用隱藏 CLI 參數（如 --max-turns, --effort）
- Agent Triggers 適合 CI/CD 自動化場景
- `claude server` 可用於避免 cold-start 的 pipeline 整合
- 來源：https://claude-code-harness-blog.vercel.app/chapters/12-feature-inventory/
