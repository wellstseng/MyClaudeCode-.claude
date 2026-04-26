"""service.py — Codex Companion HTTP Daemon.

stdlib http.server, port 3850 (configurable).
Receives hook events, manages per-session state, triggers async Codex assessments.

啟動: pythonw service.py  (Windows 背景)
      python service.py   (前景, 看 log)
"""

from __future__ import annotations

import json
import os
import signal
import sys
import threading
import time
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

# Path setup
SERVICE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))

import state as companion_state

# Lazy import assessor (may not exist during early development)
_assessor = None


def _get_assessor():
    global _assessor
    if _assessor is None:
        try:
            import assessor as _mod
            _assessor = _mod
        except ImportError:
            pass
    return _assessor


# ─── Globals ─────────────────────────────────────────────────────────────────

_start_time = 0.0
_request_count = 0
_pending_assessments: Dict[str, threading.Thread] = {}
_shutdown_event = threading.Event()
_config: Dict[str, Any] = {}

WORKFLOW_DIR = Path.home() / ".claude" / "workflow"
PID_FILE = WORKFLOW_DIR / "companion.pid"


def _load_config() -> Dict[str, Any]:
    """Load codex_companion section from workflow config."""
    config_path = WORKFLOW_DIR / "config.json"
    try:
        full = json.loads(config_path.read_text(encoding="utf-8"))
        return full.get("codex_companion", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _write_pid():
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        pass


def _remove_pid():
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


# ─── Assessment Worker ───────────────────────────────────────────────────────


def _run_assessment(session_id: str, assessment_type: str, context: Dict[str, Any]):
    """Run Codex assessment in background thread. Result written to file."""
    try:
        mod = _get_assessor()
        if mod is None:
            companion_state.write_assessment(session_id, {
                "status": "error",
                "severity": "low",
                "category": "system",
                "summary": "Assessor module not available.",
            })
            return

        # Read companion state for context
        st = companion_state.read_state(session_id) or {}
        cwd = st.get("cwd", context.get("cwd", ""))

        result = mod.run_assessment(
            assessment_type=assessment_type,
            session_id=session_id,
            tool_trace=st.get("tool_trace", []),
            cwd=cwd,
            extra_context=context,
            config=_config,
        )

        companion_state.write_assessment(session_id, result)
        _log(f"Assessment completed: {session_id[:8]} type={assessment_type} status={result.get('status')}")

    except Exception as e:
        _log(f"Assessment error: {e}")
        companion_state.write_assessment(session_id, {
            "status": "error",
            "severity": "low",
            "category": "system",
            "summary": f"Assessment failed: {e}",
        })


def _trigger_assessment(session_id: str, assessment_type: str, context: Dict[str, Any]):
    """Spawn background thread for assessment. Non-blocking."""
    key = f"{session_id}:{assessment_type}"

    # Don't pile up duplicate assessments
    existing = _pending_assessments.get(key)
    if existing and existing.is_alive():
        _log(f"Assessment already running: {key}")
        return

    companion_state.record_checkpoint(session_id, assessment_type)

    t = threading.Thread(
        target=_run_assessment,
        args=(session_id, assessment_type, context),
        daemon=True,
        name=f"assessment-{key}",
    )
    _pending_assessments[key] = t
    t.start()


# ─── Logging ─────────────────────────────────────────────────────────────────


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[companion {ts}] {msg}", file=sys.stderr, flush=True)


# ─── Request Handler ─────────────────────────────────────────────────────────


class CompanionHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        _log(format % args)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return {}

    # ─── GET ──────────────────────────────────────────────────────────

    def do_GET(self):
        global _request_count
        _request_count += 1

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = parse_qs(parsed.query)

        if path == "/health":
            self._handle_health()
        elif path == "/assessment":
            sid = (params.get("session_id") or [""])[0]
            self._handle_get_assessment(sid)
        elif path == "/status":
            self._handle_status()
        else:
            self._send_json({"error": "not found"}, 404)

    def _handle_health(self):
        uptime = time.time() - _start_time
        self._send_json({
            "status": "ok",
            "uptime_seconds": round(uptime),
            "requests": _request_count,
            "pending_assessments": sum(1 for t in _pending_assessments.values() if t.is_alive()),
        })

    def _handle_get_assessment(self, session_id: str):
        if not session_id:
            self._send_json({"error": "session_id required"}, 400)
            return

        assessment = companion_state.read_assessment(session_id)
        if assessment is None:
            self._send_json({"status": "none"})
            return

        self._send_json({"status": "available", "assessment": assessment})

    def _handle_status(self):
        self._send_json({
            "enabled": _config.get("enabled", False),
            "model": _config.get("model", "o3"),
            "uptime_seconds": round(time.time() - _start_time),
            "requests": _request_count,
            "active_threads": sum(1 for t in _pending_assessments.values() if t.is_alive()),
        })

    # ─── POST ─────────────────────────────────────────────────────────

    def do_POST(self):
        global _request_count
        _request_count += 1

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/event":
            self._handle_event()
        elif path == "/trigger":
            self._handle_trigger()
        elif path == "/shutdown":
            self._handle_shutdown()
        else:
            self._send_json({"error": "not found"}, 404)

    def _handle_event(self):
        """Accept hook event — fire-and-forget accumulation."""
        body = self._read_body()
        session_id = body.get("session_id", "")
        if not session_id:
            self._send_json({"error": "session_id required"}, 400)
            return

        event_type = body.get("type", "unknown")

        if event_type == "session_start":
            companion_state.ensure_state(session_id, body.get("cwd", ""))
        elif event_type == "session_end":
            # Don't cleanup immediately — assessment might still be writing
            pass
        else:
            # Append tool/event to trace
            companion_state.append_event(session_id, {
                "type": event_type,
                "tool": body.get("tool_name", ""),
                "input": body.get("tool_input_summary", ""),
                "output_summary": body.get("tool_output_summary", ""),
                "path": body.get("file_path", ""),
            })

        self._send_json({"ok": True})

    def _handle_trigger(self):
        """Trigger async Codex assessment."""
        body = self._read_body()
        session_id = body.get("session_id", "")
        assessment_type = body.get("type", "turn_audit")

        if not session_id:
            self._send_json({"error": "session_id required"}, 400)
            return

        context = body.get("context", {})
        _trigger_assessment(session_id, assessment_type, context)
        self._send_json({"ok": True, "type": assessment_type})

    def _handle_shutdown(self):
        self._send_json({"ok": True, "message": "shutting down"})
        _shutdown_event.set()


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    global _config, _start_time

    # Force UTF-8 on Windows
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")

    _config = _load_config()
    port = _config.get("service_port", 3850)
    _start_time = time.time()

    # PID management
    _write_pid()

    # Graceful shutdown on signal
    def _signal_handler(sig, frame):
        _log(f"Signal {sig} received, shutting down.")
        _shutdown_event.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    server = HTTPServer(("127.0.0.1", port), CompanionHandler)
    server.timeout = 1.0  # Allow checking shutdown_event every second

    _log(f"Codex Companion service started on port {port} (pid={os.getpid()})")

    try:
        while not _shutdown_event.is_set():
            server.handle_request()
    except Exception as e:
        _log(f"Server error: {e}")
    finally:
        server.server_close()
        _remove_pid()
        _log("Service stopped.")


if __name__ == "__main__":
    main()
