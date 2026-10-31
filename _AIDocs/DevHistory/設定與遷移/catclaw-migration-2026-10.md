# CatClaw → Claude Code 記憶與技能遷移（2026-10）

> 把 CatClaw（Discord agent 平台）的 boot agent 記憶、技能、排程搬到 Claude Code。
> 本檔只記機制面的決策、數字與踩坑；個人內容不在此處。

## 落點決策

| 來源（CatClaw） | 落點 | 理由 |
|---|---|---|
| boot agent 的 global／account 層 atom | 獨立私有專案資料夾的 `.claude/memory/shared/` | `~/.claude` 的 origin 是公開 repo；local realm 不進向量索引；global `MEMORY.md` 已近 40 行上限 |
| `projects/<id>/` 層 atom | 各程式碼專案自己的 `.claude/memory/shared/` | 以專案資料夾為單位 |
| 平台本身的開發知識 | CatClaw 原始碼專案的 `.claude/memory/shared/` | 同上 |
| 技能、工具、排程、憑證 | 同一個私有專案資料夾（`.claude/skills/`、`tools/`、`cron/`、`secrets/`） | 技能彼此用同層相對路徑互讀，整組搬才不斷 |

專案層 atom 仍會被其他專案的 session 召回：`ups_search` 的跨專案掃描在 trigger 命中 ≥2 時納入候選，向量查詢不分專案。

## 數字

- 具名 atom：267 顆（私有專案 229、其餘四個專案 38）。CatClaw 靠 recall 命中數自動晉升的 13 顆 `[觀]` 降回 `[臨]`，命中數轉記 `read_hits`。
- 自動萃取碎片（`ext_*`）：2096 則 → embedding 分群（KMeans 54 群，切 9 批）→ 9 個 agent 篩選合併 → 220 顆草稿，匯入 219 顆（1 顆與既有 atom cos 0.94 略過）；丟棄 373 則（transient 210、duplicate 70、generic 37、superseded 34、garbled 22）。合併 atom 一律 `[臨]`，跨日期出現次數記為 `confirmations`。
- 技能：32 個轉成 Claude Code project skill（audit 全 0 fail），3 個平台專屬技能封存。
- 排程：15 個 job 轉登記到 launchd 版排程工具，未啟用。

## 格式轉換規則（CatClaw atom → V5）

- `Scope` 一律依實際目錄決定，不看原欄位（原欄位與目錄不一致）。
- `Created-at` epoch 毫秒 → `YYYY-MM-DD`；`Last-used`／`Confirmations` 從 `.md` 搬進 access sidecar。
- sidecar `x.md.access.json`（v2，毫秒）→ `x.access.json`（v3，秒）；`read_hits = max(read_hits, confirmations)`，`confirmations` 歸 0。
- 自訂 `##` 段落降為「知識」段下的 `###`；缺「行動」段補預設值。
- trigger 截到 30 字、補到 3 個、上限 12 個。
- 保留 `[固]`／`[觀]` 信心等級需自組內容走 `write_raw` + `atom_access` + `write_index`（`write_atom` 的 create 只收 `[臨]`），來源標 `tool:migrate`。

## 遷移中修掉的缺陷

| 位置 | 缺陷 | 修法 |
|---|---|---|
| `tools/memory-vector-service/service.py` | 啟動時 Ollama 未就緒 → 落到 1024 維備援模型且永不切回；表是 4096 維，查詢全空 | 背景執行緒每 60 秒重探，可用即切回；`/health` 加 `degraded` |
| `tools/memory-vector-service/indexer.py` | 查詢例外被吞成空陣列，無訊號 | stderr 告警（5 分鐘限流） |
| 同上，增量索引 | 以 `":"` 切 `layer:atom` 當 key，`shared:<slug>` 層刪不到舊 chunk；`add` 失敗時用當批變更覆寫整張表 | 改 tuple key；既有表失敗往上拋 |
| `tools/workflow-guardian-mcp/lib/funnel.js` | 寫入後打不存在的 `/reindex`（靜默 404） | 改 `/index/incremental` |
| `hooks/wg_episodic.py` | `_purge_expired_episodic` 接受 `today` 卻用 `date.today()` 決定月份目錄 | 改用傳入日期 |
| `skills/skill-creator/scripts/audit-skill.py` | `int \| None` 在 Python 3.9 直接 TypeError | 加 `from __future__ import annotations` |
| `settings.json` | 使用者身分落到上游預設值 | 加 `CLAUDE_USER` |

