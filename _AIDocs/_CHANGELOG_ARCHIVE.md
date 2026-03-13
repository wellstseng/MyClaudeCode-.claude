# 變更記錄 — 封存

> 從 `_CHANGELOG.md` 滾動淘汰的歷史記錄。

---

| 日期 | 變更 | 涉及檔案 |
|------|------|---------|
| 2026-03-03 | **MCP 傳輸格式修正**：Content-Length header → JSONL。protocolVersion 更新至 2025-11-25。Dashboard heartbeat recovery。 | `tools/workflow-guardian-mcp/server.js` |
| 2026-03-03 | **工作流完善**：session ID prefix match、resume 後 atoms 重注入、Atom Last-used 自動刷新、sync_completed 清空 queue+files、computer-use MCP 修正 | `server.js`, `workflow-guardian.py`, `README.md`, `Install-forAI.md` |
| 2026-03-02 | Dashboard 改進 + 4 項缺陷修復 + Workflow Guardian 建立 + CLAUDE.md 情境判斷表 | 多檔案 |
| 2026-03-02 | 原子記憶系統設計完成 + 知識庫初始化 + GitHub 上傳準備 | `memory/SPEC_*`, `CLAUDE.md`, `_AIDocs/*` |
