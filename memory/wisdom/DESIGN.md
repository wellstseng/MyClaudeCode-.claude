# Wisdom Engine 設計文件（V2.8）

- Status: 🔄 規劃完成，待實作
- Created: 2026-03-10
- Work-Unit: 智慧引擎 Wisdom Engine

## 核心原則

code 預運算判斷 → 只注入結論（≤90 tokens）
vs 現行：注入 markdown 規則（~500 tokens），Claude 每次重讀重理解

小任務零注入。只在需要時才出聲 = 沉默的智慧。

## 架構總覽

```
wisdom_engine.py (~200行, ~/.claude/hooks/)
        │
  ┌─────┼─────────┐
  ▼     ▼         ▼
因果圖  情境分類  反思引擎
  │     │         │
  ▼     ▼         ▼
≤30t   0~20t    0~40t    → additionalContext ≤90 tokens
```

被 workflow-guardian.py 在 3 個 hook 點呼叫。

## 力一：因果圖（Causal Graph）

### 數學：有向加權圖 + BFS depth=2

資料檔：`memory/wisdom/causal_graph.json`

```json
{
  "nodes": {
    "auth/middleware.py": {"type": "file", "domain": "auth"},
    "ws/handler.py": {"type": "file", "domain": "realtime"},
    "session_state": {"type": "concept", "domain": "shared"}
  },
  "edges": [
    {
      "from": "auth/middleware.py",
      "to": "ws/handler.py",
      "relation": "coupled_via",
      "through": "session_state",
      "confidence": 0.85,
      "evidence": "2026-03-08 debug: 改 session 結構壞 WS"
    }
  ]
}
```

relation 類型：`coupled_via` | `depends_on` | `breaks_when`

### 查詢演算法

```python
def get_causal_warnings(graph, touched_files, max_depth=2):
    warnings, visited = [], set()
    queue = [(f, 0) for f in touched_files]
    while queue:
        node, depth = queue.pop(0)
        if node in visited or depth > max_depth:
            continue
        visited.add(node)
        for edge in graph.get_edges_from(node):
            if edge["confidence"] >= 0.6:
                warnings.append(edge)
                queue.append((edge["to"], depth + 1))
    return warnings[:3]  # ≤3 條, ~100 tokens
```

### Bayesian confidence 更新

```python
# 命中（因果預測正確）
edge.confidence = edge.confidence * 0.9 + 0.1   # 趨向 1.0
# 落空（改 A 但 B 沒壞）
edge.confidence = edge.confidence * 0.95          # 緩慢衰減
# < 0.3 → 自動移除 edge
```

### 注入格式

```
[因果] auth/middleware ←session_state→ ws/handler (0.85) | 改 session 結構須檢查 WS
```

### 寫入時機

Claude debug 時發現因果關係 → 呼叫 helper 寫入 graph。
冷啟動：無 edge 時靜默。

---

## 力二：情境分類器（Situation Classifier）

### 數學：加權評分函數 + 閾值決策

輸入：qwen3:1.7b intent 分類結果（已有）+ keyword signals

```python
def classify_situation(prompt_analysis, history):
    signals = {
        'file_count': prompt_analysis.get('estimated_files', 1),
        'is_new_feature': prompt_analysis.get('intent') == 'feature',
        'touches_arch': any(k in prompt_analysis.get('keywords', [])
                          for k in ['架構', 'refactor', '重構', 'migrate']),
        'user_quick': any(k in prompt_analysis.get('keywords', [])
                         for k in ['快速', '簡單', 'quick', 'simple']),
        'user_thorough': any(k in prompt_analysis.get('keywords', [])
                            for k in ['好好', '徹底', 'thorough', '完整']),
    }
    w = history.get('weights', DEFAULT_WEIGHTS)
    score = (
        signals['file_count'] * w['file'] +       # 預設 2.0
        signals['is_new_feature'] * w['feature'] + # 預設 4.0
        signals['touches_arch'] * w['arch'] +      # 預設 5.0
        signals['user_quick'] * w['quick'] +       # 預設 -4.0
        signals['user_thorough'] * w['thorough']   # 預設 3.0
    )
    if score <= 2:  return {'approach': 'direct', 'inject': ''}
    elif score <= 6: return {'approach': 'confirm', 'inject': '[情境:確認] 跨檔修改，建議先列範圍'}
    else:           return {'approach': 'plan', 'inject': '[情境:規劃] 架構級變更，建議 Plan Mode'}
```

