#!/usr/bin/env python3
"""SessionEnd extraction worker for V2.11 response capture.

Spawned by workflow-guardian.py as a detached subprocess at SessionEnd.
Reads context from stdin (JSON), outputs results to stdout (JSON).
Survives hook timeout — runs ~60s on GTX 1050 Ti.

V2.11 changes:
- Removed per-turn extraction (SessionEnd only)
- Intent-aware prompt templates (build/debug/design/recall)
- Pattern aggregation (word overlap >40%)
- Cross-session observation (vector search)
- Simplified consolidation (confirmations count, no auto-promotion)
"""

import json
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CLAUDE_DIR = Path.home() / ".claude"
WORKFLOW_DIR = CLAUDE_DIR / "workflow"

sys.path.insert(0, str(CLAUDE_DIR / "tools"))
from ollama_client import get_client

VALID_TYPES = ("factual", "procedural", "architectural", "pitfall", "decision")


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _empty_result() -> Dict[str, Any]:
    return {
        "extracted_items": [],
        "cross_session_observations": [],
        "aggregation_suggestions": [],
    }


# ─── Transcript helpers ──────────────────────────────────────────────────────


def _cwd_to_project_slug(cwd: str) -> str:
    slug = cwd.replace(":", "-").replace("\\", "-").replace("/", "-").replace(".", "-")
    if slug:
        slug = slug[0].lower() + slug[1:]
    return slug


def _find_transcript(session_id: str, cwd: str) -> Optional[Path]:
    slug = _cwd_to_project_slug(cwd)
    candidate = CLAUDE_DIR / "projects" / slug / f"{session_id}.jsonl"
    return candidate if candidate.exists() else None


def _extract_all_assistant_texts(
    transcript_path: Path, max_chars: int = 20000
) -> List[str]:
    """Read all assistant text blocks from JSONL transcript."""
    texts = []
    total = 0
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                try:
                    obj = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "assistant":
                    continue
                content = obj.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        t = block.get("text", "")
                        if t and len(t) > 30:
                            texts.append(t)
                            total += len(t)
                if total >= max_chars:
                    break
    except (OSError, UnicodeDecodeError):
        pass
    return texts


# ─── Ollama ───────────────────────────────────────────────────────────────────


def _call_ollama(prompt: str, model: str = None, timeout: int = 120) -> str:
    try:
        client = get_client()
        # 不用 format="json" — qwen3.5 thinking mode 與 JSON constrained decoding 衝突
        return client.generate(
            prompt, model=model, timeout=timeout,
            temperature=0.1, num_predict=2048,
        )
    except Exception:
        return ""


# ─── Prompt templates ─────────────────────────────────────────────────────────

_SYSTEM_CONTEXT = (
    "你是「原子記憶系統」的知識萃取器。萃取出的知識會存入長期記憶，供未來 session 引用。\n"
    "只萃取「這個專案/環境特有的」、「下次會用到的」事實。通用程式知識不要。\n\n"
)

_FORMAT_SPEC = (
    "輸出 JSON array: [{\"content\": \"精簡事實，最多150字\", "
    "\"type\": \"factual|procedural|architectural|pitfall|decision\"}]\n\n"
    "範例（值得萃取）:\n"
    '  {"content": "rdchat Open WebUI LDAP 端點是 /api/v1/auths/ldap，用 user 欄位（非 email）", "type": "factual"}\n'
    '  {"content": "GTX 1050 Ti 跑 qwen3:1.7b generate 約 30s，qwen3-embedding embed 約 5s", "type": "factual"}\n'
    '  {"content": "LanceDB search 用 cosine metric，min_score 0.65 以下多為噪音", "type": "architectural"}\n\n'
    "範例（不要萃取）:\n"
    '  ✗ "Python 的 dict 是 hash table" → 通用知識\n'
    '  ✗ "修改了 config.py 第 43 行" → session 進度，不是知識\n'
    '  ✗ "使用 git commit 提交變更" → 常識\n\n'
)

_RULES_COMMON = (
    "規則:\n"
    "- 只萃取此專案/環境特有的具體事實（含數值、路徑、版本、錯誤碼）\n"
    "- 跳過：程式碼片段、session 進度、隨便 Google 就能查到的知識\n"
    "- 沒有值得萃取的內容就輸出 []\n"
    "- 直接輸出 JSON，不要解釋\n"
    "/no_think\n\n"
)

