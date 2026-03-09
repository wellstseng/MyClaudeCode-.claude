# Claude Code 全域設定 — 變更記錄

> 保留最近 ~8 筆，舊條目移至 `_CHANGELOG_ARCHIVE.md`。

---

| 日期 | 變更 | 影響檔案 |
|------|------|---------|
| 2026-03-10 | V2.7 全文件版本同步：CLAUDE.md 精簡 50%（289→144 行，移除 hook 實作細節與重複偏好）、README/Install-forAI/MEMORY.md/decisions.md 版本號更新至 V2.7、架構樹加入 failures.md + toolchain.md、Token 估算更新（~1,400-1,900 tokens） | CLAUDE.md, README.md, Install-forAI.md, MEMORY.md, decisions.md, _CHANGELOG.md |
| 2026-03-05 | V2.4 環境掃描整理：Architecture.md + Project_File_Tree.md 更新到 V2.4（回應捕獲/跨 Session 鞏固/episodic 子資料夾）、SPEC 修正過時引用（LanceDB→ChromaDB, qwen3:4b→1.7b, min_score 0.65→0.45）、_INDEX.md 修正 hook 數量、全文件交叉比對一致性確認 | _AIDocs/*, SPEC, _INDEX.md |
| 2026-03-05 | V2.3 全面升級 OpenClaw Phase 1+2: MEMORY.md 重寫(155行→33行,3欄格式)、建立 root CLAUDE.md、4個新 atom(architecture/setup-guide/taxonomy/self-iteration)、更新 config-intelligence | MEMORY.md, CLAUDE.md, 4 new atoms, config-intelligence |
| 2026-03-05 | 建立 README.md（設計哲學、Token 對比、流程圖 x2、大型專案使用法）+ Install-forAI.md 安裝指南 | README.md, Install-forAI.md, memory/decisions.md |
| 2026-03-05 | 原子記憶 V2.3 S5: OpenClaw atoms 整合 — indexer.py 支援多來源目錄 + 遞迴掃描 + skip_files，config.json 加 additional_atom_dirs，memory-v2-cc.md 標記 deprecated | indexer.py, config.py, config.json, memory-v2-cc.md |
| 2026-03-05 | 原子記憶 V2.3 S6: E2E 驗證 + bug fix — memory-audit.py 加 Any import、test-memory-v21.py 修正 episodic_generation 斷言（v2.2 不寫 MEMORY.md）、Architecture.md 更新為 V2.3 | memory-audit.py, test-memory-v21.py, Architecture.md |
| 2026-03-04 | 知識庫建立：初始化 _AIDocs + git repo (MyClaudeCode-Home-.claude) | _AIDocs/*, .gitignore |
| 2026-03-04 | Memory V2 建置完成：UserPromptSubmit hook + 三階段管線 (Gate→A4+Vector→Fusion) | settings.json, memory-v2 全系統已在 OpenClawWorkSpace/.claude/ |
