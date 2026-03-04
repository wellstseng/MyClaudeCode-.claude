# 原子記憶系統規格 v2.1

> Atomic Memory System V2.1 Specification
> 適用於 Claude Code 跨 session 知識管理。
> V2：Hybrid RECALL — Keyword Trigger + Vector Semantic Search + Local LLM
> V2.1：Write Gate + Decay Enforce + Schema 擴展 + Confirmations 自動遞增

---

## 一、系統概述

原子記憶系統將 AI 助手的跨 session 知識組織為**兩層結構**：

| 層 | 路徑 | 用途 |
|----|------|------|
| 全域層 | `~/.claude/memory/` | 跨專案共用知識（使用者偏好、通用決策） |
| 專案層 | `~/.claude/projects/{slug}/memory/` | 專案綁定知識（架構、坑點、待辦） |

每層包含：
- `MEMORY.md` — 索引表 + 高頻事實（≤30 行）
- 多個 atom 檔 — 獨立主題的知識單元（≤200 行/檔）
- `_distant/` — 遙遠記憶區（已淘汰但不刪除的 atom）

---

## 二、決策記憶三層分類 [固]/[觀]/[臨]

### 2.1 分類定義

| 符號 | 名稱 | 定義 | 引用行為 |
|------|------|------|---------|
| `[固]` | 固定記憶 | 跨多次對談確認，長期有效 | 直接引用，不需確認 |
| `[觀]` | 觀察記憶 | 已決策但可能演化 | 簡短確認「X 仍適用？」 |
| `[臨]` | 臨時記憶 | 單次決策，下次觸及時應重新評估 | 明確確認「上次你決定 X，這次也這樣嗎？」 |

### 2.2 建立規則

| 觸發情境 | 初始等級 | 範例 |
|----------|---------|------|
| 使用者說「記住」「以後都這樣」「永遠不要」 | `[固]` | "Handler 以後都用傳統寫法" |
| 使用者做取捨（選 A 不選 B） | `[臨]` | "先不修 SQL injection" |
| 使用者糾正 AI 行為 | `[觀]` | "不要主動重構周圍程式碼" |
| AI 工作中發現陷阱/坑點 | `[觀]` | "AreaFacade 共享集合會重入" |
| 同 session 重複出現 3+ 次的模式 | `[觀]`（建議） | 使用者總是要求最小變動 |
| 預設（無法歸類） | `[臨]` | — |

### 2.3 晉升條件

| 路徑 | 條件 | 機制 |
|------|------|------|
| `[臨]`→`[觀]` | 2+ sessions 引用 或 使用者再次確認 | AI 主動問確認 |
| `[觀]`→`[固]` | 4+ sessions 未被推翻 或 使用者明確永久化 | 記錄演化日誌 |
| `[臨]`→`[固]` | 使用者對既有 `[臨]` 說「以後都這樣」 | 跳級晉升 |

晉升由 `Confirmations` 計數驅動：每次 session 引用且未被推翻時 +1。

### 2.4 降級與遙遠記憶

預設移入**遙遠記憶區**（`_distant/`），按 `年_月` 歸檔。`--purge` 永久刪除。

#### 觸發條件

| 條件 | 動作 | --enforce 行為 (v2.1) |
|------|------|----------------------|
| `[臨]` Last-used > 30 天 | 建議移至 `_distant/` | **自動移入** + 寫入演化日誌 |
| `[觀]` Last-used > 60 天 | 確認；無回應則移入 | 標記 `pending-review`，不自動移入 |
| `[固]` 被使用者推翻 | 降為 `[觀]` | 同左 |
| `[固]` Last-used > 90 天 | 報告提醒 | 同左（永不自動淘汰） |
| 使用者明確拒絕 | 移入遙遠記憶 | 同左 |
| TTL 設定且已過期 (v2.1) | 依 confidence 處理 | [臨] 自動移入；[觀][固] 標記 |

#### 遙遠記憶區結構

```
memory/
  _distant/
    2026_01/
      old-pitfall.md
    2026_02/
      deprecated-decision.md
```

#### 拉回機制

1. `memory-audit.py --search-distant <keyword>` 搜尋遙遠記憶
2. `memory-audit.py --restore <path>` 移回活躍區
3. 拉回後 Confidence 重置為 `[臨]`，重新走晉升流程

### 2.5 演化日誌

每個 atom 底部附加，上限 10 筆（超出合併為摘要行）：

```markdown
## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-02-26 | 建立為 [臨] | session:健檢修復 |
| 2026-03-01 | [臨]→[觀] 第2次確認 | session:效能討論 |
| 2026-03-15 | [觀]→[固] 第4次確認 | session:重構評估 |
```

---

## 三、資料夾結構與命名

### 3.1 目錄佈局

