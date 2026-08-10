# dotnet-inline-cant-cross-delegate



- Scope: global

- Author: wellstseng

- Confidence: [臨]

- Trigger: AggressiveInlining, MethodImpl, inline, delegate, event, 介面 vs event, interface dispatch, 摺進去, JIT 反組譯, 收包效能, Slave_OnReceivePacket, DOTNET_JitDisasm, Stopwatch.GetTimestamp, 委派邊界

- Created-at: 2026-06-19

- Related: toolchain, titan-dotnet-split, dotnet-interface-devirt-pgo



## 知識



- [臨] inline(含 [MethodImpl(AggressiveInlining)])只能跨 direct call,永遠跨不過 delegate/event 邊界。net8 反組譯三接法實證(同一個掛 AggressiveInlining 的 helper):(A)介面 impl 內 direct call → helper 被摺進呼叫者(甚至可能再被 devirt 摺進更上層);(B)event 直接 `+= obj.Helper` → helper 被「單獨編譯成 method」,attr 完全失效變死碼,經間接 Action.Invoke 到達;(C)event `+= x => obj.Helper(x)` → helper 摺進 lambda,但 lambda 自己變成摺不掉的 target。

- [臨] 關鍵守恆:每條路徑都剛好只有「一次摺不掉的間接跳躍」(介面 dispatch ≈ delegate invoke),工作只跑一次。摺不摺只決定那份工作物理上住在跳躍的哪一邊,不增減 hop 數 → 所以介面 vs event 計時相等。

- [臨] tslg-servercore 收包路徑微基準(net8 release, DOTNET_TieredCompilation=0, 100M×12): EMPTY body 介面+inline 2.69 / 介面+noinline 2.90 / event 2.90 ns/op(介面≈event 證實);REAL body(真實 Slave_OnReceivePacket 工作量)~20.7ns,大頭是每包都打的 Stopwatch.GetTimestamp()=QueryPerformanceCounter。AggressiveInlining 只省 0.59ns(2.78%),event vs 介面差 0.16ns(0.78%),全是雜訊級。

- [臨] 結論:收包路徑改 event 不影響效能(語意上仍建議留介面=單一固定消費者+確定性);AggressiveInlining 在「event 直接訂閱 helper」接法下是死碼應拔,維持介面則 attr 有效但效益量不出。真要優化收包先動「每包呼叫 QPC」這件事,不是 inline/event。

- [臨] 驗證法(net8+ release 即可,不需 checked runtime):`DOTNET_TieredCompilation=0 DOTNET_TieredPGO=0 DOTNET_JitDisasm="*" app.dll`,看輸出『Assembly listing for method X』清單中誰被單獨編譯(=沒被摺進去)。
- [臨] inline 真正價值不是省那次 call(~1ns),是讓 JIT 跨邊界做後續最佳化(常數摺疊/dead code/CSE/暫存器配置/邊界檢查消除/向量化)。判準=(呼叫開銷÷方法內工作量)×頻率。實證:同一顆 attr,緊迴圈 x*x+3(工作極小)inline 快 2.38x;緊迴圈 x+QPC(工作主宰)快 1.03x 無感。方法內有 syscall/atomic/alloc → inline 無感。
- [臨] 即時遊戲 inline 幾乎永遠墊底(net8 ServerGC 實測):影響排序 Gen2 GC(8.5ms,爆一個 frame,=1440萬個 packet 的 inline)≫ Gen0/1 GC(百µs)≫ OS jitter(百µs)≫ per-packet 配置(~70ns)≫ per-packet QPC(~20ns)≫ inline(0.59ns)。格鬥(240pkt/s)inline 占 budget 0.00001%;射擊(64k pkt/s)0.004%;SLG(tick 極低+瓶頸在 DB I/O/尋路/GC)更不用理。結論:別預先擔心 inline,先 profile 熱數值迴圈再說;錢砲在 零配置/GC 控制/演算法。
- [臨] tslg-servercore 完整決策記錄(含三層數據表)已寫入 _AIDocs/NetworkLayer.md 章節「收包 dispatch 的 inline / event 取捨(效能實證)」;該專案決定 NetBase 改 event + 拔 Slave_OnReceivePacket/Client_OnReceivePacket 的 AggressiveInlining。

## 行動



- 網路層/熱路徑重構評估 inline 或 介面↔event 取捨時,引用此實證,別憑直覺推「event 較慢」或「attr 一定有效」

- 看到 [MethodImpl(AggressiveInlining)] 的方法被當成 delegate/event 訂閱目標 → 標記為失效死碼,建議移除或改 lambda 包裝保留語意

