# feedback-已驗證的重複操作直接做完勿反覆確認

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 重複操作, 升級, upstream 合版, 落地, 確認, checkpoint, 別多問, 效率, AskUserQuestion
- Created-at: 2026-07-08
- Related: preferences, workflow-rules, wells-workflow-brake-mechanism, wells-workflow-copilot-not-driver

## 知識

- [臨] 已驗證且符合前例的重複性操作，直接執行到完成（含外向 push）並回報，勿再用多題 AskUserQuestion 反覆確認。實例：第 2 次做 ~/.claude upstream 原子記憶合版升級時，我出了「落地 + model/effort/statusLine 偏好」的 2 題確認，使用者直接 reject 並原樣重送「幫我進行升級」。
- **Why:** 使用者重視心流/效率，討厭為「已被既有指示涵蓋的決策」被打斷——當下 model/effort 的選擇早被他一貫的「維持本地個人化」指示回答了，再問即冗餘。首次複雜操作的分階段 checkpoint（評估→dry-run→解衝突→落地）是被接受甚至讚許的；要精簡的是「同一套流程的第 N 次重複」。
- **How to apply:** 操作若①符合先前已核准的模式 ②已驗證通過 ③剩餘決策都能由既有 standing directive 推定 → 直接做到底並回報，只把「真正全新、無法從既有指示推定」的決策以簡短 FYI 呈現（非 blocking 提問）。反之，首次/高風險/不可逆且無前例者仍 checkpoint。細節見 [[preferences]]、[[wells-workflow-brake-mechanism]]。

## 行動

- （依知識內容判斷）
