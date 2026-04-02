# Claude Code Design Patterns

- Scope: global
- Confidence: [固]
- Trigger: design pattern, 設計模式, harness checklist, fail-open, fail-closed, memoize invalidate, subprocess JSON, generator pattern, cache sharing pattern, layered permission, lazy schema, feature gating
- Last-used: 2026-04-01
- Confirmations: 1
- Related: cc-harness-overview, cc-tool-system, cc-query-loop, cc-hook-system, cc-permission-system

## 知識

### 7 大核心設計模式
- [固] P1 Generator/Async Iterator：背壓控制+組合性+取消性+型別安全
- [固] P2 Cache-Sharing Between Contexts：父子代理共享 CacheSafeParams（85-90% 成本節省）
- [固] P3 Layered Permission with Racing：Promise.race 三層競賽（ML 分類器對不確定案例回傳永不 resolve 的 Promise）
- [固] P4 Fail-Open Services：輔助服務失敗不阻塞核心功能（遙測/分析/設定 → 預設值）
- [固] P5 Lazy Schema + Feature Gating：打破循環依賴 + 編譯時死碼消除
- [固] P6 Memoize + Invalidate：快照型（Git 狀態 Session 級）vs 活躍型（Hook 設定 File watcher）
- [固] P7 Subprocess + JSON Protocol：外部程序崩潰隔離+語言無關+超時防護

### 模式間依賴
- [固] P1→P3：race 結果需在 generator 框架內被 yield
- [固] P5→P2：打破循環依賴使工具集合初始化正確
- [固] P3→P7：Hook 腳本評估基於 Subprocess + JSON

### Harness Engineering Checklist
- [固] 安全性：受控工具介面 + fail-closed + 分層權限 + 拒絕追蹤
- [固] 效能：Prompt Cache Sharing + 唯讀並行 + 串流式執行 + Memoization
- [固] 擴展性：22 個 Hook 事件 + Skill 系統 + MCP 協議 + Plugin 隔離
- [固] 可觀測性：工具進度回報 + 任務生命週期追蹤 + 成本統計 + OpenTelemetry
- [固] 韌性：上下文壓縮 + Fail-Open + Graceful Shutdown + 雙層快取

## 行動

- 開發新工具/hook/skill 時，對照 Checklist 確認安全+效能+擴展+可觀測+韌性
- 來源：https://claude-code-harness-blog.vercel.app/chapters/10-design-patterns-summary/
