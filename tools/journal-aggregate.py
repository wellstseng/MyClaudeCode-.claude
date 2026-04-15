#!/usr/bin/env python3
"""journal-aggregate.py — 從 episodic atoms + workflow state 彙整工作日誌

Usage:
    python journal-aggregate.py              # 今天的日誌
    python journal-aggregate.py 2026-04-07   # 指定日期
    python journal-aggregate.py week         # 本週週報
    python journal-aggregate.py week 2026-04-07  # 含該日期的那週
    python journal-aggregate.py range 2026-04-01 2026-04-10  # 任意日期範圍
    python journal-aggregate.py --cleanup    # 僅清理過期日誌
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Windows cp950 → UTF-8
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

CLAUDE_DIR = Path.home() / ".claude"
JOURNALS_DIR = CLAUDE_DIR / "journals"
WORKFLOW_DIR = CLAUDE_DIR / "workflow"
RETENTION_DAYS = 60

_WEEKDAY_NAMES = ["一", "二", "三", "四", "五", "六", "日"]

# Episodic 知識行中屬於統計類的 pattern（日誌中跳過）
_STAT_PATTERNS = ("閱讀 ", "閱讀區域", "版控查詢", "覆轍信號", "引用 atoms")


# ── Episodic Atoms ──────────────────────────────────────────────

def _find_episodic_dirs():
    """回傳所有 episodic 目錄 [(label, Path), ...]"""
    dirs = []
    g = CLAUDE_DIR / "memory" / "episodic"
    if g.exists():
        dirs.append(("global", g))
    proj = CLAUDE_DIR / "projects"
    if proj.exists():
        for p in proj.iterdir():
            ep = p / "memory" / "episodic"
            if ep.exists():
                dirs.append((p.name, ep))
    return dirs


def _parse_episodic(stem: str, content: str) -> dict:
    """解析 episodic atom → {workspace, summary, work_areas, files_mod, files_mod_n, knowledge, intent}"""
    info = {"stem": stem, "workspace": "", "summary": "",
            "work_areas": "", "files_mod": "", "files_mod_n": 0,
            "knowledge": [], "intent": ""}

    m = re.match(r"episodic-\d{8}-(.+?)(?:-\d+)?$", stem)
    if m:
        info["workspace"] = m.group(1)

    # 摘要
    m = re.search(r"## 摘要\s*\n(.+?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        info["summary"] = m.group(1).strip()

    # 知識
    m = re.search(r"## 知識\s*\n(.+?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        for line in m.group(1).strip().splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            if "工作區域" in line:
                info["work_areas"] = line
            elif "修改" in line and "個檔案" in line:
                info["files_mod"] = line
                nm = re.search(r"修改 (\d+) 個", line)
                if nm:
                    info["files_mod_n"] = int(nm.group(1))
            elif not any(p in line for p in _STAT_PATTERNS):
                info["knowledge"].append(line)

    # 關聯（意圖分布）
    m = re.search(r"## 關聯\s*\n(.+?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        for line in m.group(1).strip().splitlines():
            if "意圖分布" in line:
                info["intent"] = line.strip().removeprefix("- ")
                break

    return info


def _dedup_episodic(atoms: list[dict]) -> list[dict]:
    """同 workspace 的增量快照只保留最完整的那筆（files_mod_n 最大）"""
    best = {}
    for a in atoms:
        ws = a["workspace"]
        if ws not in best or a["files_mod_n"] >= best[ws]["files_mod_n"]:
            best[ws] = a
    return list(best.values())


def scan_episodic(target_date: str) -> list[dict]:
    """掃描指定日期的所有 episodic atoms（已去重）"""
    dc = target_date.replace("-", "")
    prefix = f"episodic-{dc}-"
    atoms = []
    for _label, d in _find_episodic_dirs():
        for f in sorted(d.glob(f"{prefix}*.md")):
            try:
                atoms.append(_parse_episodic(f.stem, f.read_text(encoding="utf-8")))
            except Exception:
                pass
    return _dedup_episodic(atoms)


def scan_episodic_range(start: str, end: str) -> dict[str, list[dict]]:
    """掃描日期範圍的 episodic atoms，回傳 {date: [atoms]}"""
    by_date = defaultdict(list)
    for _label, d in _find_episodic_dirs():
        if not d.exists():
            continue
        for f in sorted(d.glob("episodic-*.md")):
            m = re.match(r"episodic-(\d{8})-", f.name)
            if not m:
                continue
            dc = m.group(1)
            fdate = f"{dc[:4]}-{dc[4:6]}-{dc[6:8]}"
            if start <= fdate <= end:
                try:
                    by_date[fdate].append(
                        _parse_episodic(f.stem, f.read_text(encoding="utf-8"))
                    )
                except Exception:
                    pass
    # dedup per day
    return {d: _dedup_episodic(atoms) for d, atoms in by_date.items()}


# ── Workflow State Files ────────────────────────────────────────

def _project_name(cwd: str) -> str:
    parts = cwd.replace("\\", "/").rstrip("/").split("/")
    if len(parts) >= 2 and parts[-1] in ("Develop", "Server", "Client"):
        return f"{parts[-2]}.{parts[-1]}"
    return parts[-1] if parts else "unknown"


def scan_states(target_date: str) -> list[dict]:
    """掃描當天仍存在的 state files"""
    if not WORKFLOW_DIR.exists():
        return []
    results = []
    for f in WORKFLOW_DIR.glob("state-*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            started = data.get("session", {}).get("started_at", "")
            if started[:10] != target_date:
                continue
            sess = data["session"]
            topic = data.get("topic_tracker", {})
            kq = data.get("knowledge_queue", [])
            mod = data.get("modified_files", [])
            results.append({
                "id": sess.get("id", "")[:8],
                "project": _project_name(sess.get("cwd", "")),
                "start": started[11:16],
                "end": data.get("ended_at", "")[11:16] if data.get("ended_at") else "…",
                "prompts": topic.get("prompt_count", 0),
                "intent": topic.get("intent_distribution", {}),
                "files_modified": len(mod),
                "knowledge": [k.get("content", "")[:150] for k in kq],
            })
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return sorted(results, key=lambda s: s["start"])


def scan_states_range(start: str, end: str) -> dict[str, list[dict]]:
    """掃描日期範圍內仍存在的 state files"""
    if not WORKFLOW_DIR.exists():
        return {}
    by_date = defaultdict(list)
    for f in WORKFLOW_DIR.glob("state-*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            started = data.get("session", {}).get("started_at", "")
            sdate = started[:10]
            if not (start <= sdate <= end):
                continue
            sess = data["session"]
            topic = data.get("topic_tracker", {})
            kq = data.get("knowledge_queue", [])
            mod = data.get("modified_files", [])
            by_date[sdate].append({
                "id": sess.get("id", "")[:8],
                "project": _project_name(sess.get("cwd", "")),
                "start": started[11:16],
                "end": data.get("ended_at", "")[11:16] if data.get("ended_at") else "…",
                "prompts": topic.get("prompt_count", 0),
                "intent": topic.get("intent_distribution", {}),
                "files_modified": len(mod),
                "knowledge": [k.get("content", "")[:150] for k in kq],
            })
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return dict(by_date)


# ── Daily Journal Builder ──────────────────────────────────────

def build_journal(target_date: str) -> str:
    atoms = scan_episodic(target_date)
    states = scan_states(target_date)

    if not atoms and not states:
        return f"# 工作日誌：{target_date}\n\n> 當天無記錄。\n"

    lines = [f"# 工作日誌：{target_date}\n"]

    # ── Sessions table (from state files, if available) ──
    if states:
        lines.append(f"## Sessions ({len(states)})\n")
        lines.append("| 時間 | 專案 | Prompts | 改檔 | 主要意圖 |")
        lines.append("|------|------|---------|------|---------|")
        for s in states:
            intent_str = ", ".join(
                f"{k}({v})" for k, v in
                sorted(s["intent"].items(), key=lambda x: -x[1]) if v > 0
            )
            lines.append(
                f"| {s['start']}–{s['end']} | {s['project']} "
                f"| {s['prompts']} | {s['files_modified']} | {intent_str} |"
            )
        lines.append("")

    # ── 工作內容 (from episodic atoms, grouped by workspace) ──
    if atoms:
        by_ws = defaultdict(list)
        for a in atoms:
            by_ws[a["workspace"]].append(a)

        lines.append(f"## 工作內容 ({len(atoms)} sessions)\n")
        for ws, ws_atoms in by_ws.items():
            lines.append(f"### {ws}\n")
            for a in ws_atoms:
                if a["work_areas"]:
                    lines.append(a["work_areas"])
                if a["files_mod"]:
                    lines.append(a["files_mod"])
                for k in a["knowledge"]:
                    lines.append(k)
                if a["intent"]:
                    lines.append(f"- {a['intent']}")
            lines.append("")

    # ── 知識摘要 (from state knowledge_queue, deduplicated) ──
    seen = set()
    all_k = []
    for s in states:
        for k in s.get("knowledge", []):
            if k and k not in seen:
                seen.add(k)
                all_k.append(k)
    if all_k:
        lines.append("## 知識摘要\n")
        for k in all_k[:15]:
            lines.append(f"- {k}")
        lines.append("")

    return "\n".join(lines)


# ── Weekly Summary Builder ─────────────────────────────────────

def _week_range(ref_date: str) -> tuple[str, str, int, int]:
    """回傳 (monday_str, sunday_str, iso_year, iso_week)"""
    d = datetime.strptime(ref_date, "%Y-%m-%d")
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    iso_year, iso_week, _ = d.isocalendar()
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d"), iso_year, iso_week


def _build_period_lines(start: str, end: str) -> tuple[list[str], bool]:
    """彙整 [start, end] 區間的內容（不含標題）。回傳 (lines, has_data)。"""
    ep_by_date = scan_episodic_range(start, end)
    st_by_date = scan_states_range(start, end)

    all_dates = sorted(set(list(ep_by_date.keys()) + list(st_by_date.keys())))
    if not all_dates:
        return [], False

    lines: list[str] = []

    # ── 按專案統計 ──
    proj_stats = defaultdict(lambda: {"sessions": 0, "files": 0, "prompts": 0,
                                       "intents": defaultdict(int), "knowledge": []})

    for d in all_dates:
        for s in st_by_date.get(d, []):
            p = proj_stats[s["project"]]
            p["sessions"] += 1
            p["files"] += s["files_modified"]
            p["prompts"] += s["prompts"]
            for intent, cnt in s["intent"].items():
                p["intents"][intent] += cnt
            for k in s["knowledge"]:
                if k and k not in p["knowledge"]:
                    p["knowledge"].append(k)

        for a in ep_by_date.get(d, []):
            ws = a["workspace"]
            p = proj_stats[ws]
            p["sessions"] += 1
            p["files"] += a["files_mod_n"]
            for k in a["knowledge"]:
                if k not in p["knowledge"]:
                    p["knowledge"].append(k)

    if proj_stats:
        total_sessions = sum(p["sessions"] for p in proj_stats.values())
        total_files = sum(p["files"] for p in proj_stats.values())
        lines.append("## 工作總覽\n")
        lines.append(f"- 總 sessions: {total_sessions}")
        lines.append(f"- 總修改檔案: {total_files}")
        lines.append("")

        lines.append("| 專案 | Sessions | 改檔 | Prompts | 主要意圖 |")
        lines.append("|------|----------|------|---------|---------|")
        for proj, p in sorted(proj_stats.items(), key=lambda x: -x[1]["sessions"]):
            top_intents = ", ".join(
                f"{k}({v})" for k, v in
                sorted(p["intents"].items(), key=lambda x: -x[1])[:3]
            ) if p["intents"] else "-"
            lines.append(
                f"| {proj} | {p['sessions']} | {p['files']} "
                f"| {p['prompts']} | {top_intents} |"
            )
        lines.append("")

    # ── 按日摘要 ──
    lines.append("## 每日摘要\n")
    for d in all_dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        wd = _WEEKDAY_NAMES[dt.weekday()]
        lines.append(f"### {d} ({wd})\n")

        # State-based info
        day_states = st_by_date.get(d, [])
        if day_states:
            for s in sorted(day_states, key=lambda x: x["start"]):
                intent_str = ", ".join(
                    f"{k}({v})" for k, v in
                    sorted(s["intent"].items(), key=lambda x: -x[1]) if v > 0
                )
                lines.append(
                    f"- {s['start']}–{s['end']} **{s['project']}** "
                    f"— {s['prompts']}p, 改 {s['files_modified']} 檔 — {intent_str}"
                )

        # Episodic-based info
        day_atoms = ep_by_date.get(d, [])
        if day_atoms and not day_states:
            for a in day_atoms:
                lines.append(f"- **{a['workspace']}** — 改 {a['files_mod_n']} 檔")

        # Knowledge items for the day
        day_knowledge = []
        for s in day_states:
            for k in s.get("knowledge", []):
                if k and k not in day_knowledge:
                    day_knowledge.append(k)
        for a in day_atoms:
            for k in a["knowledge"]:
                clean = k.lstrip("- ").removeprefix("[臨] ").removeprefix("[觀] ").removeprefix("[固] ")
                if clean and clean not in day_knowledge:
                    day_knowledge.append(clean)
        if day_knowledge:
            for k in day_knowledge[:5]:
                lines.append(f"  - {k}")

        lines.append("")

    # ── 本週知識彙總 ──
    all_knowledge = []
    for p in proj_stats.values():
        for k in p["knowledge"]:
            clean = k.lstrip("- ").removeprefix("[臨] ").removeprefix("[觀] ").removeprefix("[固] ")
            if clean and clean not in all_knowledge:
                all_knowledge.append(clean)
    if all_knowledge:
        lines.append("## 知識彙總\n")
        for k in all_knowledge[:20]:
            lines.append(f"- {k}")
        lines.append("")

    return lines, True


def build_weekly(ref_date: str) -> str:
    mon, sun, iso_y, iso_w = _week_range(ref_date)
    title = f"# 週報摘要：{iso_y}-W{iso_w:02d} ({mon} ~ {sun})\n"
    body, has_data = _build_period_lines(mon, sun)
    if not has_data:
        return f"{title}\n> 該週無記錄。\n"
    return title + "\n" + "\n".join(body)


def build_range(start: str, end: str) -> str:
    title = f"# 區間日誌：{start} ~ {end}\n"
    body, has_data = _build_period_lines(start, end)
    if not has_data:
        return f"{title}\n> 該區間無記錄。\n"
    return title + "\n" + "\n".join(body)


# ── Cleanup ─────────────────────────────────────────────────────

def cleanup() -> int:
    if not JOURNALS_DIR.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed = 0
    for f in JOURNALS_DIR.glob("*.md"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", f.name)
        if m:
            try:
                if datetime.strptime(m.group(1), "%Y-%m-%d") < cutoff:
                    f.unlink()
                    removed += 1
            except ValueError:
                pass
    return removed


# ── Main ────────────────────────────────────────────────────────

def _norm_date(arg: str) -> str | None:
    if re.match(r"\d{4}-\d{2}-\d{2}$", arg):
        return arg
    if re.match(r"\d{8}$", arg):
        return f"{arg[:4]}-{arg[4:6]}-{arg[6:8]}"
    return None


def main():
    target = datetime.now().strftime("%Y-%m-%d")
    mode = "daily"
    only_cleanup = False
    range_dates: list[str] = []

    args = sys.argv[1:]
    for arg in args:
        if arg == "--cleanup":
            only_cleanup = True
        elif arg == "week":
            mode = "weekly"
        elif arg == "range":
            mode = "range"
        else:
            d = _norm_date(arg)
            if d is None:
                continue
            if mode == "range":
                range_dates.append(d)
            else:
                target = d

    if only_cleanup:
        n = cleanup()
        print(f"清理 {n} 份過期日誌 (>{RETENTION_DAYS} 天)")
        return

    JOURNALS_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "weekly":
        journal = build_weekly(target)
        _, _, iso_y, iso_w = _week_range(target)
        out = JOURNALS_DIR / f"week-{iso_y}-W{iso_w:02d}.md"
    elif mode == "range":
        if len(range_dates) != 2:
            print("用法：range YYYY-MM-DD YYYY-MM-DD", file=sys.stderr)
            sys.exit(2)
        start, end = sorted(range_dates)
        journal = build_range(start, end)
        out = JOURNALS_DIR / f"range-{start}_{end}.md"
    else:
        journal = build_journal(target)
        out = JOURNALS_DIR / f"{target}.md"

    out.write_text(journal, encoding="utf-8")
    print(journal)
    print(f"\n---\n[OK] 已存檔: {out}")

    n = cleanup()
    if n:
        print(f"[OK] 清理 {n} 份過期日誌 (>{RETENTION_DAYS} 天)")


if __name__ == "__main__":
    main()
