# dotnet-sdk10-rid-restore-runtime-pack

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: offline build, nuget-offline, RID restore, runtime pack, NU1101, SelfContained, dotnet publish -r, fetch-nuget, 離線建置
- Created-at: 2026-07-02

## 知識

- [臨] SDK 10（10.0.300 實測）下 `dotnet restore -r <RID>` 強制把 runtime pack（Microsoft.NETCore.App.Runtime.{rid}，連 WindowsDesktop/AspNetCore 家族也拉）納入 restore 圖，`/p:SelfContained=false` 擋不掉；`/p:DisableTransitiveFrameworkReferenceDownloads=true` 只能去掉 WindowsDesktop/AspNetCore 兩家族，NETCore.App.Runtime 仍必拉。影響：離線 NuGet 源（titan/orbit nuget-offline 模式）若排除 runtime pack，neutral build/test 離線 OK 但 RID restore/publish 必 NU1101
- [臨] 正解分層：離線保證劃在 neutral build/test；RID 發布離線另跑 fetch 腳本的 -SelfContained 開關把 runtime pack 全家族收進離線庫（+約180MB）。orbit 實例：tslg-servercore/fetch-nuget.ps1（2026-07-02 P1S2）
- [臨] 附帶坑：離線 nuget.config 的 XML 註解內不能寫 `--source`（XML 註解禁 `--`），restore 會報 NuGet.Config is not valid XML；另 WSL 部分複製 repo 驗證時 Directory.Build.targets（AllowUnsafeBlocks 等全域屬性）必須隨行，漏了會 CS0227

## 行動

- 規劃離線 build 時明確分層：neutral build/test vs RID 發布，後者需 runtime pack 全收
- 碰 NU1101 Microsoft.NETCore.App.Runtime.* 先查離線源是否排除 runtime pack，勿盲調 SelfContained 屬性
