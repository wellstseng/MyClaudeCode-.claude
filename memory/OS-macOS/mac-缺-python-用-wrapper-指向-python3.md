# Mac 缺 python 用 wrapper 指向 python3

- Scope: global
- Author: wellstseng
- Confidence: [臨]
- Trigger: python, python3, spawn python ENOENT, atom_write, funnel, vector service, xcode-select, AtomFunnelBlock, command not found python
- Created-at: 2026-06-22
- Related: toolchain, upstream-merge-mac-適配工作流

## 知識

- [臨] 本機 mac（holylight）無 `python`，只有 `/usr/bin/python3`（Apple CLT shim，Python 3.9.6）。該 shim 依「被呼叫名」解析：`ln -s python3 python` 會讓它找不到名為 python 的工具 → 跳 `xcode-select` 安裝提示而失敗。
- [臨] 正解：用 wrapper 而非 symlink。`~/.local/bin/python` 內容：`#!/bin/sh` + `exec /usr/bin/python3 "$@"`（以真名 python3 呼叫繞過 shim 檢查）。`~/.local/bin` 在 PATH 最前且免 sudo。
- [臨] 此 wrapper 是 workflow-guardian funnel（atom_write/atom_promote 內部 `spawn('python')`）、vector service、及任何呼叫 `python` 的 hook 能運作的前提。誤刪會讓 atom 寫入報 `spawn python ENOENT` 並被 AtomFunnelBlock 卡死。建立後 MCP server 不需重啟即生效（spawn 每次重查 PATH）。

## 行動

- 遇到 spawn python ENOENT / atom 寫入失敗 / vector 不索引 → 先確認 `~/.local/bin/python` wrapper 還在且 `python --version` 正常
- 不要用 `ln -s` 建 python（Apple shim 會擋）；要用 exec wrapper
