# 2026-04-17 Evasion Guard + Test-Fail Gate

> keywords: evasion, test-fail, failing_tests, completion-claim, pytest, Stop hook, output_block

## 摘要

程式碼攔截 LLM「錯誤的迴避」行為——不依賴模型自律，兩層擋住。

## 方案 1（硬）：測試失敗 → 不得結束

- `hooks/wg_evasion.py`（新，~115 行純函式）含 `is_test_command`/`detect_test_failure`/`claims_completion`/`detect_evasion`/`get_last_assistant_text`
- PostToolUse(Bash) 解析 pytest / tsc / node --check / jest / go test / cargo test 輸出 → 匹配 `N failed` / `SyntaxError` / `error TS\d+` / `--- FAIL:` / `test result: FAILED` 等 pattern → 失敗訊息最後 20 行寫入 `state["failing_tests"][]`
- 同 cmd 前綴重跑成功 → 自動清舊紀錄
- Stop hook 偵測 `failing_tests` 非空 + last assistant text 命中完成宣告 regex（完成/已解決/全部做完/done/finished/大功告成）→ `output_block` 硬阻擋，要求三選一：(a) 修復 (b) 標為已知 regression (c) 降級任務定義

## 方案 2（軟）：退避詞彙 → 舉證要求

- Stop 偵測 `_EVASION_RE`（不在本範圍/既有 drift/pre-existing/留給未來/超出能力/非本次改動 等）→ 寫 `state["evasion_flag"]`
- UserPromptSubmit 下一輪注入 `[Guardian:Evasion]` 要求列檔/行數成本 + 為何不算退避，注入後清旗
- Escape hatch：追蹤近 5 則 user prompt 到 `state["recent_user_prompts"]`，近 3 則命中放行詞（先這樣/留著/跳過/known regression）→ skip evasion flag + 清 failing_tests

## 配置

- `settings.json` PostToolUse matcher `Edit|Write` → `Edit|Write|Bash`
- state 欄位以 `setdefault` 增量加入，不升 schema_version

## 測試

- `tests/test_evasion_guard.py` 51 pytest cases 全綠：is_test_command 參數化 13、detect_test_failure 10、claims_completion 10、detect_evasion 6、is_dismiss_prompt 6、get_last_assistant_text 4、tail_lines 1、escape hatch 邊界 1

## 中途教訓（本身應用了 feedback-fix-on-discovery）

- 回歸測試發現 `tests/fixtures/v4_atoms_baseline.jsonl` 有 5 atom sha256 drift（上 session 合併後殘留）
- **當場刷新** `python tools/snapshot-v4-atoms.py`（66 atoms），不留「非本次改動」退避說法
- 整體回歸測 140 passed（前此為 139 passed + 1 failed）

## 涉及檔案

- `hooks/wg_evasion.py`(新)
- `hooks/workflow-guardian.py`
- `settings.json`
- `tests/test_evasion_guard.py`(新)
- `tests/fixtures/v4_atoms_baseline.jsonl`(regen)
- `_AIDocs/Architecture.md`
