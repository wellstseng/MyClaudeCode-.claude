# Session H — README/TECH 拆檔 + 版本號清理

> **模式**：不用 Plan Mode。Permission 建議 yolo 或 auto-accept。
> **CWD**：`~/.claude`
> **GIT**：完成即 commit + push（中文 log per memory/feedback-git-log-chinese.md）。
> **前置條件**：V4.1 GA 已完工（含 `dd466c2` / `8625b45` / `c65b99b` 三個補漏 commit），最新 main 含 V4.1 真實運作驗收紀錄。

---

## ⚠️ 首要規則：**等使用者補概略內容才動手**

開工第一步**不要直接改檔**。必須：

1. 讀完本 handoff 全文 + 先 glob 掃目前要改的檔案清單（只 glob / grep，不 edit）
2. 對使用者說：「**請補 README / TECH 的概略內容方向**（保留哪些段、砍哪些段、新增哪些段、語氣要多白話）」
3. **等使用者明確回覆概略內容** → 再動手
4. 若使用者回覆模糊，給具體選項題（符合 `memory/feedback-no-outsource-rigor.md` 規則：不問開放式「還有什麼」）

未等使用者概略內容就自行拆檔 → **一律視為超出授權**。

---

## 任務範圍

### 1. 版本號現況盤點（先讀，再等概略）

V4 → V4.1 演進已完成。目前標題 / metadata / 文件裡可能還有殘留的舊版本號痕跡。盤點對象：

- `README.md`（根目錄）
- `Install-forAI.md`
- 任何含 `V4.0` / `V4.1` / `v4.1.0` / `atom-v4` tag 的 Markdown 文件
- `_AIDocs/*.md`（尤其 Architecture.md / SPEC_ATOM_V4.md）
- `CLAUDE.md` / `IDENTITY.md` / `USER.md`

### 2. 版本號清理原則

- **保留**：SPEC 定稿版本號（SPEC_ATOM_V4.md 頂部、Architecture.md 架構演進段、_CHANGELOG.md 日期條目）、git tag（如 `v4.1.0-rc1`）
- **拔除**：散落在各 doc 中「本章節是 V4.1 新增」「V4.0 → V4.1 變更：XXX」這類**只給過渡期讀者、長期無用的 note**（純消耗 token 的存在）
- **更新**：所有「當前版本」/「latest」/「current」這類指涉，一律對齊 **V4.1 GA (v4.1.0)**

### 3. README.md 拆檔

**新架構**：

```
README.md       ← 人類使用者一讀就能上手（安裝 + 使用）
TECH.md         ← 技術內容（架構 / 機制 / 內部 pipeline / Hook 詳情）
```

兩檔同層（`~/.claude/` 根目錄）。

**README.md 留下什麼**（白話、簡潔）：
- 這是什麼、能幫使用者什麼（1-2 段）
- 安裝步驟（clone / 依賴 / 初次啟動）
- 首次使用的 5-10 分鐘上手流程
- 常用 skill 清單（`/init-roles`、`/memory-peek`、`/conflict-review` 等）
- 進階技術內容 → 鏈到 TECH.md

**TECH.md 接收什麼**（原 README 技術段落搬過去）：
- 架構圖 / 流程圖
- V4 三層 scope 機制說明
- V4.1 使用者決策萃取 pipeline
- Hook 系統細節
- Workflow Guardian 運作原理
- 各模組 API / 內部狀態 schema
- 任何讓新使用者卡關的技術細節

**判斷原則**：讀者如果是「想立刻用」→ 留 README；讀者是「想理解怎麼運作」→ 搬 TECH。

### 4. 調整鏈結

拆檔後：
- `_AIDocs/_INDEX.md`：把 TECH.md 加進索引表
- `README.md` 底部：加一行「技術細節見 `TECH.md`」
- `CLAUDE.md` / `@import` 關聯（如有）：檢查是否需要指向 TECH.md

---

## 工作流程

**Phase 1（零改動）**：盤點 + 問使用者概略
1. `git pull` 確保最新
2. `glob`/`grep` 掃所有含版本號的 Markdown
3. 讀 `README.md` / `Install-forAI.md` 目前完整內容
4. **對使用者提問「概略內容」**（必須具體選項題，不可開放式）

**Phase 2（等概略後動手）**：
1. 根據使用者概略拆檔（README → TECH）
2. 清版本號殘留
3. 更新 _AIDocs/_INDEX.md + CLAUDE.md 關聯
4. 若新 `TECH.md` 要進 `_AIDocs/_INDEX.md`，一併加入

**Phase 3（驗收）**：
1. `git diff --stat` 看變動量合理（README 應顯著縮短）
2. 通讀 README.md 模擬首次使用者視角，確認「一讀能馬上用」
3. 通讀 TECH.md 確認技術完整性

**Phase 4（commit + push）**：
1. 中文 log（per `memory/feedback-git-log-chinese.md`）
2. Prefix 用 `docs(refactor):` 或類似
3. Push 雙 remote（gitlab + github）

---

## 絕不碰

- `hooks/` 任何 .py
- `tools/` 任何 .py
- `workflow/config.json` / `settings.json`
- V4 atoms（memory/*.md）
- `memory/_staging/v42-candidates.md`（V4.2 queue 不動）
- `_AIDocs/DevHistory/`（歷史紀錄不改，只 append 新版本資訊）
- `tests/`

如果拆檔過程發現內容重複、不一致、有錯誤 — **不要自作主張修**，記進新 `_staging/` 檔讓使用者決定。

---

## 結束標準

- README.md 人類可讀、< 200 行（目標）
- TECH.md 技術完整、保留所有原 README 技術內容
- 版本號一致指向 v4.1.0 / V4.1
- 散落的版本標記（過渡期 note）已清
- _INDEX.md 含 TECH.md
- commit + push 完成
- 回報使用者變更摘要（`git diff --stat`）

---

## Context 連結

- 前 7 個 session handoff 已封存：`_AIDocs/DevHistory/v41-handoffs/`
- V4.1 完整開發歷程：`_AIDocs/DevHistory/v41-journey.md`
- V4.1 設計圓桌紀錄：`_AIDocs/V4.1-design-roundtable.md`
- V4 SPEC：`_AIDocs/SPEC_ATOM_V4.md`
- 架構總覽：`_AIDocs/Architecture.md`

讀這些檔可以快速進入 V4.1 脈絡，但**還是要等使用者的概略內容**才動手。
