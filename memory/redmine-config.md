# Redmine 工具設定

- Scope: global
- Confidence: [固]
- Trigger: Redmine, sgi, API, query, 日報, 週報, redmine-70
- Last-used: 2026-04-07
- Confirmations: 21
- Related: project-ecosystem, team-roster

## 知識

### API 端點
- [固] Base URL：https://redmine-70.uj.com.tw
- [固] sgi project id：11
- [固] sgi-programmer project id：26（已廢除）
- [固] 程式待辦查詢：query_id=299

### Bot 帳號（自動化用）
- [固] 帳號：wellsaibot | User ID：235
- [固] API Key：98a3085f9801d76ed26f49469c30452334a55a69

### Wells 個人帳號（查詢用，避免寫入）
- [固] 帳號：wellstseng | User ID：157
- [固] API Key：9134e8f905cf18ff82ca1a6463b5be1a2ee8e005

### CR Redmine 設定
- [固] CR Project：tsg-programmer（id=27）| Category：CR（category_id=120）
- [固] 優先度對應：Critical=A.高(3)、Improvement=B.中(2)、Minor=C.低(1)
- [固] 標題格式：`[CR][target短名] rXXXX 問題標題 (作者)`
- [固] 指派規則：SVN 作者 → query-team 查 redmineId → 找不到 fallback bot(235)

## 行動

- 操作 Redmine API 時使用 bot 帳號（wellsaibot），不用個人帳號寫入
- 日報/週報撈取以 sgi + query_id=299 為基準
