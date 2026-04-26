"""codex_companion.py — Thin hook for Codex Companion integration.

Dispatches Claude Code hook events to the companion HTTP service.
Fast path: config disabled → exit(0) immediately (< 1ms).

Events handled:
  SessionStart    → ensure service, POST /event
  UserPromptSubmit → read assessment file → inject additionalContext
  PostToolUse     → POST /event, checkpoint detection
  Stop            → POST /event, heuristic soft gate, trigger turn audit
  SessionEnd      → POST /event
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

CLAUDE_DIR = Path.home() / ".claude"
WORKFLOW_DIR = CLAUDE_DIR / "workflow"
CONFIG_PATH = WORKFLOW_DIR / "config.json"
COMPANION_DIR = CLAUDE_DIR / "tools" / "codex-companion"

# Add companion dir to path for heuristics import
sys.path.insert(0, str(COMPANION_DIR))
sys.path.insert(0, str(CLAUDE_DIR / "hooks"))


# ─── Config ──────────────────────────────────────────────────────────────────


def _load_config() -> Dict[str, Any]:
    try:
        full = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return full.get("codex_companion", {})
    except (json.JSONDecodeError, OSError):
        return {}


# ─── HTTP helpers ────────────────────────────────────────────────────────────


def _http_post(port: int, path: str, data: Dict[str, Any], timeout: float = 0.5) -> Optional[Dict]:
    """POST JSON to companion service. Returns parsed response or None on failure."""
    try:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _http_get(port: int, path: str, timeout: float = 0.5) -> Optional[Dict]:
    """GET from companion service. Returns parsed response or None on failure."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


# ─── Service lifecycle ───────────────────────────────────────────────────────


