# 專案生態

- Scope: global
- Confidence: [固]
- Trigger: 專案, SGI, TSLG, TCSM, 監控, 專案狀態, 生態
- Last-used: 2026-04-01
- Confirmations: 18
- Related: redmine-config, team-roster, hot-topics

## 知識

- [固] SGI 2.0（戰略新版）：🔴 優先・開發中，監控 Bug、閃退、登入問題
  - 路徑：`C:\Projects\SGI`
  - _AIDocs：有
- [固] TSLG（新案）：🟡 擋雷・DEMO 階段，監控規格卡點
  - 路徑：`C:\Projects\TSLG`
  - _AIDocs：無（Develop/_AIDocs 是 TCSM 的知識庫，不可直接信任）
  - [固] TSLG Develop 是從 TCSM 搬過來並做拆除工程；_AIDocs 內容與 TCSM 一致，但實際程式碼已有落差（部分內容已砍掉），閱讀時需與原始碼交叉驗證
- [固] TCSM（軌跡）：🟢 營運・維護期
  - 路徑：`C:\OlgCase\MobileAnime`
  - _AIDocs：有

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
