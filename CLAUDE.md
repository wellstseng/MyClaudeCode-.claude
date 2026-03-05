# 通用工作流引擎（原子記憶 V2.4）

> 本檔案為全域自動載入指令，適用於所有專案。
> 專案特有的知識（路徑、架構、約束）由各專案根目錄的 `CLAUDE.md` 定義。

---

## 一、文件骨架與知識庫（_AIDocs 體系）

### Session 啟動檢查（每次對話開始時執行）

**每個 session 的第一次互動前**，檢查當前專案根目錄是否有 `_AIDocs/` 目錄：

- **沒有 `_AIDocs/`** → 自動執行 `/init-project` skill（`~/.claude/commands/init-project.md`），為專案建立知識庫骨架與記憶工作流
- **已有 `_AIDocs/`** → 啟用下方「工作中維護規則」，正常工作

### 工作中維護規則

當專案**已有 `_AIDocs/`** 時，自動啟用以下規則：

1. **開工前必讀**：進行分析或修改前，先讀 `_AIDocs/_INDEX.md` 確認是否已有相關文件
2. **禁止憑記憶作業**：不確定的架構事實必須查文件或原始碼，禁止猜測
3. **活文件更新**：修改了核心結構、發現新認知、踩到陷阱時，必須更新對應 `_AIDocs/*.md` + `_CHANGELOG.md`
4. **新增文件時**：同步更新 `_AIDocs/_INDEX.md`

---

## 二、原子記憶系統（兩層 + 雙 LLM）

原子記憶分 **全域層** 和 **專案層**，每層各有 `MEMORY.md`（Atom Index + 高頻事實）。

### 雙 LLM 記憶架構

原子記憶由兩層 LLM 協作：

| 角色 | 引擎 | 職責 | 延遲 |
|------|------|------|------|
| **雲端 LLM** | Claude Code | 記憶演進決策：何時寫入、分類判斷、晉升/淘汰、衝突裁決、上下文解讀 | — |
| **本地 LLM** | Ollama qwen3 | 語意處理：embedding 生成、query rewrite、search re-ranking、intent 分類（tech/arch/ops/flow/domain）、知識萃取 | ~200-500ms |

本地 LLM 在 hook 階段（UserPromptSubmit + SessionEnd）自動執行，Claude Code 無感。
Claude Code 負責的是**理解語意後的決策**——決定記什麼、分什麼類、怎麼演進。

### 回應知識捕獲（V2.4）

Claude 的回應也自動萃取為記憶，由本地 LLM（qwen3:1.7b）處理，零雲端 token 開銷：

| 層 | 時機 | 輸入 | 上限 |
|----|------|------|------|
| 逐輪萃取 | UserPromptSubmit（非同步） | 上一輪 assistant 回應 | 3000 chars, 2 items |
| SessionEnd 補漏 | SessionEnd（同步） | 全 transcript | 20000 chars, 5 items |

所有萃取結果一律 `[臨]`，經跨 Session 鞏固後自動晉升。

### 跨 Session 鞏固（V2.4 Phase 3）

SessionEnd 時，對 knowledge_queue 中的每個 item 做向量搜尋（min_score 0.75），統計跨 session 出現次數：

- **2+ sessions 命中** → 自動晉升 `[臨]` → `[觀]`
- **4+ sessions 命中** → 標記建議晉升 `[觀]` → `[固]`（不自動執行，需使用者確認）
- 結果寫入 episodic atom 的「跨 Session 觀察」段落

### 載入順序

1. **全域 atoms** — `Read ~/.claude/memory/MEMORY.md`，比對 Trigger，命中則載入對應 atom 檔
2. **專案 atoms** — `Read` 專案對應的 auto-memory `MEMORY.md`，比對 Trigger，命中則載入

兩層都要做。全域層放跨專案共用知識（使用者偏好、通用決策），專案層放專案綁定知識（架構、坑點）。

### atom 格式

