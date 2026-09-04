# lua-弱表探測字串無效-字串是值不是物件-驗回收用堆積量測

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: weak table, 弱表, __mode, collectgarbage, GC 驗證, 記憶體洩漏, ffi.string 回收, pb.decode GC
- Created-at: 2026-09-02
- Related: titan-lua-socket-rpc機制-兩版同構

## 知識

- [臨] Lua/LuaJIT 弱表（__mode='v'）只清「物件」（table/userdata/function/thread）；字串在弱表語意中是「值」（同 number），槽位永不清除→弱表反而把字串 pin 住。用弱表驗證字串回收＝儀器本身造成洩漏假訊號。字串回收的正確儀器：曖機一輪後 collectgarbage('collect')×2 量堆積 delta，迴圈 N 輪大 payload 區分「一次性開銷（interning/快取）」與「每輪洩漏」。實證（tslg-servercore LuaHost）：pb.decode 後只 cache 單欄位，10 輪×約2MB 過手 heap delta 僅 0.5KB——欄位字串是獨立複本，不 pin decode table／來源 payload（Lua 無 string view）。

## 行動

- （依知識內容判斷）
