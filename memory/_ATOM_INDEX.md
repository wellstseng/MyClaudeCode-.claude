# Atom Trigger Index — Global

> **Deprecated mirror.** Machine source: `_atom_index.json` (V5 P3b).
> 本檔由 lib/atom_index_json.py 自動生成；勿手改。

| Atom | Path | Trigger | Scope |
|------|------|---------|-------|
| decisions-architecture | memory/decisions-architecture.md | 架構, hooks, pipeline, guardian, SessionStart, hot cache, extract-worker, vector service | global |
| decisions | memory/decisions.md | 決策, 記憶系統, 原子記憶, 架構細節, context budget | global |
| electron-uia-automation | memory/electron-uia-automation.md | Electron 自動化, VS Code 自動點擊, UIA Invoke, EVENT_E_NO_SUBSCRIBERS, PostMessage Chromium 失效, SendInput 偷塞字, AttachThreadInput, SetForegroundWindow 失敗, focus swap, ghost button, Claude Code 彈窗, GUI 工具 | global |
| feedback-workflow-discipline | _AIDocs/Failures/feedback-workflow-discipline.md | handoff, 續接, 下 session, next-phase, 順手修補, drift 修補, 重複失敗, fix-escalation, 裁決, 決策推薦, plan 路徑, SessionStart hook, commit message, 上 GIT | global |
| feedback-completion-gates | _AIDocs/Failures/feedback-completion-gates.md | 完成宣告, 收尾, pytest, run_verify, verify, smoke test, 研究先行, trial-and-error, 清理, 先清後建, 基線, 測試上傳, 上 SVN, known regression, xfail, 衍生暫存, 暫存檔, 清暫存, 收尾檢核 | global |
| feedback-tooling-reliability | _AIDocs/Failures/feedback-tooling-reliability.md | codex, codex companion, codex CLI, gpt-5, bg subprocess, DEVNULL, ready flag, subprocess Popen, MCP, 安裝 MCP, 安裝 skill, silent failure, probe burst, 規則唯一來源 | global |
| feedback-memory-structure | _AIDocs/Failures/feedback-memory-structure.md | 寫入記憶, atom 設計, atom 顆粒, 指標型, scope 敏感, GUID硬編碼, 環境相依, gitignore, git rm, memory path, _staging | global |
| feedback-rigor-standards | _AIDocs/Failures/feedback-rigor-standards.md | 縝密, 漏掉, 沒看到, max thinking, high thinking, 外包思考, 規範, rigor, 前例, precedent, 既有 drift | global |
| gdoc-harvester | memory/gdoc-harvester.md | harvester, Google Docs, Sheets, 收割, Playwright, cookie, export | global |
| preferences | memory/preferences.md | 偏好, 風格, 習慣, 語言, 回應, 執P, 執驗上P, 上GIT, Obsidian | global |
| toolchain-ollama | memory/toolchain-ollama.md | ollama, dual-backend, rdchat, qwen3, embedding, 萃取品質, thinking, Open WebUI | global |
| toolchain | memory/toolchain.md | 工具鏈, 環境設定, MCPControl, MCP新增, npm全域, 螢幕截圖, Excel MCP, LanceDB, MSYS2, cp950, PowerShell截圖, 向量服務 | global |
| workflow-icld | memory/workflow-icld.md | ICLD, 閉環, Sprint, 功能拆解, 開發計畫, 大型新功能, 新系統規劃, 規格書 | global |
| workflow-rules | memory/workflow-rules.md | 工作流程, 大型任務, 分階段, SOP, 任務拆分, 上版, GIT, Phase | global |
| workflow-svn | memory/workflow-svn.md | svn, svn-update, TortoiseSVN, 衝突, conflict | global |
| memory-pipeline-silent-failure-2026-05 | _AIDocs/Failures/memory-pipeline-silent-failure-2026-05.md | memory-review, memory-health, confirmations, episodic, 晉升, 自我迭代, 衰減掃描, 覆轍偵測 | global |
| cognitive-patterns | _AIDocs/Failures/cognitive-patterns.md | 過度工程, 代理指標, proxy metric, AI看不懂, AI在打轉, 品質回饋, 自我合理化, 編造規則, 籠統話術, 訂規保留, 設計慣例 | global |
| toolchain-batch-cmd-crlf-encoding | memory/toolchain-batch-cmd-crlf-encoding.md | batch, bat, cmd, 批次檔, 閃退, 亂碼, CRLF, LF, 換行, Write工具, adb push, chcp, BOM, 編碼 | global |
| toolchain-svn-powershell-中文log編碼 | memory/toolchain-svn-powershell-中文log編碼.md | svn, svn commit, 中文log, 中文訊息, commit message, 亂碼, -m, -F, git-bash, MSYS, revprop, 中文檔名, 上傳SVN, PowerShell svn | global |
| doc-程式人員ai協作指南 | memory/doc-程式人員ai協作指南.md | AI協作指南, AI 協作, 協作文件, WorkNote, 團隊指南, AI 最佳實踐, 新人 AI 教育 | global |
| feedback-想一下即凍結落檔 | _AIDocs/Failures/feedback-想一下即凍結落檔.md | 想一下, 考慮, 我再看, 待決, 決策中 | global |
| toolchain-win-cmd-cwd-exepath | memory/toolchain-win-cmd-cwd-exepath.md | NoDefaultCurrentDirectoryInExePath, not recognized as an internal or external command, cmd 找不到 bat, msvcbuild, bare name 執行 | global |
| titan-dotnet-split | memory/titan-dotnet-split.md | titan_dotnet, 分家, src/csharp, titan_src, git-filter-repo, 標準 .NET 佈局, build-native, luasocket, 獨立 repo, 自足 | global |
| dotnet-inline-cant-cross-delegate | memory/dotnet-inline-cant-cross-delegate.md | AggressiveInlining, MethodImpl, inline, delegate, event, 介面 vs event, interface dispatch, 摺進去, JIT 反組譯, 收包效能, Slave_OnReceivePacket, DOTNET_JitDisasm, Stopwatch.GetTimestamp, 委派邊界 | global |
| dotnet-string-gethashcode-per-process-randomized | memory/dotnet-string-gethashcode-per-process-randomized.md | GetHashCode, hash 路由, hash 釘定, FNV, consistent hashing, 後端路由 | global |
| toolchain-ps51-getcontent-utf8-file-corruption | memory/toolchain-ps51-getcontent-utf8-file-corruption.md | Get-Content, Set-Content, UTF-8, 中文檔案, PowerShell 改檔, 編碼損毀, hot reload 改檔 | global |
| dotnet-mysqldata-collation-id-相容 | memory/dotnet-mysqldata-collation-id-相容.md | MySql.Data, MySQL, collation, KeyNotFoundException, SetFieldEncoding, net8 升級, connector | global |
| dotnet-sdk10-rid-restore-runtime-pack | memory/dotnet-sdk10-rid-restore-runtime-pack.md | offline build, nuget-offline, RID restore, runtime pack, NU1101, SelfContained, dotnet publish -r, fetch-nuget, 離線建置 | global |
| designexceltodata-優化實況與驗證流 | memory/designexceltodata-優化實況與驗證流.md | DesignExcelToData, 產檔器, Design產檔器, CLI批次, CliRunner, 增量產出, EqualsWithoutHeader, FLAG_ForceGenOutput, GoldenMaster, GenReport, DataValidator, 驗證規則, SrcInfoMap, GenerateOneExcel, CliLastRun | global |
| dotnet-xunit-getentryassembly-testhost | memory/dotnet-xunit-getentryassembly-testhost.md | GetEntryAssembly, testhost, xUnit, 反射掃描, entry assembly, 模組註冊測試, assembly scan, 自動註冊 | global |
