# wells-workflow-infra-before-app

- Scope: global
- Author: wells
- Confidence: [觀]
- Trigger: 新專案啟動, AI 工作流規劃, 大任務開工, 基礎建設, 記憶系統, infrastructure
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: decisions, workflow-rules

## 知識

- [觀] 「基礎建設先於應用」是大型 AI 工作流規劃的正確順序：先把跨 session 記憶 / hook / skill 工具鏈做穩，再去做應用層任務
- [觀] 證據：Wells 自家 2026-03 ~ 05 半年——3 月先做原子記憶 V2.12 → V3.4 打穩，4 月才把能力導出到 CatClaw / Hermes / 漫畫翻譯，5 月才敢做 Doomsday 反組譯這種大批 token 消耗任務
- [觀] 順序顛倒的代價：沒有跨 session 記憶就做大任務，每個 session 都在重學上下文，等於燒錢買教訓

## 行動

- Why：跨 session 記憶 / 偵測 / 自動化是「能力放大器」，先做應用會被「每次重學上下文」「重複犯同樣的錯」「token 失控」這三件事拖死
- How to apply：
  - 規劃新工作流時，先盤點「跨 session 銜接 / 記憶 / 規則偵測」三件事的現況，缺哪個就先補
  - 應用層任務若預估會跨 3+ session，先確認基礎建設能讓上下文自動承接
  - 反例自查：當開始用 AI 做新領域工作前，先問「跨 session 接得住嗎？」答不出來就先補基建