元資料（Scope/Confidence/Trigger/Last-used/Confirmations/Type/Tags/Related/Supersedes）+ 知識段落 + 行動段落 + 演化日誌。
完整規格：`~/.claude/memory/SPEC_Atomic_Memory_System.md`

### 決策記憶三層分類

| 符號 | 說明 | 引用行為 |
|------|------|---------|
| `[固]` | 跨多次對談確認，長期有效 | 直接引用 |
| `[觀]` | 已決策但可能演化 | 觸及時簡短確認 |
| `[臨]` | 單次決策 | 觸及時明確確認 |

### 主動寫入時機

LLM 應在以下情境主動寫入/更新 atom：
1. **使用者明確要求**：「記住」「以後都這樣」→ 直接 [固]，寫入 atom
2. **使用者做了取捨**：選 A 不選 B → [臨]，附推測原因
3. **發現反覆模式**：跨 2+ 次互動的相同偏好 → [觀]
4. **踩到陷阱**：debug 超過 10 分鐘的問題 → 寫入 pitfalls atom
5. **架構決策**：影響多檔案的設計選擇 → 寫入 decisions atom
6. **工具/環境知識**：確認的版本、路徑、設定值 → 寫入對應 atom

不寫入：臨時的嘗試方案、未經確認的猜測、單次 session 不太可能復現的細節。

### 分類演進（LLM 責任）

Claude 應主動追蹤記憶分類的演進：
- **觸及已記錄的 [臨] 決策**：簡短提及 + 確認。確認 → Confirmations +1
- **Confirmations ≥ 2 的 [臨]**：主動建議晉升 → [觀]
- **Confirmations ≥ 4 的 [觀]**：主動建議晉升 → [固]（需使用者確認）
- **使用者明確推翻已記錄決策**：更新 atom，降級或標記 Supersedes
- **矛盾偵測**：新決策與已有 atom 矛盾時，標出衝突，問使用者取捨

### 晉升與淘汰

- 晉升：`[臨]` 2+ sessions → `[觀]`；`[觀]` 4+ sessions → `[固]`
- 淘汰：超期 atom 移入 `_distant/{年}_{月}/`（遙遠記憶），不刪除

### 注入上下文原則

精確度 > token 節省。衝突時，寧可多注入確保正確，不為省 token 而遺漏關鍵資訊。

- **Trigger 命中時**：載入整個 atom（不截斷），確保上下文完整
- **多 atom 命中時**：全部載入，不做 token 預算截斷。若 atom 過大（>200 行），優先載入知識段落 + 行動段落，元資料和演化日誌可省略
- **不確定是否相關時**：寧可載入再判斷，不猜測跳過
- **已載入的 atom 確認不相關時**：靜默忽略，不浪費回應 token 解釋
- **引用已記錄事實時**：直接引用，不重新分析原始碼（已有 _AIDocs 文件的不重新掃描）

### 管理原則

- `MEMORY.md` 只放索引 + 高頻事實（≤30 行），細節放 atom 檔（≤200 行）
- `_CHANGELOG.md` 保留最近 ~8 筆，舊條目移至 `_CHANGELOG_ARCHIVE.md`
- 健檢工具：`python ~/.claude/tools/memory-audit.py`（格式驗證、過期分析、晉升建議、重複偵測）
- 決策記憶也存放在各專案的 `memory/Extra_Efficiently_TokenSafe.md`

---

## 三、工作結束同步

完成有意義的修改後，**根據情境判斷哪些步驟適用**，主動向使用者提出：

> 「這次修改涉及 N 個檔案，要我同步更新 {適用項目} 嗎？」

### 情境判斷（缺少的就跳過，不要提及）

| 條件 | 同步步驟 |
|------|---------|
| 有 `_AIDocs/` | → 追加 `_CHANGELOG.md`（超 8 筆觸發滾動淘汰） |
| 有新知識/決策/坑點 | → 更新 atom 檔（知識段落 + Last-used） |
| 有 `.git/` | → 秘密洩漏檢查 → `git add` → `git commit` → `git push` |
| 有 `.svn/` | → 秘密洩漏檢查 → `svn add`（新檔案）→ `svn commit` |
| 都沒有 | → 僅更新 memory atoms（如有需要） |