## 自動萃取重新開啟

`response_capture.session_end_flush` 改回啟用。2026-07 關閉的理由是草稿零下游消費；這次補上下游：排程工具的 `memory-drafts-consolidate` job 以 headless `claude -p` 讀 `_drafts/auto-capture/`，篩選合併後經 `atom_write` 寫入，處理完的草稿移到 `_drafts/_processed/<日期>/`。`per_turn` 維持關閉。

實測：對一份既有 transcript 跑 `extract-worker`（本機 qwen3:14b，約 1–2 分鐘）產出 5 筆草稿；整併步驟手動執行一次，5 筆以 `mode=append` 併入既有 atom。headless 路徑因 CLI 登入過期未能實跑。

## 踩坑

- **專案記憶要被發現，必須有 `.claude/memory/MEMORY.md`**：`discover_all_project_memory_dirs` 只認這個檔，光有 `_atom_index.json` 不夠。新專案要先放一個帶 `<!-- AUTO-GENERATED: V4 role filter -->` 檔頭的檔，SessionStart 才會接手重生。
- **trigger 內不能有逗號**：檔頭以逗號分隔，「62,900」這類金額會被切開，造成檔頭與索引漂移。匯入時要先去掉千分位逗號。
- **`session_end_flush` 關閉時 `extract-worker` 仍會萃取**：只是 writeback 一開頭就返回，看起來像「萃到了卻沒落檔」。
- **`sync-atom-index.py --memory-dir <專案>` 會把每顆 atom 報成 `scope_drift`**：`write_index` 對專案層一律寫 `scope: global`，是檢查工具與寫入端的既有落差，不是資料錯誤。
- **本機 hook 會擋對 atom 檔的直接 Write／Edit**：技能與排程提示詞要改走 `atom_write`，狀態檔更新用 `mode=replace`。
- **小模型萃取會把「萬」譯成 million**：三個批次都出現，合併時依上下文校回。
- **`audit-skill.py`、`run_verify.py` 都吃系統 Python**：本機是 3.9，新語法要留意。
- **macOS + numpy 2.0 的 `matmul` RuntimeWarning 是誤報**，相似度數值正常。

## 現況與再遷移

2026-10-05 的遷移是預防性的：CatClaw 繼續當主力，Claude Code 這邊是靜止副本，排程工具未啟用。兩邊會持續分岔，之後可能再遷一次。

- 再遷移前跑 `07_drift_report.py`（唯讀）：比對具名 atom（對匯入帳本）、ext 碎片（對清單）、技能／工具／腳本／人格檔（對雜湊基準）、排程定義（去掉執行狀態欄位）。
- 具名 atom 匯入腳本對「來源有變」的 atom 是整顆覆寫目標，Claude 端改過的同一顆會被蓋掉。
- 技能已轉換格式，不可整包重新複製；只能依漂移報告逐檔處理。
- 切換腳本的資料同步用「來源較新才覆蓋」，避免舊憑證蓋掉已刷新的副本。
- 進行中狀態與逐類做法記在 `memory/_staging/catclaw-migration/STATUS.md`（不進版控）。

整併遠端 `main` 時另外發現的機器差異：共用的 `workflow/config.json` 沒有本機覆寫機制，模型名稱以最後推送的那台為準；本機用 Ollama 別名對齊 embedding 模型名稱。健康檢查只確認 Ollama 連得上、不確認模型存在，模型名稱不符時向量搜尋會全空而無告警。

## 一次性腳本

放在 `memory/_staging/catclaw-migration/`（不入版控）：路徑改寫、碎片分群、具名 atom 匯入、合併草稿匯入。兩支匯入腳本以 ledger 記錄來源雜湊，可重跑補差量。
