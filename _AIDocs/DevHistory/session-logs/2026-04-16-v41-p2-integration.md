# 2026-04-16 V4.1 P2 整合 — user-extract-worker.py + 整合測試 (v4.1.0-beta1)

> keywords: V4.1, P2, user-extract-worker, integration-test, v4.1.0-beta1

## 摘要

P2 主管線整合：Stop hook detached worker + L0→L1→L2 管線 + 50 條整合測。

## user-extract-worker.py（新）

Stop hook detached worker，L0→L1→L2 完整管線：
- 混合句偵測 [F10]：情緒+決策 → systemMessage skip
- 情緒承諾 24h 冷卻 [F24]
- SessionBudgetTracker ≤240 tok [F22]
- L1 robust parser 支援 variant keys
- L2 gemma4:e4b fallback 至 default model
- conf-based routing：≥0.92 confirm / 0.70-0.92 pending / <0.70 skip
- ack-then-clear [F12]

## workflow-guardian.py 整合

- Stop/SessionEnd 加 `_maybe_spawn_user_extract_worker`
- UPS confirmed_extractions 顯式提示預設同意 [F5]（使用者回「否」可攔截）

## 回歸測試

- `test_v4_atoms_unchanged.py`（新）：SHA256 全量比對，63 atoms

## 整合測試

- `test_e2e_user_extract.py`（新）：50 條（25 正 + 15 負 + 10 邊緣），需 `--ollama-live`
- P/R gate 待 rdchat 恢復後驗收（此時 rc2 → GA blocker）

## 涉及檔案

- `hooks/user-extract-worker.py`(新)
- `hooks/workflow-guardian.py`
- `tests/integration/test_e2e_user_extract.py`(新)
- `tests/integration/conftest.py`(新)
- `tests/regression/test_v4_atoms_unchanged.py`(新)
- `tests/fixtures/v4_atoms_baseline.jsonl`
- `_AIDocs/Architecture.md`
