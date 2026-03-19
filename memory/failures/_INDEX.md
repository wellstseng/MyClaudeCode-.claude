# 失敗模式記憶 — 子索引

> 原 `failures.md` 拆分為獨立子 atoms，各自 trigger 精準注入。

| Atom | 檔案 | 說明 |
|------|------|------|
| fail-env | failures/env-traps.md | 環境踩坑（Windows/MSYS2/Node/Ollama） |
| fail-assumptions | failures/wrong-assumptions.md | 假設錯誤（調查時的認知偏差） |
| fail-silent | failures/silent-failures.md | 靜默失敗（看似正常實則壞掉） |
| fail-cognitive | failures/cognitive-patterns.md | 模式誤用 + 品質回饋 |

## 共通行動規則

- debug 超過 5 分鐘時，先檢查是否有已知模式匹配
- 使用者糾正行為時，記錄到對應分類
- 工具呼叫失敗後重試成功時，評估是否值得記錄
- 新增記錄前，先向量搜尋 dedup
- 每條記錄初始為 [臨]，跨 2+ sessions 確認後晉升 [觀]

## 自動萃取（v2.13）

Guardian UserPromptSubmit 偵測使用者失敗回報關鍵字 → 背景 Ollama 萃取 → 自動寫入對應子檔案。
- 觸發：strong keyword ×1 或 weak keyword ×2（config.json `failure_extraction`）
- 新條目標記 [臨]，含 domain tags 和日期
- Dedup: word overlap ≥ 0.65 跳過
- 三維路由：失敗類型(4類) × 專案(cwd→slug) × 領域(domain_tags)
- 專案特定失敗寫入 `projects/{slug}/memory/failures/`，無專案層則寫全域