### 預設權重

```json
{"file": 2.0, "feature": 4.0, "arch": 5.0, "quick": -4.0, "thorough": 3.0}
```

權重由反思引擎在定期檢閱時校準。

### 關鍵：score ≤ 2 → 零注入，不打擾

---

## 力三：反思引擎（Reflection Engine）

### 數學：滑動窗口統計 + 異常偵測（<70% = 盲點）

資料檔：`memory/wisdom/reflection_metrics.json`

```json
{
  "window_size": 10,
  "metrics": {
    "first_approach_accuracy": {
      "single_file": {"correct": 0, "total": 0},
      "multi_file": {"correct": 0, "total": 0},
      "architecture": {"correct": 0, "total": 0}
    },
    "over_engineering_rate": {
      "user_reverted_or_simplified": 0,
      "total_suggestions": 0
    },
    "silence_accuracy": {
      "held_back_and_user_didnt_ask": 0,
      "held_back_but_user_needed": 0,
      "spoke_but_user_ignored": 0
    }
  },
  "calibrated_weights": {
    "file": 2.0, "feature": 4.0, "arch": 5.0, "quick": -4.0, "thorough": 3.0
  },
  "blind_spots": [],
  "last_reflection": null
}
```

### SessionEnd 更新

```python
def reflect(episodic_atoms, current_metrics):
    for ep in episodic_atoms:
        task_type = ep.get('task_type', 'single_file')
        had_retry = ep.get('retry_count', 0) > 0
        bucket = current_metrics['first_approach_accuracy'][task_type]
        bucket['total'] += 1
        if not had_retry:
            bucket['correct'] += 1
    # 盲點偵測
    blind_spots = []
    for task_type, bucket in current_metrics['first_approach_accuracy'].items():
        rate = bucket['correct'] / max(bucket['total'], 1)
        if rate < 0.7 and bucket['total'] >= 3:
            blind_spots.append(f"{task_type} 首次正確率 {rate:.0%}")
    current_metrics['blind_spots'] = blind_spots
    return current_metrics
```

### SessionStart 注入（僅有盲點時）

```
[自知] multi_file 首次正確率 64% — 跨檔修改建議先確認影響範圍
```

### 需要新增：PostToolUse 追蹤 retry_count

在 state 中追蹤同一檔案被重複 Edit 的次數，作為 retry 信號。

---

## 整合點（workflow-guardian.py）

| Hook | 呼叫 | 作用 |
|------|------|------|
| UserPromptSubmit | `wisdom.get_causal_warnings(modified_files)` | 因果警告注入 |
| UserPromptSubmit | `wisdom.classify_situation(prompt_analysis)` | 情境建議注入 |
| SessionStart | `wisdom.get_reflection_summary()` | 盲點提醒注入 |
| SessionEnd | `wisdom.reflect(episodics)` | 更新統計 |
| PostToolUse | state retry_count tracking | 追蹤重試次數 |

## 不改的東西

- CLAUDE.md
- atom schema（[固]/[觀]/[臨] 離散標籤保留給 Claude 看，連續分數在 code 裡）
- hook 事件種類
- MCP server

## 哲學基礎

- 亞里斯多德四因說：因果圖的 edge 編碼動力因(relation)+質料因(through)
- Phronesis（實踐智慧）：情境分類器 = 正確感知特殊情境的能力
- 蘇格拉底 γνῶθι σεαυτόν：反思引擎 = 可行動的精確自我校準
- 核心：Wisdom ≠ 知道更多（WHAT），= 理解因果（WHY）+ 判斷時機（WHEN）+ 認識自己（SELF）

## 批判與風險

- 因果圖冷啟動：新專案無 edge，前幾 session 無效果 → 靜默即可
- 情境權重初始值靠經驗猜，需 10+ session 校準
- 反思引擎需 retry_count（目前無）→ 第一階段需新增
- 三者皆漸進增強，無資料時零 token，不會比現在差
