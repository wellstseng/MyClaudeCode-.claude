# 工作流程與規則

- Scope: global
- Confidence: [固]
- Trigger: 工作流程, 大型任務, 分階段, SOP, 任務拆分, 上版, GIT, SVN, svn-update, 版本控制, vcs, 功能拆解, 實作拆解, 開發計畫, 新功能, 新系統, 實作計畫, 規格書, ICLD, 閉環, Sprint
- Last-used: 2026-03-25
- Confirmations: 46
- Type: procedural
- Tags: workflow, svn, git, vcs
- Related: decisions, workflow-icld, workflow-svn

## 知識

### 大型計畫執行
- 分階段 session 執行
- 每階段：完成 → 驗證 → 上傳 GIT → 提供下一階段 prompt 給使用者
- **「執驗上P」**：階段收尾口令，等同 執行 → 驗證 → 上 GIT → 產 Prompt（四步都做完）
- 有順序依賴的任務（分析→計畫→執行）應在同一對話完成
- 獨立子任務可安全新開對話（MEMORY.md 會自動載入）

### 製程選擇
- **Phase 模式**（預設）：按技術層切分（定義→邏輯→UI），每 Phase 結束「執驗上P」
- **ICLD 模式**：按功能切片切分，每個 Sprint 是可獨立驗證的閉環。詳見下段

選擇標準：需要中間可驗證的功能節點 → ICLD；按層堆疊即可 → Phase

### 增量式閉環開發（ICLD）
> **ICLD** = Incremental Closed-Loop Development（增量式閉環開發）

**適用條件**（滿足 2 項以上 → AI 主動建議）：
1. 預估工期 ≥ 5 天
2. 跨 Client + Server 雙端
3. 涉及 ≥ 3 個獨立子系統
4. 需要新建 ≥ 3 個檔案

**不適用**：單 session 可完成的修改、探索性原型、純重構

**Sprint 結構要素**：
| 要素 | 說明 |
|------|------|
| 目標 | 一句話：這個 Sprint 完成後能做什麼 |
| 包含 Task | 哪些 Task 組進此 Sprint |
| 步驟 | 具體實作步驟（有順序） |
| 通過條件 | Checklist，全勾才算通過 |
| 依賴 | 必須在哪些 Sprint 之後才能開始 |

**Sprint 內流程**：`[拆解] → [實作] → [驗證] → [修 bug] → [確認通過]`，未通過則回到實作

**Sprint 間依賴圖**：允許平行線（如 Server 線 / Client 線），匯合點明確標注

**AI 主動建議規則**：
- [固] 使用者提出功能需求或請求拆解時，AI 評估上述 4 項指標
- [固] 滿足 2+ 項 → 主動建議：「這個功能規模較大（{理由}），建議用 ICLD 閉環模式拆解。要我按 Sprint 模式拆嗎？」
- [固] 使用者拒絕 → 退回 Phase 模式，本次不再提
- [固] 使用者同意 → 自動進入 Plan Mode 進行 Sprint 拆解 → 產出計畫文件（`_AIDocs/plan/Feature_XXX.md`）→ 使用者確認計畫後退出 Plan Mode → 開始 S1 實作
- [固] 每個 Sprint 結束時產出驗證報告 + 下一 Sprint prompt（與「執驗上P」銜接）

**Sprint prompt / 驗證報告模板**：`~/.claude/memory/templates/icld-sprint-template.md`

### GIT 流程
- 「上 GIT」= git add + commit + push（三步都做完）
- 上版前先做秘密洩漏檢查

### SVN 更新優先規則
- [固] 每個 session 中，AI 首次修改原始碼前，若該 session 尚未執行過 SVN update，必須先詢問使用者
- [固] 適用條件：專案根目錄存在 `.svn/`（SVN 工作副本）
- [固] 非 SVN 專案（如 Git）跳過此規則
- [固] 使用者拒絕後，本 session 不再重複詢問（每 session 最多問一次）
- [固] 使用者同意 → 執行 `/svn-update` skill

### SVN 工具優先順序
- [固] 優先 TortoiseSVN GUI（`TortoiseProc.exe`，非阻塞啟動）
- [固] 降級 svn.exe CLI（加 `--non-interactive` 防掛住）
- [固] 都沒有 → 引導安裝 TortoiseSVN

### SVN 衝突處理策略
- [固] 混合模式：AI 分析衝突內容、提出合併建議，使用者逐一確認才套用
- [固] 生成檔衝突（Proto/Binding/Design）→ 建議接受遠端版本後重新生成
- [固] 二進位檔衝突 → 建議用 TortoiseSVN 或選擇版本
- [固] Pre-update 必做 `svn status` 檢查本地 .cs 修改

### 工作結束同步判斷
1. 有 _AIDocs/ → 追加 _CHANGELOG.md（超 8 筆觸發滾動淘汰）
2. 有新知識/決策 → 更新 atom 檔（知識段落 + Last-used）
3. 有 .git/ → 完整 GIT 流程
4. 有 .svn/ → 完整 SVN 流程

## 行動

- 功能需求 / 拆解請求 → 先評估規模 → 滿足 ICLD 條件則主動建議
- 大型任務主動拆分多個 session 階段，每階段結束提供延續 prompt
- 批量修改先確認 1-2 個模式正確，再批量執行
- Token 節省：有 _AIDocs 文件的不重新掃描原始碼，直接引用文件
- 首次 Edit/Write 原始碼前，檢查 `.svn/` 存在 + session 內未 update → 簡短詢問
- 衝突不自動解決，AI 分析 + 使用者確認

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-12 | 從 work-habits.md 升級為 workflow-rules.md，合併 SVN 更新規則 | V2.5→V2.10 升級 |
| 2026-03-13 | 新增 ICLD 製程（增量式閉環開發）+ 製程選擇段落 + AI 主動建議規則 | 究極武鬥大會實戰經驗 |
