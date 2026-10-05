# dotnet-interface-devirt-pgo

- Scope: global
- Author: wellstseng
- Confidence: [觀]
- Trigger: guarded devirtualization, devirt, Dynamic PGO, TieredPGO, 介面派發, interface dispatch, callvirt, monomorphic, AggressiveInlining, sealed, JitDisasm, OSR, MethodTable guard, 收包 dispatch, INodePacketHandler
- Created-at: 2026-07-23
- Related: dotnet-inline-cant-cross-delegate, titan-lua-socket-rpc機制-兩版同構

## 知識

- [觀] .NET 8 Dynamic PGO(tiered+PGO 預設開)對 monomorphic 介面呼叫點(欄位/參數靜態型別=介面、執行期單一熱型別)做不做 guarded devirtualization,取決於 callee 能不能 inline,不是取決於型別數量。net8 release scratchpad 反組譯實證(呼叫端 Drive,fgCalledCount≈5040,`optimized using Dynamic PGO`):

| callee 型態 | Tier1+PGO 產物 |
|---|---|
| 小(可 inline) | **guarded devirt + inline**:`cmp qword ptr [rsi], <MethodTable>` + `jne cold`;命中分支把 callee body 直接摺進來(`1 single block inlinees`),cold path 才是真 callvirt |
| callee 標 NoInlining(模擬大 callee) | **連 devirt 都不做**,退回純 `call [r11]IFace:Method`。JIT 判斷 guarded devirt 的收益主要來自後續 inline;不能 inline 就不值得插型別 guard+分支 |
| sealed vs 非 sealed(class+virtual) | guard 完全相同(exact MethodTable 相等比較),`sealed` 對此場景**零增量** |
| Tier1-OSR 版本 | 即使 `with Dynamic PGO` 也**不 devirt**(OSR 最佳化保守),仍純 callvirt |

- [觀] 推論到真實熱路徑:callee 若是大方法(e.g. TitanApp.HandlePacket = ReadRemaining + Log.Info(params 陣列配置+boxing+格式化),IL 大),對應上表「純 callvirt」那格 → PGO 不 inline、甚至不 devirt。此時 callee 上的 [MethodImpl(AggressiveInlining)] 三重無效:(1)介面呼叫點靜態讀不到 callee 的 attr;(2)即使 PGO devirt,callee 太大 attr 放寬的 size 預算也不夠;(3)無 inline 收益讓 PGO 索性不 devirt。移除 attr 是對的。
- [觀] sealed 的真正價值不在『介面呼叫點+PGO』(那裡 guard 本就是 exact 比較)。sealed 幫的是:receiver 靜態型別=具體 class 時的靜態 devirt、或 callvirt 到 sealed 型別可直接去虛擬化——都需要呼叫點看得到具體型別。介面欄位呼叫點看不到,故 sealed TitanApp 對收包 dispatch 無實益。
- [觀] microbenchmark 暖機陷阱:量 call-count 升階的正常 Tier1(非 OSR)時,長內圈會先觸發 OSR 蓋掉正常 tier-1;且 `DOTNET_TC_CallCountingDelayMs` 預設~100ms 內不計數、background tier-1 是異步。可靠作法=短內圈+海量外圈呼叫+`DOTNET_TC_CallCountingDelayMs=0`+尾端 Thread.Sleep 留時間給 background JIT;`DOTNET_TC_OnStackReplacement=0` 有連帶擋 tier-1 的副作用,別用。驗證指令 `DOTNET_TieredPGO=1 DOTNET_JitDisasm="Ns.Type:Method" app.dll`,看 `(Tier1)` 段有無 `cmp ...[receiver], MethodTable`。
- [觀] 效能量級收斂(同 [[dotnet-inline-cant-cross-delegate]] 既有實證):介面跳轉 <2ns 是雜訊;真要優化收包路徑第一刀切 callee 內大頭(每包 Log.Info 的 params/boxing/格式化、每包配置、QPC),不是 dispatch 層。此路徑到每秒數萬~數十萬包前,dispatch 這層都不值得動。

## 行動

- 網路/熱路徑評估『PGO 會不會幫我 devirt 介面呼叫』時,先問 callee 能不能 inline;大 callee 別指望 PGO devirt/inline,也別靠 AggressiveInlining
- 看到有人想靠 sealed 加速介面欄位呼叫點 → 指出 PGO guard 本就是 exact 比較,sealed 零增量;sealed 要幫忙得讓呼叫點看到具體型別
- 反組譯驗 devirt 時用短內圈+CallCountingDelayMs=0+尾端 sleep,避開 OSR 蓋 tier-1 的暖機陷阱
