# toolchain-batch-cmd-crlf-encoding

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: batch, bat, cmd, 批次檔, 閃退, 亂碼, CRLF, LF, 換行, Write工具, adb push, chcp, BOM, 編碼
- Created-at: 2026-06-04
- Related: toolchain, feedback-tooling-reliability, cognitive-patterns, toolchain-svn-powershell-中文log編碼, vendor-fork-hybridclr-traps

## 知識

- [臨] 用 Write/Edit 工具產 .cmd/.bat 會寫成 LF-only 換行，cmd.exe 必崩（症狀：每行讀到後半段、'xxx' is not recognized 連發、視窗閃退）。真因是 LF≠CRLF，常被誤判成 BOM/碼頁問題
- [臨] 診斷順序：先數位元組 CR(0x0D)/LF(0x0A) 數量，CR=0 即確診 LF-only。不要先猜 BOM/chcp
- [臨] .cmd/.bat 正解：CRLF 換行 + UTF-8 無 BOM + 開頭 `chcp 65001 > nul` 切 UTF-8（與 vendor-fork-hybridclr-traps 對齊，2026-06-15 裁決）。勿加 BOM：BOM 會吃掉 @echo off 第一個字元導致指令回顯；LF 才是閃退主因
- [臨] 寫法：用 PowerShell [System.IO.File]::WriteAllText 配 UTF8Encoding($false)（無 BOM）並先把 \n 正規化成 \r\n；勿用 Write 工具直接產批次檔
- [臨] 驗證批次檔別用 PS pipe + 2>&1（會被 NativeCommandError 包壞）；改 cmd /c "script < nul > out.txt 2>&1" 導檔後再 Read
- [臨] 中文 .cmd 靠檔內開頭 `chcp 65001` 自切 UTF-8（不靠 BOM）。雙擊時 cmd 以系統 OEM 碼頁 cp950(Big5) 啟動，需檔內 chcp 65001 自切；漏了才會亂碼
- [臨] 根治法：批次檔改純 ASCII（英文訊息）+ CRLF。零非 ASCII 位元組 → BOM/碼頁/IDE 全無關，永不再崩。要中文則開頭 chcp 65001 + UTF-8 無 BOM
- [臨] 雙擊 .cmd 的啟動碼頁是系統 OEM(繁中=950)，不是 PowerShell session 的 65001；重現雙擊現場用 cmd /c "chcp 950 >nul & script"

## 行動

- 寫 .cmd/.bat 一律用 PowerShell WriteAllText(UTF8Encoding($false)，無 BOM) + CRLF 正規化 + 檔內開頭 chcp 65001，不用 Write 工具
- 批次檔閃退先數 CR/LF 位元組確診，勿先猜 BOM/碼頁
- 驗證批次檔用 cmd /c 導檔到 txt 再 Read，避開 PS pipe 包裝問題
- 下結論前先實測，勿憑印象斷因（本次曾誤判 BOM）
