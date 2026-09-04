# toolchain-svn-powershell-中文log編碼

- Scope: global
- Author: wellstseng
- Confidence: [固]
- Trigger: svn, svn commit, 中文log, 中文訊息, commit message, 亂碼, -m, -F, git-bash, MSYS, revprop, 中文檔名, 上傳SVN, PowerShell svn
- Created-at: 2026-06-10

- Related: doc-程式人員ai協作指南, toolchain-batch-cmd-crlf-encoding, toolchain-ps51-getcontent-utf8-file-corruption, workflow-svn

## 知識

- [固] SVN 中文 commit log 必走 -F UTF-8無BOM 檔 + --encoding utf-8；禁用 -m 直傳中文。不只 PowerShell 5.1(CP950 傳參交)會亂，**git-bash/MSYS 的 -m 中文同樣會亂**（MSYS argv 編碼轉換損壞）— 2026-07-03 r1400 實際踩雷：為繞中文**檔名**用 git-bash svn commit exe，卻順手用 -m 中文→log 存進 repo 即亂碼
- [固] 關鍵區分：中文**檔名**編碼問題(PowerShell 5.1 傳中文 argv/targets 檔給原生 svn.exe 都損) ≠ 中文 **log**編碼問題。兩者分開解：檔名用 git-bash(UTF-8 argv 可正確傳中文檔名給 svn.exe)或 TortoiseSVN GUI；log 永遠走 -F UTF-8檔。即使已用 git-bash 繞檔名，log 仍不可用 -m
- [固] 驗證 log 真實編碼：svn log 在 console 顯示亂碼不代表 repo 內就是亂(可能只是顯示編碼)。確認真實內容用 `svn log -r N --xml` 經 cmd /c 重導向寫檔再以 [IO.File]::ReadAllText(...UTF8) 讀回 <msg> — --xml 強制 UTF-8 輸出，繞開 console 編碼
- [固] Server 鎖 revprop（E165006 Repository has not been enabled to accept revision propchanges）：commit 後 log 亂碼 **無法自行修正**（propset --revprop 遭拒），需管理員開 pre-revprop-change hook。防線全在上傳前：commit 前先 Get-Content 讀回訊息檔確認、commit 後立即 --xml 驗 log，發現異常立即通報使用者

## 行動

- 中文 log 一律 -F UTF-8無BOM檔 + --encoding utf-8；任何 shell(含 git-bash)都絕不用 -m 傳中文
- 中文檔名提交→git-bash svn 或 TortoiseSVN GUI；PowerShell/targets 檔對中文檔名皆損
- commit 後立即 `svn log -r N --xml`→cmd 重導向→UTF-8 讀回驗 <msg>；別信 console 顯示
- log 已亂且 server 鎖 revprop → 無法自修，即通報使用者轉管理員
