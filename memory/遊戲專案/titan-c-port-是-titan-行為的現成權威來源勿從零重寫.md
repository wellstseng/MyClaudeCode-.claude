# titan C# port 是 titan 行為的現成權威來源（勿從零重寫）

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: titan 移植, C# port, goo_log, log.lua, LogSchema, GooLogBridge, titan C 原始碼, 41 符號, Titan.Log, Titan.Lua
- Created-at: 2026-08-13
- Related: titan-lua-socket-rpc機制-兩版同構, titan-dotnet-split, titan-c-移植鐵則-優先用csharp設施-架構為師細節可精進

## 知識

- [觀] `C:\Projects\Titan\src\csharp\` 有一份完整的 titan C# port（Titan.Core/Net/Lua/Log/Account/Gate/Proto/App + 各自的 Tests），不是骨架，是照 C 原始碼逐行對齊的實作。
- [觀] 其中 `Titan.Log/`（LogSchema/LogBinder/LogDb/LogApp，1300+ 行）＝ C 儲存引擎（app/log/log.c、log_schema.c、log_stmt.h）的 C# 版；`Titan.Lua/Goo/GooLogBridge.cs` + `TitanGoo.Bridge.cs` 已綁齊 log.lua goo.cdef 要的 41 個 `goo_log_*` 符號，並含 goo 專用路徑（AddTableRaw / AttachFromGoo）。
- [觀] titan C 原始碼在 `C:\Projects\Titan\src\app\`；DDL 真相在 `log_stmt.h`：CREATE TABLE 只建 `id` 主鍵，其餘欄位一律 `ALTER TABLE ADD`，timestamp 與索引同樣走 ALTER（不是一發 CREATE TABLE 含全欄）。
- [觀] tslg-servercore 的 CoreModule 沒有這塊（TitanGoo 只綁 5 個核心符號）——「C# 版沒 port」的判斷只對 CoreModule 成立，對 Titan repo 不成立。

## 行動

- 要在 CoreModule/TSLG 實作任何 titan 既有行為前，先查 `Titan/src/csharp/` 有沒有現成 port，再查 `Titan/src/app/` 的 C 原始碼；兩者都在本機，不必憑記憶或猜。
- 移植時保留語意、只換基礎設施（例：DB 層 MySqlConnector → Sqlx）；語意層的怪邏輯照抄不要「順手優化」，那是 P4 對拍的基準。
