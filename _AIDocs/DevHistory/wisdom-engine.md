# Wisdom Engine + Fix Escalation Protocol

> 從 Architecture.md 移入（2026-04-17 索引化）。實作：`hooks/wisdom_engine.py`。
> keywords: wisdom, reflection, 反思, fix_escalation, 精確修正升級, situation classifier

## Wisdom Engine 組件

- **情境分類器**：2 條硬規則（file_count/is_feature → confirm；touches_arch → plan）
- **反思引擎**：first_approach_accuracy + over_engineering_rate + silence_accuracy + Bayesian 校準
- **Fix Escalation Protocol**：同一問題修正第 2 次起強制 6 Agent 精確修正會議，Guardian 自動偵測 + `/fix-escalation` skill 介入

## Fix Escalation 觸發

- `wisdom_retry_count ≥ 2` → UserPromptSubmit 注入 `[Guardian:FixEscalation]` 提醒走 `/fix-escalation`
- 一次性旗標：`fix_escalation_warned` 避免重複注入
- 相關 feedback atom：`memory/feedback/feedback-fix-escalation.md`

## 跨 Session 鞏固

- 廢除自動晉升，改為 Confirmations +1 簡單計數
- 4+ sessions → 建議晉升（不自動執行，由 `atom_promote` MCP tool 執行）
- 統一 dedup 閾值 0.80
- SessionEnd 衝突偵測：向量搜尋 score 0.60-0.95 → 寫入 episodic 衝突警告

詳見 `memory/decisions.md`（晉升規則）、`memory/decisions-architecture.md`（核心架構決策）。
