#!/usr/bin/env python3
"""journal-aggregate.py — 從 episodic atoms + workflow state 彙整工作日誌

Usage:
    python journal-aggregate.py              # 今天的日誌
    python journal-aggregate.py 2026-04-07   # 指定日期
    python journal-aggregate.py week         # 本週週報
    python journal-aggregate.py week 2026-04-07  # 含該日期的那週
    python journal-aggregate.py month        # 本月月報
    python journal-aggregate.py month 2026-04    # 指定月份月報
    python journal-aggregate.py range 2026-04-01 2026-04-10  # 任意日期範圍（逐日產）
    python journal-aggregate.py --cleanup    # 僅清理過期日誌
"""

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
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

_obsidian_env = os.environ.get("CLAUDE_JOURNAL_OBSIDIAN_DIR")
OBSIDIAN_BASE = Path(_obsidian_env) if _obsidian_env else None
OBSIDIAN_SUBDIR = {"daily": "日報", "weekly": "週報", "monthly": "月報"}

VCS_TIMEOUT = 10
MAX_FILES_LIST = 30  # 修改檔案清單上限

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


def _mod_paths(mod: list) -> list[str]:
    """從 modified_files 取出 path 字串清單。"""
    paths = []
    for m in mod:
        if isinstance(m, dict):
            p = m.get("path", "")
        else:
            p = str(m)
        if p:
            paths.append(p)
    return paths


def _state_record(data: dict) -> dict:
    sess = data["session"]
    started = sess.get("started_at", "")
    topic = data.get("topic_tracker", {})
    kq = data.get("knowledge_queue", [])
    mod_paths = list(dict.fromkeys(_mod_paths(data.get("modified_files", []))))
    cwd = sess.get("cwd", "")
    return {
        "id": sess.get("id", "")[:8],
        "project": _project_name(cwd),
        "cwd": cwd,
        "start": started[11:16],
        "end": data.get("ended_at", "")[11:16] if data.get("ended_at") else "…",
        "prompts": topic.get("prompt_count", 0),
        "intent": topic.get("intent_distribution", {}),
        "modified_files": mod_paths,
        "files_modified": len(mod_paths),
        "knowledge": [k.get("content", "")[:200] for k in kq],
    }


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
            results.append(_state_record(data))
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
            by_date[sdate].append(_state_record(data))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return dict(by_date)


# ── Daily Journal Builder ──────────────────────────────────────

def _truncate(s: str, n: int = 60) -> str:
    s = s.strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def _project_summary_line(project: str, sessions: list[dict],
                         commits: list[tuple[str, str]],
                         unique_files: int) -> str:
    if commits:
        msgs = "；".join(_truncate(m) for _, m in commits[:4])
        suffix = f"…等 {len(commits)} 個" if len(commits) > 4 else ""
        return f"- **{project}** ({len(commits)} commits): {msgs}{suffix}"
    if unique_files > 0:
        return f"- **{project}**: 改 {unique_files} 檔（未 commit）"
    prompts = sum(s["prompts"] for s in sessions)
    if prompts > 0:
        return f"- **{project}**: {prompts} prompts（純討論）"
    return f"- **{project}**: 閒置"


