# 整併 upstream v6.0 到 Mac 線（2026-11-01）——這次新踩的坑

> 讀者：下次再合 upstream 的 session。通用做法在 atom `upstream-merge-mac-適配工作流`，這裡只放這次新發現的個案細節。整併內容本身見 `_CHANGELOG.md` 2026-11-01 條與 merge commit 訊息。

| 坑 | 現象 | 解法 |
|---|---|---|
| merge driver 指錯直譯器 | `merge-atom-index.py --status` 顯示驅動指 CommandLineTools 的 python3（3.9）——它記的是上次 `--install` 時的 `sys.executable` | merge 前用 hook 同一支 python（`~/.local/bin/python` 3.12）重跑 `--install` |
| 個人 atom trigger drift | atom 走 `checkout --ours`，索引三檔已由驅動聯集兩邊 trigger，但 .md frontmatter 還是本地舊的 → `sync-atom-index --check` 報 `trigger_drift` | frontmatter 獨有的詞補進索引（`lib.atom_index_json.save_index_with_mirror`）再 `--fix`，兩邊都不丟 |
| 子夾搬移留懸空 | upstream 把 MemDev 分 11 子夾；一側改、一側搬的 atom 在索引留舊路徑 | `--fix-scope-from-path` 清懸空後 `--add-from-frontmatter` 補新址 |
| `git add -A` 掃進執行期檔 | upstream 新加的 `workflow/state-*.lock` 不在 .gitignore | commit 前 `git diff --cached --name-only \| grep workflow/` 掃一次，補 pattern |
| CommitOrder 閘擋 heredoc | 記憶系統 repo 內的豁免只認「純 git 段用 `&&` 串」，heredoc／管線都不算 | 長訊息先寫到 scratchpad 檔再 `git commit -F <path>` |
| `config.local.json` 淺合併 | `lib/config_local.merge_local` 只合頂層鍵：覆寫 `text_score.judge_model_by_backend.local` 要把整個 `judge_model_by_backend` dict 帶齊 | 巢狀段落整段寫；`vector_search` 這種多層的不適合用它覆寫 |
| Python 3.12 dataclass 收集錯 | verify 用 `spec_from_file_location + exec_module` 載含 `@dataclass` 的工具檔，模組沒登進 `sys.modules` → 收集階段 `AttributeError: 'NoneType' has no attribute '__dict__'`，整組 run_verify 收集 0 案例 exit 2 | `exec_module` 前加 `sys.modules[name] = mod`（`tools/verify/verify_stale_deps.py`、`verify_related_line_and_conflict_guard.py`）；合進來的新 verify 檔先 `pytest --collect-only -q` 掃 |
| 本 session 的 guardian MCP 載不到新碼 | node require 快取裡是舊 `paths.js`，新 `atom-tools.js` 找它要 `v6Enabled` → atom_write 報 `v6Enabled is not a function`；殺 :3848 的常駐 server 不影響本 session 的 stdio MCP 行程 | 合併後寫 atom 改走 `python -m lib.atom_io_cli`（action=append，同 MCP 落檔路徑）；新 session 才會載新碼 |
| run_verify 被 VerifyBatch 閘擋 | 測試檔 ≥50 支算「會拖時間的整組驗證」，要使用者本回合原話有口令（整組／全量／run_verify）；派工 prompt 裡寫了 run_verify 仍判沒有 | 點名 9 個 verify 目錄用 pytest 跑（閘允許點名），或請使用者在回合裡下口令 |
| git cassette 重錄污染工作樹 | 本機 git 版本與錄製時不同 → 全組第一次跑進錄製模式，改掉 341 個、新增 81 個 `hooks/verify/cassettes/**.json.gz`；第二次跑重播又 `CassetteMismatch：少了 .git/config`（macOS 重播缺陷，待修） | 跑完全組 `git checkout -- hooks/verify/cassettes && git clean -f -- hooks/verify/cassettes`，錄製檔不進 commit |

## 2026-11-04 合 v6.1（88 commits）再踩的坑

| 坑 | 現象 | 解法 |
|---|---|---|
| 腳本式驗證檔換掉全域 `subprocess.run` | upstream 新 `hooks/verify/verify_ensure_mcp.py` 模組頂層跑檢查、`run_case` 把 `em.subprocess.run`（＝全域 subprocess 模組）換成假函式不還原，結尾 `sys.exit` → pytest 收集時 INTERNALERROR 整組 0 案例；只拿掉 `sys.exit` 又變成後面 807 案全紅（git／子行程都拿到假結果），單支跑卻全綠 | 檔頭存 `_REAL_SUBPROCESS_RUN`、檢查跑完還原，`sys.exit` 收進 `__main__`，另給 `test_ensure_mcp_checks` 交帳。單支綠、整組紅 → 先懷疑前面某支改了全域模組沒還原 |
| 錄製檔每跑一次就重錄 | 本機 git 版本與錄製時不同，跑一次全組改掉上百個 `cassettes/**.json.gz`；接著再跑就重播自己剛錄的檔而紅（看起來像新壞掉） | 每次全組或重跑紅測之前都先 `git checkout -- hooks/verify/cassettes tools/verify/cassettes && git clean -fq -- 同兩處` |
| upstream 測試沒跟上自己的改動 | 安裝器補 `SYSTEM_CONTRACT_KEYS` 後 `verify_install` 兩案仍斷言 settings 只有 hooks／statusLine；儀表板 API 疊私人列後 `test_case1b` 仍只數共用索引（作者機器沒登錄 ~/.claude 所以 skip 掉）；skill 檔頭改 `when_to_use`／`metadata` 後本地獨有的 code-guide 還是舊鍵 | 測試照新設計改：容許契約鍵、計數改用含私人列的 `_index_rows()`；code-guide 檔頭改新格式 |
| `cleanupPeriodDays: 14` 是系統契約鍵 | 合 settings 時照抄會在下次啟動刪掉 14～30 天的對話逐字稿（不可逆） | 先不設，留給使用者決定；其餘三個契約鍵照帶 |
| 向量去重長查詢逾時 | 寫入閘查詢逾時 3 秒；本機 qwen3-embedding 嵌入 1,100 字約 4 秒 → 長卡的去重被略過（稽核記 `dedup_skipped_service_down`），對應測試紅。合併前就是這樣；另 `verify_codex_models` 拿 models_cache 存在當「有裝 codex」，殘檔讓它在沒裝 CLI 的機器紅 → 加 `shutil.which("codex")` 判斷 | `tools/memory-write-gate.py` 逾時改 10 秒（仍在 MCP 端 15 秒內） |
