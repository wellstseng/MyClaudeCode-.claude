# /upload — 上傳附件到 Discord

> 將檔案或文字內容透過 MEDIA token 上傳至 Discord。
> 全域 Skill，適用任何對話。

---

## 使用方式

```
/upload [路徑或指示]
```

### 範例

```
/upload /tmp/report.md
/upload /Users/wellstseng/data.csv
/upload 把剛才的回覆存成 summary.md 上傳
/upload 把上面的程式碼存成 main.py 上傳
```

---

## 輸入

$ARGUMENTS

---

## 執行步驟

### 分流

**有 $ARGUMENTS 且是絕對路徑**（以 `/` 開頭）：
→ 跳到 Step 2，直接輸出 MEDIA token。

**有 $ARGUMENTS 且是描述性文字**（例如「把剛才的回覆存成 xxx 上傳」）：
→ 執行 Step 1：從描述推斷要存的內容和檔名，寫入 `/tmp/`，再到 Step 2。

**無 $ARGUMENTS**：
→ 詢問使用者：「要上傳哪個檔案？請提供路徑，或說明要把什麼內容存成檔案上傳。」
→ 等待回覆後繼續。

---

## Step 1：建立暫存檔（需要時）

根據使用者指示：
- 推斷要儲存的內容（上一則回覆、特定程式碼、自訂文字）
- 推斷檔名（從描述中提取，例如「summary.md」、「report.md」）
- 若無明確檔名 → 用 `upload_YYYYMMDD_HHMMSS.md` 格式
- 用 Write 工具寫入 `/tmp/{檔名}`

---

## Step 2：輸出 MEDIA token

在回覆中輸出以下格式（Discord bot 會自動攔截並上傳）：

```
MEDIA: /path/to/file
```

同時告知使用者：
> 「已送出上傳指令：`{檔名}`（{檔案大小} bytes）」

若是暫存檔，補充：
> 「暫存於 `/tmp/{檔名}`，可隨時刪除。」