def _llm_summary(proj_data: list, active_days: int | None = None) -> str:
    """呼叫本地 Ollama 產生 2-4 句話速覽。失敗回 ""。"""
    try:
        sys.path.insert(0, str(Path.home() / ".claude" / "tools"))
        from ollama_client import OllamaClient, OllamaBackend  # type: ignore
    except ImportError:
        return ""

    # 直接用本地 backend，不試遠端（避免 timeout 拖長 journal 產出）
    model = os.environ.get("CLAUDE_JOURNAL_LLM_MODEL", "qwen3:1.7b")
    local_backend = OllamaBackend(
        name="local", base_url="http://127.0.0.1:11434", auth=None,
        llm_model=model, embedding_model=None, priority=1,
        enabled=True, think=False, llm_num_predict=512,
    )
    client = OllamaClient([local_backend])

    # 組裝精簡 context
    blocks: list[str] = []
    for item in proj_data:
        if len(item) != 4:
            continue
        _key, g, commits, _vcs = item
        parts = [f"[{g['project']}]"]
        if commits:
            for cid, msg in commits[:6]:
                parts.append(f"  commit: {msg}")
        else:
            files = {f for s in g["sessions"] for f in s["modified_files"]}
            if files:
                parts.append(f"  改檔(未commit): {len(files)} 檔")
                for fp in list(files)[:5]:
                    parts.append(f"    - {Path(fp).name}")
        # top knowledge
        kq = []
        for s in g["sessions"]:
            kq.extend(s["knowledge"][:3])
        for a in g["atoms"]:
            kq.extend(a.get("knowledge", [])[:2])
        seen: set = set()
        kq_unique = []
        for k in kq:
            ck = _clean_knowledge(k)
            if ck and ck not in seen:
                seen.add(ck)
                kq_unique.append(ck)
        for k in kq_unique[:3]:
            parts.append(f"  知識: {_truncate(k, 100)}")
        blocks.append("\n".join(parts))

    context_text = "\n\n".join(blocks)
    period_hint = f"這是一份 {active_days} 天的區間彙總。" if active_days else "這是今日的工作記錄。"
    prompt = f"""{period_hint}請用繁體中文寫一段 2-4 句的「做了什麼」速覽。

資料：
{context_text}

嚴格規則（違反者視為錯誤輸出）：
1. 直接輸出純文字段落，禁止條列、禁止 markdown、禁止項目符號 -
2. 禁止任何前言（如「以下」「總結」「工程主管」「請注意」）
3. 禁止任何時間詞開頭（如「今天」「本次」「這次」）
4. 全部寫在同一段，句子之間用句號分隔
5. 每個專案一句話，不超過 4 句總長
6. 只寫做了什麼、產出什麼，不寫統計數字
"""
    try:
        result = client.generate(prompt, timeout=20, think=False)
        return _strip_preamble((result or "").strip())
    except Exception:
        return ""


def _strip_preamble(text: str) -> str:
    """移除 LLM 常見前言 + 條列前綴。"""
    text = re.sub(r"^<think>.*?</think>\s*", "", text, flags=re.DOTALL)
    # 開頭前言只刪第一次
    for pattern in [
        r"^工程主管.*?[:：]\s*\n?",
        r"^以下是?.*?[:：]\s*\n?",
        r"^(總結|速覽|摘要).*?[:：]\s*\n?",
    ]:
        text = re.sub(pattern, "", text, count=1)
    # 「做了什麼：」可能出現多次，全刪
    text = re.sub(r"做了什麼[:：]\s*", "", text)
    # 把條列轉成段落（移除每行開頭的 - / *）
    cleaned_lines = []
    for line in text.splitlines():
        stripped = re.sub(r"^\s*[-*•]\s*", "", line).strip()
        if stripped:
            cleaned_lines.append(stripped)
    # 用空格而非換行接，避免 LLM 把句子拆行
    return " ".join(cleaned_lines).strip()


def _build_summary(proj_data: list, grand_sessions: int, grand_prompts: int,
                   grand_files: int, grand_commits: int,
                   active_days: int | None = None) -> list[str]:
    lines = ["## 總結", ""]

    # LLM 速覽（Ollama 不在則跳過）
    llm_text = _llm_summary(proj_data, active_days)
    if llm_text:
        lines.append(llm_text)
        lines.append("")

    # 統計數字
    stats = [
        f"{len(proj_data)} 專案",
        f"{grand_sessions} sessions",
        f"{grand_prompts} prompts",
        f"{grand_files} 檔",
        f"{grand_commits} commits",
    ]
    if active_days is not None:
        stats.insert(0, f"活躍 {active_days} 天")
    lines.append(" · ".join(stats))
    lines.append("")

    # 結構事實列
    for item in proj_data:
        if len(item) == 4:
            _key, g, commits, _vcs = item
        else:
            continue
        unique_files = len({f for s in g["sessions"] for f in s["modified_files"]})
        lines.append(_project_summary_line(g["project"], g["sessions"], commits, unique_files))
    lines.append("")
    return lines


def _intent_str(intent: dict) -> str:
    return " ".join(f"{k}({v})" for k, v in sorted(intent.items(), key=lambda x: -x[1]) if v > 0)


