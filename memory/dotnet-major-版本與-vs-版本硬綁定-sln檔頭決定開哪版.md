# dotnet-major-版本與-vs-版本硬綁定-sln檔頭決定開哪版

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: NETSDK1209, net10, .NET 10, VS 2026, Visual Studio 18, TFM 升級, LTS 升級, sln 檔頭, VisualStudioVersion, IDE 建不起來, CLI 能建 VS 不能建
- Created-at: 2026-08-20
- Related: dotnet-sdk10-rid-restore-runtime-pack, toolchain, titan-dotnet-split

## 知識

- [觀] .NET major 版本與 Visual Studio 版本**硬綁定、無 workaround**：VS 17.x(2022) 最高只支援 net9，目標 net10 在 IDE 內開必報 NETSDK1209「目前的 Visual Studio 版本不支援將 .NET 10.0 設定為目標」。net10 需 VS 18.0+（＝**Visual Studio 2026**，微軟自此改純數字版號、不再冠年份）。閘門在 SDK targets `Microsoft.NET.TargetFrameworkInference.targets` 的 `_CheckForUnsupportedNETCoreVersion`：條件含 `BuildingInsideVisualStudio=='true'` 且 `MSBuildVersion < MinimumVisualStudioVersionForUnsupportedTargetFrameworkVersion`——**只擋 IDE 內建置**（2026-08-20 tslg-servercore/TSLG net8→net10 實踩）
- [觀] 由此產生的典型誤判現象：**CLI `dotnet build` 全綠、VS 開起來卻整排紅**。原因是兩者解析到不同 SDK——CLI 走最新版（實例 10.0.302），VS 走它自己支援上限內的最高版（實例 9.0.316，錯誤訊息裡的路徑會露餡）。診斷起手式：看錯誤訊息中的 SDK 路徑版號，不是看 `dotnet --version`
- [觀] `.sln` 檔頭的 `# Visual Studio Version N` / `VisualStudioVersion = N.x` 決定**按兩下時 VSLauncher 挑哪一版 IDE**。升 TFM 後若不同步改檔頭，即使新版 VS 已裝好，按兩下仍被導去舊版 → 撞同一個錯，看起來像「升級失敗」。同機多版 VS 可並存（實例清單在 `C:\ProgramData\Microsoft\VisualStudio\Packages\_Instances\*\state.json`，含 workloads；舊版 vswhere.exe 認不得 VS 18、回空，要改查此處或直接讀 devenv.exe 的 ProductVersion）
- [觀] 改 sln 檔頭的 regex 地雷（本次實際踩中）：`VisualStudioVersion = [\d.]+` **未加行首錨點會連 `MinimumVisualStudioVersion` 一起改掉**（後者字串包含前者）。`MinimumVisualStudioVersion` 是相容性下限（慣例 10.0.40219.1）**不該動**，被改成新版號會讓舊 VS 拒開方案。正解：regex 加 `^` 錨點或 multiline，改完務必 diff 逐行驗

## 行動

- 升 TFM 跨 major 版本前，先確認團隊 IDE 版本能否支援——這是比套件相依更硬的前置條件，且屬全團隊協調成本（每人都要裝新 VS），須先與團隊對齊再動手
- 遇「CLI 能建、VS 不能建」先看錯誤訊息裡的 SDK 路徑版號，判斷是版本閘還是真編譯錯
- 升 TFM 時 .sln 檔頭 VS 標記一併更新（只改 VisualStudioVersion 兩行，MinimumVisualStudioVersion 留原值），否則按兩下仍開舊 IDE
- 查同機 VS 版本用 _Instances\*\state.json 或 devenv.exe ProductVersion，別只信 vswhere（舊版不認新 VS）
