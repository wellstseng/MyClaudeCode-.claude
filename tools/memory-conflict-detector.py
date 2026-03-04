#!/usr/bin/env python3
"""
memory-conflict-detector.py — Atomic Memory Conflict Detection (v2.1 Sprint 2)

掃描所有活躍 atom，透過向量相似度找出疑似衝突對，
再用本地 LLM (qwen3:1.7b) 判定 AGREE/CONTRADICT/EXTEND/UNRELATED。

Session-end 離線路徑，不在 hook timeout 內執行。

Usage:
    python memory-conflict-detector.py                  # 全掃描
    python memory-conflict-detector.py --atom X         # 只掃 atom X 的衝突
    python memory-conflict-detector.py --dry-run        # 不呼叫 LLM，只列 candidate pairs
    python memory-conflict-detector.py --json           # JSON 輸出
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CLAUDE_DIR = Path.home() / ".claude"
AUDIT_LOG = CLAUDE_DIR / "memory" / "_vectordb" / "audit.log"

# Confidence ranking for arbitration
CONF_RANK = {"[固]": 3, "[觀]": 2, "[臨]": 1}

# ─── Atom Discovery (lightweight, no dependency on memory-audit.py) ──────────

META_RE = re.compile(r"^-\s+([\w-]+):\s*(.+)$")
SKIP_FILES = {"MEMORY.md", "_CHANGELOG.md", "_CHANGELOG_ARCHIVE.md"}
SKIP_PREFIXES = ("SPEC_", "_")
BULLET_RE = re.compile(r"^- \[([固觀臨])\]\s*(.+)")


def discover_layers() -> List[Tuple[str, Path]]:
    """Discover global + project memory layers."""
    layers = []
    global_mem = CLAUDE_DIR / "memory"
    if global_mem.is_dir():
        layers.append(("global", global_mem))
    projects_dir = CLAUDE_DIR / "projects"
    if projects_dir.is_dir():
        for proj_dir in sorted(projects_dir.iterdir()):
            if proj_dir.is_dir():
                mem_dir = proj_dir / "memory"
                if mem_dir.is_dir():
                    layers.append((f"project:{proj_dir.name}", mem_dir))
    return layers


def discover_atoms(layers: List[Tuple[str, Path]]) -> List[Tuple[str, Path, str]]:
    """Find atom files. Returns [(layer, path, atom_name), ...]."""
    atoms = []
    for layer_name, mem_dir in layers:
        for md_file in sorted(mem_dir.glob("*.md")):
            if md_file.name in SKIP_FILES:
                continue
            if any(md_file.name.startswith(p) for p in SKIP_PREFIXES):
                continue
            atoms.append((layer_name, md_file, md_file.stem))
    return atoms


def parse_atom_meta(path: Path) -> Dict[str, Any]:
    """Extract metadata from atom file."""
    meta = {"title": "", "scope": "", "confidence": "", "last_used": "", "tags": []}
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return meta
    for line in text.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            meta["title"] = line[2:].strip()
        m = META_RE.match(line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key == "Scope":
                meta["scope"] = val
            elif key == "Confidence":
                cm = re.search(r"\[(固|觀|臨)\]", val)
                meta["confidence"] = f"[{cm.group(1)}]" if cm else val
            elif key == "Last-used":
                meta["last_used"] = val
            elif key == "Tags":
                meta["tags"] = [t.strip() for t in val.split(",") if t.strip()]
    return meta


def extract_facts(path: Path) -> List[str]:
    """Extract knowledge bullet points from atom's 知識 section."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return []

    facts = []
    in_knowledge = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip()
            in_knowledge = "知識" in section
            continue
        if in_knowledge and stripped.startswith("- "):
            # Strip confidence prefix if present
            bm = BULLET_RE.match(stripped)
            if bm:
                facts.append(bm.group(2).strip())
            else:
                facts.append(stripped[2:].strip())
    return [f for f in facts if len(f) > 10]  # Skip trivially short


# ─── Vector Service Query ────────────────────────────────────────────────────

def vector_search(query: str, top_k: int = 10, min_score: float = 0.40) -> List[Dict]:
    """Search via Memory Vector Service."""
    try:
        import urllib.parse
        params = urllib.parse.urlencode({"q": query, "top_k": top_k, "min_score": min_score})
        url = f"http://127.0.0.1:3849/search?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


# ─── LLM Conflict Classification ─────────────────────────────────────────────

