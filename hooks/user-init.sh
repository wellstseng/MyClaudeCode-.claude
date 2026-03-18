#!/bin/bash
# user-init.sh — SessionStart hook
# Generates USER.md and IDENTITY.md from template + per-user overrides.

CLAUDE_DIR="$HOME/.claude"
USERNAME="$(whoami | sed 's/.*\\/\//; s/.*\\\\//')"

# === USER.md ===
USER_FILE="$CLAUDE_DIR/USER-${USERNAME}.md"
USER_TEMPLATE="$CLAUDE_DIR/USER.template.md"
USER_TARGET="$CLAUDE_DIR/USER.md"

if [ ! -f "$USER_FILE" ] && [ -f "$USER_TEMPLATE" ]; then
  cp "$USER_TEMPLATE" "$USER_FILE"
fi
if [ -f "$USER_FILE" ]; then
  cp "$USER_FILE" "$USER_TARGET"
fi

# === IDENTITY.md ===
ID_FILE="$CLAUDE_DIR/IDENTITY-${USERNAME}.md"
ID_TEMPLATE="$CLAUDE_DIR/IDENTITY.template.md"
ID_TARGET="$CLAUDE_DIR/IDENTITY.md"

if [ ! -f "$ID_FILE" ] && [ -f "$ID_TEMPLATE" ]; then
  cp "$ID_TEMPLATE" "$ID_FILE"
fi
if [ -f "$ID_FILE" ]; then
  cp "$ID_FILE" "$ID_TARGET"
fi
