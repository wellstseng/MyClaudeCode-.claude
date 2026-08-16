# coremodule-entry-assembly-拓撲前提地雷-orbit-tslg同dna

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: GetEntryAssembly, 反射掃描, 模組註冊, DataModule, assembly 拆分, 殼專案, GetModule null, Orbit CoreModule, tslg-servercore, 靜默失敗, HandlerHelper
- Created-at: 2026-07-28
- Related: project-ecosystem, arch-rules, wells-design-principles-明碼優先-職責分離-防呆擋非法

## 知識

- [觀] Orbit 與 tslg-servercore 的 CoreModule 同 DNA（後者自前者 fork），原型別發現全走 `Assembly.GetEntryAssembly().GetTypes()` 掃 attribute/繼承，隱含拓撲前提「entry assembly＝實作 assembly」。實作拆進共用 dll（如 TSLG GameCore → Game.Core.dll，exe 變殼）後掃描靜默回空，GetModule<T>() 全 null，到事件掛載/dereference 才 NRE，離根因很遠
- [觀] TSLG 側已改明碼註冊（tslg-servercore a93574c + SVN r1646，2026-07-28）；Orbit 本家未改，地雷仍在——SGI 2.0 若做 assembly 拆分/共用化重構會在同點同樣方式爆
- [觀] 同病點清單（掃 entry assembly 或字串 assembly 名）：HandlerHelper.GetServerModuleTypes/GetClientModuleTypes（TSLG 已刪，Orbit 仍在）、DataModuleUtils.FetchModuleType(Assembly.Load)、DataModuleDB、應用端 AutoRegisterManagers/[ClientController] 掃描、GmServer MAP_DLL 字串。FetchModuleType 的 try/catch 會吞掉 Assembly.Load 失敗（雙重靜默）
- [觀] 偵測法：掃描式註冊系統的健康檢查＝起服時驗證註冊數非零/符合預期；掃到 0 個應 throw 而非繼續

## 行動

- 碰 Orbit/tslg-servercore 模組註冊相關代碼時先對照此清單
- 任何專案規劃 assembly 拆分前，先 grep GetEntryAssembly/Assembly.Load 盤點拓撲前提依賴
