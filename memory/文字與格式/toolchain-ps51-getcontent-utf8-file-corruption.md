# toolchain-ps51-getcontent-utf8-file-corruption

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: Get-Content, Set-Content, UTF-8, 中文檔案, PowerShell 改檔, 編碼損毀, hot reload 改檔
- Created-at: 2026-07-02
- Related: toolchain-svn-powershell-中文log編碼, toolchain-batch-cmd-crlf-encoding

## 知識

- [觀] PS 5.1 `Get-Content`（無 -Encoding）讀無 BOM 的 UTF-8 檔案時用 ANSI（台灣系統 = CP950）解碼；UTF-8 中文字尾位組若落在 CP950 lead byte 範圍會吞掉緊接的換行符，行結構被破壞（兩行併一行）。round-trip 寫回（Set-Content）後檔案實質損毀——Lua 腳本案例：中文註解行吞掉換行→下一行 `local X = ...` 被併進註解→變數變 nil，載入不報錯、執行才炸（2026-07-02 P2S3 E2E 實踩）
- [觀] 修改含非 ASCII 內容的檔案一律用 `[IO.File]::ReadAllText/WriteAllText($f, $s, (New-Object Text.UTF8Encoding($false)))` 或 Claude 的 Edit/Write 工具；另注意 PS 5.1 `-Encoding utf8` 寫出會帶 BOM
- [固] 同根因新變體（2026-07-11 tslg-servercore-lua build-native.ps1 實踩）：AI Write 工具產出的 .ps1 預設 UTF-8 無 BOM——powershell.exe 5.1 執行無 BOM 檔按系統 ANSI(CP950) 解碼，中文註解變亂碼且可能吞掉換行/產生語法噪音，**症狀不是語法錯誤而是靜默行為異常**（該次：dumpbin 匯出抽查在互動重現全過、-File 執行必失敗，考掉半小時）。修法：寫完 ps1 立即以 [IO.File]::WriteAllText(path, text, [Text.UTF8Encoding]::new($true)) 補 BOM；.sh/.c 等非 PS 檔維持無 BOM。判別法：head -c 3 | xxd 看 EF BB BF

## 行動

- 禁用 PS 5.1 Get-Content/Set-Content 裸呼叫做中文（或任何非 ASCII）檔案的讀改寫 round-trip
- 改完檔若行為詭異（變數變 nil、行數對不上）先懷疑編碼 round-trip 損毀
