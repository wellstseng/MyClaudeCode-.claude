# Atom Index — Global

> Session 啟動時先讀此索引。比對 Trigger → Read 對應 atom。

| Atom | Path | Trigger | Confidence |
|------|------|---------|------------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference, 語言, 回應, 執P, 執驗上P, 上GIT, 上傳GIT | [固] |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統 | [固] |
| excel-tools | memory/excel-tools.md | Excel, xls, xlsx, 讀取, 試算表, spreadsheet, openpyxl, xlrd | [固] |
| workflow-rules | memory/workflow-rules.md | 工作流程, 大型任務, 分階段, SOP, 任務拆分, 上版, GIT, svn, svn-update, 版本控制, 同步, vcs | [固] |
| failures | memory/failures.md | 失敗, 錯誤, debug, 踩坑, pitfall, crash, 重試, retry, workaround, 陷阱 | [固] |
| toolchain | memory/toolchain.md | 工具, 環境, 指令, command, path, 路徑, bash, git, python, npm, ollama | [固] |
| fix-escalation | memory/feedback_fix_escalation.md | 修正, 重試, 第二次, 升級, escalation, 精確修正, fix, retry | [固] |
| unity-yaml | memory/unity/unity-yaml.md | Unity YAML, fileID, GUID, PrefabInstance, .prefab, .meta, 型別ID, 序列化, Missing Script | [固] |
| gdoc-harvester | memory/gdoc-harvester.md | harvester, Google Docs, Sheets, 收割, Playwright, cookie, export | [觀] |
| feedback-research | memory/feedback_research_first.md | 試錯, trial-and-error, 不熟悉, API, 框架, 搜尋, research | [固] |
| doc-index-system | memory/doc-index-system.md | 系統架構, 檔案結構, file tree, hook, skill, tool, 升級, 迭代 | [臨] |
| feedback_upload_discord | memory/feedback_upload_discord.md | 上傳, 傳附件, 壓縮傳, upload, MEDIA, Discord 附件 | [固] |
| feedback_global_install | memory/feedback_global_install.md | 安裝MCP, 安裝skill, install MCP, install skill, 新增MCP | [固] |
| feedback_no_test_to_svn | memory/feedback_no_test_to_svn.md | 上SVN, svn commit, 測試碼, 新手作業, 不可上傳 | [固] |
| workflow-icld | memory/workflow-icld.md | ICLD, 閉環, Sprint, 功能拆解, 開發計畫, 大型新功能 | [固] |
| toolchain-ollama | memory/toolchain-ollama.md | ollama, dual-backend, rdchat, qwen3, embedding, 萃取品質 | [固] |
| workflow-svn | memory/workflow-svn.md | svn, svn-update, TortoiseSVN, 衝突, conflict | [固] |
| decisions-architecture | memory/decisions-architecture.md | 架構細節, vector service, ollama backend, extraction, ACT-R | [固] |

---

## 高頻事實

- [固] 使用者: wellstseng | 平台: Windows 11 Pro
- [固] Guardian @ localhost:3848 | Vector @ localhost:3849
- [固] Vector DB: LanceDB | search_min_score: 0.65
- [固] Dual-Backend: rdchat qwen3.5:9b(pri=1,think) → local qwen3:1.7b(pri=2) | embedding: local qwen3-embedding
- [固] 原子記憶 V2.18：V2.12 基底 + upstream V2.18 系統升級 + 個人記憶保留
- [固] Excel: `~/.claude/tools/read-excel.py`（Python3 + openpyxl + xlrd）
- [固] SVN 專案修改前必問 svn update（每 session 一次）| Skill: /svn-update
- [觀] Wisdom Engine: 硬規則情境分類 + 反思校準(over_engineering + silence_accuracy)

---

## 參考文件（不自動注入，開發記憶系統時手動讀取）

> 提到「改 hook」「改記憶系統」「atom 格式」「迭代規則」「檢索演算法」時，先讀這些：

| 文件 | Path | 用途 |
|------|------|------|
| SPEC | memory/_reference/SPEC_Atomic_Memory_System.md | 完整系統規格（950 行） |
| self-iteration | memory/_reference/self-iteration.md | 自我迭代 3 條原則 + 演進紀錄 |
| v2.9-design | memory/_reference/v3-design-spec.md | V2.9 檢索強化設計（ACT-R/Aliases/Spreading） |
| v3-research | memory/_reference/v3-research-insights.md | 認知科學/唯識理論研究筆記 |
