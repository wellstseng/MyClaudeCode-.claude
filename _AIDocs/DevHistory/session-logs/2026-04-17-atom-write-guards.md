# 2026-04-17 Atom 寫入防呆強化 + feedback 目錄整理 + atom_promote 合併流程

> keywords: AUTO-DRAFT, Atom-Write Guard, feedback/, merge_to_preferences, atom_promote

## 摘要

四個改動解決不同痛點。

## (1) AUTO-DRAFT tag 硬規則

- `wg_hot_cache.py::format_injection_line()` 把 auto-extract 注入訊息改為 `[HotCache:src ⚠AUTO-DRAFT·[臨]] ... | 規則：auto-extract 僅供參考，未經 4+ session 驗證，禁止引用為事實、禁止以 [固]/[觀] 存入`
- 兩個注入點（UPS L770 + PostToolUse L1485）改用 helper

## (2) Atom-Write Guard

- `workflow-guardian.py::handle_user_prompt_submit` 偵測「記住/存起來/值得存/寫 atom/存成 [固]」等關鍵字 → 注入一次性硬規則：新 atom 一律 [臨]、單次成功 ≠ 穩定模式、晉升走 atom_promote、更新既有走 `mode=append`

## (3) feedback 目錄整理

- 11 個 feedback atom 統一改名（`_` → `-`）+ 移入 `memory/feedback/` 子資料夾
- `wg_iteration.py::scan_dirs` 加 `feedback/`
- `_ATOM_INDEX.md` 18 條 feedback trigger 以保守原則收窄（移除 `git` / `決策` / `選擇` / `drift` / `失敗` / `research` 等單字寬 trigger）
- cross-ref 同步：toolchain.md / workflow-rules.md / env-traps.md / Project_File_Tree.md / v4_atoms_baseline.jsonl 7+4 條 path

## (4) atom_promote merge_to_preferences

- `server.js::atom_promote` 新增 `merge_to_preferences` 參數（scope=global）：[觀]→[固] 時自動把「## 知識」行追加到 `preferences.md` 的歸檔合併段 + 搬到 `memory/_archived/{date}-{name}.md`
- 未帶 flag 時也附提示

## 驗證

- node --check + python import + pytest 全綠（baseline drift 為 session 開始前既有——當時判斷為「非本次改動所致」，**後續 session 證明此說法違反 feedback-fix-on-discovery，應當場刷新**）

## 涉及檔案

- `hooks/wg_hot_cache.py`
- `hooks/workflow-guardian.py`
- `hooks/wg_iteration.py`
- `tools/workflow-guardian-mcp/server.js`
- `memory/_ATOM_INDEX.md`
- `memory/feedback/`（新資料夾，11 檔移入）
- `memory/toolchain.md`
- `memory/workflow-rules.md`
- `_AIDocs/Failures/env-traps.md`
- `_AIDocs/Project_File_Tree.md`
- `_AIDocs/Architecture.md`
- `tests/fixtures/v4_atoms_baseline.jsonl`
