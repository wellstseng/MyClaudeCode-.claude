# orbit-hotfix-lua-direction

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: Orbit, 熱修, 熱更, hotfix, Lua導入, LuaJIT, 郁方, 團隊簡報, shim-less, titangoo, 指標注入
- Created-at: 2026-07-13
- Related: lua-bridge, project-ecosystem, decisions-architecture, titan-lua-socket-rpc機制-兩版同構

## 知識

- [臨] 方向：Orbit server 熱修採 Lua 熱更，參考 Titan 架構但走 shim-less 直綁（C# ↔ Lua 兩層，無 C 中介：UnmanagedCallersOnly 指標經 lightuserdata 注入 __goo_ptrs 全域表 → Lua ffi.cast 快取直呼）。理由：符合郁方需求 + 團隊最熟悉——TSLG servercore（tslg-servercore-lua）已落地實證（94e2776，titangoo shim 與 dotnet.call 整層拆除，+167/−919，測試全綠）
- [固] 選型論證：市面 C# Lua 方案吃不到 LuaJIT——MoonSharp=純 C# 直譯器（最慢）；NLua/KeraLua=native binding 但綁官方 Lua 5.4。LuaJIT 優勢雙重：JIT 執行快 + ffi 跨界呼叫近零開銷（編成近乎裸 call，ffi.cast 函式指標與具名符號同速），NLua 類每次跨界都有 wrapper 稅
- [固] 介面窄=可枚舉白名單：核心熱路徑收斂至個位數專屬 call（TSLG 現況五符號），加 call SOP 四行（C# UnmanagedCallersOnly＋Exports 一行／Lua typedef＋cast 一行）；不帶泛用通道——dotnet.call 是「加符號五站鏈成本」的解藥，shim-less 下成本歸零故不需要，實需時後補=多注入一個指標
- [臨] shim 存在理由考證（為何 Orbit 不需要）：titan C 版 goo_* 是行程原生符號、無 shim；titangoo.dll 是 titan_dotnet 為讓 titan Lua 腳本按名 cdef 寫法不改而生的相容性道具（C# 無法具名匯出）。腳本自持的專案從第一天就沒有它的存在理由。注意：若原樣搬 titan entities.lua 則不等價——其封包路徑真用 goo 配置器，需先改寫借用式
- [固] 風險論述關鍵句（簡報用）：C#↔Lua ffi 邊界是「結構上唯一沒有編譯期保護的地方」——C# delegate* cast 有編譯期檢查、Lua 端 typedef 字串只在執行期對齊，錯了不報錯直接靜默踩記憶體 → 測試是取代編譯器的唯一防線；驗證火力集中此處是結構推導，不是經驗猜測
- [固] 記憶體鐵則兩條：慢 I/O（Mongo 類）不同步過橋（卡 tick），走非同步 op：發起 call 立刻返回 + 每 tick poll 收割；C#→Lua 動態 buffer 一律借用協定（Lua 拿到立刻 ffi.string 複製、指標不外流，包進 wrapper 讓業務碼摸不到），禁「C# 配、Lua 放」——行程內無中立配置器，跨 CRT free = heap corruption
- [固] 團隊簡報敘事順序：方向（參考 Titan、去其歷史包袱）→ 原理（UnmanagedCallersOnly 指標注入 + ffi.cast，delegate 概念）→ 選型理由（LuaJIT 效能 + 市面方案缺口）→ 風險收斂（窄介面 + 邊界測試 + 借用協定）
- [臨] Lua 端 protobuf 選型定案（2026-07-21，tslg 66e2fdc 落地）：lua-protobuf 0.5.3（單檔 pb.c＋protoc.lua 純 Lua 執行期解析 .proto），非 titan 同款 pbc——pbc 需預編 proto.pb 管線且停止演進；兩者 API 幾乎同形，唯一縫收在 scripts/lib/pb.lua 門面（titan lib/pb 對位），換引擎只動這一片。分工鐵則：Lua 只序列化 payload（pb bytes），Packet 信封（opcode/佇列/refcount/socket）鎖宿主，殼 (netId,buf,len) WriteRaw 不透明轉發（titan goo_rpc_*_send 同構）。加 message SOP：放 .proto ＋ wrapper register 一行，零重編
- [固] lua-protobuf 64-bit 鐵則：LuaJIT(5.1) 路徑下純數字字串會被 lua_tonumber 先轉 double（u64 max 直接報 number has no integer representation）——64-bit 欄位進出一律 '#'+十進位字串（'#123'/'#-123' 走精確逐位解析；decode 配 pb.option int64_as_string 回同形）

## 行動

- Orbit 導入時直接以 TSLG servercore 拆除後版本為範本：CoreModule/Lua/{TitanGoo.cs,LuaHost.cs} + scripts/core/goo.lua（94e2776）
- LuaBridge_Cookbook.md 仍是 shim 架構描述（重寫待辦）——重寫前以 _CHANGELOG 2026-07-21 條目為現況正典
- 被細問「固定幾個 API」時：核心熱路徑收斂至個位數槽位，慢 I/O 走 op 佇列——比模糊的「幾個」更有說服力
- 方向拍板（郁方確認/立項）後將 [臨] 升 [固] 並補記決策日期於 _AIDocs/DevHistory
