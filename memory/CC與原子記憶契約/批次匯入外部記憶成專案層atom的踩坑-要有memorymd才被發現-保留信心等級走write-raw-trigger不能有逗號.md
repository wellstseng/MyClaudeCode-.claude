# 批次匯入外部記憶成專案層atom的踩坑-要有MEMORY.md才被發現-保留信心等級走write-raw-trigger不能有逗號

- Scope: global
- Author: wellstseng
- Source: 取代 local 卡「CatClaw 遷移到 Claude Code 的落點與踩坑」的通用部分；session fbcd954e 2026-11-15
- Confidence: [臨]
- Trigger: 批次匯入 atom, 專案記憶匯入, 外部記憶遷移, tool:migrate, MEMORY.md 發現, trigger 逗號, scope_drift, 差量再匯入
- Created-at: 2026-11-14
- Quote: 「直接跳過改新環境跑」

## 知識

- [臨] 專案記憶要被 `discover_all_project_memory_dirs` 發現，必須有 `.claude/memory/MEMORY.md`（帶 `<!-- AUTO-GENERATED: V4 role filter -->` 檔頭，SessionStart 會接手重生）；光有 `_atom_index.json` 不夠。
- [臨] 批次匯入要保留 [固]/[觀] 不能走 write_atom（create 只收 [臨]），改自組內容走 `write_raw` + `atom_access.init_access/write_access_field` + `write_index`，source 用 `tool:migrate`，每個回傳值都要檢查 `.ok`。
- [臨] trigger 內不能有逗號：檔頭以逗號分隔，金額的千分位會被切開造成檔頭與索引漂移；匯入前先去掉。
- [臨] `sync-atom-index.py --memory-dir <專案>` 會把每顆報成 scope_drift（write_index 對專案層一律寫 scope=global），是工具落差不是資料錯誤。
- [臨] 差量再匯入的兩個地雷：以來源雜湊判斷變更的匯入腳本會整顆覆寫目標，目標端改過的要先比對再手動合併；已轉換格式的技能檔不可整包重新複製，只能依差量報告逐檔處理。
- [臨] 對話自動萃取的碎片數百則以內直接逐則讀比跑分群快；實測 220 則約三分之一是重複或過程性狀態，丟棄要留每則去向紀錄。
- [臨] 完整紀錄：`_AIDocs/DevHistory/設定與遷移/` 下的遷移文件；一次性腳本在 `memory/_staging/` 的遷移資料夾。

## 行動

- 同類批次匯入先讀 DevHistory 那份的格式轉換規則，沿用 staging 的匯入腳本
- 匯入後跑索引一致性檢查並確認向量索引已重建
