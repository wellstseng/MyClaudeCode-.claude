# 2026-04-17 _CHANGELOG 自動滾動 + Architecture 索引化

> keywords: changelog-roll, architecture, DevHistory, index, PostToolUse

## 摘要

兩個程式碼強制化改動，配合使用者原則「留給人讀無意義 → 只保留 AI 不會變笨的最小集」。

## Part A：_CHANGELOG AI 自動滾動

- 新建 `tools/changelog-roll.py`（120 行，零依賴）+ `/changelog-roll` skill
- `workflow-guardian.py::handle_post_tool_use` 新增 `_maybe_auto_roll_changelog` gate：偵測 `_CHANGELOG.md` 寫入 → rows > `config.changelog_auto_roll.threshold`（預設 8）→ detached subprocess 跑 roll，fail-open
- `workflow/config.json` 加 `changelog_auto_roll: {enabled, threshold}`
- `tests/test_changelog_roll.py` 8 條（5 純工具邏輯 + 3 PostToolUse 自動觸發 mock 驗證：Popen 被呼叫 / 未超閾值時不呼叫 / 非 _CHANGELOG 檔案時不呼叫）
- 實跑：26 → 8 條，ARCHIVE +18

## Part B：Architecture.md → Index 型

- 413 行 → 150 行（-64%），32KB → 12KB
- 穩定子系統拆 7 個新 DevHistory 子檔 + v41-journey.md §10 擴充：
  - `ollama-backend.md`（Dual-Backend 退避）
  - `memory-pipeline.md`（檢索管線 + 回應捕獲 + V3 三層即時管線）
  - `session-mgmt.md`（SessionStart 去重 + Merge self-heal）
  - `v4-layers.md`（專案自治層 + V4 三層 scope + JIT）
  - `v4-conflict.md`（三時段衝突偵測 + ASCII 流程圖）
  - `wisdom-engine.md`（Wisdom + Fix Escalation + 跨 session 鞏固）
  - `settings-config.md`（權限 + 工具鏈）
- 主檔只留：Hook 事件表 / Hook 模組表 / 輔助 Hook / Skills 表 / Evasion Guard + Auto-Roll（演化中 feature）/ 子系統索引 + keywords / MCP atom_write 參數表

## 驗證

- 148 pytest 全綠
- baseline 刷新 66→67 atoms
- 自動 roll 端到端驗證：本 session 加新 entry 時 PostToolUse hook 真的 fire → 主檔 9→8、ARCHIVE +1

## 涉及檔案

- `tools/changelog-roll.py`(新)
- `commands/changelog-roll.md`(新)
- `tests/test_changelog_roll.py`(新)
- `workflow/config.json`
- `hooks/workflow-guardian.py`
- `_AIDocs/Architecture.md`(rewrite)
- `_AIDocs/DevHistory/*`(7 新+1 擴)
- `_AIDocs/DevHistory/_INDEX.md`
- `_AIDocs/DocIndex-System.md`
- `_AIDocs/_CHANGELOG.md`
- `_AIDocs/_CHANGELOG_ARCHIVE.md`
