# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統
- Last-used: 2026-03-09
- Confirmations: 53
- Type: decision

## 知識

### 核心架構
- [固] 原子記憶 V2.5：Hybrid RECALL + Ranked Search + Keyword Boost + Self-healing Cache + 回應捕獲 + 跨 Session 鞏固 + Workflow Guardian
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

### 自我迭代原則（Self-Iteration）
- [固] **記憶系統自我演進**：原子記憶不只記錄事實，系統本身也隨使用深化。每次 Claude 閱讀、執行、達成目標的過程中，應主動抽取可提升「良善」「協助」「精確」的關鍵邏輯
- [固] **演進維度**：(1) 精確度 — 發現更好的判斷模式時更新行動規則 (2) 協助力 — 識別使用者未明說但反覆需要的支援模式 (3) 良善性 — 降低使用者認知負擔、減少來回確認的摩擦
- [固] **演進觸發**：(1) 同類問題第 2 次出現 → 記錄模式 (2) 使用者糾正 Claude 的判斷 → 更新規則 (3) 某個行動規則連續 3+ 次被跳過 → 檢討是否該淘汰 (4) 新的工具/流程被確認有效 → 納入標準流程
- [固] **演進邊界**：自我迭代只更新「行動」和「知識」段落，不自行修改「元資料」的 Confidence 層級（晉升仍需使用者確認或跨 session 鞏固機制）
- [固] **定期檢閱週期**：每 5±2 個 session（約 3~7 個），Claude 應主動進行一次近期 session 回顧
- [固] **檢閱內容**：(1) 掃描近期 episodic atoms + knowledge_queue (2) 找出重疊性高的使用者要求模式 (3) 將反覆出現的要求收攏為 [觀] 或晉升為 [固] (4) 更新向量資料庫
- [固] **檢閱觸發判斷**：Claude 在 SessionStart 時檢查 episodic 目錄的 atom 數量與最後檢閱時間，超過週期則在適當時機（任務間隙或使用者首發後）主動提出
- [固] **檢閱輸出**：產出簡短報告 — 發現的重複模式、建議的晉升/合併、已執行的更新。報告本身不另存檔，結果直接寫入對應 atom

### 歷史決策
- [固] 記憶檢索統一用 Python，已移除 Node.js memory-v2（2026-03-05 退役）
- [固] Stop hook 只保留 Guardian 閘門，移除 Discord 通知
- [固] OpenClaw workspace atoms 透過 additional_atom_dirs 整合（extra:openclaw 層，5 atoms）

## 行動

- 記憶寫入走 write-gate 品質閘門
- 向量搜尋 fallback 順序：Ollama → sentence-transformers → keyword
- Guardian 閘門最多阻止 2 次，第 3 次強制放行

## 演化日誌

- 2026-03-05: 建立 README.md（哲學/Token比較/流程圖/大型專案使用法）+ Install-forAI.md 安裝指南
- 2026-03-05: V2.3 合併安裝，從公司版遷移核心工具鏈到家用電腦
- 2026-03-05: LanceDB → ChromaDB（i7-3770 不支援 AVX2，LanceDB search crash）
- 2026-03-05: embedding model 指定 qwen3-embedding:0.6b（避免 latest 4.7GB 版 timeout）
- 2026-03-05: search_min_score 從 0.65 降至 0.45（0.6b 小模型 score 普遍較低）
- 2026-03-05: OpenClaw atoms 整合（additional_atom_dirs），Node.js memory-v2 退役
- 2026-03-05: V2.3 全面升級 OpenClaw Phase 1+2 完成 — MEMORY.md 3欄格式修正、root CLAUDE.md、4個大師級 atom
- 2026-03-05: V2.4 Phase 1+2（回應捕獲）+ Phase 3（跨 Session 鞏固）上線
- 2026-03-05: SessionEnd timeout 5→30s，修復 episodic atom 不生成 bug
- 2026-03-05: episodic 移入 memory/episodic/（不進 git），hardware.md 從 git 移除
- 2026-03-05: .gitignore 整理 — 只保留 OpenClaw project memory，排除 session-env/、.claude/
- 2026-03-05: fix: workflow-guardian stdout/stderr 強制 UTF-8（Windows cp950 導致中文亂碼）
- 2026-03-06: V2.5 Hybrid Search Keyword Boost（專有名詞召回率提升）+ Self-healing Collection Cache（ChromaDB 失效自動恢復）
- 2026-03-09: [固] 主動續航（Session Continuity）— 段落完成即存、Token 上限預警存檔、重試追蹤、執行中項目清單、跨 Session 接續
- 2026-03-09: [固] 三級注入策略（Level 0/1/2）+ 人性化 Trigger + 工作單元命名 + 自我迭代原則
- 2026-03-09: [固] 定期檢閱週期（每 5±2 session）— 近期 session 回顧、重複模式收攏晉升、向量庫同步
