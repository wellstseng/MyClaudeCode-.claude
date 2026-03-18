# 變更記錄

> 保留最近 ~8 筆。舊條目移至 `_CHANGELOG_ARCHIVE.md`。

---

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-03-18 | **V2.12 逐輪增量萃取**：Stop hook 觸發 per-turn extraction（byte_offset 增量讀取 + cooldown 120s + PID 併發保護 + min_new_chars 500 門檻）。`_spawn_extract_worker()` 共用化（SessionEnd + per-turn）。修正 `handle_session_end()` intent 選取 bug（`get("top")` → `max(dist)`）。per-turn 結果直接回寫 state knowledge_queue，SessionEnd 自然 dedup | `hooks/extract-worker.py`, `hooks/workflow-guardian.py`, `workflow/config.json` |
| 2026-03-18 | **AIDocs keyword 重新設計**：`_INDEX.md` 加 keywords 欄（手動精準關鍵字）、`extract_aidocs_keywords()` 優先讀顯式 keywords fallback 描述提取、matching 改用 `_kw_match()` 防短詞誤匹配、`AiDocsEntry` 改 3-tuple | `_AIDocs/_INDEX.md`, `hooks/workflow-guardian.py` |
| 2026-03-18 | **`/atom-debug` skill**：新增注入/萃取 debug log 開關。開啟後記錄每次 additionalContext 注入內容、episodic atom 萃取、extract-worker LLM 萃取結果至 `~/.claude/Logs/atom-debug.log`。ERROR log 不受開關控制，含 stack trace | `commands/atom-debug.md`, `hooks/workflow-guardian.py`, `hooks/extract-worker.py`, `workflow/config.json` |
| 2026-03-17 | **V2.12 精確修正計畫**：新增 `/fix-escalation` skill（6 Agent 會議制）+ Guardian hook FixEscalation 信號注入（retry≥2）+ `rules/session-management.md` 精確修正升級段落 + `feedback_fix_escalation.md` atom | `commands/fix-escalation.md`, `hooks/workflow-guardian.py`, `rules/session-management.md`, `memory/feedback_fix_escalation.md`, `memory/MEMORY.md`, `README.md`, `Install-forAI.md` |
| 2026-03-13 | **自檢修復 7 項**：fix silence_accuracy 跨 process 失效（改讀 state）、統一 over_engineering 寫入路徑（消除雙寫競爭）、刪除逐輪萃取死代碼 ~65 行、config per_turn_enabled→false、MEMORY.md failures [觀]→[固]、reflection_metrics 清殘留+重置、toolchain ChromaDB→LanceDB | `hooks/wisdom_engine.py`, `hooks/workflow-guardian.py`, `workflow/config.json`, `memory/MEMORY.md`, `memory/wisdom/reflection_metrics.json`, `memory/toolchain.md` |
| 2026-03-13 | **對外文件更新 Dual-Backend**：README 補充 Dual-Backend 架構+三階段退避+靜態停用旗標；Install 補 rdchat 設定步驟+移除內部 URL+移除過時 extract-worker；Architecture 補 Dual-Backend+Long DIE+ollama_client 工具 | `README.md`, `Install-forAI.md`, `_AIDocs/Architecture.md` |
| 2026-03-13 | **/read-project**: 新增 DocIndex-System.md（76 檔系統索引）+ doc-index-system atom | `_AIDocs/DocIndex-System.md`, `memory/doc-index-system.md`, `memory/MEMORY.md` |
| 2026-03-13 | **選擇性 cherry-pick**：從來源 V2.10 合併 `/continue` skill + `/resume` staging 安全網 + `BOOTSTRAP.md` + `workflow-rules.md` 補回大型計畫/GIT/同步判斷段落 | `commands/continue.md`, `commands/resume.md`, `BOOTSTRAP.md`, `memory/workflow-rules.md` |
_(舊條目已移至 `_CHANGELOG_ARCHIVE.md`。最近移入：2026-03-13 Atom 整理)_
