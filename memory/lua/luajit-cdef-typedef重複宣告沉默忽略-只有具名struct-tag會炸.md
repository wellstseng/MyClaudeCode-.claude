# luajit-cdef-typedef重複宣告沉默忽略-只有具名struct-tag會炸

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: ffi.cdef, cdef, typedef, redefine, pcall ffi.cdef, luajit, 熱更 re-require, goo.bind, fp_typedef
- Created-at: 2026-08-27
- Related: luajit-ffi-函式指標型別三種等價寫法-ctype相等比較不可靠, goo-ffi-補0是lua讀取端協定-結尾0兼錯誤通道

## 知識

- [臨] LuaJIT `ffi.cdef` 對 **typedef 重複宣告是沉默成功**（不 error），且第一次的定義獲勝——連「同名不同簽名」也沉默（`typedef void (*fp_a)(int)` 之後再 `typedef int (*fp_a)(double)`，`ffi.typeof("fp_a")` 仍是第一版）。anonymous-struct typedef（`typedef struct { ... } sbuf;`）同樣沉默成功。
- [臨] **只有具名 struct/enum tag** 重複宣告會 error：`struct nm { int a; };` 再宣告一次 → `attempt to redefine 'nm'`。所以「pcall 防熱更 re-require 重複宣告」這個理由，對純 typedef 的 cdef 區塊根本不成立。
- [臨] 危害：`pcall(ffi.cdef, ...)` 把 **cdef 語法錯誤也一起吞掉**（例：`declaration specifier expected near 'this'`）。宣告等於沒生效，錯誤會遲到呼叫當下才以「型別不存在」爆，離現場很遠。正解＝只吞訊息含 `redefine` 的錯，其餘 `error(err, N)` 往上丟。
- [臨] 衍生鐵則：**同名 typedef 全庫只准一處**。兩個模組各自 typedef 同一個 `fp_goo_xxx` 卻寫不同參數時，先載入者勝、後者以錯簽名呼叫＝踩壞堆疊，無任何警告。
- [臨] 實證方法：`CoreModule/Lua/native/build/luajit21/src/luajit.exe` 直接跑；該 exe 不含 jit.* 模組，`-bl` 語法檢查不可用，改用 `-e "loadfile(...)"`。

## 行動

- 寫 app 域下行綁定時直接用 `goo.bind` / `goo.bind_optional`（CoreModule/scripts/core/goo.lua），不要再手寫 pcall+assert+cast 三段。
- 看到任何 `pcall(ffi.cdef, ...)` 裸寫法就當作可疑：確認它防的是具名 struct/enum tag，否則它只是在吞語法錯誤。
- 新增 fp_* typedef 前先 grep 全庫確認沒有同名者。
