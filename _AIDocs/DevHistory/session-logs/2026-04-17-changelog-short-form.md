# 2026-04-17 _CHANGELOG 短格式化 + session-logs 子目錄

> keywords: changelog, short-form, session-logs, token-diet

## 摘要

上一輪滾動後使用者發現 `_CHANGELOG.md` 還是 16KB — 8 條 rows 每條都是 2KB 超長單行中文敘事。根因：row 數對了但單條肉塊還是肥。

## 動作

- 建 `_AIDocs/DevHistory/session-logs/` 子目錄
- 8 條既有 entry 拆：詳細敘述全部搬 `session-logs/{date}-{slug}.md`，主檔每條只留「標題 + 一句 summary + log 連結 + 主要檔案」
- `tools/changelog-roll.py::TABLE_HEADER_RE` 擴容忍：接受「涉及檔案 / 主要檔案 / 檔案」三種 header variant

## 結果

- `_CHANGELOG.md`：16KB → 4KB（-75%），每條 row ~200-400 字（原本 ~2KB）
- 每條 row 仍保留「標題 + 一句 what + 主要檔案清單」— AI 一眼可判斷是否要進 log 詳讀

## 往後約定

新 entry 格式：

```
| date | **標題** — 一句 what summary。[log](DevHistory/session-logs/{date}-{slug}.md) | 主要檔案 |
```

詳細實作記錄進 `session-logs/{date}-{slug}.md`（完整技術描述、檔案清單、驗證數字、教訓）。

## 涉及檔案

- `_AIDocs/_CHANGELOG.md`（短格式化）
- `_AIDocs/DevHistory/session-logs/`（新目錄）
- `_AIDocs/DevHistory/session-logs/2026-04-17-*.md`(3 新)
- `_AIDocs/DevHistory/session-logs/2026-04-16-v41-*.md`(5 新)
- `tools/changelog-roll.py`（header regex 寬鬆化）