```
~/.claude/
  memory/                              # 全域層
    MEMORY.md                          # 索引 (≤30 行)
    {atom-name}.md                     # 活躍 atom
    _distant/                          # 遙遠記憶
      {年}_{月}/
        {atom-name}.md
  tools/
    memory-audit.py                    # 健檢腳本

  projects/{project-slug}/
    memory/                            # 專案層
      MEMORY.md                        # 索引 (≤30 行)
      {atom-name}.md                   # 活躍 atom
      _distant/                        # 遙遠記憶
        {年}_{月}/
          {atom-name}.md
```

### 3.2 Atom 檔案命名慣例

- **小寫 kebab-case**：`architecture.md`, `sgi-pitfalls.md`
- **描述內容領域**，最長 40 字元
- **不加日期前綴**（日期在元資料）
- **可加類別前綴**：`risk-auth.md`, `decision-protobuf.md`

### 3.3 Atom 元資料標準格式

```markdown
# [Atom 標題]

- Scope: [global|project]
- Confidence: [固|觀|臨]
- Type: semantic                 ← v2.1（semantic/episodic/procedural，預設 semantic）
- Trigger: kw1, kw2, kw3
- Last-used: YYYY-MM-DD
- Created: YYYY-MM-DD            ← v2.1（首次建立日期）
- Confirmations: N
- TTL: 30d                       ← v2.1（可選，null = 由 confidence 決定）
- Expires-at: YYYY-MM-DD         ← v2.1（可選，自動計算）
- Privacy: public                ← v2.1（public/internal/sensitive，預設 public）
- Tags: pitfall, architecture    ← v2.1（可選，分類標籤）
- Related: other-atom-name       ← v2.1（可選，關聯 atom）
- Supersedes: old-atom-name      ← v2.1（可選，取代的舊 atom）
- Quality: 0.85                  ← v2.1（Write Gate 品質評分，0-1）

## 知識

- [固] 事實 1
- [觀] 事實 2

## 行動

- 觸及時的執行指引

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
```

**必要欄位**：Scope, Confidence, Trigger, Last-used
**v2.1 可選欄位**（不存在時使用預設值，既有 atom 零修改即可運作）：

| 欄位 | 預設值 | 說明 |
|------|--------|------|
| Type | semantic | semantic/episodic/procedural |
| Created | （空） | 首次建立日期 |
| Confirmations | 0 | session 引用且未推翻時自動 +1 |
| TTL | null | 自訂存活期，null = 由 confidence 閾值決定 |
| Expires-at | null | 自動計算或手動設定 |
| Privacy | public | public/internal/sensitive |
| Tags | （空） | 分類標籤 |
| Related | （空） | 關聯 atom 名稱 |
| Supersedes | （空） | 取代的舊 atom 名稱 |
| Quality | （空） | Write Gate 品質評分（0-1） |

**必要區段**：知識, 行動
**可選區段**：演化日誌

### 3.4 MEMORY.md 索引格式

```markdown
# Atom Index — {層名稱}

> Session 啟動時先讀此索引。比對 Trigger → Read 對應 atom。

| Atom | Path | Trigger | Confidence |
|------|------|---------|------------|
| {name} | memory/{name}.md | kw1, kw2 | [固] |

---

## 高頻事實

- [固] 事實 1（5~7 條最常用事實）
```

**硬限制**：≤30 行。超過時必須將細節移至 atom 檔。

### 3.5 Trigger 關鍵詞設計原則

- **中英混合**：中文操作語 + 英文技術術語
- **每 atom 3~8 個**：太少=永遠不觸發，太多=過度觸發
- **避免同層重疊**：兩 atom 共用關鍵字→合併或區分
- **含症狀詞**：`crash`, `失敗`, `找不到`（錯誤情境也能觸發）
- **含動作詞**：`建置`, `deploy`, `修復`（操作意圖觸發）

### 3.6 記憶路徑碎片化處理

Claude Code auto-memory 路徑由工作目錄自動生成。同一邏輯專案可能產生多份 memory。

**原則**：
1. 每個邏輯專案指定唯一**主記憶路徑**
2. 其他路徑的 MEMORY.md 開頭加 pointer：
   ```markdown
   > ⚠️ 此專案主記憶位於 `~/.claude/projects/{主路徑}/memory/`，本路徑為副本。
   ```
3. 健檢腳本偵測重複（比對標題 + Trigger），報告疑似重複並建議合併

---

## 四、落地運作流程

### 4.1 Session 啟動（載入）

```
1. Read 全域 MEMORY.md
   └→ 取得 Atom Index 表 + 高頻事實

2. Read 專案 MEMORY.md
   └→ 取得 Atom Index 表 + 高頻事實

3. 比對使用者第一個訊息 vs 兩層 Trigger 關鍵詞
   └→ 命中 → Read 對應 atom 檔
   └→ 未命中 → 不載入（省 token）
```

