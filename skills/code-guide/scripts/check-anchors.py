#!/usr/bin/env python3
"""check-anchors: 驗證導讀地圖內所有程式碼引用錨點（路徑存在 + 行號在範圍內）。

用法:
  python check-anchors.py <導讀md檔> --root <專案根絕對路徑>

掃描 markdown 連結 [text](path#L行號)，逐一檢查：
  1. path（相對 --root）檔案存在
  2. 行號 >= 1 且 <= 檔案總行數
  3. 錨點格式合法（#L<n> 或 #L<n>-L<m>）
跳過 fenced code block / inline code（模板說明性引用不誤殺）、http(s) 外部連結、
以及不帶 #L 錨點的純文件連結（只有指向程式碼檔且帶錨點的才是受檢對象）。

輸出 JSON 到 stdout (UTF-8)。exit 0 = 全過，1 = 有違規，2 = 內部錯誤。
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Windows Python 預設 cp950 stdout 中文會亂碼 → 強制 UTF-8（必備）
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
ANCHOR_RE = re.compile(r"^L(\d+)(?:-L(\d+))?$")


def strip_code_regions(text: str) -> str:
    """把 fenced code block 與 inline code 的內容換成空白（保留行數），避免誤殺說明性引用。"""
    out_lines = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append("")
            continue
        if in_fence:
            out_lines.append("")
            continue
        out_lines.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out_lines)


def count_lines(path: Path) -> int:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


def check(md_path: Path, root: Path) -> dict:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    text = strip_code_regions(text)

    checked = 0
    violations = []
    line_count_cache = {}

    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in LINK_RE.finditer(line):
            label, target = m.group(1), m.group(2)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if "#" not in target:
                continue  # 不帶錨點的純文件連結不受檢
            rel, _, anchor = target.partition("#")
            am = ANCHOR_RE.match(anchor)
            if not am:
                violations.append({"line": lineno, "link": target, "reason": f"錨點格式非 #L<n>：#{anchor}"})
                continue
            checked += 1
            file_path = (root / rel.replace("/", "\\")).resolve()
            if not file_path.is_file():
                violations.append({"line": lineno, "link": target, "reason": f"檔案不存在：{rel}"})
                continue
            if file_path not in line_count_cache:
                line_count_cache[file_path] = count_lines(file_path)
            total = line_count_cache[file_path]
            start = int(am.group(1))
            end = int(am.group(2)) if am.group(2) else start
            if start < 1 or end > total or start > end:
                violations.append({
                    "line": lineno, "link": target,
                    "reason": f"行號超界：L{start}{'-L' + str(end) if am.group(2) else ''}（檔案共 {total} 行）",
                })

    return {
        "status": "ok" if not violations else "fail",
        "checked": checked,
        "violations": violations,
    }


def main():
    p = argparse.ArgumentParser(description="驗證導讀地圖的程式碼引用錨點")
    p.add_argument("md_file", type=str, help="導讀地圖 markdown 檔路徑")
    p.add_argument("--root", type=str, required=True, help="專案根絕對路徑（相對連結的基準）")
    args = p.parse_args()

    try:
        md_path = Path(args.md_file)
        root = Path(args.root)
        if not md_path.is_file():
            print(json.dumps({"status": "error", "reason": f"導讀檔不存在：{md_path}"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(2)
        if not root.is_dir():
            print(json.dumps({"status": "error", "reason": f"專案根不存在：{root}"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(2)
        result = check(md_path, root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["status"] == "ok" else 1)
    except Exception as e:
        # silent failure 風險點：所有未預期錯誤都要走這條，吐 JSON 到 stderr 才能被上層捕捉
        print(json.dumps({"status": "error", "reason": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
