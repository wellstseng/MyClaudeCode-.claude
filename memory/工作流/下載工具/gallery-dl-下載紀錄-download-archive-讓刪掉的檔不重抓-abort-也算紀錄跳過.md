# gallery-dl-下載紀錄-download-archive-讓刪掉的檔不重抓-abort-也算紀錄跳過

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: gallery-dl, download-archive, 下載紀錄, 重複下載, 刪掉後重抓, --abort
- Created-at: 2026-11-03
- Source: session:164208c3#16d6c83a 2026-11-03
- Quote: 「修改SKILL 加上過濾的選項 如果有指定kid 照片下載下來後只保留符合特徵的照片 可以按照主角, 合照, 不確定三個分類，其餘全部刪掉 不確定的篩選後我確認完會刪掉」

## 知識

- [臨] gallery-dl 預設靠「檔案存不存在」跳過。下載後會刪檔、搬檔的流程要加 --download-archive <sqlite>：檢查下載紀錄排在檢查檔案之前，就算檔案不在也會跳過，輸出一樣是「# 路徑」。
- [臨] --abort N 的「連續 N 張跳過」也算下載紀錄跳過的，只補新照片的模式照樣會停。
- [臨] 要補登既有的檔案，用 gallery_dl.archive.connect(path, extractor.category, Extractor.archive_fmt).add(kwdict) 寫，不要手拼 key（例：Facebook 的 key 是 facebook{id}.{extension}）。預設只有下載成功才寫進紀錄，被 --filesize-min 淘汰的不會寫。

## 行動

- 用 gallery-dl 抓完會刪檔或搬檔的流程，一開始就加 --download-archive，並先補登既有檔案再刪