### 4.2 對話中（觸發與累積）

```
每次使用者訊息：

  1. 掃描訊息 vs 未載入 atom 的 Trigger
     └→ 新命中 → Read 該 atom

  2. 引用已載入 atom 知識時：
     └→ [固] → 直接引用
     └→ [觀] → 簡短確認
     └→ [臨] → 明確確認

  3. 產生新知識時：
     └→ 暫存在 session context
     └→ 記錄：內容 + 分類依據 + 觸發情境
```

### 4.3 Session 結束（同步寫入）

```
完成有意義修改後，主動提出同步建議：

1. 彙整 session 新知識
   └→ 歸類到既有 atom 或建立新 atom
   └→ 標記 [固]/[觀]/[臨]

2. 更新 atom 檔
   └→ 新知識 → 加入知識段落
   └→ 已引用 atom → Last-used + Confirmations +1
   └→ 演化日誌 → 追加記錄

3. 更新 MEMORY.md 索引（若有新增/移除 atom）

4. 檢查淘汰條件 → 超期 atom 提醒移入遙遠記憶

5. 版控提交
```

### 4.4 定期健檢（手動觸發）

```
python memory-audit.py
  → 格式合規檢查
  → 過期分析 + 晉升/降級建議
  → 索引一致性驗證
  → 重複偵測（碎片化）
  → 遙遠記憶掃描
  → 產出報告
```

---

## 五、健檢腳本規格

### 5.1 檔案

`~/.claude/tools/memory-audit.py` — Python 3.8+，零外部依賴。

### 5.2 CLI

```
python memory-audit.py [OPTIONS]

掃描與報告：
  (預設)                    掃描全部層，產出 Markdown 報告
  --global-only             只掃描全域層
  --project PATH            指定專案 memory 目錄
  --json                    JSON 格式輸出
  --verbose                 含逐 atom 詳細資訊

自動淘汰（v2.1）：
  --enforce                 自動執行淘汰：[臨]>30d 移入 _distant/，[觀]>60d 標記 pending-review
  --dry-run                 搭配 --enforce，只報告不執行

遙遠記憶操作：
  --search-distant <kw>     搜尋遙遠記憶區
  --restore <path>          從遙遠記憶拉回活躍區
  --move-distant <path>     手動移入遙遠記憶
```

### 5.3 檢查項目

| 類別 | 檢查 | 閾值 |
|------|------|------|
| 格式合規 | 必要元資料（Scope/Confidence/Trigger/Last-used） | 缺一報錯 |
| 格式合規 | 必要區段（知識/行動） | 缺一報錯 |
| 格式合規 | Confidence 值合法 | 必須為 [固]/[觀]/[臨] |
| 格式合規 | MEMORY.md 行數 | ≤30 行 |
| 格式合規 | Atom 檔行數 | ≤200 行 |
| 格式合規 | Trigger 數量 | 3~8 個 |
| 過期分析 | [臨] Last-used | >30 天建議移入遙遠記憶 |
| 過期分析 | [觀] Last-used | >60 天建議確認 |
| 過期分析 | [固] Last-used | >90 天列入提醒 |
| 晉升建議 | [臨] Confirmations | ≥2 建議晉升為 [觀] |
| 晉升建議 | [觀] Confirmations | ≥4 建議晉升為 [固] |
| 索引一致 | 索引 ↔ 檔案交叉比對 | 零 mismatch |
| 碎片偵測 | 跨路徑 atom 標題+Trigger 相似度 | 報告疑似重複 |

### 5.4 閾值常數

```python
STALENESS_THRESHOLDS = {'[固]': 90, '[觀]': 60, '[臨]': 30}
PROMOTION_THRESHOLDS = {'[臨]': 2, '[觀]': 4}
INDEX_MAX_LINES = 30
ATOM_MAX_LINES = 200
TRIGGER_RANGE = (3, 8)
```

---

## 六、Write Gate（v2.1 新增）

### 6.1 概述

Write Gate 在新知識寫入前進行品質評估與去重檢查，降低噪音累積。

### 6.2 決策流

```
新知寫入決策流：
┌─ 使用者說「記住」「以後都這樣」
│  └→ 直接 Add，[固]，quality=1.0
│
├─ AI 偵測到坑點/陷阱
│  └→ Add，[觀]，quality=0.7
│
└─ 其他新知識
   │
   ├─ Dedup 檢查：embed → search existing (score>0.80)
   │  ├─ >0.95 → Skip（完全重複）
   │  ├─ 0.80-0.95 → 建議 Update 既有 atom
   │  └─ <0.80 → 進入品質評分
   │
   └─ Quality Score（rule-based）：
      ├─ ≥0.5 → Add
      ├─ 0.3-0.5 → Ask User 確認
      └─ <0.3 → Skip（log to audit trail）
```

