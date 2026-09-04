# wells-workflow-tell-ai-what-you-hate

- Scope: global
- Author: wells
- Confidence: [觀]
- Trigger: AI 行為糾正, feedback atom, 偏好設定, 行為校正, 不喜歡, 別這樣做
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: preferences, decisions, feedback-no-outsource-rigor, feedback-decision-no-tech-menu

## 知識

- [觀] 「讓 AI 知道你不喜歡什麼」比反覆解釋「你要做什麼」高效得多
- [觀] 證據：Wells 半年累積的 12 條 feedback-* atom **沒有一條是預先設計的**——全部是被使用者明確糾正後才寫進記憶
- [觀] 機制：AI 訓練分布有「平均值傾向」，要靠**負面樣本**拉它離開預設行為
- [觀] 範例：feedback-no-tech-menu（不要列技術選單）、feedback-no-outsource-rigor（high mode 不要把思考外包）、feedback-fix-on-discovery（發現了立即修不要拖延）

## 行動

- Why：正向描述「請這樣做」常被 AI 理解成「one of many acceptable behaviors」，繼續走預設；負向描述「不要 X」配上 Why 能精準拉回
- How to apply：
  - 當被使用者糾正某行為時，立即評估「這是一次性還是會反覆」→ 後者就立刻寫 feedback atom
  - feedback atom 必含三段：規則本身 + Why（事件起因 / 對話日期）+ How to apply（觸發情境）
  - 主動偵察：當使用者連續兩次糾正類似行為，提議寫成 feedback atom 而非每次重講
