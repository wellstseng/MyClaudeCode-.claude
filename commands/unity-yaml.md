# /unity-yaml — Unity YAML Asset 操作

> 解析、生成、修改 Unity .asset / .prefab / .unity 檔案。
> 全域 Skill，適用所有 Unity 專案。

---

## 使用方式

```
/unity-yaml <操作描述>
```

### 參數

| 參數 | 必填 | 說明 | 範例 |
|------|------|------|------|
| 操作描述 | 是 | 要執行的操作（自然語言） | `解析 MapData.asset 的結構` |

### 使用範例

```
/unity-yaml 解析 MapData.asset 的結構
/unity-yaml 生成一個新的 ScriptableObject asset
/unity-yaml 修改 MapData.asset 的 ChunkSize 為 150
/unity-yaml 從 MapData_001.asset 模板複製一份 MapData_003.asset
```

### 錯誤處理

- **未帶操作描述** → 顯示本使用說明（含操作類型列表），結束
- **操作類型不明確** → 詢問使用者要做哪種操作
- **檔案路徑不存在** → 提示路徑不存在

工具位置：`~/.claude/tools/unity-yaml-tool.py`

---

## 操作類型

### 1. 解析 (parse)

讀取 Unity YAML 檔案並輸出 JSON 結構。

```bash
python ~/.claude/tools/unity-yaml-tool.py parse "<filepath>"
```

用途：分析現有 asset 結構、查找特定欄位值。

### 2. 生成 ScriptableObject (.asset)

從 JSON 規格生成 .asset 檔案。

**需要資訊：**
- `name`：Asset 名稱
- `script_guid`：對應 C# MonoScript 的 GUID（從 `.cs.meta` 取得）
- `fields`：自訂欄位的 key-value

```bash
python ~/.claude/tools/unity-yaml-tool.py generate-asset '<json_spec>' "<output_path>"
```

JSON 規格範例：
```json
{
  "name": "MyConfig",
  "script_guid": "abc123def456789012345678abcdef00",
  "fields": {
    "health": 100,
    "speed": 5.5,
    "spawnPoints": [{"x": 1, "y": 0, "z": 3}]
  }
}
```

**生成後必須同時生成 .meta：**
```bash
python ~/.claude/tools/unity-yaml-tool.py generate-meta "<output_path>.meta"
```

### 3. 生成 Prefab (.prefab)

生成含 GameObject 階層的簡單 prefab。

```bash
python ~/.claude/tools/unity-yaml-tool.py generate-prefab '<json_spec>' "<output_path>"
```

JSON 規格範例：
```json
{
  "name": "EnemySpawner",
  "position": {"x": 0, "y": 0, "z": 0},
  "children": [
    {"name": "SpawnPoint_A", "position": {"x": 5, "y": 0, "z": 0}},
    {"name": "SpawnPoint_B", "position": {"x": -5, "y": 0, "z": 0}}
  ]
}
```

**生成後必須同時生成 .meta：**
```bash
python ~/.claude/tools/unity-yaml-tool.py generate-meta "<output_path>.meta" --importer PrefabImporter
```

### 4. 修改欄位 (modify)

修改現有 Unity YAML 檔案的特定欄位。

```bash
python ~/.claude/tools/unity-yaml-tool.py modify "<filepath>" "<field_path>" "<value>"
```

field_path 格式：`ClassName.field.subfield` 或 `field.subfield`（單物件檔案）

範例：
```bash
python ~/.claude/tools/unity-yaml-tool.py modify "MapData.asset" "MonoBehaviour.Setting.ChunkSize" "150"
```

### 5. 模板化複製 (template)

從現有 asset 複製並替換指定欄位。

```bash
python ~/.claude/tools/unity-yaml-tool.py template "<source>" "<output>" '<json_replacements>'
```

替換 JSON 範例：
```json
{
  "MonoBehaviour.m_Name": "NewMapData",
  "MonoBehaviour.Setting.Name": "003",
  "MonoBehaviour.Setting.ChunkNum.x": 50
}
```

### 6. 生成 .meta

為任何 asset 生成對應的 .meta 檔案。

```bash
python ~/.claude/tools/unity-yaml-tool.py generate-meta "<output_path>" [--guid <guid>] [--importer <type>]
```

| Importer | 對應檔案類型 |
|----------|-------------|
| NativeFormatImporter | .asset (預設) |
| PrefabImporter | .prefab |
| DefaultImporter | .unity, 資料夾 |

---

## 執行流程

### Step 1: 判斷操作類型

根據使用者描述判斷要做哪種操作（parse / generate / modify / template）。
若不明確，詢問使用者。

### Step 2: 收集必要資訊

- **生成 .asset**：需要 script GUID → 從對應 `.cs.meta` 檔讀取
- **生成 prefab**：需要階層結構描述
- **修改**：需要檔案路徑 + 欄位路徑 + 新值
- **模板**：需要來源檔 + 替換 mapping

若使用者只給了 C# class 名稱但沒給 GUID：
```bash
# 在專案中搜尋對應的 .cs.meta
grep -r "guid:" "$(find . -name 'ClassName.cs.meta' -print -quit 2>/dev/null)"
```

### Step 3: 執行操作

呼叫 `unity-yaml-tool.py` 對應的子命令。

### Step 4: 驗證

- 生成的檔案：用 `parse` 命令回讀確認結構正確
- GUID 衝突檢查：`grep -r "<generated_guid>" Assets/ --include="*.meta"` 確認無重複
- 回報結果給使用者

---

## 限制與注意事項

- **不要從零生成 .unity scene** — 太複雜，建議用 Unity `-batchmode -executeMethod`
- **不要生成含複雜 Component 的 prefab**（ParticleSystem、Animator 等）— 參數太多易出錯，建議用模板
- 生成的 .asset / .prefab **必須配對 .meta 檔**，否則 Unity 開啟時會自動生成隨機 GUID 導致引用斷裂
- Unity YAML 用 2-space 縮排，工具已內建此格式
- fileID 對 ScriptableObject 固定為 `11400000`，prefab 物件用隨機大數
