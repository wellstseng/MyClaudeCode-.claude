# Claude Code Source 參照

- Scope: global
- Confidence: [固]
- Trigger: Claude Code, claudecode, claude code 架構, context 管理, token 控制, session 處理, 安全邊界
- Last-used: 2026-04-11
- Confirmations: 60

## 知識

- [固] Claude Code source 路徑：`/Users/wellstseng/project/claudecode/`
- [固] 關鍵目錄：`context/`（context 管理）、`coordinator/`（任務協調）、`history.ts`（歷史）、`bridge/`（外部橋接）、`commands/`（指令）、`assistant/`（SDK session 歷史，非 prompt 組裝）、`constants/prompts.ts`（system prompt 組裝）
- [固] 學習模式：遇到 CatClaw 架構決策（context 管理、token 控制、安全邊界、session 處理），主動帶出「Claude Code 怎麼做」對比，讓 Wells 邊做邊學

## 行動

遇到 CatClaw 相關架構決策時，先查 claudecode/ 對應模組，再提供「CC 做法 vs CatClaw 現況 vs 建議」三欄對比
