# 原子記憶版本遷移紀錄

> 從 decisions.md「核心架構」段落移出的版本遷移敘述。描述的是「怎麼遷過來的」而非「現在是什麼」。

## V2.21 Phase 4：現有資料遷移
- `migrate-v221.py`（tools/）：_AIAtoms/*.md + 個人 memory/*.md 合併 → {project_root}/.claude/memory/
- 舊 MEMORY.md 改指標型（Status: migrated-v2.21）
- project-registry.json 自動更新
- 已遷移：SGI / 加班系統 / FastSVNViewer

## V2.21 Phase 3：專案自治層建置
- `init-project` skill Step 6 建立 `.claude/` 結構（memory/, hooks/, .gitignore, MEMORY.md 模板, project_hooks.py delegate 模板）
- `_call_project_hook()` subprocess 隔離呼叫（5s timeout, 全例外吞噬）
- `handle_session_start` 末尾呼叫 on_session_start delegate

## V2.21 Phase 2：Project Registry + 路徑切換
- `register_project()` SessionStart 自動呼叫
- `get_project_memory_dir()` 新路徑優先（{project_root}/.claude/memory/）
- `find_project_root()` 加 `.claude/memory/MEMORY.md` 辨識
- _AIAtoms merge 邏輯移除

## V2.20：路徑集中化 + bug 修復
- wg_paths.py 路徑集中化
- Bug 修復 C5~C7, W8~W13

## V2.18：Section-Level 注入 + Trigger 精準化
- V2.17 全功能 + Section-Level 注入 + Trigger 精準化 + 規則精簡 + 反向參照自動修復

## 歷史決策
- 記憶檢索統一用 Python（Node.js memory-v2 已於 2026-03-05 退役）
- Stop hook 只保留 Guardian 閘門
