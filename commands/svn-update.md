# /svn-update — SVN 更新工作目錄

> 在修改程式碼前執行 SVN update，確保工作目錄與伺服器同步。
> 全域 Skill，適用所有 SVN 專案。

---

## 執行流程

### Step 1: 確認 SVN 工作副本

1. 確認當前工作目錄（或其父目錄）是 SVN 工作副本：

```bash
svn info --show-item wc-root 2>/dev/null
```

- 若失敗 → 告知使用者「當前目錄不是 SVN 工作副本」，結束
- 若成功 → 記錄 WC root 路徑，繼續

### Step 2: Pre-update 檢查

1. 取得當前 revision：

```bash
svn info --show-item revision "$(svn info --show-item wc-root)"
```

2. 檢查本地修改狀態：

```bash
svn status "$(svn info --show-item wc-root)" 2>&1
```

3. 判斷：
   - 若有 `M`（modified）的 `.cs` 檔案 → 警告使用者：「有 N 個本地修改的 .cs 檔案，update 可能產生衝突。繼續？」
   - 等使用者確認後繼續
   - 若無本地修改或使用者確認繼續 → Step 3

### Step 3: 偵測工具並執行更新

依序檢查可用的 SVN 工具：

**3a. 檢查 TortoiseSVN（優先）**

```bash
TSVN=$(which TortoiseProc.exe 2>/dev/null)
if [ -z "$TSVN" ] && [ -f "/c/Program Files/TortoiseSVN/bin/TortoiseProc.exe" ]; then
  TSVN="/c/Program Files/TortoiseSVN/bin/TortoiseProc.exe"
fi
```

若找到 TortoiseProc.exe → 非阻塞啟動 GUI：

```bash
cmd //c start "" "$(cygpath -w "$TSVN")" /command:update /path:"$(cygpath -w "$(svn info --show-item wc-root)")" /closeonend:0
```

啟動後提醒使用者：

> TortoiseSVN 更新視窗已開啟。
> - 完成後請告知「完成」
> - 若有衝突請告知「有衝突」

等待使用者回報：
- 「完成」→ Step 4（驗證）
- 「有衝突」→ Step 5（衝突處理）

**3b. TortoiseSVN 未找到 → svn.exe CLI**

```bash
svn update --non-interactive "$(svn info --show-item wc-root)" 2>&1
```

解析輸出：
- `C ` 開頭 → 衝突（Conflict）
- `U ` / `A ` / `D ` → 正常更新/新增/刪除
- `At revision` 或 `Updated to revision` → 更新成功

判斷結果：
- 無衝突 → 回報成功 + revision 號，進入 Step 4
- 有衝突 → 列出衝突檔案清單，進入 Step 5

**3c. 都沒有 → 安裝引導**

告知使用者並提供安裝選項：

> 系統上找不到 TortoiseSVN 或 svn.exe。建議安裝 TortoiseSVN：
>
> **選項 A — winget（推薦）：**
> ```
> winget install TortoiseSVN.TortoiseSVN
> ```
>
> **選項 B — Chocolatey：**
> ```
> choco install tortoisesvn
> ```
>
> **選項 C — 手動下載：**
> https://tortoisesvn.net/downloads.html
>
> 安裝時建議勾選「command line client tools」，會同時安裝 svn.exe。
> 安裝完成後請重新開啟終端機再執行 `/svn-update`。

結束。

### Step 4: 驗證更新結果

1. 確認新 revision：

```bash
svn info --show-item revision "$(svn info --show-item wc-root)"
```

2. 檢查工作副本狀態：

```bash
svn status "$(svn info --show-item wc-root)" | head -20
```

3. 回報摘要：
   - 更新前後 revision 號
   - 本地修改數量（`M` 開頭）
   - 告知使用者可以開始修改程式碼

### Step 5: 衝突處理（混合模式）

**5a. 列出衝突檔案**

```bash
svn status "$(svn info --show-item wc-root)" | grep "^C "
```

顯示衝突檔案清單，並分類：
- **生成檔**（`Shared/Proto/*`、`*_Binding.cs`、`Design*.cs`）→ 建議「接受遠端版本後重新生成」
- **二進位檔**（`.mat`、`.png`、`.bytes`、`.asset`）→ 建議用 TortoiseSVN 選擇版本或手動處理
- **程式碼**（`.cs`）→ AI 分析衝突

**5b. AI 分析程式碼衝突**

對每個衝突的 `.cs` 檔案：
1. 讀取檔案，找 `<<<<<<<`、`=======`、`>>>>>>>` 衝突標記
2. 分析衝突區域：本地改了什麼、遠端改了什麼
3. 提出具體合併建議（附程式碼）
4. **等使用者逐一確認**才套用修改
5. 確認後執行 `svn resolved <file>` 標記已解決

**5c. 合併工具輔助**

偵測可用的合併工具：

```bash
which TortoiseMerge.exe 2>/dev/null
which kdiff3.exe 2>/dev/null
which WinMergeU.exe 2>/dev/null
```

若有可用工具，提供開啟選項：

```bash
cmd //c start "" "$(cygpath -w "$(which TortoiseMerge.exe)")" "$(cygpath -w "<conflict_file>")"
```

或透過 TortoiseProc：

```bash
cmd //c start "" "$(cygpath -w "$TSVN")" /command:conflicteditor /path:"$(cygpath -w "<conflict_file>")"
```

**5d. 記錄使用者偏好**

使用者選用的合併方式/工具，記錄到 `~/.claude/memory/workflow-rules.md` atom：
- 首次記錄為 `[觀]`
- 重複使用後建議晉升 `[固]`

**5e. 衝突解決後確認**

所有衝突處理完畢後：
1. 再次 `svn status` 確認無 `C` 狀態
2. 若仍有未解決衝突 → 提醒使用者
3. 全部解決 → 回到 Step 4 驗證

---

## 注意事項

- 本 Skill **只做 update**，不做 commit（commit 由工作結束同步處理）
- `--non-interactive`：防止認證過期時 bash 掛住，改為報錯提示使用者手動認證
- `cygpath -w`：Git Bash 路徑需轉換為 Windows 路徑給 TortoiseProc
- TortoiseSVN `/closeonend:0` = 不自動關閉視窗（讓使用者看到結果）
- 若 SVN 認證失敗（`E170013`），提示使用者在終端機手動執行 `svn update` 輸入帳密以快取認證
