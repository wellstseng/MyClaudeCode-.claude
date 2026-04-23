# 專案生態

- Scope: global
- Confidence: [固]
- Trigger: 專案, SGI, TSLG, TCSM, Orbit, Titan, Server, 監控, 專案狀態, 生態
- Last-used: 2026-04-14
- Confirmations: 39
- Related: redmine-config, team-roster, hot-topics, unity-mcp-自動化工具鏈

## 知識

- [固] SGI 2.0（戰略新版）：🔴 優先・開發中，監控 Bug、閃退、登入問題
  - 路徑：`C:\Projects\SGI`（含 Client + Server）
  - _AIDocs：有
  - .claude/memory：無
  - Server 核心：Orbit（`C:\Projects\Orbit`）
- [固] TSLG（新案）：🟡 擋雷・DEMO 階段，監控規格卡點
  - 路徑：`C:\Projects\TSLG`
  - _AIDocs：`C:\Projects\TSLG\_AIDocs\`（已建立，含 Orbit vs Titan 比較分析）
  - .claude/memory：預定 `C:\Projects\TSLG\.claude\memory\`（尚未建立）
  - 注意：`Develop/_AIDocs` 是 TCSM 的知識庫，不可直接信任
  - [固] TSLG Develop（Client）是從 TCSM 搬過來並做拆除工程；_AIDocs 內容與 TCSM 一致，但實際程式碼已有落差（部分內容已砍掉），閱讀時需與原始碼交叉驗證
  - [固] TSLG Server 是從 SGI Server 搬過來的，底層核心同為 Orbit
  - [固] TSLG Server 策略：保留 SGI Server 的底與業務邏輯，參考 Titan 進行大幅度業務與架構重構（非打掉重練）
  - [固] TSLG Server 基建升級已完成（2026-04-08）：.NET 8 + CoreModule 3.0.1 + sgi 跨 repo link 全拔除
  - [固] TSLG Server SVN：`svn://uj-svn.uj.com.tw/PJA146_TSLG/programmer_server/Develop/Server`
  - [固] TSLG Server 知識庫進度文件：`C:\Projects\TSLG\_AIDocs\orbit-merge-progress.md`
- [固] TCSM（軌跡）：🟢 營運・維護期
  - 路徑：`C:\OlgCase\MobileAnime`
  - _AIDocs：有
  - Server 核心：Titan（`C:\Projects\Titan`）
- [固] Orbit（SGI Server Core + TSG 框架）：SGI 後端 Server 核心，並擴展為 Titan-style .NET 框架
  - 路徑：`C:\Projects\Orbit`
  - _AIDocs：有（`C:\Projects\Orbit\_AIDocs\`）— 10 支文件含 Architecture / DB / Net / Data / Config / Peripheral / CommonUtilities / **TsgFamily / Gate**（2026-04-15 新增）
  - .claude/memory：有（`C:\Projects\Orbit\.claude\memory\`）— 含架構、DB、網路、周邊模組、**orbit-tsg**（2026-04-15 新增）
  - 定位：SGI server 的核心框架 + TSLG Server 的出發點 + Titan-inspired TSG 家族（分散式遊戲伺服器 .NET 地基）
  - [固] TSLG 分支：`tslg_1.0`（CoreModule 3.0.2，已整合 NetMQ 4.0.1.13 + Tsg 家族 + GateApp）
  - [固] `Directory.Build.targets` 定義 `USE_NODE_CONNECT` + `_UJ_MODIFY` — 影響所有 CoreModule 編譯
  - [固] **TSG 家族位置**：`CoreModule/Tsg/{Codec,Net,Stack,Gate,Proto}/`（2026-04-15 整併，原 TsgNet/Titan/Rpc-submodule/Protobuf-submodule 全統一）
  - [固] **submodule 全脫鉤**（2026-04-15）：Rpc + Protobuf submodule 刪除，`.gitmodules` 清空，source 併入 CoreModule
  - [固] **GateApp v0 完成**（2026-04-15，commits `746ebff` + `2401737`）：`C:\Projects\Orbit\GateApp\`，TSLG Client 可連 port 21100 完成 LOGIN round-trip
  - [固] 驗證：protobuf-net (titan.Client proto2) 與 Google.Protobuf (Tsg.TsgClient proto3) wire 100% 相容
  - [固] Orbit GateApp 取代 TSLG/Develop/Server/GateApp（後者是 POC，已不是主線）
  - [固] `dotnet build ServerApp.sln -c Release` = 0 errors（2026-04-15）
- [固] Titan（TCSM Server Core）：TCSM 的後端 Server 核心（C + Lua）
  - 路徑：`C:\Projects\Titan`
  - _AIDocs：有（`C:\Projects\Titan\_AIDocs\`）
  - .claude/memory：有（`C:\Projects\Titan\.claude\memory\`）— 含 arch-overview, db-schema, service-topology, lua-bridge
  - 服務：Coord / Gate / Proxy / Account / Log（ZeroMQ 拓撲 + TCP Client Gateway）
  - 注意：應用端邏輯在另外的環境，Titan 是純 server core
  - 定位：TSLG Server 重構時的架構參考對象

## CatClaw 總控工作目錄

- [固] 路徑：`C:\Users\wellstseng\.catclaw`（Git repo，Claude Code 主工作目錄）
- [固] 定位：跨專案整合用總控目錄，不屬於單一專案，專門用於多專案整合作業
- [固] 結構：`catclaw.json`（Discord bot 設定）、`workspace/`（data / reports / scripts）
- [固] 功能：Discord bot、cron 排程、Redmine 報表、跨專案腳本整合

## 行動

- 提到專案優先度時，SGI 2.0 最高
- Redmine 日報/週報以 sgi 為主要追蹤對象
- 操作 TSLG 時，Develop/_AIDocs 只做參考，必須查原始碼確認實際狀態
- TSLG Server 重構時：先查 Orbit _AIDocs/memory 了解現有架構，再查 Titan _AIDocs/memory 了解目標架構
- 跨專案整合任務在 `.catclaw` 下進行，不強求切換到各專案目錄
