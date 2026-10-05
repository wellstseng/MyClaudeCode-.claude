# wells-workflow-multi-llm-ledger

- Scope: global
- Author: wells
- Confidence: [觀]
- Trigger: 多 agent, 多 LLM, 平行協作, 任務分派, subagent, claim, 範圍認領, Doomsday Phase2
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: decisions, workflow-rules

## 知識

- [觀] 多 LLM / 多 agent 平行協作的最低成本同步機制是「**人類看得懂的純文字 ledger**」——用 Markdown 文件當共享 task table
- [觀] 證據：Doomsday Phase2 機械翻譯時 Claude / Codex / Gemini 平行翻譯混淆碼，用 `Doomsday_Phase2_Progress.md` 當共享 ledger，每個 LLM 自己 claim / release 範圍，避免重複翻譯同一 namespace
- [觀] 機制好處：不需要中央 coordinator、不需要 lock 機制、人類隨時看得到誰在做什麼、誰落後

## 行動

- Why：分散式系統的 coordination 通常用 lock / queue / message bus，但多 LLM 場景下 LLM 之間沒有低延遲通訊，且使用者也需要可視性——Markdown ledger 同時解決協調 + 觀測
- How to apply：
  - 多 agent 要平行做同類任務（翻譯範圍、檔案處理、PR review）→ 先建一份 `XXX_Progress.md` ledger
  - Ledger 內容：任務清單 + 認領者 + 狀態 + commit hash（已完成時）+ 備註
  - 每個 agent 開工前必讀 ledger、claim 後寫入、完工後 commit 連 ledger 更新一起 push
  - 反模式：用 SQLite 或 redis 當 task table——LLM 不會主動 poll，且使用者看不到