適用的步驟都要做完，不要只做一半。

### Workflow Guardian 自動監督

`~/.claude/hooks/workflow-guardian.py` 會在背景追蹤修改：
- **PostToolUse**：自動記錄 Edit/Write 修改的檔案
- **Stop 閘門**：若有未同步的修改，會阻止 Claude 結束並提醒
- **防無限迴圈**：最多阻止 2 次，第 3 次強制放行
- MCP tools（`workflow_signal`）：同步完成後發 `sync_completed` 解除閘門
- Dashboard：`http://127.0.0.1:3848`

---

## 三½、識流工作流（Consciousness Stream）

當使用者說「**透過識流進行…**」或「**用識流處理…**」時，啟用識流處理管線：

1. 執行 `/consciousness-stream` skill（`~/.claude/commands/consciousness-stream.md`）
2. 依九層管線處理：觸→五識→六識→七識→八識→光明心→轉智→執行→薰習
3. 輸出格式化的識流報告
4. 完成後執行薰習迴寫（更新 atoms、pitfalls、decisions、CHANGELOG）

識流也可以在高風險或跨系統的複雜任務中**建議使用**（但不強制）。

> 完整規格: `E:\AI-Develop\consciousness-stream\architecture\consciousness-stream-spec.md`
> 記憶 Atom: `consciousness-stream.md`（Trigger: 識流、意識流、透過識流、八識、轉識成智）

---

## 四、風險分級框架

所有專案通用的分級概念（具體分級項目由各專案 CLAUDE.md 定義）：

| 風險等級 | 通用原則 |
|---------|---------|
| **低** | 讀檔、搜尋、分析、產出報告 → 確認路徑正確即可 |
| **中** | 新增檔案、修改非核心邏輯 → 先讀取相關檔案 |
| **高** | 修改核心業務邏輯 → 必須讀文件 + 原始碼，遵循 SOP |
| **極高** | 修改框架基類、共用定義 → 必須向使用者確認，列出影響範圍 |

---

## 五、對話管理

### 拆分指引

- 獨立子任務可安全新開對話（MEMORY.md 會自動載入）
- 拆分前確保：新發現已寫入 `_AIDocs/`、`_CHANGELOG.md` 已更新、重要事實已存入 MEMORY.md
- 有順序依賴的任務（分析 → 計畫 → 執行）應在同一對話完成

### 主動提醒開新 Session

當以下任一條件成立時，主動提醒使用者考慮開新 session：

- **Context 被系統壓縮過**（收到 compaction 通知或先前訊息摘要）
- **當前任務已告一段落**，且接下來的工作與前面無強順序依賴
- **對話已累積大量工具呼叫**，回應明顯變慢

提醒格式（簡短即可）：
> 「這個 session 已經蠻長了，建議開新 session 繼續。重要資訊已存入 MEMORY.md。」

提醒前確保：當前產出的新知識、決策、變更都已寫入 MEMORY.md / _AIDocs。

### Token 節省原則

- 已決策的事項不重複深入分析，但簡短提及讓使用者知道 AI 有記住
- 已有 `_AIDocs` 分析文件的內容，不重新掃描原始碼，直接引用文件
- 大量重複性修改，先修改 1-2 個確認模式正確，再批量執行

---

## 六、使用者核心偏好

- **輕量極簡**：偏好直接、低抽象的解法，不用不需要的框架
- **高可讀性**：一個檔案看完相關邏輯，不需跳轉多處
- **反對過度綁定**：框架層應薄，開發者要能理解底層
- **不自動產生文件**：不主動建立 README / 文件檔案，除非被要求
- **回應語言**：一律使用繁體中文回應（技術術語可用英文）