### 6.3 Quality Score 計算

| 條件 | 分數 |
|------|------|
| 長度 >20 chars | +0.15 |
| 長度 >50 chars | +0.10 |
| 技術術語 ≥2 | +0.15 |
| 使用者明確觸發 | +0.35 |
| 含具體值（版本號/路徑/設定值） | +0.15 |
| 非暫時性（不含 timeout/retry/暫時） | +0.10 |

### 6.4 工具

`~/.claude/tools/memory-write-gate.py` — CLI 入口，搭配 session-end 同步使用。

```
python memory-write-gate.py --content "知識文字" [--classification "[觀]"] [--trigger-context "..."]
  → 輸出 JSON：{action, quality_score, reason, dedup_match?}
```

### 6.5 設定

`~/.claude/workflow/config.json` 的 `write_gate` 區塊：

```json
{
  "enabled": true,
  "auto_threshold": 0.5,
  "ask_threshold": 0.3,
  "dedup_score": 0.80,
  "skip_on_explicit_user": true
}
```

---

## 七、向量搜尋層（RAG）

### 7.1 概述

向量搜尋作為 keyword trigger 的**補充層**（非替換），提升語意相關但用詞不同的 atom 觸發率。

架構：**Hybrid RECALL** — keyword matching（確定性、10ms）+ semantic search（概率性、200-500ms）並行。

### 7.2 元件

| 元件 | 位置 | 用途 |
|------|------|------|
| Memory Vector Service | `tools/memory-vector-service/service.py` | HTTP daemon @ port 3849 |
| indexer.py | 同目錄 | 段落級 atom chunking + embedding + ChromaDB |
| searcher.py | 同目錄 | 語意搜尋 |
| reranker.py | 同目錄 | LLM re-ranking / query rewrite / 知識萃取 |
| rag-engine.py | `tools/rag-engine.py` | CLI 入口 |
| ChromaDB | `memory/_vectordb/` | 向量持久化存儲 |

### 7.3 Embedding 模型（雙軌）

| 後端 | 模型 | 用途 |
|------|------|------|
| Ollama | `qwen3-embedding` | 主力（MTEB 多語言 #1） |
| sentence-transformers | `BAAI/bge-m3` | Fallback（Ollama 未啟動時） |

### 7.4 索引策略

- **段落級切割**：每個 `- ` bullet point 為一個 chunk（向量化單位）
- 元資料區（Scope/Confidence/Trigger）和演化日誌不索引
- 每個 chunk 攜帶 metadata：atom_name, section, confidence, layer, file_hash
- 增量索引：比對 file_hash，只重新索引有變動的 atom
- PostToolUse hook 自動觸發增量索引

### 7.5 搜尋流程

```
UserPromptSubmit (3s timeout)
├─ keyword match (existing, ~10ms)
├─ HTTP → Vector Service (~200-500ms, timeout 2s)
├─ merge & deduplicate (keyword 優先)
└─ load atoms within token budget
```

### 7.6 本地 LLM 功能（離線路徑）

| 功能 | 模型 | 觸發 | 延遲 |
|------|------|------|------|
| 查詢改寫 | qwen3:4b | `rag-engine.py search --enhanced` | ~2s |
| Re-ranking | qwen3:4b | `rag-engine.py search --rerank` | ~4s |
| 知識萃取 | qwen3:4b | session 結束同步 | ~3s |

### 7.7 設定

`~/.claude/workflow/config.json` 的 `vector_search` 區塊：

```json
{
  "enabled": true,
  "service_port": 3849,
  "embedding_backend": "ollama",
  "embedding_model": "qwen3-embedding",
  "fallback_backend": "sentence-transformers",
  "fallback_model": "BAAI/bge-m3",
  "ollama_llm_model": "qwen3:4b",
  "search_top_k": 5,
  "search_min_score": 0.65,
  "search_timeout_ms": 2000,
  "auto_start_service": true,
  "auto_index_on_change": true
}
```

---

## 八、版本紀錄

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-03-02 | 初版：三層分類 + 資料夾結構 + 健檢腳本規格 |
| 1.1 | 2026-03-03 | 新增 §七 向量搜尋層（RAG）規格 |
| 2.0 | 2026-03-03 | **原子記憶 V2**：Hybrid RECALL 實作完成（keyword + vector + LLM） |
| 2.1 | 2026-03-04 | **V2.1 Sprint 1**：Schema 擴展（Type/TTL/Tags/Related/Supersedes/Quality）、Write Gate §六、--enforce 自動淘汰、Confirmations 自動遞增 |
