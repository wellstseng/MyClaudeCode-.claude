# feedback no-legacy-by-default

- Scope: global
- Author: wellstseng
- Confidence: [固]
- Trigger: 改架構, 整合, 去重複, 拔掉, 舊欄位, 向後相容, deprecated, schema 變更, dead config, 整合的部分, V1 V2 並存
- Last-used: 2026-05-26
- Confirmations: 3
- Created-at: 2026-05-23
- Related: feedback-fix-on-discovery, workflow-rules, decisions-architecture

## 知識

- [固] **架構變更時，舊的版本/欄位/路徑預設一律拔除**，不留向後相容；要保留必須由 Wells 明確說「保留 X」
- [固] Why：2026-05-23 Ollama 設定整合，第一輪我選擇「保守保留 + inheritance fallback」（保留 host/model 欄位給向下相容）。Wells 反饋「整合的部分有把沒用的拔掉了嗎」，他要拔；後續又補「之後有改架構，舊的內容不准留，除非我有說」明確訂為全域規則
- [固] How：計畫階段（EnterPlanMode）就要分「拔除清單」與「保留清單」；保留清單必須附明確功能依存或 Wells 講過的理由，不接受「向後相容」「以防萬一」這類自我擔心
- [固] 反例（不能做）：寫「欄位不刪（向後相容）」、加 deprecated 註解但保留 code path、把欄位改 optional 留著、V1 殘留跟新 V2 並存
- [固] 例外（仍可保留）：純 bug fix（非架構變更）、第三方公開 API、Wells 明說保留
- [固] 連動：跟 [[feedback-fix-on-discovery]] 互補 — fix-on-discovery 講「順手發現的不在範圍別處理」；本條講「在範圍的舊東西默認就拔」

## 行動

- 改架構 PR 計畫文件必出現「## 拔除清單」與「## 保留清單（附理由）」兩節
- 不出現「為了向後相容保留 X」這類論述，除非 Wells 講過
- 收到「整合」「去重複」「清理」這類關鍵字 → 直接套用本規則
