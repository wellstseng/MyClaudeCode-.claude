# SVN Windows 中文 Commit Log 編碼陷阱

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: SVN, commit log, 中文, UTF-8, CP950, Windows, 亂碼, encoding, BOM, commit message, svn:log
- Last-used: 2026-05-27
- Confirmations: 11
- Created-at: 2026-04-30
- Related: workflow-svn

## 知識

- [臨] Windows 上 svn ci -F message.txt 預設用 native codepage（CP950）讀 message file，UTF-8 中文會被誤判轉碼後存進 repo → 爛字元（不可逆，repo 端 svn:log 通常未開放修改）
- [臨] 修法：commit message 必須寫成 BOM UTF-8 檔 + 命令列加 --encoding UTF-8。PowerShell 寫法：`[System.IO.File]::WriteAllText($path, $msg, (New-Object System.Text.UTF8Encoding $true))`（第二參 true = 加 BOM）
- [臨] 驗證 repo 內容是否真的存對，不能只看 `svn log -r N`（終端 codepage 會二次破壞顯示）。要用 `svn log -r N --xml`：XML 強制 UTF-8 規範，能成功 parse 就代表 repo 內容是正確 UTF-8
- [臨] 用 hex 比對：正確存的 UTF-8 中文應該是 e4-e9 開頭的 3-byte 序列；如果看到 3f（問號）+ ee/e2 + a0-bf 等私人使用區字元混雜，就是寫入時被誤轉碼了
- [臨] 已 commit 的爛 log 若 repo svn:log 未開放修改，唯一補救：對任一受影響檔做小修整、重 commit 一次，新 commit log 寫清楚『補上 rN 的 commit log（編碼亂碼）+ 原意說明』。SVN 不接受空 commit，必須有實質檔案差異
- [臨] 用 PowerShell 讀回驗證：`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; ([xml](svn log -r N --xml PATH)).log.logentry.msg` 可正確顯示中文

## 行動

- 寫中文 commit message 前一律先建 BOM UTF-8 檔，再 svn ci -F file --encoding UTF-8
- commit 後立刻 svn log -r N --xml 驗證一次（不能只看 svn log -r N）
- 若發現 r 已爛掉：對檔案做小修整 + 重 commit 補 log，不要嘗試 svn propedit svn:log（多數 server 沒開）
- Bash 環境下也用 PowerShell 寫 message file（PowerShell 對 UTF-8 BOM 控制較直接）
