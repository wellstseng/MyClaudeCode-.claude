#!/usr/bin/env python3
"""
safety-guard.py — PreToolUse 全域安全防護 hook

攔截危險的工具呼叫：
- Bash: 系統破壞指令、程序管理、敏感操作
- Write/Edit: 系統路徑、憑證檔案、hook 自保護
- Read: 憑證檔案（防外洩）

判定：
- 命中 → stdout JSON { "decision": "block", "reason": "..." }
- 沒命中 → 不輸出（放行）
"""

import json
import os
import re
import sys


# ── 黑名單定義 ────────────────────────────────────────────────────────────────

# Bash 指令黑名單（正規表達式，case-insensitive）
BASH_BLOCKLIST = [
    # 系統破壞
    r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/\s*$",     # rm -rf / 或 rm /
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*\s+/(?:etc|sys|proc|dev|boot|usr|System|Library)\b",
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*\s+~\s*$",          # rm -rf ~
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+[06]\b",
    r"\bsystemctl\s+(poweroff|reboot|halt)\b",

    # 程序管理（防止 catclaw 自我重啟迴圈）
    r"\bpm2\s+(restart|stop|delete|kill)\b",
    r"\bpm2\s+start\b",
    r"\bcatclaw\.js\b",
    r"\bkill\s+-9\s",
    r"\bkill\s+-s\s*(KILL|SIGKILL|9)\b",
    r"\bpkill\b",
    r"\bkillall\b",

    # 敏感操作
    r"\bcurl\b.*\|\s*(ba)?sh\b",                    # curl | sh
    r"\bwget\b.*\|\s*(ba)?sh\b",                    # wget | sh
    r"\bchmod\s+[0-7]*777\b",                       # chmod 777
    r"\bchmod\s+\+s\b",                              # setuid
    r">\s*/etc/",                                     # 寫入 /etc/
    r">\s*/dev/sd",                                   # 寫入磁碟裝置

    # 危險的 git 操作
    r"\bgit\s+push\s+.*--force\s+.*main\b",
    r"\bgit\s+push\s+.*--force\s+.*master\b",
]

# 路徑黑名單（Write / Edit / Read 共用）
PATH_BLOCKLIST_WRITE = [
    # 系統目錄
    r"^/etc\b",
    r"^/sys\b",
    r"^/proc\b",
    r"^/dev\b",
    r"^/boot\b",
    r"^/root\b",
    r"^/usr\b",
    r"^/System\b",
    r"^/Library\b",
    r"^/private/etc\b",

    # Hook 自保護（防止修改安全防護本身）
    r"\.claude/hooks/safety-guard\.py$",
    r"\.claude/settings\.json$",
]

# 憑證檔案（Write/Edit 禁寫，Read 也禁讀防外洩）
CREDENTIAL_PATTERNS = [
    r"\.env$",
    r"\.env\.",
    r"credentials\.json$",
    r"service[_-]?account.*\.json$",
    r"/\.ssh/",
    r"/\.aws/",
    r"/\.gnupg/",
]


# ── 檢查邏輯 ────────────────────────────────────────────────────────────────

def check_bash(command: str) -> "str | None":
    """檢查 Bash 指令是否命中黑名單，回傳 reason 或 None"""
    for pattern in BASH_BLOCKLIST:
        if re.search(pattern, command, re.IGNORECASE):
            return f"危險指令被攔截：{pattern}"
    return None


def check_path_write(file_path: str) -> "str | None":
    """檢查 Write/Edit 路徑是否命中黑名單"""
    resolved = os.path.expanduser(file_path)
    for pattern in PATH_BLOCKLIST_WRITE:
        if re.search(pattern, resolved):
            return f"禁止寫入系統路徑：{resolved}"
    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, resolved, re.IGNORECASE):
            return f"禁止修改憑證檔案：{resolved}"
    return None


def check_path_read(file_path: str) -> "str | None":
    """檢查 Read 路徑是否為憑證檔案（防外洩）"""
    resolved = os.path.expanduser(file_path)
    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, resolved, re.IGNORECASE):
            return f"禁止讀取憑證檔案：{resolved}"
    return None


# ── 主程式 ────────────────────────────────────────────────────────────────

def main():
    # PreToolUse hook 透過 stdin 接收 JSON
    raw = sys.stdin.read()
    if not raw.strip():
        return

    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input", {})

    reason = None

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        reason = check_bash(command)

    elif tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        reason = check_path_write(file_path)

    elif tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        reason = check_path_read(file_path)

    if reason:
        result = {"decision": "block", "reason": reason}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