def _is_service_running(port: int) -> bool:
    """Quick check: is something listening on the companion port?"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return sock.connect_ex(("127.0.0.1", port)) == 0
    finally:
        sock.close()


def _ensure_service(config: Dict[str, Any]) -> None:
    """Start companion service if not running."""
    port = config.get("service_port", 3850)

    # Health check first
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health", method="GET")
        with urllib.request.urlopen(req, timeout=1):
            return  # Already running
    except Exception:
        pass

    # Port guard
    if _is_service_running(port):
        return  # Port occupied, likely starting up

    service_path = COMPANION_DIR / "service.py"
    if not service_path.exists():
        return

    try:
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        CREATE_BREAKAWAY_FROM_JOB = 0x01000000

        log_path = CLAUDE_DIR / "Logs" / "codex-companion.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(str(log_path), "a")

        try:
            kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": log_fh,
            }
            if sys.platform == "win32":
                kwargs["creationflags"] = CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB

            subprocess.Popen([sys.executable, str(service_path)], **kwargs)
        except Exception:
            log_fh.close()
            raise
    except Exception:
        pass  # Fail silently — companion is optional


# ─── Output helpers (same protocol as workflow-guardian) ──────────────────────


def _output_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)


def _output_context(event_name: str, text: str) -> None:
    _output_json({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    })


def _output_block(reason: str) -> None:
    _output_json({"decision": "block", "reason": reason})


def _output_nothing() -> None:
    sys.exit(0)


# ─── Checkpoint detection ────────────────────────────────────────────────────


_PLAN_TOOLS = {"ExitPlanMode", "EnterPlanMode"}

_READ_ONLY_TOOLS = {"Read", "Glob", "Grep", "Agent", "WebSearch", "WebFetch"}
_WRITE_TOOLS = {"Edit", "Write"}


def _detect_checkpoint(tool_name: str, session_state: Dict[str, Any]) -> Optional[str]:
    """Determine if this tool use triggers a checkpoint.

    Returns checkpoint type or None.
    """
    # Explicit plan mode exit
    if tool_name in _PLAN_TOOLS:
        return "plan_review"

    # Quick-plan detection: first write tool after a run of read-only tools
    if tool_name in _WRITE_TOOLS:
        trace = session_state.get("tool_trace", [])
        if trace:
            # Check if all previous tools in trace were read-only
            prev_tools = [t.get("tool", "") for t in trace[:-1]]
            if prev_tools and all(t in _READ_ONLY_TOOLS for t in prev_tools if t):
                return "plan_review"

    # Architecture file detection
    if tool_name in _WRITE_TOOLS:
        import re
        arch_re = re.compile(
            r"(?:bridge|provider|adapter|factory|service|client|transport|middleware|gateway)"
            r"(?:\.py|\.ts|\.js|\.rs)$",
            re.IGNORECASE,
        )
        trace = session_state.get("tool_trace", [])
        if trace:
            last = trace[-1]
            if arch_re.search(last.get("path", "")):
                return "architecture_review"

    return None


# ─── Event handlers ──────────────────────────────────────────────────────────


def handle_session_start(input_data: Dict[str, Any], config: Dict[str, Any]):
    port = config.get("service_port", 3850)
    session_id = input_data.get("session_id", "")

    _ensure_service(config)

    # Give service a moment to start, then post event
    _http_post(port, "/event", {
        "session_id": session_id,
        "type": "session_start",
        "cwd": input_data.get("cwd", ""),
    }, timeout=1.0)

    _output_nothing()


def handle_user_prompt_submit(input_data: Dict[str, Any], config: Dict[str, Any]):
    """Inject pending Codex assessment as additionalContext."""
    session_id = input_data.get("session_id", "")
    if not session_id:
        _output_nothing()

    # Read assessment from file (no HTTP needed — resilient to service downtime)
    try:
        assessment_path = WORKFLOW_DIR / f"companion-assessment-{session_id}.json"
        data = json.loads(assessment_path.read_text(encoding="utf-8"))

        if data.get("injected", False):
            _output_nothing()

        assessment = data.get("assessment", {})
        if not assessment or assessment.get("status") == "error":
            _output_nothing()

        # Format assessment for injection
        atype = assessment.get("_assessment_type", "review")
        severity = assessment.get("severity", "low")
        status = assessment.get("status", "ok")
        summary = assessment.get("summary", "")
        action = assessment.get("recommended_action", "")
        corrective = assessment.get("corrective_prompt", "")

        type_label = {
            "plan_review": "Plan Review",
            "turn_audit": "Turn Audit",
            "architecture_review": "Architecture Review",
        }.get(atype, "Review")

        lines = [f"[Codex Companion: {type_label}] status={status} severity={severity}"]
        if summary:
            lines.append(f"摘要：{summary}")
        if action:
            lines.append(f"建議：{action}")
        if corrective:
            lines.append(f"修正提示：{corrective}")

        context_text = "\n".join(lines)

        # Token budget: ~300 tokens ≈ 600 chars Chinese
        if len(context_text) > 600:
            context_text = lines[0] + "\n" + f"摘要：{summary[:400]}"

        # Mark as injected
        data["injected"] = True
        tmp = assessment_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(assessment_path)

        _output_context("UserPromptSubmit", context_text)

    except (json.JSONDecodeError, OSError, KeyError):
        _output_nothing()


def handle_post_tool_use(input_data: Dict[str, Any], config: Dict[str, Any]):
    """Accumulate events + detect checkpoints."""
    port = config.get("service_port", 3850)
    session_id = input_data.get("session_id", "")
    tool_name = input_data.get("tool_name", "")

    if not session_id:
        _output_nothing()

    # Extract tool info
    tool_input = input_data.get("tool_input", "")
    if isinstance(tool_input, dict):
        # For Edit/Write: extract file_path
        file_path = tool_input.get("file_path", "")
        input_summary = file_path or json.dumps(tool_input, ensure_ascii=False)[:200]
    elif isinstance(tool_input, str):
        file_path = ""
        input_summary = tool_input[:200]
    else:
        file_path = ""
        input_summary = str(tool_input)[:200]

    # POST event (fire-and-forget)
    event_data = {
        "session_id": session_id,
        "type": "tool_use",
        "tool_name": tool_name,
        "tool_input_summary": input_summary,
        "tool_output_summary": "",  # tool_output not available in PostToolUse env
        "file_path": file_path,
    }
    result = _http_post(port, "/event", event_data)

    # Checkpoint detection
    if result:
        # Read updated state from service response (lightweight)
        # Actually we need the state from file for detection
        try:
            state_path = WORKFLOW_DIR / f"companion-state-{session_id}.json"
            st = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            st = {"tool_trace": []}

        checkpoint = _detect_checkpoint(tool_name, st)
        if checkpoint:
            _http_post(port, "/trigger", {
                "session_id": session_id,
                "type": checkpoint,
                "context": {},
            })

    _output_nothing()


def handle_stop(input_data: Dict[str, Any], config: Dict[str, Any]):
    """Run heuristic soft gate + trigger async turn audit."""
    port = config.get("service_port", 3850)
    session_id = input_data.get("session_id", "")

    if not session_id:
        _output_nothing()

    # POST stop event
    _http_post(port, "/event", {
        "session_id": session_id,
        "type": "stop",
    })

    # Run synchronous heuristic checks (no LLM, < 10ms)
    soft_gate_config = config.get("soft_gate", {})

    if soft_gate_config.get("completion_evidence", True):
        try:
            import heuristics

            # Read guardian state for modified_files context
            guardian_state_path = WORKFLOW_DIR / f"state-{session_id}.json"
            try:
                guardian_state = json.loads(guardian_state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                guardian_state = {}

            # Read companion state for tool_trace
            try:
                comp_state_path = WORKFLOW_DIR / f"companion-state-{session_id}.json"
                comp_state = json.loads(comp_state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                comp_state = {}

            # Merge: guardian has modified_files, companion has tool_trace
            merged_state = {
                "modified_files": guardian_state.get("modified_files", []),
                "accessed_files": guardian_state.get("accessed_files", []),
                "tool_trace": comp_state.get("tool_trace", []),
            }

            results = heuristics.triggered_results(merged_state)

            if results:
                max_sev = heuristics.max_severity(results)
                if max_sev == "high":
                    # Soft gate: block with heuristic reason
                    detail = heuristics.format_for_context(results)
                    _output_block(
                        f"Codex Companion 軟閘：偵測到高風險缺漏。\n{detail}\n"
                        "請補充驗證或修正後再收尾。"
                    )

        except Exception:
            pass  # Heuristics failure → degrade gracefully

    # Trigger async turn audit (fire-and-forget)
    _http_post(port, "/trigger", {
        "session_id": session_id,
        "type": "turn_audit",
        "context": {},
    })

    _output_nothing()


def handle_session_end(input_data: Dict[str, Any], config: Dict[str, Any]):
    port = config.get("service_port", 3850)
    session_id = input_data.get("session_id", "")

    _http_post(port, "/event", {
        "session_id": session_id,
        "type": "session_end",
    })

    _output_nothing()


# ─── Main dispatcher ─────────────────────────────────────────────────────────

HANDLERS = {
    "SessionStart": handle_session_start,
    "UserPromptSubmit": handle_user_prompt_submit,
    "PostToolUse": handle_post_tool_use,
    "Stop": handle_stop,
    "SessionEnd": handle_session_end,
}


def main():
    # Force UTF-8 on Windows
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")

    # Fast path: read config, check enabled
    config = _load_config()
    if not config.get("enabled", False):
        sys.exit(0)

    # Read stdin
    try:
        raw = sys.stdin.buffer.read()
        input_data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    event = input_data.get("hook_event_name", "")
    handler = HANDLERS.get(event)
    if handler is None:
        sys.exit(0)

    try:
        handler(input_data, config)
    except SystemExit:
        raise
    except Exception as e:
        # Never crash — log to stderr and exit cleanly
        print(f"[codex_companion] Error in {event}: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
