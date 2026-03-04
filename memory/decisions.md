# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工作流, workflow, 設定, config, 記住, MCP
- Last-used: 2026-03-04
- Confirmations: 9

## 知識

- [固] 版控同步支援 Git 和 SVN，自動偵測 .git/ 或 .svn/
- [固] MCP servers 實際可用: playwright, openclaw-notify, workflow-guardian, computer-use
- [固] computer-use 正確套件名: `computer-use-mcp`（社群維護），需 Node 22 LTS 執行（jimp ESM 在 Node 24 上壞掉）
- [固] Node 22 LTS 可攜版安裝在 `~/.claude/tools/node22/node-v22.14.0-win-x64/`，專給 computer-use-mcp 使用
- [固] browser-use 已從 .claude.json 移除（需付費 API key），Playwright 已覆蓋瀏覽器自動化
- [固] OpenClaw 的 atoms/ 目錄僅歸屬 OpenClaw，不作為 Claude Code 全域 atom 來源
- [固] Workflow Guardian：hooks 事件驅動的工作流監督系統，自動追蹤修改、Stop 閘門阻止未同步結束、Atom Last-used 自動刷新
- [固] session ID 支援 prefix match（截短 8 碼即可操作 workflow_signal 等工具）
- [固] sync_completed 信號自動清空 knowledge_queue + modified_files，並寫入 `ended_at` 供 auto-cleanup 使用
- [固] **Session state auto-cleanup 三層策略**：Tier 1（有 ended_at，1min TTL）、Tier 2（orphan done 無 ended_at，30min）、Tier 3（stale working，24h）。TTL 可在 `config.json` 的 `cleanup` 區塊調整
- [固] SessionEnd hook `async: true` 導致 `ended_at` 從未被 Python hook 寫入；靠 sync_completed 信號補寫 + 三層 fallback 解決
- [固] 工作結束同步須根據情境判斷適用步驟（有 _AIDocs 才更新 _CHANGELOG，有 .git/.svn 才版控）
- [固] **MCP stdio 傳輸格式**: Claude Code v2.x 使用 JSONL（`{...}\n`），不是 Content-Length header。自寫 MCP server 必須用 JSONL + protocolVersion `2025-11-25`，否則 30 秒超時 failed
- [固] **Dashboard v2.1**: Tabbed UI（Sessions/Episodic/Health/Tests/Vector），API: /api/episodic, /api/health, /api/test-run, /api/vector-status, /api/knowledge-queue
- [固] Node.js `exec` > `execFile` on Windows：`execFile` 找不到 Python（WindowsApps stub），`exec` 透過 shell 可正常解析 PATH；路徑需用正斜線避免反斜線被 shell 當逸出字元
- [固] **Promotion hint (v2.1.1)**：atom 注入時若 Confirmations 達門檻（[臨]≥2→[觀]、[觀]≥4→[固]），自動在 context 附提醒，讓 Claude 主動確認是否晉升。已驗證通過（todo.md [觀]→⚡hint）
- [臨] **Episodic atoms 不列 MEMORY.md 索引**：TTL 短（24d）且 vector search 可召回，列索引會撐爆 30 行限制。待改 hook 的 `_generate_episodic_atom()` 跳過索引插入

## 行動

- 工作結束同步時，先判斷情境（_AIDocs? .git? .svn?），只提及適用的步驟
- 同步完成後透過 MCP `workflow_signal("sync_completed")` 通知 Guardian 解除閘門
- 自行開發 MCP server 時，用 JSONL 格式收發，不要用 Content-Length header
