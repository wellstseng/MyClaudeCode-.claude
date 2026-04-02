# 專案生態

- Scope: global
- Confidence: [固]
- Trigger: 專案, SGI, TSLG, TCSM, Orbit, Titan, Server, 監控, 專案狀態, 生態
- Last-used: 2026-04-02
- Confirmations: 28
- Related: redmine-config, team-roster, hot-topics

## 知識

- [固] SGI 2.0（戰略新版）：🔴 優先・開發中，監控 Bug、閃退、登入問題
  - 路徑：`C:\Projects\SGI`
  - _AIDocs：有
  - Server 核心：Orbit（`C:\Projects\Orbit`）
- [固] TSLG（新案）：🟡 擋雷・DEMO 階段，監控規格卡點
  - 路徑：`C:\Projects\TSLG`
  - _AIDocs：無（Develop/_AIDocs 是 TCSM 的知識庫，不可直接信任）
  - [固] TSLG Develop（Client）是從 TCSM 搬過來並做拆除工程；_AIDocs 內容與 TCSM 一致，但實際程式碼已有落差（部分內容已砍掉），閱讀時需與原始碼交叉驗證
  - [固] TSLG Server 是從 SGI Server 搬過來的，底層核心同為 Orbit
  - [固] TSLG Server 策略：保留 SGI Server 的底與業務邏輯，參考 Titan 進行大幅度業務與架構重構（非打掉重練）
- [固] TCSM（軌跡）：🟢 營運・維護期
  - 路徑：`C:\OlgCase\MobileAnime`
  - _AIDocs：有
  - Server 核心：Titan（`C:\Projects\Titan`）
- [固] Orbit（SGI Server Core）：SGI 的後端 Server 核心
  - 路徑：`C:\Projects\Orbit`
  - 定位：SGI server 的核心框架，TSLG Server 的出發點
- [固] Titan（TCSM Server Core）：TCSM 的後端 Server 核心（C + Lua）
  - 路徑：`C:\Projects\Titan`
  - _AIDocs：有（`C:\Projects\Titan\_AIDocs\`）
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
- 操作 TSLG 時，_AIDocs 只做參考，必須查原始碼確認實際狀態
- 跨專案整合任務在 `.catclaw` 下進行，不強求切換到各專案目錄
