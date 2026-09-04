# mongodb-replacement-upsert-不併filter等值鍵

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: mongodb, upsert, ReplaceOne, replacement, filter, nUpserted, 查無, UpdateOne, $set, mongo 寫入消失
- Created-at: 2026-08-28

## 知識

- [臨] MongoDB upsert 行為不對稱：**operator-update（$set 形）的 upsert 會把 filter 的等值條件併進新文件；replacement（整份取代形）的 upsert 不會**——新文件＝取代文件本身（＋自動 _id）。症狀：以 {key:x} 當 filter 的 ReplaceOne upsert 插入的文件缺 key 欄位，之後按 key 查詢永遠接不回來、每次 upsert 再插一份無主檔（profiler 實證 nUpserted=1 但查無）。修法：replace 形文件自己把 filter 鍵補進去（tslg-servercore GooMongo.EnsureUidInReplaceDoc 實例）。
- [臨] titan 對照：titan C／titan_dotnet 的 mongo 層同様沒補 uid（util_mongo.c 與我們逐行同構），但 titan 天然無事——它在 BaseEntity.archive_module_define 把 uid 注入存檔定義，全量 dump 的文件自帶 uid（tracked $set 形才 path_to_ignore 忽略 uid，那條路 server 會併）。tslg-servercore 裁掉該靜態轉手時斷了這半條閉環，修法＝防護移到 C# 送出層。寓意：裁剪藍本的「轉手層」時，檢查裡面有無隱含行為（如欄位注入）需要異地補位。

## 行動

- 寫 ReplaceOne/replace 形 upsert 時，確認取代文件自帶查詢鍵；懷疑「寫入成功但查無」先開 db.setProfilingLevel(2) 看 server 端實收的 command 與 nUpserted
