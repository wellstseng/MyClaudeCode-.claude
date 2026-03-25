# 架構技術細節

- Scope: global
- Confidence: [固]
- Trigger: 架構細節, vector service, ollama backend, extraction, ACT-R, episodic tracking, context budget
- Last-used: 2026-03-25
- Confirmations: 89
- Type: decision
- Tags: architecture, infrastructure
- Related: decisions, toolchain, toolchain-ollama, doc-index-system, silent-failures

## 知識

### 回應捕獲
- [固] 逐輪增量（Stop hook）+ SessionEnd 全量，共用 _spawn_extract_worker()
- [固] 情境感知萃取：依 session intent 調整 prompt
- → 詳細參數見 `_reference/SPEC_impl_params.md`

### 基礎設施
- [固] Vector Service @ localhost:3849 | Dashboard @ localhost:3848
- [固] Ollama Dual-Backend: rdchat qwen3.5（主力萃取, pri=1）+ local qwen3:1.7b（fallback, pri=2）+ qwen3-embedding
- [固] LanceDB（AVX2 支援），search_min_score: 0.65
- [固] MCP 傳輸格式：JSONL，protocolVersion 2025-11-25
- [固] _call_ollama_generate: num_predict=2048, timeout=120s（qwen3 thinking ~30s on GTX 1050 Ti）
- [固] extract-worker think=true + num_predict=8192（rdchat），detached subprocess

### 檢索強化
- [固] Project-Aliases：MEMORY.md `> Project-Aliases:` 行，跨專案掃描
- [固] Related-Edge Spreading：BFS depth=1 沿 Related 邊帶出相關 atoms
- [固] ACT-R Activation：`B_i = ln(Σ t_k^{-0.5})`，access.json 最近 50 筆
- [固] Blind-Spot Reporter：matched + injected + alias 全空 → `[Guardian:BlindSpot]`

### Session 軌跡追蹤
- [固] Read Tracking：PostToolUse 攔截 Read，去重記錄（同檔只記首次，最多 30 檔）
- [固] VCS Query Capture：regex 匹配 git/svn log/blame/show/diff（最多 10 筆）
- [固] 純閱讀 Session：accessed_files ≥ 5 且無修改 → 也生成 episodic
- [固] 暫存區：`projects/{slug}/memory/_staging/`，每個專案獨立

### Token Diet
- [固] strip + 壓縮 + lazy search，實測省量：注入側 ~350 tok/session + 萃取側 ~1200 tok/session
- → 詳細參數見 `_reference/SPEC_impl_params.md`

### Wisdom Engine
- [固] 反思指標：over_engineering_rate + silence_accuracy
- [固] Bayesian 校準：architecture 連續 3+ 失敗 → 提升 arch 敏感度

### 自我迭代自動化（V2.16）
- [固] 衰減分數 + 自動晉升（Confirmations ≥ 20）+ 震盪持久化 + archive candidates
- → 詳細公式與參數見 `_reference/SPEC_impl_params.md`

### 覆轍偵測（V2.17）
- [固] 寄生式：附著在 episodic atom，SessionEnd 寫信號 → SessionStart 跨 session 偵測
- [固] 職責切分：session 內重試 → fix-escalation；atom 反覆修改 → 震盪偵測；跨 session 行為模式 → 覆轍偵測

### Section-Level 注入（V2.18）
- [固] `ranked_search_sections()`：groupby atom 保留 top-3 chunks，回傳 `sections: [{section, text, score, line_number}]`
- [固] `_semantic_search()` 4-tuple 回傳：`(name, path, triggers, sections)`，先試 `/search/ranked-sections`，404 fallback `/search/ranked`
- [固] `_extract_sections()`：regex 解析 `##`/`###` section map → 匹配 hints（精確+子字串 fuzzy）→ 保留 atom 標題 + Related 行 + 匹配 sections
- [固] SECTION_INJECT_THRESHOLD = 300 tokens，低於此值全量注入
- [固] 安全閥：匹配 0 section → None → 全量；提取 ≥ 原文 70% → None → 全量
- [固] 實測：decisions-architecture 963→305 tok（省 69%）、decisions 488→67 tok（省 87%）

### 環境維護
- [固] rules/ 模組化：CLAUDE.md ~50 行，4 規則檔自動載入
- [固] Atom 健康度：atom-health-check.py（Related 完整性 + 懸空引用 + 過期掃描）
- [固] 環境清理：cleanup-old-files.py 定期清除 shell-snapshots/debug/workflow

## 行動

- 開發/調修記憶系統時載入此 atom
- 修改 hook/tool 前確認此處記載的參數值
- 新增基礎設施時更新對應段落

## 演化日誌

| 日期 | 變更 | 來源 |
|------|------|------|
| 2026-03-19 | 從 decisions.md 拆出技術細節 | 系統精修 |
| 2026-03-19 | 新增 Token Diet V2.14 段落（7 條 [固]） | V2.14 驗證 |
| 2026-03-22 | 新增自我迭代自動化（V2.16）段落（7 條 [固]） | V2.16 文件同步 |
| 2026-03-22 | 新增覆轍偵測（V2.17）段落（4 條 [觀]） | 覆轍偵測實作 |
| 2026-03-23 | V2.17 合併升級至公司電腦 | 跨機合併 |
| 2026-03-24 | 新增 Section-Level 注入（V2.18）段落（6 條 [固]） | Phase 2 實作 |