def ollama_classify(fact_a: str, atom_a: str, conf_a: str,
                    fact_b: str, atom_b: str, conf_b: str,
                    model: str = "qwen3:1.7b",
                    base_url: str = "http://127.0.0.1:11434") -> str:
    """Ask LLM to classify relationship. Returns AGREE/CONTRADICT/EXTEND/UNRELATED."""
    prompt = (
        f"Classify the relationship between two knowledge facts from a memory system.\n\n"
        f"Fact A (from {atom_a}, confidence {conf_a}):\n{fact_a}\n\n"
        f"Fact B (from {atom_b}, confidence {conf_b}):\n{fact_b}\n\n"
        f"Reply with exactly one word: AGREE, CONTRADICT, EXTEND, or UNRELATED.\n"
        f"/no_think"
    )
    messages = [
        {"role": "system", "content": "You classify memory relationships. Reply with exactly one word."},
        {"role": "user", "content": prompt},
    ]
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        text = result.get("message", {}).get("content", "").strip().upper()
        # Extract classification from response
        for label in ("CONTRADICT", "EXTEND", "AGREE", "UNRELATED"):
            if label in text:
                return label
        return "UNRELATED"
    except Exception as e:
        print(f"  [LLM error] {e}", file=sys.stderr)
        return "ERROR"


# ─── Arbitration ──────────────────────────────────────────────────────────────

def arbitrate(meta_a: Dict, meta_b: Dict) -> Dict[str, Any]:
    """Determine winner for CONTRADICT pair. Returns suggestion dict."""
    scope_a = meta_a.get("scope", "")
    scope_b = meta_b.get("scope", "")
    conf_a = meta_a.get("confidence", "")
    conf_b = meta_b.get("confidence", "")
    date_a = meta_a.get("last_used", "")
    date_b = meta_b.get("last_used", "")

    reason = ""
    winner = "a"

    # Rule 1: project > global
    if "project" in scope_a and "global" in scope_b:
        winner, reason = "a", "project scope overrides global"
    elif "project" in scope_b and "global" in scope_a:
        winner, reason = "b", "project scope overrides global"
    # Rule 2: higher confidence wins
    elif CONF_RANK.get(conf_a, 0) > CONF_RANK.get(conf_b, 0):
        winner, reason = "a", f"higher confidence ({conf_a} > {conf_b})"
    elif CONF_RANK.get(conf_b, 0) > CONF_RANK.get(conf_a, 0):
        winner, reason = "b", f"higher confidence ({conf_b} > {conf_a})"
    # Rule 3: newer Last-used wins
    elif date_a > date_b:
        winner, reason = "a", f"more recent ({date_a} > {date_b})"
    elif date_b > date_a:
        winner, reason = "b", f"more recent ({date_b} > {date_a})"
    else:
        winner, reason = "a", "tie — manual review recommended"

    return {"winner": winner, "reason": reason}


# ─── Audit Log ────────────────────────────────────────────────────────────────

