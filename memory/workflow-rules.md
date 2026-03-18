# 工作流規則（全域）

- Scope: global
- Confidence: [固]
- Type: procedural
- Trigger: 工作流程, 大型任務, 分階段, SOP, 任務拆分, 上版, GIT, 版本控制, 同步, vcs, 功能拆解, 實作拆解, 開發計畫, 新功能, 新系統, 實作計畫, 規格書, ICLD, 閉環, Sprint
- Last-used: 2026-03-18
- Created: 2026-03-06
- Confirmations: 47
- Tags: workflow, vcs
- Related: decisions, workflow-svn

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

### 工作結束同步判斷
→ 詳見 `rules/sync-workflow.md`（同步條件表 + Guardian 閘門）

## 行動

- 功能需求 / 拆解請求 → 先評估規模 → 滿足 ICLD 條件則主動建議
- 大型任務主動拆分多個 session 階段，每階段結束提供延續 prompt
- 批量修改先確認 1-2 個模式正確，再批量執行
- Token 節省：有 _AIDocs 文件的不重新掃描原始碼，直接引用文件

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-06 | 建立為 [固]（使用者明確要求） | session:SVN 工作流規則建立 |
| 2026-03-13 | 合併來源 V2.10 的大型計畫/GIT/同步判斷段落 + 擴展 Trigger | session:選擇性 cherry-pick |
| 2026-03-17 | 合併 wellstseng V2.11：新增 ICLD 製程（增量式閉環開發）+ 製程選擇 + AI 主動建議規則 | session:wellstseng merge |
| 2026-03-18 | 拆分 SVN 規則至 workflow-svn.md，移除 SVN triggers | atom-debug 精準化 |
