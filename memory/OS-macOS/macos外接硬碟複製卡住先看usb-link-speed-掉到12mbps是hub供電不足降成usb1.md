# macOS外接硬碟複製卡住先看USB-Link-Speed-掉到12Mbps是hub供電不足降成USB1

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 外接碟, 複製卡住, 複製很慢, Link Speed, 12 Mb/s, SPUSBHostDataType, USB hub, 供電不足, My Passport, 行程卡 U 狀態
- Created-at: 2026-11-03
- Related: macos-zsh下log指令被內建蓋掉-查系統日誌要寫usr-bin-log
- Source: session:ee5a8659#a6c546ed 2026-11-03

## 知識

- [臨] macOS 外接碟複製跑一陣子就卡住、報錯：先跑 `system_profiler SPUSBHostDataType` 看該碟 `Link Speed`。掉到 12 Mb/s（USB 1.1，上限約 1 MB/s）且跟另一顆碟掛在同一個 USB2 hub 下、Power Allocated 500mA → hub 供電不夠、碟重置後降速重新列舉。症狀：讀任何檔都慢到 50KB/s～1MB/s、讀取行程卡在 U（不可中斷）、連 mount/unmount 都要數分鐘，log 裡沒有明確 I/O error。解法：兩顆碟各自直插 Mac 本機埠。
- [臨] 判斷是單檔壞軌還是整顆碟：去讀一個先前已成功複製的檔，也慢 → 整顆碟或連線問題。

## 行動

- 外接碟複製卡住/很慢：先查 system_profiler SPUSBHostDataType 的 Link Speed 與是否經 hub，再懷疑壞軌
- 使用者兩顆 bus-powered 碟接同一個 USB2 hub → 建議各自直插本機
