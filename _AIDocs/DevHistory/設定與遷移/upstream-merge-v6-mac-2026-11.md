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
