---
name: backlog-optimization
description: 待優化項目清單 — CatClaw 排程系統、自主重啟等功能的進度追蹤
type: project
---

## 已完成

1. **Signal file 重啟機制** — PM2 監聽 signal/ 目錄，寫入 RESTART 觸發重啟（2026-03-20）
2. **重啟回報** — 重啟後自動在觸發頻道發通知，帶 channelId（2026-03-20）
3. **錯誤分類** — acp.ts 區分 overloaded/502/rate limit/timeout 等（2026-03-20）
4. **Cron 排程模組** — croner 驅動，支援 cron/every/at 三種模式（2026-03-20）
5. **Cron job 獨立存放 + hot-reload** — 定義+狀態合併在 data/cron-jobs.json，config.json 只留全域開關，fs.watch() 存檔即生效（2026-03-20）

## 待處理

1. **排程 Runtime CRUD** — 暫停中。目前 job 透過編輯 cron-jobs.json 管理，無 Discord 指令介面
2. **自主重啟** — 服務能自行偵測異常並重啟

**Why:** 使用者 2026-03-20 提出，排程系統和自動重啟為近期優化方向。
**How to apply:** Runtime CRUD 需決定介面（Discord 指令？API？）；自主重啟待排程穩定後再做。
