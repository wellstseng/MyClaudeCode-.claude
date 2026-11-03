# macOS-zsh下log指令被內建蓋掉-查系統日誌要寫usr-bin-log

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: log show, /usr/bin/log, zsh log builtin, 系統日誌, unified log, too many arguments, macOS 查 log
- Created-at: 2026-11-03
- Source: session:ee5a8659#a6c546ed 2026-11-03
- Quote: 「我現在要把MyPassport的資料複製到Seagate Exp 但跑一陣子就會報錯卡住 我現在也不知道到底跑了多少」

## 知識

- [臨] macOS 的 zsh 裡 `log` 是內建指令（記錄登入用），`log show --last 1h ...` 會報 `log:1: too many arguments`；若再加 `2>/dev/null` 就變成無聲無輸出，看起來像「日誌裡沒有東西」。查系統統一日誌一律寫 `/usr/bin/log show ...`。

## 行動

- macOS 查系統日誌用 /usr/bin/log 全路徑，不寫裸 log
- log 查詢沒輸出時先拿掉 2>/dev/null 看是不是指令本身報錯
