# titan-c-移植鐵則-優先用csharp設施-架構為師細節可精進

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: titan 移植, TitanC, C 移植, goo_log, log.c, 移植鐵則, C# 設施, port, 照抄, 簡化
- Created-at: 2026-08-14
- Related: titan-c-port-是-titan-行為的現成權威來源勿從零重寫, orbit-hotfix-lua-direction, titan-dotnet-split

## 知識

- [觀] Wells 裁定（2026-08-15，tslg-servercore log.lua 串接 LogEngine 案）：Titan C 功能移植鐵則——優先以 C# 原生設施進行移植（例：GCHandle/void* 對照表可用 C# 物件模型＋純值 ABI 取代；native 字串配置可用借用協定 scratch buffer 取代）。
- [觀] Titan C 參考的是其設計架構（分層、生命週期、語意序列），細節可精進、簡化——不照抄 C 的指標管線與資源管理形狀。與 atom titan-c-port（語意照抄、勿順手優化）的分界：語意/行為序列仍照抄為對拍基準；基礎設施與 ABI 形狀按 C# 慣用法重設計。語意怪癖遇性能疑慮或潛在 bug 應優化，且優化必須兩側一致（Lua 與 C# 服務層同步或載明對拍白名單）。
- [觀] 首例：log 綁定殼去指標化——titan 39 支 void* ABI 收斂為 28 支純值符號（schema 域 12→1 走 JSON 投影、req 域隱式 current、字串借用協定），GooMem/GooHandles 整層不移植。
- [觀] Wells 裁定（2026-08-26，entities 復刻討論）約束本鐵則的『可精進』適用時機：採**兩階段分離、先完整移植再優化**——移植期照藍本（entities_titan.lua）原樣搬，含 action 狀態機等內部實作，只微調接口對上既裁現況（gate 歸 C#、Node 已拆、BaseEntity 已分、AppData 對位）；簡化/重寫留到移植完成、行為驗證過後的獨立階段提案。理由：邊搬邊優化分不清差異是精進還是搬錯。已上線既裁偏離（純 Lua timer、chan 2 條聚合）維持現狀不溯及；後續段落（get_async、action 機、Query/Archiver 接線）一律先照抄，優化點記 _staging/ 待移植完再提。
- [觀] 裁定澄清（2026-08-26 晚，Wells 退版 e16fe0e）：「先完整移植」的執行方式≠挑零頭逐段接（get_async 單搬那種），而是 **entities.lua 以藍本整檔為基準照搬**，只挖掉已知拆出者（gate 驗證歸 C#、client 域→client.lua、Node 已拆）；chanq、action 佇列、timer 等內部機制一律照搬，沒有 MongoDB 也不阻擋（DB handler 呼叫點到 Query 橋通了才活）。我自劃的「既裁偏離不溯及」線被否決：純 Lua timer、同步 create 這些都要扲回藍本形。e16fe0e（零頭式 get_async 段）已 revert（da6e59c）。

## 行動

- 在 CoreModule/TSLG 移植 titan C 行為時：先讀 titan C/C# port 取語意權威，再以 C# 設施重新表達邊界與資源管理，勿照抄指標形狀
- 與對拍測試並用：架構簡化的正當性由逐字對拍背書
