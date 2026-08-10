# worktree-session-驗證前先同步目標分支

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: worktree, 落後, ff-only, 孤兒目錄, stale branch, 驗證前同步, merge --ff-only, ahead behind
- Created-at: 2026-07-15
- Related: 併發-session-共用工作樹-收尾選擇性-staging-勿-git-add-a

## 知識

- [臨] Claude Code worktree session 的分支起點可能遠落後任務指名的目標分支：實例 2026-07-15 tslg-servercore-lua，worktree 停在 71be42d、落後 dev/lua 34 commits，任務前提 commit（1a7379b 整合Titan.Core）根本不在歷史裡——若直接跑「刪除前引用驗證」會全是假命中而誤判停手（反向情境更危險：誤信已整合而錯刪仍被引用的代碼）。
- [臨] 判別法：git rev-list --left-right --count HEAD...<target> 一眼看領先/落後；0 領先＋落後 N → git merge --ff-only <target> 純快轉後再驗證/操作，之後的 commit 恰領先目標一步、可乾淨合回。

## 行動

- 任務指名目標分支（如 dev/lua）時，開工第一步對照 HEAD 與目標分支 ahead/behind；落後就先 ff 同步，再做任何驗證、刪改或建置基線。
