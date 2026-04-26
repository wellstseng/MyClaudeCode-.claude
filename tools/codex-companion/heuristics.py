"""heuristics.py — Rule-based soft gate checks for Codex Companion.

No LLM calls. All checks run < 10ms.
Input: Guardian state dict (from wg_core.read_state).
Output: list of HeuristicResult.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HeuristicResult:
    name: str
    triggered: bool
    severity: str  # "low" | "medium" | "high"
    detail: str


# --- patterns ---

_VERIFY_CMD_RE = re.compile(
    r"(?:^|\s)(?:"
    r"pytest|python\s+-m\s+pytest|"
    r"npm\s+(?:run\s+)?test|jest|vitest|"
    r"node\s+--check|tsc|"
    r"go\s+test|cargo\s+test|"
    r"dotnet\s+test|"
    r"python\s+.*\.py|"  # running a script counts as verify
    r"make\s+(?:test|check|build)|"
    r"(?:npm|yarn|pnpm)\s+run\s+build"
    r")(?:\s|$)"
)

_COMPLETION_RE = re.compile(
    r"(完成|已解決|全部做完|done|finished|all\s+set|wrapped\s+up|大功告成|搞定|收尾|總結)",
    re.IGNORECASE,
)

_ARCH_FILE_RE = re.compile(
    r"(?:bridge|provider|adapter|factory|service|client|transport|middleware|gateway)"
    r"(?:\.py|\.ts|\.js|\.rs)$",
    re.IGNORECASE,
)


def _get_tool_trace(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tool trace from companion state or guardian state."""
    return state.get("tool_trace", [])


def _get_modified_files(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return state.get("modified_files", [])


def _get_accessed_files(state: Dict[str, Any]) -> List[str]:
    return state.get("accessed_files", [])


# --- individual heuristics ---

def check_missing_verification(state: Dict[str, Any]) -> HeuristicResult:
    """有 Edit/Write 但沒有 test/build/run 的 Bash 指令。"""
    modified = _get_modified_files(state)
    if not modified:
        return HeuristicResult("missing_verification", False, "low", "")

    trace = _get_tool_trace(state)
    has_verify = False
    for t in trace:
        if t.get("tool") == "Bash":
            cmd = t.get("input", "")
            if _VERIFY_CMD_RE.search(cmd):
                has_verify = True
                break

    if has_verify:
        return HeuristicResult("missing_verification", False, "low", "")

    file_names = list({m.get("path", "").rsplit("/", 1)[-1] for m in modified})
    return HeuristicResult(
        "missing_verification",
        True,
        "medium",
        f"Modified {len(modified)} file(s) ({', '.join(file_names[:5])}) but no test/build command detected.",
    )


def check_completion_without_evidence(
    state: Dict[str, Any], stop_text: str = ""
) -> HeuristicResult:
    """宣稱完成但修改少且無測試。"""
    has_claim = bool(_COMPLETION_RE.search(stop_text))
    if not has_claim:
        # also check last few tool trace entries for completion-like output
        trace = _get_tool_trace(state)
        for t in trace[-3:]:
            if _COMPLETION_RE.search(t.get("output_summary", "")):
                has_claim = True
                break

    if not has_claim:
        return HeuristicResult("completion_without_evidence", False, "low", "")

    modified = _get_modified_files(state)
    trace = _get_tool_trace(state)
    has_verify = any(
        t.get("tool") == "Bash" and _VERIFY_CMD_RE.search(t.get("input", ""))
        for t in trace
    )

    if len(modified) >= 2 and has_verify:
        return HeuristicResult("completion_without_evidence", False, "low", "")

    issues = []
    if len(modified) < 2:
        issues.append(f"only {len(modified)} file(s) modified")
    if not has_verify:
        issues.append("no verification command found")

    return HeuristicResult(
        "completion_without_evidence",
        True,
        "high",
        f"Completion claimed but: {'; '.join(issues)}.",
    )


def check_architecture_change(state: Dict[str, Any]) -> HeuristicResult:
    """新建 bridge/provider/adapter/service 等結構性檔案。"""
    modified = _get_modified_files(state)
    arch_files = [
        m.get("path", "")
        for m in modified
        if _ARCH_FILE_RE.search(m.get("path", ""))
    ]

    if not arch_files:
        return HeuristicResult("architecture_change", False, "low", "")

    names = [p.rsplit("/", 1)[-1] for p in arch_files]
    return HeuristicResult(
        "architecture_change",
        True,
        "medium",
        f"Structural file(s) created/modified: {', '.join(names)}. Consider architecture review.",
    )


def check_spinning(state: Dict[str, Any]) -> HeuristicResult:
    """連續 ≥ 3 次 Read 同一檔案但沒有 Edit。"""
    trace = _get_tool_trace(state)
    if len(trace) < 3:
        return HeuristicResult("spinning", False, "low", "")

    read_counts: Dict[str, int] = {}
    edited: set = set()

    for t in trace:
        tool = t.get("tool", "")
        path = t.get("path", "") or t.get("input", "")
        if tool == "Read" and path:
            read_counts[path] = read_counts.get(path, 0) + 1
        elif tool in ("Edit", "Write") and path:
            edited.add(path)

    spinning_files = [
        p for p, c in read_counts.items()
        if c >= 3 and p not in edited
    ]

    if not spinning_files:
        return HeuristicResult("spinning", False, "low", "")

    names = [p.rsplit("/", 1)[-1] for p in spinning_files[:3]]
    return HeuristicResult(
        "spinning",
        True,
        "low",
        f"Read {', '.join(names)} ≥3 times without editing. Possible analysis loop.",
    )


# --- aggregate ---

def run_all(
    state: Dict[str, Any], stop_text: str = ""
) -> List[HeuristicResult]:
    """Run all heuristics and return results (triggered or not)."""
    return [
        check_missing_verification(state),
        check_completion_without_evidence(state, stop_text),
        check_architecture_change(state),
        check_spinning(state),
    ]


def triggered_results(
    state: Dict[str, Any], stop_text: str = ""
) -> List[HeuristicResult]:
    """Run all heuristics and return only triggered ones."""
    return [r for r in run_all(state, stop_text) if r.triggered]


def max_severity(results: List[HeuristicResult]) -> str:
    """Return the highest severity among triggered results."""
    order = {"low": 0, "medium": 1, "high": 2}
    if not results:
        return "low"
    return max(results, key=lambda r: order.get(r.severity, 0)).severity


def format_for_context(results: List[HeuristicResult]) -> str:
    """Format triggered heuristics for additionalContext injection."""
    triggered = [r for r in results if r.triggered]
    if not triggered:
        return ""
    lines = [f"[Codex Companion: Heuristic Gate] {len(triggered)} flag(s)"]
    for r in triggered:
        lines.append(f"  [{r.severity}] {r.name}: {r.detail}")
    return "\n".join(lines)