def _rel_path(p: str, base: str) -> str:
    if not base:
        return p
    try:
        return str(Path(p).relative_to(base)).replace("\\", "/")
    except (ValueError, OSError):
        return p.replace("\\", "/")


def _clean_knowledge(k: str) -> str:
    s = k.lstrip("- ").removeprefix("[臨] ").removeprefix("[觀] ").removeprefix("[固] ").strip()
    return s


def _build_project_block(project: str, cwd: str, sessions: list[dict],
                         atoms: list[dict], commits: list[tuple[str, str]],
                         vcs: str | None) -> list[str]:
    lines: list[str] = []
    header_meta = cwd if cwd else ""
    if vcs:
        header_meta = f"`{header_meta}` · {vcs}" if header_meta else vcs
    elif header_meta:
        header_meta = f"`{header_meta}`"

    lines.append(f"## {project}")
    if header_meta:
        lines.append(header_meta)
    lines.append("")

    # Sessions
    if sessions:
        total_prompts = sum(s["prompts"] for s in sessions)
        total_files = sum(s["files_modified"] for s in sessions)
        agg_intent: dict = defaultdict(int)
        for s in sessions:
            for k, v in s["intent"].items():
                agg_intent[k] += v
        intent = _intent_str(agg_intent)
        lines.append(
            f"**Sessions ({len(sessions)})** · {total_prompts} prompts · "
            f"{total_files} 改檔" + (f" · {intent}" if intent else "")
        )
        for s in sessions:
            lines.append(f"- `{s['start']}–{s['end']}`")
        lines.append("")

    # Commits
    if commits:
        lines.append(f"**Commits ({len(commits)})**")
        for cid, msg in commits:
            lines.append(f"- `{cid}` {msg}")
        lines.append("")

    # 修改檔案 (deduped, relative)
    files_set: list[str] = []
    seen = set()
    for s in sessions:
        for fp in s["modified_files"]:
            rel = _rel_path(fp, cwd)
            if rel not in seen:
                seen.add(rel)
                files_set.append(rel)
    if files_set:
        shown = files_set[:MAX_FILES_LIST]
        more = len(files_set) - len(shown)
        lines.append(f"**修改檔案 ({len(files_set)})**")
        for fp in shown:
            lines.append(f"- `{fp}`")
        if more > 0:
            lines.append(f"- … 還有 {more} 個")
        lines.append("")

    # Episodic 摘要 (若有)
    if atoms:
        for a in atoms:
            if a.get("summary"):
                lines.append(f"**摘要**")
                lines.append(a["summary"])
                lines.append("")
                break

    # 知識
    knowledge: list[str] = []
    kseen = set()
    for s in sessions:
        for k in s["knowledge"]:
            ck = _clean_knowledge(k)
            if ck and ck not in kseen:
                kseen.add(ck)
                knowledge.append(ck)
    for a in atoms:
        for k in a.get("knowledge", []):
            ck = _clean_knowledge(k)
            if ck and ck not in kseen:
                kseen.add(ck)
                knowledge.append(ck)
    if knowledge:
        lines.append(f"**知識 ({len(knowledge)})**")
        for k in knowledge[:15]:
            lines.append(f"- {k}")
        lines.append("")

    return lines


