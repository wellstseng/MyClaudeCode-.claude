# 覆轍：reply.ts 分散式增量修改

- Scope: global
- Confidence: [固]
- Trigger: reply.ts, 分散修改, 增量修改, 同檔案多次, same_file_3x
- Last-used: 2026-03-25
- Confirmations: 1
- Related: fail-cognitive

## 問題模式

- [固] reply.ts 跨 5+ session 被修改 3 次以上（turnId 傳遞 → recordAssistantTurn → thinking 累積）
- [固] 根因：功能設計不完整就動手，每次補一小塊，形成分散式修改
- [固] 症狀：同一功能的 interface 分 N 次加到同一個 function signature

## 行動

- 修改 reply.ts / discord.ts / session.ts 等核心串聯檔案前，先完整設計 interface，一次改完
- 有 `same_file_3x` 警告時，停下來先盤點「這個功能還缺什麼」，不要又補一刀
