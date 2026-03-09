# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統
- Last-used: 2026-03-10
- Confirmations: 59
- Type: decision

## 知識

### 核心架構
- [固] 原子記憶 V2.7：V2.6 + CLAUDE.md 精簡 50%（289→144 行，移除 hook 實作細節與重複內容）+ failures/toolchain atoms + Output Quality Feedback
- [固] 雙 LLM：Claude Code（雲端決策）+ Ollama qwen3（本地語意處理）
- [固] 7 hook 事件全由 workflow-guardian.py 統一處理（SessionStart/UserPromptSubmit/PostToolUse/PreCompact/Stop/SessionEnd + PreToolUse 由 inbox-check.js）

### 記憶檢索管線（V2.5）
- [固] UserPromptSubmit: Intent 分類（qwen3:1.7b）→ Trigger 匹配 → Vector Search → Keyword Boost → Ranked Merge → additionalContext
- [固] V2.5 Hybrid Search: 向量結果疊加 keyword matching boost（大寫詞、引號短語、中文專有名詞），雙命中 +0.1，keyword 救回 +0.05
- [固] V2.5 Self-healing Cache: ChromaDB collection reference 快取 + 失效自動 invalidate + retry；連續失敗計數器超閾值升級警告
- [固] 降級順序：Ollama 不可用 → 純 keyword | Vector Service 掛 → graceful fallback
- [固] 索引 4 層：global → project → extra:openclaw → episodic（向量發現）

### 回應捕獲（V2.4）
- [固] 逐輪萃取：UserPromptSubmit 非同步讀取上一輪 assistant 回應，qwen3:1.7b 萃取知識（≤3000 chars, 2 items）
- [固] SessionEnd 補漏：同步掃描全 transcript（≤20000 chars, 5 items）
- [固] 萃取結果一律 [臨]，經跨 Session 鞏固後自動晉升

### 跨 Session 鞏固（V2.4 Phase 3）
- [固] SessionEnd 時對 knowledge_queue 做向量搜尋（min_score 0.75）
- [固] 2+ sessions 命中 → 自動晉升 [臨]→[觀]；4+ sessions → 建議晉升 [觀]→[固]
- [固] 結果寫入 episodic atom「跨 Session 觀察」段落

### Episodic atom
- [固] SessionEnd 自動生成，TTL 24d，存放於 memory/episodic/（不進 git）
- [固] 門檻：modified_files ≥ 1 且 session 時長 ≥ 2 分鐘
- [固] 不列入 MEMORY.md index，靠 vector search 發現

### 基礎設施
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] Ollama models: qwen3-embedding:0.6b（embedding）+ qwen3:1.7b（萃取/分類）
- [固] Vector DB: ChromaDB（i7-3770 不支援 AVX2，LanceDB 不適用）
- [固] MCP 傳輸格式：JSONL，protocolVersion 2025-11-25

### 主動續航（Session Continuity）
- [固] **段落完成即存**：完成一個段落的動作（不論驗證是否通過）前，立即將進度寫入原子記憶
- [固] **Token 上限預警存檔**：判斷 session 快碰觸 token 上限時，優先將當前工作狀態寫入 atom（任務名稱、進度、下一步、阻塞點）
- [固] **重試追蹤**：反覆修正/重試的場景，記錄重試次數、每次調整的重點、成功/失敗原因
- [固] **執行中項目清單**：以 atom 記錄「目前執行中的項目」，新 session 首次發話時主動檢查是否有未完成項目
- [固] **跨 Session 接續**：不論跨越多少 session，透過原子記憶確保接續上下文完整。項目完成或確定中斷時，標記為已完成/已中斷
- [固] **向量庫同步**：寫入/更新 atom 時，同步更新向量記憶庫（確保新 session 的語意搜尋能找到）
- [固] **三級注入策略**：Level 0（首發必注，≤500 tokens compact 摘要，無條件）→ Level 1（關聯展開，語意命中時載入完整 atom）→ Level 2（歷史召回，已結案項目的摘要+教訓）
- [固] **人性化 Trigger**：續航相關 trigger 涵蓋自然語言 — 繼續, 接著做, 承接, 我剛剛, 上次, 還沒做完, 做到哪, 之前那個, 回到, resume, continue, 還記得嗎, 進度如何

### 工作單元命名（Work Unit Naming）
- [固] **萬物皆可命名**：不只 plan 有代號，任何 session 中出現的有價值細節、邏輯推導、使用者指示、架構洞察，都應賦予簡短命名（如「WS 重連邏輯」「UTF-8 修正 v3」「使用者指示：不要過度封裝」）
- [固] **命名即追蹤**：被命名的工作單元自動取得狀態（🔄 進行中 / ⏸ 暫停 / ✅ 完成 / ❌ 中斷），可跨 session 引用
- [固] **命名粒度**：一個工作單元 = 一個可獨立描述的成果或決策。太大則拆分，太小則合併
- [固] **命名時機**：(1) 開始執行一個有意義的修改前 (2) 使用者給出明確指示時 (3) 發現重要邏輯洞察時 (4) debug 進入反覆修正時

