---
name: feedback_upload_discord
description: 使用者說「上傳MD」「傳附件」「壓縮傳我」時，自動寫檔並輸出 MEDIA token 上傳 Discord
type: feedback
---

當使用者說「上傳MD給我」、「存成MD傳我」、「壓縮傳我」、「上傳檔案」、「附件給我」等語句時，不需要詢問確認，直接執行：

1. 判斷適合的格式（`.md`、`.py`、`.csv`、`.zip` 等）
2. 用 Write 工具寫入 `/tmp/{合適的檔名}`
3. 在回覆中輸出 `MEDIA: /tmp/{檔名}`，Discord bot 自動攔截並上傳

**Why:** 使用者已建立 Discord bot 的 MEDIA token 上傳機制，每次確認流程太慢。

**How to apply:** 凡涉及「上傳」「傳附件」「壓縮傳」字眼，且當前環境是 Discord session（或不確定），直接走 MEDIA token 流程。不需問「要怎麼上傳」。
