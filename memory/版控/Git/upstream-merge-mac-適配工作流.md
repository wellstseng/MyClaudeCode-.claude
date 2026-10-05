# upstream-merge-mac-適配工作流

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: upstream merge, 整併, fork 同步, merge upstream, 衝突解, checkout --ours, settings 接線, python 3.9, write_text newline, 測資可移植
- Created-at: 2026-07-06
- Related: mac-缺-python-用-wrapper-指向-python3, toolchain, feedback-tooling-reliability, merge-時-sot-索引檔-ours-策略誤清-catalog-post-mortem, upstream合併-實例檔誤track會蓋本地實例-vector增量搶跑道

## 知識

- [臨] fork 三角工作流：pull 追 upstream（團隊 repo）、push 走 origin（自己 fork）；`git config remote.pushDefault origin` 讓裸 push 不誤打 upstream（2026-07-06 已設）
- [臨] merge upstream 定向衝突解：memory/ 個人記憶檔一律 `checkout --ours`（是資料分歧非真衝突）；settings.json 取 ours 後必須 diff 兩邊 hooks 結構補「功能接線 delta」（event/matcher/新 hook），只補 lang_guard 這種顯性新檔不夠——PostCompact/PostToolBatch/matcher 升級這種隱性 delta 會漏，靠 run_verify 的 settings 斷言測試抓
- [臨] upstream（Windows 開發）合入 Mac 的三類適配：(1) settings 接線用 python3 不抄 pythonw 絕對路徑 (2) Path.write_text(newline=) 是 3.10+ API、macOS 系統 Python 3.9.6 會 TypeError，改 open(..., newline=) (3) 測資寫死 r'C:\...' 在 POSIX 是相對路徑，resolve 後落回 rootdir 之下造成誤判，需 platform-aware
- [臨] merge 前必打 tag（backup-pre-upstream-merge-YYYYMMDD）；merge 後 `python3 run_verify.py` 當煙測主力（1 秒級），失敗逆向分流：settings 斷言=接線缺口、TypeError=版本差異、路徑斷言=可移植性
- [臨] guardian server(:3848) 舊碼無退出 handler，SIGTERM 無效需 SIGKILL；殺後下個 session SessionStart 自動拉新版（新碼有 stdin-EOF 交棒）
- [臨] vcs-sync 背景 worker（記憶自動上版控）的 fetch／push 對象是分支追蹤的遠端：本 fork 的 main 追蹤 upstream（對方 repo），所以合入後要在 workflow/config.json 關 vcs_sync.push 與 vcs_sync.pull.enabled，或先把 main 追蹤改到 origin 再開
- [臨] tools/verify/verify_install.py 會 clone 本 repo 的已提交 HEAD 當安裝來源：合併未 commit 時它讀到舊樹而假紅（缺新檔、缺新設定鍵），要先本地 commit 再跑 run_verify 才看得到真結果
- [臨] upstream 的 Python 底線是 3.10（install.py --verify 會報 FAIL）；系統 Python 3.9 的機器每次升級都要重做 write_text(newline=) 改寫（用 AST 掃 Expr 陳述句批次改成 with open），且 verify_install 有三個測試在 3.9／非 Windows／settings 無 statusLine 下固定紅
- [臨] 使用者說「幫我把 git 上傳」不算版控口令，commit 閘會擋；要他明說「上GIT」

## 行動

- merge upstream 前：fetch + merge-tree dry-run 估衝突面 + 打 backup tag
- 衝突解：個人資料 ours、程式碼吃 theirs、settings ours+補接線 delta（用腳本 diff 兩邊 hooks 結構）
- merge 後：run_verify.py 全綠才 commit push；重啟 :3848 guardian
- Windows→Mac 合碼盯三件：pythonw 路徑、3.10+ API、C:\ 測資
