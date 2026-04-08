# AI 自主開發實驗協作模式

- Scope: global
- Confidence: [觀]
- Trigger: AI自主開發, AI自主, Sprint自主, 協作實驗, harness agent, subagent協作, PM角色, AI當開發, 啟動協作實驗, 協作模式
- Last-used: 2026-04-09
- Confirmations: 21

## 知識

- [觀] 完整教程文件位置：`~/.claude/collab/AI-Human-Collaboration-Guide.md`（v1.1，含 Sprint 3 規則）
- [觀] 角色分工：Wells = PM（需求/方向/驗收）；Claude = 開發者（目標搜尋/subagent 調度/實作/測試）
- [觀] 標準啟動語：「Sprint X 開始，目標：{目標說明}，你自主搜尋目標後回報我再開始」
- [觀] 溝通頻道：Discord PM 頻道 1485277764205547630
- [觀] 核心規則：**事前事中事後三段回報** + 每目標完成後報 token 用量（從 `<usage>total_tokens</usage>` 讀取）
- [觀] 5+ agent 標準配置：Design / Security / Dev / QA / Test
- [觀] 安全邊際：綠區自主 / 黃區告知後執行 / 紅區必須等人類確認
- [觀] 測試頻道：1484061896217858178
- [觀] 協作知識庫：`~/.claude/collab/`（版控於 HomeClaudeCode-.claude）
- [觀] 中斷接回：每個目標 Design 完成後存 `_staging/next-phase.md`，新 session 讀此檔接續
- [觀] Context 自管：使用率 >70% 時完成當前目標 → commit → 提醒 PM 開新 session
- [觀] 壓縮續接規則（唯一允許壓縮的情境）：自主開發時若 context 接近上限，可進行壓縮，但必須產好續接 prompt（含完整狀態）並重新貼一次，避免漏訊喪失記憶。具體做法：完成當前目標 → commit → 產出 `_staging/next-phase.md` 續接檔 → 壓縮或開新 session → 讀續接檔接續
- [觀] 每階段報告規則：每個目標/階段完成後，必須產出 md 報告檔（放 `_staging/`），回報給 PM。報告內容需完整詳細：做了什麼、為什麼做、花了多少時間、如何做、潛在問題、怎麼測試、測試結果——越詳細越好

## Sprint 3 全部完成（2026-04-02）

- ✅ B1+B2：session:end 接線 + consolidate 排程（cb206c6）
- ✅ C11+C10+C8：mention 過濾 + config 備份 + web 監控（f55c115）
- ✅ C1：Tool 超時保護（9dbd79d）
- ✅ C2：Session checksum（b877836）
- ✅ C3：Turn-level metrics（52efe1a）
- ✅ C4：Subagent dependency tracking + cascade abort（d9fb264）
- ✅ C5：訊息中止流程 + queue 清空（bd7a2ac）
- ✅ C7：web_fetch + web_search 工具移植（17e156e）

## Phase 2 狀態

- [觀] Phase 2 大目標：CatClaw 自治管理（自主開發能力）— 基礎功能齊備
- [觀] CatClaw 現有工具：spawn_subagent, read/write/edit/glob/grep/run_command, web_fetch, web_search, memory_recall, config-get/patch, subagents
- [觀] 下一步方向：自治開發指揮流程（讓 CatClaw 自己能跑 Sprint）

## 行動

- 收到「啟動 Sprint X 自主開發」→ 讀指南 + 讀 `_staging/next-phase.md` 確認接續狀態
- 開工前必須先向 Wells 回報目標清單 + agent 分工計畫，不可直接動手
- 每個目標：事前 → 事中（每 agent 完成時）→ 事後（含 commit + token 合計）
- 測試必做：每個目標完成後在測試頻道（1484061896217858178）測試，回報測試方式
- 自主執行時：Wells 說「做到完」→ 無需詢問，執行完整 backlog 後才彙報
