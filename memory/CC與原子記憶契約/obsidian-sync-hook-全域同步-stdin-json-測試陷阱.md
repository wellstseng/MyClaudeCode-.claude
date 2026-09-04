# obsidian-sync hook 全域同步 + stdin-JSON 測試陷阱

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: obsidian-sync, obsidian, Obsidian 同步, _global, 全域 memory 同步, PostToolUse hook 測試, stdin JSON, echo 反斜線, MSYS bash, hook 測試陷阱
- Last-used: 2026-05-22
- Confirmations: 0
- Created-at: 2026-05-22
- Related: toolchain, workflow-icld

## 知識

- [臨] obsidian-sync.py (PostToolUse hook) 原本只同步專案 memory (路徑須符合 .claude/projects/{slug}/memory/)；2026-05-22 已擴充：~/.claude/memory/*.md 等全域 memory 會同步到 vault 的 ClaudeCode/_global/ 子資料夾，但 /memory/_staging/ (進行中草稿) 刻意排除。vault 路徑不含 /memory/ 故寫 vault 不會遞迴觸發。
- [臨] win32 MSYS bash 手測「吃 stdin-JSON 的 hook」時，echo / printf 會把單引號內的反斜線吃掉 (\\Users → \Users)，送進去變成非法 JSON，hook 的 except JSONDecodeError: return 會靜默吞掉，看起來像 hook 壞掉但其實沒執行。症狀：runpy 跑完 exit=0 但目標檔沒產生。正解：用 python -c "import json,sys; sys.stdout.write(json.dumps({...}))" 產生合法 payload 再 pipe 給 hook，路徑用 r'...' raw string。

## 行動

- 改/測 PostToolUse 等吃 stdin-JSON 的 hook 時，別用 echo/printf 手刻 JSON，改用 python json.dumps 產生 payload
- 全域 atom 改完會自動進 Obsidian ClaudeCode/_global/，無需手動複製
