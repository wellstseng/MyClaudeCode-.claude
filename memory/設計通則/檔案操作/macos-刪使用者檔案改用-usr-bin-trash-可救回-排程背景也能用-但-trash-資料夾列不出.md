# macos-刪使用者檔案改用-usr-bin-trash-可救回-排程背景也能用-但-trash-資料夾列不出

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: 垃圾桶, trash, 刪除檔案, macOS, 可救回, ~/.Trash
- Created-at: 2026-11-03
- Source: session:164208c3#16d6c83a 2026-11-03
- Quote: 「修改SKILL 加上過濾的選項 如果有指定kid 照片下載下來後只保留符合特徵的照片 可以按照主角, 合照, 不確定三個分類，其餘全部刪掉 不確定的篩選後我確認完會刪掉」

## 知識

- [臨] macOS 26 內建 /usr/bin/trash <檔案…>，會把檔案丟到垃圾桶，清空前都救得回。程式要自動刪使用者的檔案（例如篩掉的照片）時用它，不要用 rm。
- [臨] pm2 底下的排程子程序也能用（實測）。沒有「完整磁碟取用權」時 ls ~/.Trash 會報 Operation not permitted，所以確認有沒有丟掉要看原位置檔案還在不在，不要去列垃圾桶。

## 行動

- 程式要刪使用者的檔案時用 /usr/bin/trash，丟完檢查原位置確認