_PROMPT_TEMPLATES = {
    "build": (
        _SYSTEM_CONTEXT
        + "本次 session 類型：開發建構。重點關注：架構決策、工具配置、框架行為、API 特性。\n\n"
        + _FORMAT_SPEC + _RULES_COMMON
        + "Session 文字:\n{text}\n\nJSON:"
    ),
    "debug": (
        _SYSTEM_CONTEXT
        + "本次 session 類型：除錯。重點關注：根因分析、錯誤模式、誤導性症狀、環境相關的坑。\n\n"
        + _FORMAT_SPEC + _RULES_COMMON
        + "Session 文字:\n{text}\n\nJSON:"
    ),
    "design": (
        _SYSTEM_CONTEXT
        + "本次 session 類型：設計。重點關注：設計決策的理由、權衡分析、被否決的方案及原因。\n\n"
        + _FORMAT_SPEC + _RULES_COMMON
        + "Session 文字:\n{text}\n\nJSON:"
    ),
}


def _build_prompt(intent: str, text: str) -> str:
    template = _PROMPT_TEMPLATES.get(intent, _PROMPT_TEMPLATES["build"])
    return template.format(text=text[:4000])


# ─── Parse + Dedup ────────────────────────────────────────────────────────────


def _parse_llm_response(raw: str) -> List[dict]:
    if not raw:
        return []
    items = []
    try:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            items = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        for m in re.finditer(r'"content"\s*:\s*"([^"]{10,150})"', raw):
            items.append({"content": m.group(1), "type": "factual"})
    return items


def _word_overlap_score(a: str, b: str) -> float:
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def _dedup_items(
    items: List[dict], existing_queue: List[dict], threshold: float = 0.80
) -> List[dict]:
    """Validate, deduplicate, and format extracted items."""
    existing_contents = [q.get("content", "") for q in existing_queue if q.get("content")]
    results = []
    now = _now_iso()

    for item in items[:5]:
        content = item.get("content", "").strip()
        if not content or len(content) < 10:
            continue

        # Check overlap against existing queue
        skip = False
        for ec in existing_contents:
            if _word_overlap_score(content, ec) >= threshold:
                skip = True
                break
        if skip:
            continue

        # Check overlap against already-accepted results
        for r in results:
            if _word_overlap_score(content, r["content"]) >= threshold:
                skip = True
                break
        if skip:
            continue

        kt = item.get("type", "factual")
        if kt not in VALID_TYPES:
            kt = "factual"

        results.append({
            "content": content[:150],
            "classification": "[臨]",
            "knowledge_type": kt,
            "source": "session-end",
            "confirmations": 1,
            "at": now,
        })
        existing_contents.append(content)

    return results


# ─── Pattern aggregation ──────────────────────────────────────────────────────


def _check_trigger_overlap(items: List[dict]) -> List[dict]:
    """Check for overlapping topics among extracted items (n<=5, O(n^2) ok)."""
    suggestions = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            ca = items[i].get("content", "")
            cb = items[j].get("content", "")
            score = _word_overlap_score(ca, cb)
            if score > 0.40:
                suggestions.append({
                    "item_a": ca,
                    "item_b": cb,
                    "overlap_score": round(score, 2),
                })
    return suggestions


# ─── Cross-session observation ────────────────────────────────────────────────


