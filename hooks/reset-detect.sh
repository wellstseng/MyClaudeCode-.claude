#!/bin/bash
# Hook: UserPromptSubmit — detect !reset command and trigger reset-judy.sh
# stdin: JSON with "prompt" field

PROMPT=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt',''))" 2>/dev/null)

if echo "$PROMPT" | grep -q '!reset'; then
    bash "$HOME/.claude/scripts/reset-judy.sh" &>/dev/null &
    echo '{"outputToUser":"[Reset] 正在執行 reset-judy.sh..."}' >&3 2>/dev/null || true
fi
