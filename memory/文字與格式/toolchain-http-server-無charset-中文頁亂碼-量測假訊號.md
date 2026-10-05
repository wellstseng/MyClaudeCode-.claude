# toolchain-http-server-無charset-中文頁亂碼-量測假訊號

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: python -m http.server, charset, 亂碼, mojibake, 本機預覽, SVG 驗證, getBBox, meta charset, latin-1
- Created-at: 2026-08-20

## 知識

- [臨] `python -m http.server` 送 text/html 不帶 charset，HTML 又沒 `<meta charset="utf-8">` 時 Chrome 對 http 來源退回 latin-1 解碼：中文全變 mojibake。危害不只顯示——每個中文字被拆成 3 個 latin-1 字元，JS `getBBox()` 量出的文字寬度嚴重膨脹，版面自動檢測（壓字/溢出）會回報假陽性，照著修會誤改本來正確的幾何（2026-08-20 tslg Docs 圖解驗證實踩：三筆『文字互疊』全是假訊號）
- [臨] file:// 開同一檔 Chrome 會自動偵測 UTF-8 不亂碼，所以「本機瀏覽器開起來正常」不代表 http 伺服器 serve 也正常，兩條路徑編碼行為不同

## 行動

- 產生 HTML 的工具（如 Docs/build.py）輸出樣板第一行永遠帶 `<meta charset="utf-8">`；手寫驗證用 HTML 同樣先放
- 用瀏覽器 JS 量測中文頁版面前，先確認頁 title/內文非亂碼（tabs context 的 title 是最快的訊號）；亂碼時所有寬度量測作廢
