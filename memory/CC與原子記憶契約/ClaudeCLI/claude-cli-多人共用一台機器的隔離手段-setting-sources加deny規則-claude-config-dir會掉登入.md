# claude-cli-多人共用一台機器的隔離手段-setting-sources加deny規則-CLAUDE_CONFIG_DIR會掉登入

- Scope: global
- Author: wellstseng
- Source: 實測 session 2026-10-29（catclaw DM bridge 開發），claude CLI 2.1.312
- Confidence: [臨]
- Trigger: CLAUDE_CONFIG_DIR, setting-sources, permissions.deny, 隔離, 多使用者, claude -p 隔離, 不載 CLAUDE.md, deny 規則, Not logged in
- Created-at: 2026-10-29

## 知識

- [臨] 實測 claude 2.1.312 / macOS：`CLAUDE_CONFIG_DIR` 指到新目錄啟動 `claude -p` 直接回「Not logged in · Please run /login」——macOS 的 OAuth 憑證跟 config dir 綁在一起，想用它做多使用者隔離會失去登入態，不可行。
- [臨] `--setting-sources project,local`（排除 user）實測後 `~/.claude/CLAUDE.md` 的 @import（IDENTITY/USER）不再載入，user 層 settings.json 的 hooks 也不跑；只剩帳號 email 可辨識。這是「同一登入、不同人用」時隔離個人身份與記憶的可行手段。
- [臨] `--settings '{"permissions":{"deny":["Read(//abs/path/**)"]}}'` 實跑：Read 被拒，工具回「File is in a directory that is denied by your permission settings」。`//` 開頭 = 檔案系統絕對路徑；Read 規則連帶管 Glob/Grep，Edit 規則連帶管 Write/NotebookEdit。Bash 無法用路徑規則擋，只能靠審批或 disallowedTools。
- [臨] `--settings` 旗標只能給一次，多個設定（如 alwaysThinkingEnabled 與 permissions.deny）要合併成同一個 JSON 再傳。

## 行動

- 要讓同一台機器、同一登入服務多個人：用 --setting-sources project,local + permissions.deny + 每人獨立 cwd；不要試 CLAUDE_CONFIG_DIR
- deny 的工作目錄要放在被 deny 的路徑之外（例如 /Users/Shared），否則自己擋自己
- 改旗標前先 claude --help 確認該版本有此旗標；未知旗標會讓 child 立刻 exit 1
