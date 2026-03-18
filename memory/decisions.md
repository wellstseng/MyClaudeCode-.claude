# 全域決策

- Scope: global
- Confidence: [固]
- Trigger: 全域決策, 工具, 工作流, workflow, guardian, hooks, MCP, 記憶系統
- Last-used: 2026-03-18
- Confirmations: 55
- Type: decision

## 知識

### 核心架構
- [固] 原子記憶 V2.12：Hybrid RECALL + Ranked Search + 回應捕獲（僅 SessionEnd）+ 跨 Session 鞏固（簡化計數）+ Write Gate + 自我迭代（3 條精簡）+ Wisdom Engine（硬規則+反思校準）+ 檢索強化 + Context Budget + 衝突偵測 + Atom 健康度 + Fix Escalation Protocol（6 Agent 精確修正會議）
- [固] 雙 LLM：Claude Code（雲端決策）+ Ollama qwen3（本地語意處理）
- [固] 6 hook 事件全由 workflow-guardian.py 統一處理（SessionStart/UserPromptSubmit/PostToolUse/PreCompact/Stop/SessionEnd）

### 記憶檢索管線（V2.3 起）
- [固] UserPromptSubmit: Intent 分類（qwen3:1.7b）→ Trigger 匹配 → Vector Search → Ranked Merge → additionalContext
- [固] 降級順序：Ollama 不可用 → 純 keyword | Vector Service 掛 → graceful fallback
- [固] 索引 2 層：global → project（向量發現），所有層統一 `**/*.md` 遞迴掃描 + `_` 前綴目錄跳過

### 回應捕獲（V2.4→V2.11）
- [固] V2.11: 廢除逐輪萃取（per_turn_enabled: false），僅保留 SessionEnd 全 transcript 萃取
- [固] V2.11: 情境感知萃取（依 session intent 調整 prompt：build/debug/design/recall）
- [固] V2.11: 跨 Session 觀察（vector search top_k=5, min_score=0.75 → 2+ sessions 命中生成觀察段落）
- [固] SessionEnd 萃取：同步掃描全 transcript（≤20000 chars, 5 items）
- [固] 萃取結果一律 [臨]，由 Confirmations 計數驅動後續晉升
- [固] V2.5: 萃取 prompt 可操作性標準、知識類型 6 種、format:json、Write Gate CJK-aware

### 跨 Session 鞏固（V2.4→V2.11 簡化）
- [固] V2.11: 廢除自動晉升 [臨]→[觀]，改為 Confirmations +1 簡單計數
- [固] 4+ sessions 命中 → 建議晉升（不自動執行），統一 dedup 閾值 0.80
- [固] 結果寫入 episodic atom「跨 Session 觀察」段落

### Episodic atom
- [固] SessionEnd 自動生成，TTL 24d，存放於 memory/episodic/（不進 git）
- [固] 門檻：modified_files ≥ 1 且 session 時長 ≥ 2 分鐘
- [固] 不列入 MEMORY.md index，靠 vector search 發現

### 基礎設施
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] Ollama Dual-Backend: rdchat qwen3.5（主力萃取, pri=1）+ local qwen3:1.7b（fallback, pri=2）+ qwen3-embedding（embedding）
- [固] Vector DB: LanceDB（此電腦支援 AVX2，LanceDB 效能穩定）
- [固] search_min_score: 0.65（完整版 embedding 精確度足夠）
- [固] MCP 傳輸格式：JSONL，protocolVersion 2025-11-25
- [固] _call_ollama_generate: num_predict=2048, timeout=120s（qwen3 thinking mode 需 ~30s on GTX 1050 Ti）
- [固] SessionEnd 萃取由 extract-worker.py detached subprocess 執行（hook timeout=30s，萃取需 ~60s）

### 自我迭代（V2.6→V2.11）
- [固] V2.11: 精簡為 3 條核心原則：品質函數（Hook）、證據門檻（Claude）、震盪偵測（Hook）
- [固] 定期檢閱：SessionStart 檢查 episodic 計數 → 提醒掃描近期 patterns

### Wisdom Engine（V2.8→V2.11）
- [固] V2.11: 移除因果圖（CausalGraph class + causal_graph.json），冷啟動零邊，維護成本>收益
- [固] V2.11: 情境分類器改為 2 條硬規則（file_count+is_feature → confirm; touches_arch+file_count → plan）
- [固] V2.11: 反思引擎新增 over_engineering_rate（同檔 Edit 2+ 次）+ silence_accuracy（held_back 追蹤）
- [固] V2.11: Bayesian 權重校準（architecture 連續 3+ 失敗 → 提升 arch 敏感度）
- [固] guardian lazy import + graceful fallback，冷啟動零 token，注入上限 ≤90 tokens

