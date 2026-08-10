# vscode-csdevkit-鎖目錄擋-git-mv-逐子項繞過

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: git mv, Permission denied, csdevkit, C# Dev Kit, rename directory, 目錄鎖, 搬遷, build-server
- Created-at: 2026-07-12
- Related: toolchain, toolchain-win-cmd-cwd-exepath

## 知識

- [臨] 2026-07-12 Windows 下 VS Code C# Dev Kit(CPS 常駐 dotnet 程序)持有專案目錄 handle,git mv 整目錄報 fatal: Permission denied(目錄 rename 需 DELETE 權限,任一開啟 handle 即擋)。鎖在目錄本身而非內容——逐子項 mv 全數成功可繞過(實證:tslg-servercore-lua LuaModule/native 整搬失敗、7 個子項個別搬全過)。
- [臨] dotnet build-server shutdown 對此無效(鎖主是 Dev Kit 非 Roslyn/MSBuild server)。殘殼空目錄待 Dev Kit reload 專案(csproj 從 sln 移除後)自然鬆手,稍後 rm 即可。鎖主辨識:Get-CimInstance Win32_Process -Filter "Name='dotnet.exe'" 看 CommandLine 含 csdevkit/CPS。

## 行動

- 搬遷目錄撞 Permission denied:先逐子項 mv 繞過,殘殼收尾再刪;勿殺 Dev Kit 程序(使用者編輯器在用)
