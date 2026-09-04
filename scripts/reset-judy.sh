#!/bin/bash
# Reset Claude Code CLI session (sends /clear to tmux session)
# Can be called from: Discord (!reset), SSH, another terminal, cron, etc.
#
# Usage: reset-judy.sh [session-name]

SESSION_NAME="${1:-judy}"

# Check tmux
if ! command -v tmux &>/dev/null; then
    echo "❌ tmux not found"
    exit 1
fi

# Check session exists
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "❌ No tmux session '$SESSION_NAME'"
    echo "Start with: ~/.claude/scripts/start-judy-discord.sh"
    exit 1
fi

# Send /clear to the session
tmux send-keys -t "$SESSION_NAME" '/clear' Enter

echo "✅ Sent /clear to session '$SESSION_NAME'"