### V2.11 新增機制
- [固] Context Budget：additionalContext 硬上限 3000 tokens，超額按 ACT-R activation 由低到高 truncate
- [固] 衝突偵測自動化：SessionEnd 對修改 atoms 做向量搜尋（score 0.60-0.95），寫入 episodic 衝突警告
- [固] PostToolUse 品質追蹤：同檔 Edit 2+ 次 → reverted_count，SessionEnd 寫入 reflection_metrics
- [固] Atom 健康度工具：atom-health-check.py（Related 完整性 + 懸空引用清除 + 過期掃描）
- [固] .claude/rules/ 模組化：CLAUDE.md 瘦身至 ~50 行，4 個規則檔自動載入
- [固] 環境清理：shell-snapshots/debug/workflow 300+ 垃圾檔案清除 + cleanup-old-files.py 定期工具

### 記憶檢索強化（V2.9）
- [固] Project-Aliases：MEMORY.md 加 `> Project-Aliases:` 行，跨專案掃描先比對 aliases → 注入全文
- [固] Related-Edge Spreading：`spread_related()` BFS depth=1，沿 Related 邊帶出相關 atoms
- [固] ACT-R Activation Scoring：`B_i = ln(Σ t_k^{-0.5})`，access.json 保留最近 50 筆，高分優先注入
- [固] Blind-Spot Reporter：三重空判斷（matched + injected + alias 全空）→ 注入 `[Guardian:BlindSpot]`

### Session 全軌跡追蹤（V2.10）
- [固] Read Tracking：PostToolUse 攔截 Read tool，去重記錄 accessed_files（同檔只記首次）
- [固] VCS Query Capture：PostToolUse 攔截 Bash tool，regex 匹配 git/svn log/blame/show/diff
- [固] Episodic 閱讀軌跡：`_build_read_tracking_section()` 生成 `## 閱讀軌跡` section（最多 30 檔 + 10 筆版控查詢）
- [固] 純閱讀 Session：accessed_files ≥ 5 且無修改時也生成 episodic atom
- [固] 暫存區管理：`projects/{slug}/memory/_staging/` 專案層暫存區，每個專案獨立續接。.gitignore 排除，SessionEnd 提醒清理

### V2.12 精確修正計畫
- [固] Fix Escalation Protocol：同一問題修正第 2 次起，強制啟動 6 Agent 精確修正會議（外部搜索+專案調查+正反辯論 2 輪+落地分析+垃圾回收）
- [固] Guardian hook 自動偵測：UserPromptSubmit 檢查 wisdom_retry_count ≥ 2 → 注入 `[Guardian:FixEscalation]` 信號
- [固] `/fix-escalation` skill：固定化 agent prompt 模板，5 Phase 流程（暫停→蒐集→辯論→深度挑戰→決策執行→驗證）
- [固] 自我驗證+成效追蹤：連續 3 次未解決強制暫停與使用者對齊

### 歷史決策
- [固] 記憶檢索統一用 Python，已移除 Node.js memory-v2（2026-03-05 退役）
- [固] Stop hook 只保留 Guardian 閘門，移除 Discord 通知

## 行動

- 記憶寫入走 write-gate 品質閘門
- 向量搜尋 fallback 順序：Ollama → sentence-transformers → keyword
- Guardian 閘門最多阻止 2 次，第 3 次強制放行

## 演化日誌

- 2026-03-05: 初始建立 — V2.4 合併（回應捕獲/鞏固/episodic）+ LanceDB + Dual-Backend
- 2026-03-11: V2.8→V2.10 — Wisdom Engine + 檢索強化(ACT-R/Spreading) + Session 全軌跡追蹤
- 2026-03-13: V2.11 全面升級 — 精簡（砍逐輪萃取/因果圖/自動晉升/迭代8→3）+ 品質（衝突偵測/反思校準）+ 模組化（rules/+Context Budget）
- 2026-03-13: 自檢修復 — 清除因果圖殘留 + Context Budget 動態化 + 索引同步 + atom 去重 + extract-worker 啟用
- 2026-03-17: V2.12 精確修正計畫 — Fix Escalation Protocol（6 Agent 會議制）+ Guardian 自動偵測 + /fix-escalation skill
