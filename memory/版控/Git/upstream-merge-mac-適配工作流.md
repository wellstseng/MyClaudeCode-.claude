# upstream-merge-mac-適配工作流

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: upstream merge, 整併, fork 同步, merge upstream, 衝突解, checkout --ours, settings 接線, python 3.9, write_text newline, 測資可移植
- Created-at: 2026-07-06
- Related: mac-缺-python-用-wrapper-指向-python3, toolchain, feedback-tooling-reliability, merge-時-sot-索引檔-ours-策略誤清-catalog-post-mortem

## 知識

- [臨] fork 三角工作流：pull 追 upstream（團隊 repo）、push 走 origin（自己 fork）；`git config remote.pushDefault origin` 讓裸 push 不誤打 upstream（2026-07-06 已設）
- [臨] merge upstream 定向衝突解：memory/ 個人記憶檔一律 `checkout --ours`（是資料分歧非真衝突）；settings.json 取 ours 後必須 diff 兩邊 hooks 結構補「功能接線 delta」（event/matcher/新 hook），只補 lang_guard 這種顯性新檔不夠——PostCompact/PostToolBatch/matcher 升級這種隱性 delta 會漏，靠 run_verify 的 settings 斷言測試抓
- [臨] upstream（Windows 開發）合入 Mac 的三類適配：(1) settings 接線用 python3 不抄 pythonw 絕對路徑 (2) Path.write_text(newline=) 是 3.10+ API、macOS 系統 Python 3.9.6 會 TypeError，改 open(..., newline=) (3) 測資寫死 r'C:\...' 在 POSIX 是相對路徑，resolve 後落回 rootdir 之下造成誤判，需 platform-aware
- [臨] merge 前必打 tag（backup-pre-upstream-merge-YYYYMMDD）；merge 後 `python3 run_verify.py` 當煙測主力（1 秒級），失敗逆向分流：settings 斷言=接線缺口、TypeError=版本差異、路徑斷言=可移植性
- [臨] guardian server(:3848) 舊碼無退出 handler，SIGTERM 無效需 SIGKILL；殺後下個 session SessionStart 自動拉新版（新碼有 stdin-EOF 交棒）

## 行動

- merge upstream 前：fetch + merge-tree dry-run 估衝突面 + 打 backup tag
- 衝突解：個人資料 ours、程式碼吃 theirs、settings ours+補接線 delta（用腳本 diff 兩邊 hooks 結構）
- merge 後：run_verify.py 全綠才 commit push；重啟 :3848 guardian
- Windows→Mac 合碼盯三件：pythonw 路徑、3.10+ API、C:\ 測資
