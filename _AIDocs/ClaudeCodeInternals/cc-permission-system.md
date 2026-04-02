# Claude Code Permission Architecture

- Scope: global
- Confidence: [固]
- Trigger: permission system, 權限架構, PermissionMode, BashClassifier, ML classifier, checkPermissions, bypassPermissions, alwaysAllow, alwaysDeny, permission racing, 權限檢查
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-tool-system, cc-hook-system

## 知識

### 四層權限模型
- [固] Layer 1：Tool-Level（tool.checkPermissions(input, context)）
- [固] Layer 2：Global Rules Engine（alwaysAllowRules / alwaysDenyRules / alwaysAskRules）
- [固] Layer 3：三條平行路徑 Promise.race → InteractiveHandler / HookHandler / BashClassifier

### 七步決策漏斗（checkPermissionsAndCallTool）
- [固] 1a alwaysDenyRules（不可繞過）→ 1b alwaysAskRules → 1c tool.checkPermissions → 1d Tool deny → 1e requiresUserInteraction（bypass-immune）→ 1f Content-level ask → 1g safetyCheck paths
- [固] 2a Mode-based short-circuit → 2b alwaysAllowRules match → 3 Passthrough → handler race

### Promise.race 競賽
- [固] ML 分類器對不確定操作回傳永不 resolve 的 Promise → 自動降級到下一層
- [固] Speculative Classification：分類器在 LLM token streaming 時就啟動（~50ms），快於 UI dialog（~120ms）

### Denial Tracking（級聯升級）
- [固] 雙計數器：consecutiveDenials（成功重置）+ totalDenials（永不重置）
- [固] 門檻：3 consecutive 或 20 total → fallback 到 interactive mode + 警告
- [固] Headless（subagent）模式下直接 AbortError 終止

### bypassPermissions 模式
- [固] 需 `--dangerously-skip-permissions` CLI flag
- [固] 跳過 Layer 3，但無法繞過：alwaysDenyRules、requiresUserInteraction、safetyCheck paths
- [固] 子代理只繼承 WORKER_ALLOWED_TOOLS，限制爆炸半徑

### PermissionDecision 型別
- [固] allow（可含 updatedInput）、deny（含 reason）、ask、hook_result

## 行動

- 開發新工具時，需定義 checkPermissions() 和安全屬性
- Hook 可透過 PermissionRequest 在權限決定過程中介入（非事後）
- 來源：https://claude-code-harness-blog.vercel.app/chapters/04-permission-architecture/
