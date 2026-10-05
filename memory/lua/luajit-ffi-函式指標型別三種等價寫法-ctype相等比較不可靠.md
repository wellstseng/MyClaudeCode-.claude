# luajit-ffi-函式指標型別三種等價寫法-ctype相等比較不可靠

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: luajit, ffi, cdef, 函式指標, function pointer, typedef, ffi.cast, ffi.typeof, ctype, goo.cdef, titangoo
- Created-at: 2026-08-27
- Related: titan-lua-socket-rpc機制-兩版同構, orbit-hotfix-lua-direction, luajit-cdef-typedef重複宣告沉默忽略-只有具名struct-tag會炸

## 知識

- [臨] LuaJIT FFI 宣告函式指標型別有三種等價寫法（實測 luajit21 win-x64，三者 cast 後呼叫真實函式結果一致）：(1) 指標 typedef `typedef void (*fp)(int);` → `ffi.cast("fp", p)`；(2) 函式型別 typedef `typedef void fn(int);` → 用時加星 `ffi.cast("fn *", p)`（單獨 `ffi.cast("fn", p)` 會噴 invalid C type）；(3) 不 typedef，cast 現場寫匿名型別 `ffi.cast("void (*)(int)", p)`。慣例用 (1)：cdef 區塊直接對應 C header，cast 字串最短。
- [臨] 函式指標的 ctype 不做結構性 dedup：`ffi.typeof("void (*)(int)") == ffi.typeof("void (*)(int)")` 為 false，兩個簽名相同的 typedef 互比也是 false（對比 `ffi.typeof("int *") == ffi.typeof("int *")` 為 true）。→ 不可用 `==` 驗證函式指標型別相符。
- [臨] `tostring(ffi.typeof("fp"))` 印出 `ctype<void (*)()>` —— 參數列被省略。→ 不能靠印出來辨識/比對簽名。
- [臨] 讀 C 宣告心法：先遮掉 typedef 當變數宣告，從識別字往右讀、遇 `)` 轉左、括號優先。`void (*fp)(int)` = 指向〔吃 int 回 void 的函式〕的指標；`void *fp(int)` = 吃 int 回 void* 的函式。差別在括號把 `*` 的結合提前。

## 行動

- 寫 goo.cdef / titangoo 橋接的函式指標槽時照慣例用指標 typedef 寫法，與現有 fp_goo_* 系列一致
- 要驗證 Lua 側拿到的函式指標型別對不對，不要寫 `ffi.typeof(a) == ffi.typeof(b)`（恆 false）；改為實際呼叫做 round-trip 驗證
