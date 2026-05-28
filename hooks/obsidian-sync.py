#!/usr/bin/env python3
"""
PostToolUse hook: Claude Code memory → Obsidian 同步
觸發條件：Write 或 Edit tool 寫入 memory/ 目錄下的 .md 檔案
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

# ★ Obsidian vault 路徑
OBSIDIAN_BASE = Path(r"C:\Users\wellstseng\Obsidian\知識庫\ClaudeCode")

def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    # 只處理 memory 目錄下的 .md 檔案
    if "/memory/" not in file_path.replace("\\", "/") or not file_path.endswith(".md"):
        return

    # 提取 project slug
    # 專案記憶體: ~/.claude/projects/{slug}/memory/{file}.md → slug = 專案名
    # 全域記憶體: ~/.claude/memory/{file}.md          → slug = _global
    normalized = file_path.replace("\\", "/")
    match = re.search(r"\.claude/projects/([^/]+)/memory/", normalized)
    if match:
        slug = match.group(1)
    elif re.search(r"\.claude/memory/", normalized):
        # _staging 為進行中草稿，不進長期知識庫
        if "/memory/_staging/" in normalized:
            return
        slug = "_global"
    else:
        return
    filename = os.path.basename(file_path)
    target_dir = OBSIDIAN_BASE / slug
    target_path = target_dir / filename

    # 讀取來源檔案
    source = Path(file_path)
    if not source.exists():
        return

    content = source.read_text(encoding="utf-8")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 組裝 frontmatter
    frontmatter = f"""---
source: claude-code-memory
project: {slug}
synced_at: {now}
original_path: {file_path}
---

"""

    # 如果原文已有 frontmatter 就替換
    if content.startswith("---\n"):
        end_idx = content.find("\n---\n", 4)
        if end_idx != -1:
            body = content[end_idx + 5:]
        else:
            body = content
    else:
        body = content

    output = frontmatter + body

    # 寫入 Obsidian
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_text(output, encoding="utf-8")

if __name__ == "__main__":
    main()
