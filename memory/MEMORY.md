# Atom Index — Global

> Session 啟動時先讀此索引。比對 Trigger → Read 對應 atom。

| Atom | Path | Trigger | Confidence |
|------|------|---------|------------|
| preferences | memory/preferences.md | 偏好, 風格, 習慣, style, preference, 語言, 回應, 執P, 執驗上P, 上GIT | [固] |
| decisions | memory/decisions.md | 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統 | [固] |
| excel-tools | memory/excel-tools.md | Excel, xls, xlsx, 讀取, 試算表, spreadsheet, openpyxl, xlrd | [固] |
| workflow-rules | memory/workflow-rules.md | 工作流程, 大型任務, 分階段, SOP, 任務拆分, 上版, GIT, svn, svn-update, 版本控制, 同步, vcs | [固] |
| failures | memory/failures.md | 失敗, 錯誤, debug, 踩坑, pitfall, crash, 重試, retry, workaround | [固] |
| toolchain | memory/toolchain.md | 工具, 環境, 指令, command, path, 路徑, bash, git, python, npm, ollama | [固] |
| hardware | memory/hardware.md | 硬體, 電腦, 升級, hardware, PC, GPU, CPU, 顯卡, 記憶體, RAM, 主機板 | [觀] |
| unity-yaml | memory/unity/unity-yaml.md | Unity YAML, fileID, GUID, PrefabInstance, .prefab, .meta, 型別ID, 序列化, Missing Script | [固] |
| gdoc-harvester | memory/gdoc-harvester.md | harvester, Google Docs, Sheets, 收割, Playwright, cookie, export | [觀] |
| feedback-research | memory/feedback_research_first.md | 試錯, trial-and-error, 不熟悉, API, 框架, 搜尋, research | [固] |
| doc-index-system | memory/doc-index-system.md | 系統架構, 檔案結構, file tree, hook, skill, tool, 升級, 迭代 | [臨] |

## 高頻事實

- [固] 使用者: holyl | Windows 10 Pro | 回應語言: 繁體中文
- [固] MCP: playwright, openclaw-notify, workflow-guardian, computer-use | Guardian:3848 | Vector:3849
- [固] Ollama: local qwen3:1.7b + qwen3-embedding:0.6b | ChromaDB SQLite（i7-3770 不支援 AVX2）
- [固] V2.11：SessionEnd萃取(extract-worker) + 鞏固 + 迭代(3條) + Wisdom + ContextBudget + rules/模組化
- [固] Excel: `~/.claude/tools/read-excel.py` | SVN 每session必問update（/svn-update）

> 參考文件（開發記憶系統時讀）：SPEC(`_reference/SPEC_Atomic_Memory_System.md`) | self-iteration | v3-design | v3-research