def write_audit(entries: List[Dict]) -> None:
    """Append conflict detection results to audit.log (JSONL)."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Main Scan Logic ─────────────────────────────────────────────────────────

def scan_conflicts(
    target_atom: Optional[str] = None,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:
    """Scan for conflicts across all active atoms.

    Strategy:
    1. Extract facts from each atom's 知識 section
    2. For each fact, vector-search for similar facts in OTHER atoms
    3. Pairs with score 0.70-0.95 = candidate conflicts
    4. LLM classifies each candidate (unless dry_run)
    """
    layers = discover_layers()
    atoms = discover_atoms(layers)

    if target_atom:
        atoms = [(l, p, n) for l, p, n in atoms if n == target_atom]
        if not atoms:
            print(f"Atom '{target_atom}' not found.", file=sys.stderr)
            return []

    # Collect all facts with their metadata
    all_facts: List[Dict[str, Any]] = []
    atom_metas: Dict[str, Dict] = {}

    for layer, path, name in atoms:
        meta = parse_atom_meta(path)
        meta["layer"] = layer
        meta["atom_name"] = name
        atom_metas[f"{layer}:{name}"] = meta

        facts = extract_facts(path)
        for fact in facts:
            all_facts.append({
                "text": fact,
                "atom_name": name,
                "layer": layer,
                "confidence": meta["confidence"],
            })

    print(f"Scanning {len(atoms)} atoms, {len(all_facts)} facts...", file=sys.stderr)

    # Find candidate pairs via vector similarity
    candidates: List[Dict] = []
    checked_pairs = set()

    for fact_info in all_facts:
        results = vector_search(fact_info["text"], top_k=5, min_score=0.60)
        for r in results:
            r_atom = r.get("atom_name", "")
            r_layer = r.get("layer", "")
            # Skip same atom
            if r_atom == fact_info["atom_name"] and r_layer == fact_info["layer"]:
                continue
            # Skip if score too high (likely same fact) or too low
            score = r.get("score", 0)
            if score > 0.95 or score < 0.60:
                continue
            # Deduplicate pair
            pair_key = tuple(sorted([
                f"{fact_info['layer']}:{fact_info['atom_name']}:{fact_info['text'][:50]}",
                f"{r_layer}:{r_atom}:{r.get('text', '')[:50]}"
            ]))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            candidates.append({
                "fact_a": fact_info["text"],
                "atom_a": fact_info["atom_name"],
                "layer_a": fact_info["layer"],
                "conf_a": fact_info["confidence"],
                "fact_b": r.get("text", ""),
                "atom_b": r_atom,
                "layer_b": r_layer,
                "conf_b": r.get("confidence", ""),
                "similarity": score,
            })

    print(f"Found {len(candidates)} candidate pairs.", file=sys.stderr)

    if dry_run:
        return candidates

    # LLM classification
    results = []
    audit_entries = []

    for i, cand in enumerate(candidates):
        print(f"  [{i+1}/{len(candidates)}] {cand['atom_a']} vs {cand['atom_b']} "
              f"(sim={cand['similarity']:.3f})...", file=sys.stderr)

        label = ollama_classify(
            cand["fact_a"], cand["atom_a"], cand["conf_a"],
            cand["fact_b"], cand["atom_b"], cand["conf_b"],
        )
        cand["classification"] = label

        if label == "CONTRADICT":
            meta_a = atom_metas.get(f"{cand['layer_a']}:{cand['atom_a']}", {})
            meta_b = atom_metas.get(f"{cand['layer_b']}:{cand['atom_b']}", {})
            arb = arbitrate(meta_a, meta_b)
            cand["arbitration"] = arb

        results.append(cand)

        audit_entries.append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "action": "conflict_scan",
            "atom_a": cand["atom_a"],
            "atom_b": cand["atom_b"],
            "similarity": round(cand["similarity"], 4),
            "classification": label,
        })

    if audit_entries:
        write_audit(audit_entries)

    return results


# ─── Output Formatting ───────────────────────────────────────────────────────

def print_report(results: List[Dict], dry_run: bool = False) -> None:
    """Print human-readable conflict report."""
    if not results:
        print("No conflicts or candidates found.")
        return

    if dry_run:
        print(f"\n=== Candidate Pairs ({len(results)}) ===\n")
        for i, r in enumerate(results, 1):
            print(f"[{i}] {r['atom_a']} ({r['layer_a']}) <-> {r['atom_b']} ({r['layer_b']})")
            print(f"    Similarity: {r['similarity']:.3f}")
            print(f"    A: {r['fact_a'][:80]}...")
            print(f"    B: {r['fact_b'][:80]}...")
            print()
        return

    contradictions = [r for r in results if r.get("classification") == "CONTRADICT"]
    extends = [r for r in results if r.get("classification") == "EXTEND"]
    agrees = [r for r in results if r.get("classification") == "AGREE"]

    print(f"\n=== Conflict Detection Report ===")
    print(f"Total pairs scanned: {len(results)}")
    print(f"  CONTRADICT: {len(contradictions)}")
    print(f"  EXTEND: {len(extends)}")
    print(f"  AGREE: {len(agrees)}")
    print(f"  UNRELATED/ERROR: {len(results) - len(contradictions) - len(extends) - len(agrees)}")

    if contradictions:
        print(f"\n--- CONTRADICTIONS ({len(contradictions)}) ---\n")
        for r in contradictions:
            arb = r.get("arbitration", {})
            winner_label = r[f"atom_{arb.get('winner', 'a')}"]
            print(f"  {r['atom_a']} vs {r['atom_b']} (sim={r['similarity']:.3f})")
            print(f"    A [{r['conf_a']}]: {r['fact_a'][:100]}")
            print(f"    B [{r['conf_b']}]: {r['fact_b'][:100]}")
            print(f"    Suggestion: keep {winner_label} ({arb.get('reason', '')})")
            print()

    if extends:
        print(f"\n--- EXTENSIONS ({len(extends)}) ---\n")
        for r in extends:
            print(f"  {r['atom_a']} extends {r['atom_b']} (sim={r['similarity']:.3f})")
            print(f"    Consider merging or adding Related link.")
            print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Atomic Memory Conflict Detector (v2.1)")
    parser.add_argument("--atom", help="Only scan conflicts for this atom")
    parser.add_argument("--dry-run", action="store_true", help="List candidates without LLM classification")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = scan_conflicts(target_atom=args.atom, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_report(results, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
