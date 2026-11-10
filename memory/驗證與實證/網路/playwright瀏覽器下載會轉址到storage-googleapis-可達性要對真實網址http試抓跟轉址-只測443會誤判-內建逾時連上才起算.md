# playwright瀏覽器下載會轉址到storage-googleapis-可達性要對真實網址HTTP試抓跟轉址-只測443會誤判-內建逾時連上才起算

- Scope: global
- Author: wellstseng
- Source: 實測 curl -sIL cdn.playwright.dev CfT 網址；playwright-core 1.59.1 lib/server/utils/happyEyeballs.js、utils/network.js
- Confidence: [臨]
- Trigger: playwright install, Chrome for Testing, Chromium 下載卡住, postinstall 卡住, storage.googleapis.com, PLAYWRIGHT_DOWNLOAD_HOST, 網路可達性探測, 公司網路擋下載
- Created-at: 2026-11-10

## 知識

- [臨] cdn.playwright.dev/builds/cft/... 會 307 轉到 storage.googleapis.com（實測 curl -sIL）；ffmpeg 則轉到 playwright.download.prss.microsoft.com。只測 cdn.playwright.dev:443 連得上 ≠ 下載得到，公司網路擋 Google 儲存站時會誤判放行
- [臨] playwright 的 PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT（預設 30s）是連上之後的閒置逾時：它的 happyEyeballs agent 等 TCP connect 才交出 socket，連線本身無逾時（讀 playwright-core 1.59 原始碼）；目的地被黑洞時要等 OS TCP 逾時 × 5 次重試
- [臨] 真實下載網址用 `playwright install --dry-run chromium` 取（列 Install location 與 Download url/fallback），已安裝看各 Install location 下的 INSTALLATION_COMPLETE 標記，不看 executablePath 存在（解壓到一半也會有執行檔）

## 行動

- 包 playwright 瀏覽器下載時：對 dry-run 列出的真實網址做 HTTP GET 試抓並跟轉址，限時收第一筆資料、量幾秒速度推算總時間
- 真正下載再包一層整體時限，超時 SIGTERM（讓安裝鎖釋放）後清 os.tmpdir()/playwright-download-*
- 使用者回報卡在 Downloading Chrome for Testing → 先請他 curl storage.googleapis.com 那個網址驗是否被擋
