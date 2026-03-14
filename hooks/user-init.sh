#!/bin/bash
# user-init.sh — SessionStart hook
# Ensures USER-{username}.md exists and USER.md points to it.

CLAUDE_DIR="$HOME/.claude"
USERNAME="$(whoami | sed 's/.*\\/\//; s/.*\\\\//')"
USER_FILE="$CLAUDE_DIR/USER-${USERNAME}.md"
TEMPLATE="$CLAUDE_DIR/USER.template.md"
TARGET="$CLAUDE_DIR/USER.md"

# 1) First-time user: copy template → USER-{username}.md
if [ ! -f "$USER_FILE" ] && [ -f "$TEMPLATE" ]; then
  cp "$TEMPLATE" "$USER_FILE"
fi

# 2) Generate USER.md from per-user file
if [ -f "$USER_FILE" ]; then
  cp "$USER_FILE" "$TARGET"
fi
