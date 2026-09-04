# wells-workflow-small-automation-payoff

- Scope: global
- Author: wells
- Confidence: [觀]
- Trigger: 自動化, hook, stream idle, watchdog, 卡死, 沉默失敗, silent failure, LLM 不回覆
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: pitfalls-provider, decisions-architecture

## 知識

- [觀] 小自動化的回報遠超預期——半年下來真正關鍵的自動化都不是炫技 hook，而是「**讓系統永遠會用某種方式講話給我聽**」的小東西
- [觀] 範例：CatClaw codex-oauth provider 加 60s stream idle watchdog——程式碼加不到 30 行，但解掉「我傳訊息到 Discord，AI 從此消失」這種讓使用者對整套系統失去信心的問題
- [觀] 對立：浮華 hook（自動產 commit message / 自動格式化 / 自動 generate doc）耗大量設計時間，回報卻有限，因為它們不解決「信心崩塌」級的問題
- [觀] 判斷準則：自動化價值 ≈「不做會丟失多少使用者信心」而非「省多少時間」

## 行動

- Why：使用者信心一旦崩塌（系統默默卡住、無錯誤訊息、不知道發生什麼事），整套工具會被棄用；省 5 分鐘的炫技 hook 救不回信心
- How to apply：
  - 自動化優先順序：silent failure 偵測 > 重複動作省力 > 智慧化建議
  - 凡是「stream / 網路 / 子程序 / 等待」場景必加 idle watchdog（5s 檢查、60s 觸發、清楚錯誤訊息）
  - 任何「使用者送出指令後系統無回應」的路徑都要有 fallback 通知（⚠️ 訊息、status update、log）
  - 評估新 hook / skill 時自問：「不做這個會讓我什麼時候信心崩塌？」答不出來的，優先級降低
