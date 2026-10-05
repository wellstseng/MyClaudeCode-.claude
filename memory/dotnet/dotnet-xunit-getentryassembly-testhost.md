# dotnet-xunit-getentryassembly-testhost

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: GetEntryAssembly, testhost, xUnit, 反射掃描, entry assembly, 模組註冊測試, assembly scan, 自動註冊
- Created-at: 2026-07-03
- Related: dotnet-string-gethashcode-per-process-randomized

## 知識

- [臨] 2026-07-03 xUnit（.NET Core testhost）下 Assembly.GetEntryAssembly() 回傳 testhost，不是測試組件——所有「掃 entry assembly 自動註冊」的反射路徑（如 orbit HandlerHelper.GetServerModuleTypes/GetClientModuleTypes）在單測中掃不到測試組件內定義的型別，無法直測；副作用是好的：測試專案裡宣告的假模組型別也不會污染其他走真註冊流程的測試
- [臨] 繞法：改測吃顯式參數的同型邏輯路徑——GetModuleHandlers(obj, type) 收 Type、DataModuleUtils.FetchModuleType(dict, assemblyName, …) 收組件名（Assembly.Load("測試組件名") 已載入直接命中），pa index/開放泛型比對邏輯與 entry-assembly 掃描版同型，等效覆蓋

## 行動

- 要測 entry-assembly 反射掃描時，先確認該 API 是否有收 Type/assemblyName 的顯式參數兄弟路徑，測那條
- 在測試專案宣告假註冊型別（attribute 標記類）前，先確認生產掃描路徑是否 GetEntryAssembly——是的話不會互相污染，可放心宣告
