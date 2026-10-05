# CatClaw 遷移到 Claude Code 的落點與踩坑

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: CatClaw 遷移, wendy 專案, ext 碎片, 專案記憶匯入, tool:migrate, MEMORY.md 發現, trigger 逗號, cronctl, 批次匯入 atom
- Created-at: 2026-10-05
- Related: 自動萃取層淨值審查-調整式拔除-2026-07, catclaw-agent-routing-boundaries

## 知識

- [臨] CatClaw boot agent 的記憶、技能、排程落在 `~/project/wendy`（`.claude/memory/shared/`、`.claude/skills/`、`cron/`、`secrets/`），不放 `~/.claude`：origin 是公開 repo、local realm 不進向量索引、global MEMORY.md 近 40 行上限。
- [臨] 專案記憶要被 `discover_all_project_memory_dirs` 發現，必須有 `.claude/memory/MEMORY.md`；光有 `_atom_index.json` 不夠。新專案先放帶 `<!-- AUTO-GENERATED: V4 role filter -->` 檔頭的檔，SessionStart 會接手重生。
- [臨] 批次匯入要保留 [固]/[觀] 時不能走 write_atom（create 只收 [臨]），改自組內容走 `write_raw` + `atom_access.init_access/write_access_field` + `write_index`，source 用 `tool:migrate`，每個回傳值都要檢查 `.ok`。
- [臨] trigger 內不能有逗號：檔頭以逗號分隔，金額如「62,900」會被切開造成檔頭與索引漂移；匯入前先去千分位逗號。
- [臨] `sync-atom-index.py --memory-dir <專案>` 會把每顆 atom 報成 scope_drift，因為 write_index 對專案層一律寫 scope=global；這是工具落差不是資料錯誤，判讀時略過該欄。
- [臨] 專案層 atom 仍會跨專案召回：ups_search 在 trigger 命中 ≥2 時納入其他專案的 atom，向量查詢不分專案。
- [臨] 排程工具 `~/project/wendy/cron/cronctl.py` 用 launchd 觸發，`install` 之前不會排進任何 job；claude 型 job 依賴 CLI 登入有效，過期時回 `OAuth session expired`。
- [臨] 完整紀錄在 `_AIDocs/DevHistory/catclaw-migration-2026-10.md`，一次性腳本在 `memory/_staging/catclaw-migration/`。

## 行動

- 再做同類批次匯入時先讀 DevHistory 那份的「格式轉換規則」與「踩坑」，沿用 staging 裡的兩支匯入腳本
- 匯入後跑各專案的 sync-atom-index 檢查，並確認向量索引已重建
