# Discord 附件上傳流程

- Scope: global
- Confidence: [固]
- Trigger: 上傳, 傳附件, 壓縮傳, upload, MEDIA, Discord 附件
- Last-used: 2026-03-30
- Confirmations: 13
- Related: preferences

## 知識

- [固] 使用者說「上傳MD給我」「存成MD傳我」「壓縮傳我」「上傳檔案」「附件給我」時，不需詢問確認，直接執行
- [固] 流程：判斷格式 → Write 寫入 `/tmp/{檔名}` → 回覆輸出 `MEDIA: /tmp/{檔名}`
- [固] Discord bot 自動攔截 MEDIA token 並上傳
- [固] 支援格式：.md、.py、.csv、.zip 等

## 行動

- 凡涉及「上傳」「傳附件」「壓縮傳」字眼，直接走 MEDIA token 流程，不問「要怎麼上傳」
