# wells-workflow-brake-mechanism

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 工作流洞見, 煞車, 重試, retry, 越改越爛, hook
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: feedback-fix-escalation, failures, decisions, feedback-已驗證的重複操作直接做完勿反覆確認

## 知識

- [臨] AI 不會自己停下來反省——你要幫它設計煞車機制：Fix Escalation 是從「AI 越修越爛」的痛苦裡學到的。AI 沒有「我好像在做蠢事」的自覺。Hook 是最好的煞車工具——程式化的規則比口頭提醒可靠一百倍
- [臨] 煞車設計三要素：(1) retry 偵測（Guardian 自動計數）(2) 強制暫停（連續 3 次未解決）(3) 多角度審查（6 Agent 會議）

## 行動

- 設計 AI 輔助流程時，煞車機制應與功能實作同等優先
