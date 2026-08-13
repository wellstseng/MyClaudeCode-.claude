# titan-dotnet-split





- Scope: global


- Author: wellstseng


- Confidence: [觀]


- Trigger: titan_dotnet, 分家, src/csharp, titan_src, git-filter-repo, 標準 .NET 佈局, build-native, luasocket, 獨立 repo, 自足


- Created-at: 2026-06-13


- Related: csharp-port, dotnet-inline-cant-cross-delegate, dotnet-mysqldata-collation-id-相容, titan-lua-socket-rpc機制-兩版同構





## 知識





- [觀] 2026-06-14 src/csharp 已 git-filter-repo 分家為獨立 repo titan_dotnet（remote ssh://git@gitlab.uj.com.tw:2224/Titan/titan_dotnet.git，main），與 C 版 titan_src 完全獨立、各持共用件副本；保留 21 commits .NET 移植歷史。標準 .NET 佈局：根 Titan.sln/publish.ps1/native/_AIDocs/conf + 專案在 src/Titan.* + deps(luajit21/luaclib/lz4/mongoc/pbc)/scripts/res/lib 各持副本。雙平台自足驗證全綠（Win 177/0/0；WSL 155過0失敗22skip=基線）


- [觀] 分家自足三大隱性缺口（grep '..\..\..' 抓不到）：①deps 清單漏 pbc（build-native protobuf clib 需要，已補第五項）②build-native.sh 漏裝 luasocket 純 Lua 件 socket.lua/ltn12/mime（被 gitignore、C 版靠 cmake luasocket install 落地，分家後 WSL proxy/rest/trail 測試報 module 'socket' not found；已補 --install 從 deps/luaclib/luasocket/src 複製，對齊 build-native.ps1 208-214）③測試夾具 4 檔 Path.Combine 硬編 'src','csharp','Titan.Lua.Tests'（分家後 csharp 段消失，TITAN_RES 指錯 → init.lua 全掛）


- [觀] 分家附帶決策：剪除 lib/sys/centos6（2070 檔 C 版 CentOS6 執行期遺留、.NET 零引用、含 Windows 不相容 symlink，正是 tar 解壓失敗主因）；帶入 .gitattributes（* eol=lf + *.sh eol=lf，保 build-native.sh 在 WSL checkout 不被 CRLF 汙染 shebang）；build-native.sh 設 755


- [觀] titan_dotnet 環境相依件（gitignore、非 repo 缺陷，各平台自備）：lib/nodejs/node_modules 須各平台 npm install（zeromq 原生綁定，Windows copy 到 Linux 會讓 ZsockJs 測試 30s timeout）；WSL NuGet 快取從 /mnt/c rsync 後 grpc.tools protoc/grpc_csharp_plugin 需 chmod +x（fmask 剝 execute 位）；WSL 測試需 docker titan-mysql(3307) + TITAN_TRAIL_ROOT=/mnt/c/OlgCase/.../Titan + TITAN_NODE=vendored node

- [觀] 2026-06-15 離線自足雙軌入庫：NuGet（nuget-offline/ 57 nupkg + nuget.config 鎖源）＋ npm（lib/nodejs/node_modules 65M/6138 檔，zeromq 四平台 prebuilds linux-x64/win32-x64/win32-ia32/darwin-x64 自足）→ fresh clone 零連網即可 build/test/publish。重建：fetch-nuget.{ps1,sh} / fetch-npm.{ps1,sh}（後者 node18 守門 + npm ci 鎖版，--update/-Update 升版改 lock）。.gitattributes 加 lib/nodejs/node_modules/** -text 保 vendored 原樣（zeromq 自帶 .gitattributes 更精細故沿用）。

- [觀] TitanREST 跑前必清 ELECTRON_RUN_AS_NODE：VSCode/Electron 遺留會讓 zeromq node-gyp-build 誤判 runtime=electron、找不到 prebuild 而炸；publish wrapper（publish.sh:132 / publish.ps1:178）與 Titan.Rest launcher 已內建清除。實證 node18 清掉後 zeromq/express/protobufjs/pm2 全 load 成功。
- [觀] titan_dotnet 專案根目錄 = C:\Projects\titan_dotnet（與目前 Orbit session 不同專案，檔案層可讀，知識不自動注入本 session context）。知識庫 = 根目錄下 `_AIDocs/`（10+ 份文件：Architecture_Overview、CSharp_Port{,_Map,_Plan,_Runbook,_Benchmark,_Verify_Linux,_Verify_Windows}、Config_Reference、Database_Schema 等）。專案級 .claude 在 `C:\Projects\titan_dotnet\.claude`。標準 .NET 佈局：根 Titan.sln/publish.{ps1,sh}/build-native.{ps1,sh}、src/、共用件 deps/scripts/res/lib、native/conf 在根。

## 行動





- 改 titan_dotnet 相對路徑：sln 在根、專案在 src/、共用件(deps/scripts/res/lib)在根、native/_AIDocs/conf 在根；csproj ProjectReference 同層不變，但 res/conf/native link 依新深度重對基


- wire 格式真相在 titan_src repo 的 C 源碼（src/titan、src/app）；動 wire 前先讀 C 源


- 驗證自足一律從全新 clone 跑 build-native + dotnet build/test + publish smoke，勿用既有 build 樹


