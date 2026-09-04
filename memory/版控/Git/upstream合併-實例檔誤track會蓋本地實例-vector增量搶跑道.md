# upstream合併-實例檔誤track會蓋本地實例-vector增量搶跑道

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: upstream merge, fork 同步, IDENTITY 被蓋, 實例檔, instance 檔, vector 全量重建, already_running, index race, 去識別化
- Created-at: 2026-09-04
- Related: upstream-merge-mac-適配工作流, git-已push-commit-勿改寫-雙-push-url-gitlab-main-force-保護致遠端分叉, toolchain

## 知識

- [臨] 合併 fork/upstream 時，若對方誤把「實例檔」（IDENTITY.md／USER.md／.mcp.json 這類每機自持、本地不追蹤的檔）commit 進版控，merge 會直接蓋掉本地實例且無衝突提示（本地未追蹤＝git 認為無 ours 版）。實例：fork Mac 線誤 track 舊版 IDENTITY.md stub，merge 後本地完整契約實例被換成 stub，靠 verify_always_load_contracts 紅燈才發現。防法：merge 後 `git ls-files IDENTITY.md USER*.md .mcp.json`，任何實例檔出現在 index → `git rm --cached` 並從 template 重建。
- [臨] vector service 的 `POST /index`（全量）會被 auto_index_on_change 的增量索引搶跑道：檔案大搬家後增量連環觸發，全量 POST 一直回 `already_running`。要全量就用重試迴圈（idle 時立刻 POST、拿到非 already_running 回應才算排入），單發 POST + 等 idle 會誤判已重建（chunks/layers 根本沒變）。
- [臨] 專案層 `.claude/memory/personal/<user>/` 目錄名綁 wg_roles 的 user 解析；de-identify 改預設帳號後，舊帳號名目錄的個人 atom 會可見性倒置（讀不到）。改名目錄還不夠：三索引檔的 path 與 atom frontmatter 的 `Scope: personal:<user>` 都要跟著改，最後 `sync-atom-index --fix-scope-from-path` 收尾。

## 行動

- merge upstream/fork 後：檢查實例檔是否被 track、grep 舊帳號絕對路徑、專案層 personal 目錄名是否對齊現任 user
- 要全量重建 vector：用 already_running 重試迴圈，完成後驗 layers 清單而非只看 indexing:null
