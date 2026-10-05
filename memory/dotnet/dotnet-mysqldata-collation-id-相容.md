# dotnet-mysqldata-collation-id-相容

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: MySql.Data, MySQL, collation, KeyNotFoundException, SetFieldEncoding, net8 升級, connector
- Created-at: 2026-07-02
- Related: titan-dotnet-split, toolchain, sqlx-讀取端三個踩點字串定序tinyint-當-booldesc-的-enum

## 知識

- [臨] MySql.Data 8.0.22 連 MySQL Server 8.0.30+ 會在 MySqlField.SetFieldEncoding() 丟 KeyNotFoundException（例:key '19974'）——舊 connector 內建 collation/charset id 表不含 8.0.30+ 新增的 id。修法:升 MySql.Data 至 8.0.33（同 8.0.x 線最保守版本即可），不需跨 8.1+/9.x。2026-07-02 tslg-servercore P1S1 實機驗出（server 8.0.42）:升版前 6 支測試全掛、升版後 9/9 過。
- [臨] 症狀特徵:build 全綠、連線成功，僅在讀取欄位 metadata 時炸——容易誤判為資料問題而非 connector 版本問題。TargetFramework 升級（3.1→net8）本身無關，純粹是 server 版本 vs connector 版本落差。

## 行動

- （依知識內容判斷）
