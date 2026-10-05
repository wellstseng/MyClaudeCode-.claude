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
- [臨] 2026-10-06 起本機 wrapper 改指 3.12：`~/.local/bin/python` → `exec "$HOME/.local/venvs/py312/bin/python"`（uv 管理的獨立版 Python 3.12 建的 venv，套件用 `uv pip install --python ~/.local/venvs/py312/bin/python <pkg>` 裝）。`python3` 仍是系統 3.9；記憶系統的工具與驗證一律用 `python` 跑。退回只要把 wrapper 那行換回 `exec /usr/bin/python3 "$@"`
- [臨] `python` 是全機共用：換直譯器前要把其他專案腳本用到的第三方套件一併裝進新環境（先 AST 掃 import、兩邊各測 find_spec）
- [臨] macOS 26.2 上 Homebrew 的 python@3.12 bottle 不能用：pyexpat 連到系統 libexpat 缺符號 `_XML_SetAllocTrackerActivationThreshold`，plistlib／pip 全掛（platform.mac_ver() 回空字串是症狀）。改用 uv 的獨立版 Python
- [臨] `brew uninstall <formula>` 會順手 autoremove 其他孤兒相依（實踩：ripgrep 被一起移除）；卸載後比對 `brew --cache` 的 bottle 名與 `brew list` 找出被帶走的再裝回。brew 在 repo 目錄下執行失敗時可能留下 `{{pkgetc}}/` 這種未展開樣板名的殘留資料夾

## 行動

- 遇到 spawn python ENOENT / atom 寫入失敗 / vector 不索引 → 先確認 `~/.local/bin/python` wrapper 還在且 `python --version` 正常
- 不要用 `ln -s` 建 python（Apple shim 會擋）；要用 exec wrapper