def build_journal(target_date: str) -> str:
    atoms = scan_episodic(target_date)
    states = scan_states(target_date)

    if not atoms and not states:
        return f"# {target_date} 工作日誌\n\n> 當天無記錄。\n"

    # 以 cwd（或 workspace fallback）分組
    by_proj: dict[str, dict] = defaultdict(lambda: {
        "project": "", "cwd": "", "sessions": [], "atoms": [],
    })
    for s in states:
        key = s["cwd"] or s["project"]
        g = by_proj[key]
        g["project"] = s["project"]
        g["cwd"] = s["cwd"]
        g["sessions"].append(s)
    for a in atoms:
        key = a["workspace"]
        g = by_proj[key]
        if not g["project"]:
            g["project"] = a["workspace"]
        g["atoms"].append(a)

    # Commits + 統計
    proj_data = []
    total_commits = 0
    for key, g in by_proj.items():
        commits, vcs = commits_for(g["cwd"], target_date) if g["cwd"] else ([], None)
        total_commits += len(commits)
        proj_data.append((key, g, commits, vcs))

    total_sessions = sum(len(g["sessions"]) for _, g, _, _ in proj_data)
    total_prompts = sum(s["prompts"] for _, g, _, _ in proj_data for s in g["sessions"])
    total_files = sum(s["files_modified"] for _, g, _, _ in proj_data for s in g["sessions"])

    # 排序：有 commit 的優先，然後依 prompts 數
    proj_data.sort(key=lambda x: (-len(x[2]), -sum(s["prompts"] for s in x[1]["sessions"])))

    lines = [f"# {target_date} 工作日誌", ""]
    lines.extend(_build_summary(proj_data, total_sessions, total_prompts,
                                total_files, total_commits))
    lines.append("| Sessions | Prompts | 改檔 | Commits |")
    lines.append("|:--:|:--:|:--:|:--:|")
    lines.append(f"| {total_sessions} | {total_prompts} | {total_files} | {total_commits} |")
    lines.append("")

    for _key, g, commits, vcs in proj_data:
        lines.append("---")
        lines.append("")
        lines.extend(_build_project_block(g["project"], g["cwd"], g["sessions"],
                                          g["atoms"], commits, vcs))

    return "\n".join(lines).rstrip() + "\n"


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

    return _render_period(all_dates, ep_by_date, st_by_date), True


def _render_period(all_dates: list[str], ep_by_date: dict, st_by_date: dict) -> list[str]:
    # 以 cwd（fallback workspace）分組，跨整個區間
    by_proj: dict[str, dict] = defaultdict(lambda: {
        "project": "", "cwd": "", "sessions": [], "atoms": [],
        "dates": set(),
    })
    for d in all_dates:
        for s in st_by_date.get(d, []):
            key = s["cwd"] or s["project"]
            g = by_proj[key]
            g["project"] = s["project"]
            g["cwd"] = s["cwd"]
            g["sessions"].append(s)
            g["dates"].add(d)
        for a in ep_by_date.get(d, []):
            key = a["workspace"]
            g = by_proj[key]
            if not g["project"]:
                g["project"] = a["workspace"]
            g["atoms"].append(a)
            g["dates"].add(d)

    # 各專案彙整 commits（區間內每天 commits 的聯集）
    proj_data = []
    grand_commits = 0
    for key, g in by_proj.items():
        commits: list[tuple[str, str]] = []
        vcs = None
        if g["cwd"]:
            seen_ids = set()
            for d in sorted(g["dates"]):
                day_commits, vcs_d = commits_for(g["cwd"], d)
                if vcs_d:
                    vcs = vcs_d
                for cid, msg in day_commits:
                    if cid not in seen_ids:
                        seen_ids.add(cid)
                        commits.append((cid, msg))
        grand_commits += len(commits)
        proj_data.append((key, g, commits, vcs))

    grand_sessions = sum(len(g["sessions"]) for _, g, _, _ in proj_data)
    grand_prompts = sum(s["prompts"] for _, g, _, _ in proj_data for s in g["sessions"])

    # 改檔（去重至專案內）
    grand_files = 0
    for _, g, _, _ in proj_data:
        seen = set()
        for s in g["sessions"]:
            seen.update(s["modified_files"])
        grand_files += len(seen)

    # 排序：有 commit 的優先
    proj_data.sort(key=lambda x: (-len(x[2]), -sum(s["prompts"] for s in x[1]["sessions"])))

    # ── 總結 ──
    lines: list[str] = []
    lines.extend(_build_summary(proj_data, grand_sessions, grand_prompts,
                                grand_files, grand_commits, active_days=len(all_dates)))

    # ── 總覽表 ──
    lines.append("| Sessions | Prompts | 改檔 | Commits | 活躍天數 |")
    lines.append("|:--:|:--:|:--:|:--:|:--:|")
    lines.append(f"| {grand_sessions} | {grand_prompts} | {grand_files} | {grand_commits} | {len(all_dates)} |")
    lines.append("")

    # ── 各專案 ──
    for _key, g, commits, vcs in proj_data:
        lines.append("---")
        lines.append("")
        lines.extend(_build_project_block(g["project"], g["cwd"], g["sessions"],
                                          g["atoms"], commits, vcs))

    # ── 每日簡述 ──
    lines.append("---")
    lines.append("")
    lines.append("## 每日簡述")
    lines.append("")
    for d in all_dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        wd = _WEEKDAY_NAMES[dt.weekday()]
        day_states = st_by_date.get(d, [])
        if day_states:
            parts = []
            for s in sorted(day_states, key=lambda x: x["start"]):
                parts.append(f"{s['project']} {s['prompts']}p")
            lines.append(f"- **{d} ({wd})** · " + " | ".join(parts))
        else:
            day_atoms = ep_by_date.get(d, [])
            if day_atoms:
                parts = [f"{a['workspace']} {a['files_mod_n']}f" for a in day_atoms]
                lines.append(f"- **{d} ({wd})** · " + " | ".join(parts))
    lines.append("")

    return lines


