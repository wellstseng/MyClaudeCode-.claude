# Obsidian Vault 位置

- Scope: global
- Confidence: [固]
- Type: reference
- Trigger: obsidian, vault, WellsDB, 筆記庫, 寫到obsidian, 放到obsidian, 輸出obsidian
- Related: preferences

## 知識

- [固] **Obsidian vault 根目錄：`~/WellsDB/`**（本機資料夾，**非 iCloud 同步**）
- [固] 既有子目錄分類：`AI應用經驗彙整/`、`AI進修/`、`CatClaw工具規格/`、`CatClaw議題追蹤/`、`工作日誌/`、`工作簿/`、`投資分析/`、`漫畫/`、`生活記事/`、`知識庫/`、`計畫與報告/`、`人生經驗/`、`封存/`
- [固] 命名慣例：檔名前綴日期 `YYYY-MM-DD_主題.md`（範例：`2026-05-19_這半年AI應用經驗彙整.md`）

## 反例（不要踩）

- [固] `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/` **不是**使用者用的 vault；該路徑被 macOS TCC 擋 `ls` 但 `cp`/`Write` 可寫，容易誤判為「成功放進 vault」
- [固] Windows 端 `C:\Users\wellstseng\Obsidian\` 是另一台機器的本機路徑，與 mac 端 `~/WellsDB/` 不同步

## How to apply

- 使用者說「放到 Obsidian / 輸出到 Obsidian / 寫到 vault」→ 預設目標是 `~/WellsDB/{對應子目錄}/`
- 不確定主題對應哪個子目錄時，先 `ls ~/WellsDB/` 看現有分類，沿用既有目錄，不要自建新目錄