### 自我迭代引擎（Self-Iteration V2.6）
- [固] **8 條演進原則**（跨學科理論背書，詳見 `memory/openclaw-self-iteration.md`）：
  - (1) 品質函數：確認(+)/糾正(−)/無回饋(0) 三類訊號驅動規則調整
  - (2) 收斂優先：規則總數趨向收斂，新增前先檢查可合併的既有規則
  - (3) 證據門檻：≥2 次獨立 session 觀察才建立正式規則（hook 自動追蹤）
  - (4) 淘汰勇氣：每新增 1 條 → 檢查淘汰 1 條（Via negativa）
  - (5) 震盪偵測：3 session 內同 atom 改 2+ 次 → 暫停（hook 自動偵測）
  - (6) 成熟度模型：學習期(<15)/穩定期(15-50)/成熟期(>50)（hook 自動計算）
  - (7) 三維演進：精確度/協助力/良善性 Pareto 平衡
  - (8) 演進邊界：只改行動/知識，絕對禁止自改 Confidence
- [固] **自動化基礎設施**：
  - SessionEnd: `_collect_iteration_metrics()` 收集 atoms_referenced + atoms_modified
  - SessionEnd: `_detect_oscillation()` 掃描近 3 session episodic 偵測震盪
  - SessionStart: `_check_periodic_review_due()` 檢查定期檢閱是否到期（預設每 6 session）
  - SessionStart: `_calculate_maturity_phase()` 計算系統成熟度階段
  - State schema 1.2: 新增 `iteration_metrics` 欄位
- [固] **定期檢閱流程**：hook 觸發提醒 → Claude 掃描 episodic + knowledge_queue → 收攏/晉升規則 → 寫入 `workflow/last_review_marker.json` 重置計數器

### 記憶強化（V2.7）
- [觀] **failures.md**：失敗模式記憶（環境踩坑/假設錯誤/模式誤用/生成品質回饋），procedural type，45 天淘汰
- [觀] **toolchain.md**：工具鏈實戰記憶（Windows 差異/已驗證指令/路徑版本/特殊配置），procedural type
- [觀] **Output Quality Feedback**：PostToolUse 的 `_check_output_quality()` 偵測跨 session 重寫檔案，結果寫入 `state["quality_feedback"]`，SessionEnd 自動記入 episodic 知識段落
- [觀] **跨專案模式掃描**：定期檢閱時比較不同專案 episodic atoms，跨 2+ 專案共通模式收攏為全域知識
- [固] **CLAUDE.md 精簡（V2.7）**：289→144 行（-50%），移除 hook 實作細節（雙 LLM 表格、Hybrid Search、回應捕獲、跨 Session 鞏固、三級注入策略）、移除與 preferences.md 重複的偏好段落、風險分級框架；保留 Claude 決策指令（三層分類、寫入時機、分類演進、同步流程、自我迭代 8 條）

### 歷史決策
- [固] 記憶檢索統一用 Python，已移除 Node.js memory-v2（2026-03-05 退役）
- [固] Stop hook 只保留 Guardian 閘門，移除 Discord 通知
- [固] OpenClaw workspace atoms 透過 additional_atom_dirs 整合（extra:openclaw 層，5 atoms）

## 行動

- 記憶寫入走 write-gate 品質閘門
- 向量搜尋 fallback 順序：Ollama → sentence-transformers → keyword
- Guardian 閘門最多阻止 2 次，第 3 次強制放行
- 大幅修改前 session 生成的程式碼（>30% 變動）時，記錄品質回饋到 failures.md「生成品質回饋」分類
- debug 超過 5 分鐘時，先查 failures.md 已知模式再嘗試新方案
- 定期檢閱時，比較不同專案的 episodic atoms，找出跨 2+ 專案的共通模式（程式風格、錯誤處理、架構偏好），收攏為全域 atom 知識

## 演化日誌

- 2026-03-05: V2.3 合併安裝 + V2.4 回應捕獲/跨 Session 鞏固 + ChromaDB 遷移 + OpenClaw 整合（12 項變更壓縮）
- 2026-03-06: V2.5 Hybrid Search Keyword Boost + Self-healing Collection Cache
- 2026-03-09: [固] 主動續航 + 三級注入 + 工作單元命名 + 定期檢閱
- 2026-03-10: [固] V2.6 Self-Iteration Engine（8 條演進原則 + 跨學科理論背書 + metrics/震盪/成熟度/檢閱自動化）
- 2026-03-10: [觀] V2.7 記憶強化 — failures.md + toolchain.md + Output Quality Feedback（PostToolUse 跨 session 偵測）+ 跨專案模式掃描
- 2026-03-10: [固] V2.7 CLAUDE.md 精簡 — 289→144 行（-50%），移除 hook 實作細節與重複偏好，保留 Claude 決策指令