def build_weekly(ref_date: str) -> str:
    mon, sun, iso_y, iso_w = _week_range(ref_date)
    title = f"# {iso_y}-W{iso_w:02d} 週報 ({mon} ~ {sun})\n"
    body, has_data = _build_period_lines(mon, sun)
    if not has_data:
        return f"{title}\n> 該週無記錄。\n"
    return title + "\n" + "\n".join(body).rstrip() + "\n"


def _month_range(month_arg: str | None) -> tuple[str, str, str]:
    """月份引數 'YYYY-MM' 或 None（=本月），回傳 (start, end, label)。"""
    if month_arg:
        y, m = (int(x) for x in month_arg.split("-"))
    else:
        now = datetime.now()
        y, m = now.year, now.month
    start = datetime(y, m, 1)
    end = (datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)) - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), f"{y:04d}-{m:02d}"


def build_monthly(month_arg: str | None) -> tuple[str, str]:
    start, end, label = _month_range(month_arg)
    title = f"# {label} 月報 ({start} ~ {end})\n"
    body, has_data = _build_period_lines(start, end)
    if not has_data:
        return f"{title}\n> 該月無記錄。\n", label
    return title + "\n" + "\n".join(body).rstrip() + "\n", label


def _iter_dates(start: str, end: str):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    cur = s
    while cur <= e:
        yield cur.strftime("%Y-%m-%d")
        cur += timedelta(days=1)


def has_records(target_date: str) -> bool:
    return bool(scan_episodic(target_date)) or bool(scan_states(target_date))


# ── Obsidian Mirror ─────────────────────────────────────────────

def mirror_to_obsidian(content: str, filename: str, kind: str) -> Path | None:
    if OBSIDIAN_BASE is None:
        return None
    sub = OBSIDIAN_SUBDIR.get(kind)
    if sub is None or not OBSIDIAN_BASE.parent.exists():
        return None
    target_dir = OBSIDIAN_BASE / sub
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / filename
        target.write_text(content, encoding="utf-8")
        return target
    except OSError as e:
        print(f"[WARN] Obsidian 鏡射失敗: {e}", file=sys.stderr)
        return None


# ── VCS Commits ─────────────────────────────────────────────────

def _find_repo_root(cwd_str: str) -> tuple[Path, str] | None:
    """從 cwd 往上找 .git/.svn，回傳 (repo_root, vcs_kind)。"""
    if not cwd_str:
        return None
    p = Path(cwd_str)
    if not p.exists():
        return None
    for cur in [p, *p.parents]:
        if (cur / ".git").exists():
            return cur, "git"
        if (cur / ".svn").exists():
            return cur, "svn"
    return None


