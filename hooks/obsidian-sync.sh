#!/bin/bash
# PostToolUse hook: Claude Code memory → Obsidian 同步
#
# 觸發條件：Write 或 Edit tool 寫入 memory/ 目錄下的 .md 檔案
# 目標：~/WellsDB/知識庫/ClaudeCode/{project-slug}/
#
# Claude Code hook 透過 stdin 接收 JSON：
#   Write: { "tool_name": "Write", "tool_input": { "file_path": "..." }, ... }
#   Edit:  { "tool_name": "Edit",  "tool_input": { "file_path": "...", "old_string": "...", "new_string": "..." }, ... }

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")

# 只處理 Write 和 Edit
if [ "$TOOL_NAME" != "Write" ] && [ "$TOOL_NAME" != "Edit" ]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# 只處理 memory 目錄下的 .md 檔案
if [[ "$FILE_PATH" != *"/memory/"* ]] || [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

# 從路徑提取 project slug
# 路徑格式: ~/.claude/projects/{slug}/memory/{file}.md
SLUG=$(echo "$FILE_PATH" | sed -n 's|.*\.claude/projects/\([^/]*\)/memory/.*|\1|p')
if [ -z "$SLUG" ]; then
  exit 0
fi

FILENAME=$(basename "$FILE_PATH")
TARGET_DIR="$HOME/WellsDB/知識庫/ClaudeCode/$SLUG"
TARGET_PATH="$TARGET_DIR/$FILENAME"

# 確保目標目錄存在
mkdir -p "$TARGET_DIR"

# 讀取來源檔案（Edit 後檔案已被修改，直接讀最新版）
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

CONTENT=$(cat "$FILE_PATH")
NOW=$(date "+%Y-%m-%d %H:%M:%S")

# 組裝 frontmatter + 內容
# 如果原文已有 frontmatter 就替換
if echo "$CONTENT" | head -1 | grep -q "^---$"; then
  BODY=$(echo "$CONTENT" | awk 'BEGIN{skip=0; found=0} /^---$/{if(found==0){found=1;skip=1;next} else if(skip==1){skip=0;next}} skip==0{print}')
  cat > "$TARGET_PATH" <<ENDOFFILE
---
source: claude-code-memory
project: $SLUG
synced_at: $NOW
original_path: $FILE_PATH
---

$BODY
ENDOFFILE
else
  cat > "$TARGET_PATH" <<ENDOFFILE
---
source: claude-code-memory
project: $SLUG
synced_at: $NOW
original_path: $FILE_PATH
---

$CONTENT
ENDOFFILE
fi

exit 0
