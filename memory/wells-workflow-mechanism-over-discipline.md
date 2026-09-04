# wells-workflow-mechanism-over-discipline — 不靠決心靠機制

- Scope: global
- Confidence: [觀]
- Type: wisdom
- Trigger: 紀律, 決心, 機制, 自動偵測, guardian, hook, 自動化, 靠記得
- Author: wells（口述）/ judy（彙整）
- Created-at: 2026-05-22
- Source: ~/WellsDB/AI進修/Wells的AI工作流心路歷程-Home-Claude-CLI.md（洞見 3）
- Related: feedback-fix-escalation, decisions, decisions-architecture, workflow-rules

## 知識

- [觀] **任何「靠人記得」的紀律都會崩，靠機制才會穩**
- [觀] Wells 已用機制取代決心的具體例子：
  - **重試 ≥2 自動偵測**：Guardian hook 偵測 `wisdom_retry_count >= 2` → 自動注入 `[Guardian:FixEscalation]`，不靠 Wells 喊停
  - **handoff 6 區塊強制**：`/handoff` skill 套模板，徒手不漏 6 區塊
  - **SVN 異動清單檢核**：執行同步前自動比對是否含測試/工具類檔
  - **DocDrift 攔截**：src 改了未更新 _AIDocs，PreToolUse 直接擋 commit
  - **Evasion Guard regex**：偵測「下次/之後/晚點/稍後再處理」攔截敷衍式延後
  - **same_file_3x 偵測**：同檔重複改判覆轍（規劃文件已加白名單排除）
  - **延後語/外包語/敷衍語/技術選單** → atom + trigger 注入，AI 自察前先被提醒
- [觀] 不適合機制化的層：方向校正 / 產品定位 / [觀]→[固] 晉升決策 → 還是 Wells 手動拍

## 行動

- **Why**：意志力是有限資源；session 越長 / 任務越複雜 / 越深夜，紀律越容易崩。寫成 hook + atom + 自動偵測 → 0 邊際成本維持，且跨 session 不衰減
- **How to apply（給 AI 端）**：發現某條規則「需要使用者反覆提醒才生效」 → 不是規則不好，是缺機制。評估是否能轉成：(1) hook 偵測 (2) atom trigger 注入 (3) PreToolUse 攔截。其中之一即可
- **How to apply（給其他開發者）**：每次需要靠自己「記得做某事」才能維持品質 → 那條規則總會在某個累的時候崩。把它寫成腳本/hook/檢核清單，不要靠紀律
- **例外**：方向校正、產品收斂、價值判斷 → 機制不可替代人類，這類保留人工
- **檢核問句**：這條規則我是不是「沒靠提醒就會忘」？是 → 機制化候選