def _resolve_author(repo_root: Path, vcs: str) -> str:
    env_override = os.environ.get("CLAUDE_JOURNAL_AUTHOR")
    if env_override:
        return env_override
    if vcs == "git":
        try:
            r = subprocess.run(
                ["git", "-C", str(repo_root), "config", "user.name"],
                capture_output=True, text=True, timeout=VCS_TIMEOUT,
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    return os.environ.get("USERNAME") or os.environ.get("USER") or ""


def _git_commits(repo_root: Path, date: str, author: str) -> list[tuple[str, str]]:
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), "log",
             f"--since={date} 00:00:00", f"--until={date} 23:59:59",
             f"--author={author}", "--pretty=format:%h|%s"],
            capture_output=True, text=True, timeout=VCS_TIMEOUT,
        )
        if r.returncode != 0:
            return []
        return [tuple(line.split("|", 1)) for line in r.stdout.splitlines() if "|" in line]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def _svn_commits(repo_root: Path, date: str, author: str) -> list[tuple[str, str]]:
    next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        r = subprocess.run(
            ["svn", "log", "--xml", "--non-interactive",
             "-r", f"{{{date}}}:{{{next_day}}}"],
            capture_output=True, text=True, timeout=VCS_TIMEOUT, cwd=str(repo_root),
        )
        if r.returncode != 0:
            return []
        tree = ET.fromstring(r.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ET.ParseError):
        return []

    out: list[tuple[str, str]] = []
    for entry in tree.findall("logentry"):
        a = entry.find("author")
        if a is None or (a.text or "").strip() != author:
            continue
        rev = entry.get("revision", "?")
        msg_node = entry.find("msg")
        msg = ""
        if msg_node is not None and msg_node.text:
            msg = msg_node.text.strip().splitlines()[0] if msg_node.text.strip() else ""
        out.append((f"r{rev}", msg))
    return out


def commits_for(cwd_str: str, date: str) -> tuple[list[tuple[str, str]], str | None]:
    """回傳 (commits, vcs_kind)。失敗或無 VCS 回傳 ([], None)。"""
    info = _find_repo_root(cwd_str)
    if info is None:
        return [], None
    repo_root, vcs = info
    author = _resolve_author(repo_root, vcs)
    if not author:
        return [], vcs
    if vcs == "git":
        return _git_commits(repo_root, date, author), "git"
    return _svn_commits(repo_root, date, author), "svn"


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
    month_arg: str | None = None

    args = sys.argv[1:]
    for arg in args:
        if arg == "--cleanup":
            only_cleanup = True
        elif arg == "week":
            mode = "weekly"
        elif arg == "month":
            mode = "monthly"
        elif arg == "range":
            mode = "range"
        elif mode == "monthly" and re.match(r"\d{4}-\d{2}$", arg):
            month_arg = arg
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
        fname = f"week-{iso_y}-W{iso_w:02d}.md"
        out = JOURNALS_DIR / fname
        out.write_text(journal, encoding="utf-8")
        print(journal)
        print(f"\n---\n[OK] 已存檔: {out}")
        mirrored = mirror_to_obsidian(journal, fname, "weekly")
        if mirrored:
            print(f"[OK] Obsidian: {mirrored}")
    elif mode == "monthly":
        journal, label = build_monthly(month_arg)
        fname = f"month-{label}.md"
        out = JOURNALS_DIR / fname
        out.write_text(journal, encoding="utf-8")
        print(journal)
        print(f"\n---\n[OK] 已存檔: {out}")
        mirrored = mirror_to_obsidian(journal, fname, "monthly")
        if mirrored:
            print(f"[OK] Obsidian: {mirrored}")
    elif mode == "range":
        if len(range_dates) != 2:
            print("用法：range YYYY-MM-DD YYYY-MM-DD", file=sys.stderr)
            sys.exit(2)
        start, end = sorted(range_dates)
        produced = 0
        skipped = 0
        for d in _iter_dates(start, end):
            if not has_records(d):
                skipped += 1
                continue
            journal = build_journal(d)
            fname = f"{d}.md"
            out = JOURNALS_DIR / fname
            out.write_text(journal, encoding="utf-8")
            mirrored = mirror_to_obsidian(journal, fname, "daily")
            mirror_str = f" → {mirrored}" if mirrored else ""
            print(f"[OK] {d}: {out}{mirror_str}")
            produced += 1
        print(f"\n[OK] 區間 {start} ~ {end}：產生 {produced} 份日報，跳過 {skipped} 個無記錄日")
    else:
        journal = build_journal(target)
        fname = f"{target}.md"
        out = JOURNALS_DIR / fname
        out.write_text(journal, encoding="utf-8")
        print(journal)
        print(f"\n---\n[OK] 已存檔: {out}")
        mirrored = mirror_to_obsidian(journal, fname, "daily")
        if mirrored:
            print(f"[OK] Obsidian: {mirrored}")

    n = cleanup()
    if n:
        print(f"[OK] 清理 {n} 份過期日誌 (>{RETENTION_DAYS} 天)")


if __name__ == "__main__":
    main()
