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
- [臨] 現況（2026-10-05 快照）：這是預防性遷移、尚未切換。CatClaw 仍是主力並持續寫入，Claude 這邊是靜止副本，之後可能要再遷一次補差量。現況與再遷移手冊在 `memory/_staging/catclaw-migration/STATUS.md`。
- [臨] 再遷移前先跑 `07_drift_report.py`（唯讀）看 CatClaw 自基準後變了什麼；基準是 `skills-baseline.json`，補完後用 `--save-baseline` 重設。
- [臨] 再遷移的兩個地雷：(1) `04_import_atoms.py` 對來源有變的 atom 是整顆覆寫目標，Claude 這邊改過同一顆會被蓋掉；(2) 技能不可整包重新複製，已轉換的 SKILL.md 與 references 會被蓋回 CatClaw 格式，只能依漂移報告逐檔處理。
- [臨] 共用的 `workflow/config.json` 沒有本機覆寫機制，模型名稱是另一台機器的。本機以 `ollama cp qwen3-embedding:8b qwen3-embedding` 建別名讓 embedding 可用；少了別名時向量搜尋全空且無告警，因為健康檢查只看 Ollama 連得上、不檢查模型存在。
- [臨] 排程工具未 install；`session_end_flush` 已開但整併 job 沒在跑，草稿會累積在 `_drafts/auto-capture/`，切換前要手動整併或關掉開關。
- [臨] 合併遠端後當下 session 的 guardian MCP 會新舊模組混載，atom_write 回 `spawn failed … file argument … undefined`；重啟 CC 即恢復，期間可改用 `python -m lib.atom_io_cli`。

## 行動

- 再做同類批次匯入時先讀 DevHistory 那份的「格式轉換規則」與「踩坑」，沿用 staging 裡的兩支匯入腳本
- 匯入後跑各專案的 sync-atom-index 檢查，並確認向量索引已重建
