# toolchain-win-cmd-cwd-exepath

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: NoDefaultCurrentDirectoryInExePath, not recognized as an internal or external command, cmd 找不到 bat, msvcbuild, bare name 執行
- Created-at: 2026-06-12

- Related: vscode-csdevkit-鎖目錄擋-git-mv-逐子項繞過

## 知識

- [臨] 本機（wellstseng Win11）設有 NoDefaultCurrentDirectoryInExePath：cmd 從 CWD 以 bare name 執行 bat/exe 一律報 'not recognized'，但 dir/if exist 看得到檔案，極難診斷。解法：(1) 給絕對/顯式相對路徑（.\xxx.bat）；(2) 若第三方建置腳本內部用 bare name（如 LuaJIT msvcbuild.bat 呼 minilua/buildvm），在 runner 開頭 set NoDefaultCurrentDirectoryInExePath= 清掉該環境變數即恢復 CWD 搜尋。實例：Titan src/csharp/native/build-native.ps1。

## 行動

- （依知識內容判斷）
