# 變更記錄

> 保留最近 ~8 筆（PostToolUse hook 自動滾動到 `_CHANGELOG_ARCHIVE.md`）。
> 每條僅留「標題 + 一句摘要 + 詳情 log 連結」。實作細節見 `DevHistory/session-logs/{date}-{slug}.md`。

---

## 2026-04-02 V3.1 Token Diet — 原子記憶精簡
- Phase 1 直刪：移除 31 條 Claude 不使用的自動化描述條目
- Phase 2 信號自描述化：5 個 Guardian 信號加入行動指令，移除冗餘 atom 條目
- Phase 3 JIT 按需注入：記憶系統開發知識移到 `_reference/internal-pipeline.md`，複合條件觸發
- Phase 4 MCP atom_write/promote tools：程式化 atom 寫入，rules/memory-system.md 精簡
- **成果**：decisions+arch+memory-system 從 1,841→631 tok（**-65.7%, -1,210 tok**），超越計畫目標 36%

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-04-17 | **_CHANGELOG 短格式化 + session-logs 子目錄** — 每條 ~2KB 單行敘事拆為「標題 + log 連結」，8 條遷入 `DevHistory/session-logs/`。[log](DevHistory/session-logs/2026-04-17-changelog-short-form.md) | `_AIDocs/_CHANGELOG.md`, `_AIDocs/DevHistory/session-logs/*`(8 新) |
| 2026-04-17 | **_CHANGELOG 自動滾動 + Architecture 索引化** — PostToolUse auto-roll + 8 pytest；Architecture 413→150 行（-64%），7 DevHistory 子檔。[log](DevHistory/session-logs/2026-04-17-changelog-and-architecture.md) | `tools/changelog-roll.py`(新), `commands/changelog-roll.md`(新), `tests/test_changelog_roll.py`(新), `workflow/config.json`, `hooks/workflow-guardian.py`, `_AIDocs/Architecture.md`(rewrite), `_AIDocs/DevHistory/*`(7 新+1 擴) |
| 2026-04-17 | **Evasion Guard + Test-Fail Gate** — Bash 測試失敗偵測 + Stop 完成宣告攔截 + UPS 退避舉證要求，51 pytest。[log](DevHistory/session-logs/2026-04-17-evasion-guard.md) | `hooks/wg_evasion.py`(新), `hooks/workflow-guardian.py`, `settings.json`, `tests/test_evasion_guard.py`(新) |
| 2026-04-17 | **Atom 寫入防呆 + feedback 目錄整理 + atom_promote 合併** — AUTO-DRAFT tag / Atom-Write Guard / feedback/ 子資料夾 / merge_to_preferences。[log](DevHistory/session-logs/2026-04-17-atom-write-guards.md) | `hooks/wg_hot_cache.py`, `hooks/workflow-guardian.py`, `hooks/wg_iteration.py`, `tools/workflow-guardian-mcp/server.js`, `memory/feedback/` |
| 2026-04-16 | **V4.1 GA** `v4.1.0` — 清除 rc2 blocker（ollama_client / user-extract-worker / prompt regex 三處根因）P=1.000 R=0.480。[log](DevHistory/session-logs/2026-04-16-v41-ga.md) | `tools/ollama_client.py`, `hooks/user-extract-worker.py`, `tests/integration/test_e2e_user_extract.py`, `workflow/config.json` |
| 2026-04-16 | **V4.1 P4 Session 評價機制** `v4.1.0-rc2` — `wg_session_evaluator.py` 5 維度評分 + Agent 多 Role 模擬 + `/memory-session-score`。[log](DevHistory/session-logs/2026-04-16-v41-p4.md) | `hooks/wg_session_evaluator.py`(新), `hooks/user-extract-worker.py`, `commands/memory-session-score.md`(新), `tools/memory-session-score.py`(新) |
| 2026-04-16 | **V4.1 P3 UX Commands** `v4.1.0-rc1` — `/memory-peek` + `/memory-undo` + 每日推送 [F18] + 隱私體檢 [F21]。[log](DevHistory/session-logs/2026-04-16-v41-p3.md) | `commands/memory-peek.md`(新), `commands/memory-undo.md`(新), `tools/memory-peek.py`(新), `tools/memory-undo.py`(新), `tools/init-roles.py` |
| 2026-04-16 | **V4.1 P2 整合** `v4.1.0-beta1` — `user-extract-worker.py` L0→L1→L2 管線 + 整合測 50 條。[log](DevHistory/session-logs/2026-04-16-v41-p2-integration.md) | `hooks/user-extract-worker.py`(新), `tests/integration/test_e2e_user_extract.py`(新), `tests/regression/test_v4_atoms_unchanged.py`(新) |
