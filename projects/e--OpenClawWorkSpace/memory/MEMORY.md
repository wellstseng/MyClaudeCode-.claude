# Atom Index — OpenClaw Project

> 工作目錄: `E:\OpenClawWorkSpace` | 版本: 2026.3.2
> 配置: `.openclaw\openclaw.json`（需 OPENCLAW_CONFIG_PATH）
> GitHub: `holylight1979/OpenClaw-AtomicMemory` + `OpenClawPanel`

| Atom | Path | Trigger |
|------|------|---------|
| decisions | memory/decisions.md | 修改 OpenClaw 配置, 安裝升級, 安全策略, ngrok 啟動, Discord 設定, LINE 設定, sandbox, Gateway auth |
| pitfalls | memory/pitfalls.md | 錯誤訊息, 異常行為, 啟動失敗, 設定不生效, 沒有回應, 連不上, Discord bot, webhook 失敗, ngrok error, 404, 502 |
| bridge | memory/bridge.md | Bridge 服務, Claude Code 整合, LINE→Claude, port 3847, inbox, to-claude, to-openclaw |
| openclaw-config-intelligence | memory/openclaw-config-intelligence.md | 修改 openclaw.json, 新增 channel/group, 設定不生效除錯, 參數依賴關係 |
| openclawdesktop | memory/openclawdesktop.md | 桌面自動化 MCP, 截圖, UI Automation, SendInput, DPI, desktop automation, OpenClawDesktop |
| desktop-workflow | memory/desktop-workflow.md | 操作畫面, 切換視窗, 監測 session, GUI 自動化 |
| gateway-controlui-routing | memory/gateway-controlui-routing.md | controlUi 路由, Dashboard Not Found, 405, SPA catch-all, basePath, 升級 2026.3.2, LINE webhook 404 |
| gateway-chat-send-routing | memory/gateway-chat-send-routing.md | chat.send, LINE 推送, cross-context messaging, session routing, deliverOutboundPayloads, OriginatingChannel |
| consciousness-stream | memory/consciousness-stream.md | 識流, 意識流, 透過識流, 八識, 轉識成智, 高風險任務, 跨系統任務 |
| openclaw-architecture | memory/openclaw-architecture.md | OpenClaw 架構, 運作流程, Gateway 管線, preprocessor 管線, 演算法, 降級, 服務拓撲 |
| openclaw-setup-guide | memory/openclaw-setup-guide.md | 安裝 OpenClaw, 啟動 Gateway, 環境設定, 首次設定, 重新部署, 服務啟停, start-gateway |
| openclaw-taxonomy | memory/openclaw-taxonomy.md | 人事時地物, 五大分類, taxonomy, 分類系統, categories.json, 子分類, atomPaths |
| openclaw-self-iteration | memory/openclaw-self-iteration.md | 升級 OpenClaw, 版本管理, config merge, plugin 管理, 自我除錯, 迭代, 維護 |
| openclaw-latest-issues | memory/openclaw-latest-issues.md | OpenClaw 官方文件, 最新版本, breaking changes, 升級問題, 已知問題, 故障排除, openclaw doctor, release notes |

---

## 高頻事實

- [固] Gateway: port 18789 (WS+webhook), 18791 (Browser), 18792 (CDP)。啟動: `start-gateway.bat`
- [固] 雙記憶共存: V2.3 (Claude Code, Python, ChromaDB) + Preprocessor (Gateway agent, Node.js, LanceDB)
- [固] 雙向通訊: CC→OC (gateway-chat.js, ws://127.0.0.1:18789/ws) | OC→CC (inbox.jsonl + inbox-check.js)
- [固] LLM: OpenAI Codex OAuth (gpt-5.3-codex) + Ollama qwen3 (1.7b/0.6b embedding/0.6b reranker)
- [固] 平台: Discord (groupPolicy=open) + LINE (ngrok + traffic-policy) + Bridge (port 3847)
- [固] 人事時地物: Gateway preprocessor 五大分類 (taxonomy/categories.json, 30 子分類)
