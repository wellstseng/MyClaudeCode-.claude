# 雲端同步資料夾內不放SQLite-GoogleDB是Drive鏡像會間歇disk-IO-error

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: GoogleDB, Google Drive, 雲端同步, sqlite, disk I/O error, OperationalError, download-archive, gallery-dl, 輸出資料夾
- Created-at: 2026-10-05

## 知識

- [臨] Wells 的 Mac 上 ~/GoogleDB 是 Google Drive 桌面版的「鏡像同步」根目錄（2026-10-06 查 DriveFS 的 root_preference_sqlite.db 確認）；寫進去的檔案會自動上傳到他的雲端硬碟，大量輸出前要意識到這點
- [臨] 把 SQLite 資料庫放在該同步資料夾內被長時間程序持續讀寫 → 間歇性 `sqlite3.OperationalError: disk I/O error`（實測 gallery-dl 的 --download-archive：同一指令在非同步的暫存目錄跑 400+ 張零錯誤，搬進同步資料夾後兩次分別在第 10、第 69 張後爆；單次短寫入探測卻會成功，所以探測通過不代表安全）
- [臨] 根因為推論未直接證實：同步程式碰觸資料庫或其 journal 檔。已證實的只有「位置在同步資料夾內」這個變因與錯誤共現
- [臨] 正確做法：狀態類檔案（SQLite、journal、lock、索引）一律放同步資料夾之外，或乾脆不用資料庫——gallery-dl 預設就會跳過已存在的檔案，--abort N 對「檔案已存在」的跳過同樣有效，不需要 --download-archive

## 行動

- 要在 ~/GoogleDB 底下產生輸出時，只放最終成品檔；任何 SQLite／暫存狀態檔改放非同步路徑
- 遇到 sqlite disk I/O error 先看資料庫是否位於雲端同步資料夾（Drive／iCloud／Dropbox），再懷疑磁碟或權限
