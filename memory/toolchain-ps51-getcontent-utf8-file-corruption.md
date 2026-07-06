# toolchain-ps51-getcontent-utf8-file-corruption

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: Get-Content, Set-Content, UTF-8, 中文檔案, PowerShell 改檔, 編碼損毀, hot reload 改檔
- Created-at: 2026-07-02
- Related: toolchain-svn-powershell-中文log編碼, toolchain-batch-cmd-crlf-encoding

## 知識

- [臨] PS 5.1 `Get-Content`（無 -Encoding）讀無 BOM 的 UTF-8 檔案時用 ANSI（台灣系統 = CP950）解碼；UTF-8 中文字尾位組若落在 CP950 lead byte 範圍會吞掉緊接的換行符，行結構被破壞（兩行併一行）。round-trip 寫回（Set-Content）後檔案實質損毀——Lua 腳本案例：中文註解行吞掉換行→下一行 `local X = ...` 被併進註解→變數變 nil，載入不報錯、執行才炸（2026-07-02 P2S3 E2E 實踩）
- [臨] 修改含非 ASCII 內容的檔案一律用 `[IO.File]::ReadAllText/WriteAllText($f, $s, (New-Object Text.UTF8Encoding($false)))` 或 Claude 的 Edit/Write 工具；另注意 PS 5.1 `-Encoding utf8` 寫出會帶 BOM

## 行動

- 禁用 PS 5.1 Get-Content/Set-Content 裸呼叫做中文（或任何非 ASCII）檔案的讀改寫 round-trip
- 改完檔若行為詭異（變數變 nil、行數對不上）先懷疑編碼 round-trip 損毀