def _cross_session_search(
    items: List[dict], session_id: str, config: Dict[str, Any]
) -> List[dict]:
    """Vector search each item for cross-session patterns."""
    vs_config = config.get("vector_search", {})
    if not vs_config.get("enabled", True):
        return []

    port = vs_config.get("service_port", 3849)
    cs_config = config.get("cross_session", {})
    min_score = cs_config.get("min_score", 0.75)
    timeout_s = cs_config.get("timeout_seconds", 5)
    current_prefix = session_id[:8] if session_id else ""

    observations = []

    for item in items:
        content = item.get("content", "")
        if not content or len(content) < 20:
            continue

        try:
            params = urllib.parse.urlencode({
                "q": content[:200],
                "top_k": 5,
                "min_score": min_score,
            })
            url = f"http://127.0.0.1:{port}/search/ranked?{params}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    results = json.loads(resp.read())
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    url = f"http://127.0.0.1:{port}/search?{params}"
                    req = urllib.request.Request(url, headers={"Accept": "application/json"})
                    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                        results = json.loads(resp.read())
                else:
                    continue

            # Count distinct sessions from episodic atoms
            session_atoms = set()
            for r in results:
                atom_name = r.get("atom_name", "")
                if "episodic" in atom_name.lower():
                    if current_prefix and current_prefix in atom_name:
                        continue
                    session_atoms.add(atom_name)
                elif atom_name:
                    session_atoms.add(f"atom:{atom_name}")

            hit_count = len(session_atoms)
            if hit_count < 2:
                continue

            # Increment confirmations (no classification change)
            item["confirmations"] = item.get("confirmations", 1) + hit_count

            obs = {
                "content": content[:80],
                "sessions_hit": hit_count,
                "matched_atoms": sorted(session_atoms),
                "suggest_promotion": hit_count >= 4,
            }

            if hit_count >= 4:
                item["promotion_hint"] = (
                    f"建議晉升 → [觀]（{hit_count} sessions 命中，需使用者確認）"
                )

            observations.append(obs)

        except Exception:
            continue  # Skip this item, try next

    return observations


# ─── Main orchestrator ────────────────────────────────────────────────────────


def run_extraction(ctx: Dict[str, Any]) -> Dict[str, Any]:
    session_id = ctx.get("session_id", "")
    cwd = ctx.get("cwd", "")
    config = ctx.get("config", {})
    knowledge_queue = ctx.get("knowledge_queue", [])
    intent = ctx.get("session_intent", "build")

    # recall sessions rarely produce new knowledge
    if intent == "recall":
        return _empty_result()

    # Find and read transcript
    transcript = _find_transcript(session_id, cwd)
    if not transcript:
        return _empty_result()

    rc = config.get("response_capture", {})
    max_chars = rc.get("session_end_max_chars", 20000)
    texts = _extract_all_assistant_texts(transcript, max_chars=max_chars)
    if not texts:
        return _empty_result()

    combined = "\n---\n".join(texts)
    if len(combined) < 50:
        return _empty_result()

    # LLM extraction with intent-aware prompt
    prompt = _build_prompt(intent, combined)
    raw = _call_ollama(prompt)
    parsed = _parse_llm_response(raw)
    if not parsed:
        return _empty_result()

    # Dedup against existing knowledge_queue (threshold 0.80)
    items = _dedup_items(parsed, knowledge_queue, threshold=0.80)
    if not items:
        return _empty_result()

    # Pattern aggregation
    aggregation = _check_trigger_overlap(items)

    # Cross-session vector search
    observations = _cross_session_search(items, session_id, config)

    return {
        "extracted_items": items,
        "cross_session_observations": observations,
        "aggregation_suggestions": aggregation,
    }


# ─── Entry point ──────────────────────────────────────────────────────────────


def main():
    try:
        # New interface: read JSON from stdin
        raw_input = sys.stdin.read()
        ctx = json.loads(raw_input)
        result = run_extraction(ctx)
        sys.stdout.write(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(f"[extract-worker] error: {e}", file=sys.stderr)
        sys.stdout.write(json.dumps(_empty_result()))


def _legacy_main():
    """Backward-compatible CLI args mode (for pre-S3A guardian)."""
    session_id = sys.argv[1]
    cwd = sys.argv[2]
    config = json.loads(sys.argv[3])

    # Read state to get knowledge_queue
    state_path = WORKFLOW_DIR / f"state-{session_id}.json"
    state = {}
    if state_path.exists():
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    ctx = {
        "session_id": session_id,
        "cwd": cwd,
        "config": config,
        "knowledge_queue": state.get("knowledge_queue", []),
        "session_intent": "build",  # legacy mode defaults to build
    }
    result = run_extraction(ctx)

    # Legacy mode: write results back to state file (same as old behavior)
    if result.get("extracted_items"):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        state["pending_extraction"] = result["extracted_items"]
        state["last_updated"] = _now_iso()
        tmp = state_path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            tmp.replace(state_path)
        except OSError:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass


if __name__ == "__main__":
    try:
        if len(sys.argv) >= 4:
            _legacy_main()
        else:
            main()
    except Exception:
        pass  # Silent failure — never block Claude Code
