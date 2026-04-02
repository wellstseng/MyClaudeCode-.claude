# 變更記錄

> 保留最近 ~8 筆。舊條目移至 `_CHANGELOG_ARCHIVE.md`。

---

## 2026-04-02 V3.1 Token Diet — 原子記憶精簡
- Phase 1 直刪：移除 31 條 Claude 不使用的自動化描述條目
- Phase 2 信號自描述化：5 個 Guardian 信號加入行動指令，移除冗餘 atom 條目
- Phase 3 JIT 按需注入：記憶系統開發知識移到 `_reference/internal-pipeline.md`，複合條件觸發
- Phase 4 MCP atom_write/promote tools：程式化 atom 寫入，rules/memory-system.md 精簡
- **成果**：decisions+arch+memory-system 從 1,841→631 tok（**-65.7%, -1,210 tok**），超越計畫目標 36%

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-04-02 | **V3.1 Token Diet**：4 Phase 精簡原子記憶 — 直刪 31 條 + 信號自描述化 5 個 + JIT _reference + MCP atom_write/promote。decisions+arch+memory-system 1,841→631 tok (-65.7%) | `memory/decisions.md`, `memory/decisions-architecture.md`, `rules/memory-system.md`, `hooks/wg_iteration.py`, `hooks/wisdom_engine.py`, `hooks/workflow-guardian.py`, `memory/_reference/internal-pipeline.md`(新), `tools/workflow-guardian-mcp/server.js` |
| 2026-04-02 | **V3.0 文件全面升級**：README V3.0（標題+三欄Token表+速度效率表+架構+流程圖+Skills 17個+V3子系統+版本歷史）+ Install-forAI V3升級section + Architecture/Project_File_Tree/DocIndex/INDEX 更新 + 7 commands 移除版號標記 | `README.md`, `Install-forAI.md`, `_AIDocs/*.md`, `commands/*.md`, `CLAUDE.md` |
| 2026-04-02 | **V3 Phase1 實作：Hot Cache + Quick Extract**：新建 wg_hot_cache.py（lock+原子寫入 3 API）、quick-extract.py（Stop async hook, qwen3:1.7b 快篩→hot cache）、decisions-architecture.md Hot Cache 段落 [臨]→[觀] | `hooks/wg_hot_cache.py`(新), `hooks/quick-extract.py`(新), `memory/decisions-architecture.md` |
| 2026-04-02 | **V3 三層即時管線升級**：decisions.md 新增 V3 管線+SessionStart 風暴修復決策、decisions-architecture.md 新增 Hot Cache/Async Hook/去重技術細節、cc-hook-system.md 補充 additionalContext 可用性差異 | `memory/decisions.md`, `memory/decisions-architecture.md`, `_AIDocs/ClaudeCodeInternals/cc-hook-system.md` |
| 2026-04-01 | **atom 全面精簡 — 經歷敘述型內容歸檔**：10 個 atom 移除演化日誌段落、decisions.md 移除 5 條版本遷移敘述（V2.18~V2.21）改為 2 條現狀事實、toolchain-ollama.md A/B 完整表格改為 3 條結論、移除各處版本標籤前綴。歸檔至 `_AIDocs/DevHistory/`（3 檔）。估計省 ~1100 tok/session | `memory/*.md`（10 atoms）, `_AIDocs/DevHistory/*`（3 新檔） |
| 2026-04-01 | **原子記憶系統全面驗證 + 修正**：decisions.md 修正 4 處 + architecture 計數器歸零 + Vector DB full reindex | `memory/decisions.md`, `memory/wisdom/reflection_metrics.json` |
| 2026-03-30 | **_AIDocs V2.21 全面同步**：Architecture.md V2.17→V2.21 + Project_File_Tree 重寫 + DocIndex 更新 | `_AIDocs/Architecture.md`, `_AIDocs/Project_File_Tree.md`, `_AIDocs/DocIndex-System.md`, `_AIDocs/_INDEX.md` |
_(舊條目已移至 `_CHANGELOG_ARCHIVE.md`。最近移入：2026-03-30 清理/Dashboard + 2026-03-27 V2.21 Phase 7/文件同步)_
