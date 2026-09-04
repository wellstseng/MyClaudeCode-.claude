#!/bin/bash
# Start Claude Code in a tmux session for Discord remote control
# Usage: start-judy-discord.sh [project-dir]
#
# Prerequisites: brew install tmux

SESSION_NAME="judy"
PROJECT_DIR="${1:-$HOME/project/catclaw}"

# Check tmux
if ! command -v tmux &>/dev/null; then
    echo "❌ tmux not found. Install: brew install tmux"
    exit 1
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' already running."
    echo "  Attach:  tmux attach -t $SESSION_NAME"
    echo "  Reset:   ~/.claude/scripts/reset-judy.sh"
    echo "  Kill:    tmux kill-session -t $SESSION_NAME"
    exit 0
fi

# Start Claude Code in tmux
tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR" \
    "claude --channels plugin:discord@claude-plugins-official --dangerously-skip-permissions"

echo "✅ Claude Code started in tmux session '$SESSION_NAME'"
echo "  Attach:  tmux attach -t $SESSION_NAME"
echo "  Detach:  Ctrl-B then D"
echo "  Reset:   ~/.claude/scripts/reset-judy.sh"
echo "  Discord: type !reset in channel"
