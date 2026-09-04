# Sqlx 讀取端三個踩點：字串定序、TINYINT 當 bool、DESC 的 ENUM

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: Sqlx, MysqlxClient, unknown type: Bytes, utf8mb3, utf8mb4_0900_as_cs, collation, TINYINT bool, DESC, SHOW INDEX, X protocol, MysqlxUtils.Column
- Created-at: 2026-08-13
- Related: dotnet-mysqldata-collation-id-相容

## 知識

- [臨] Sqlx（CoreModule/Db/Sqlx）的欄位中繼資料解析只認得特定定序：字串欄是 `utf8mb4_0900_as_cs`（id 278）家族才讀得回；utf8mb3 建的字串欄直接丟 `NotSupportedException: unknown type: Bytes`，而且是在 client loop 丟——整條連線被打斷，不只是那筆查詢失敗。
- [臨] Sqlx 把 TINYINT（Uint length<=4）一律當 bool 解，值超過 1 就丟 `ArgumentException: Value does not fall within the expected range`。要讀一般 TINYINT 要 `CAST(x AS SIGNED)`。
- [臨] `DESC` / `SHOW INDEX` 的結果集含 ENUM 欄位，Sqlx 完全沒處理 ENUM → 同樣斷線；改查 information_schema 也要 `CAST(... AS BINARY)`（它的欄位是 utf8mb4_0900_ai_ci）。
- [臨] 這些在正式環境沒爆，是因為產品自己建的庫/表都是 utf8mb4_0900_as_cs（`MysqlxClient.Use` 與 `InternalMigrate` 寫死）；一碰到別人建的表或 MySQL 8 預設定序就現形。

## 行動

- 用 Sqlx 存取的表，建表 DDL 一律帶 `DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs`（兼講 4 位元組字元）；照抄舊系統的 `CHARSET=utf8` 會變成寫得進讀不出。
- 用 Sqlx 讀別人建的表前先確認定序與 TINYINT 欄；要讀表結構改查 information_schema 並 CAST AS BINARY，別用 DESC/SHOW INDEX。
