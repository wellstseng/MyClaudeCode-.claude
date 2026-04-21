#!/usr/bin/env python3
"""
snapshot-v4-atoms.py — V4 Atoms Baseline Snapshot [F13]

Reads project-registry.json, scans all project + global atoms,
outputs tests/fixtures/v4_atoms_baseline.jsonl.

Each line: {"path": "abs_path", "sha256": "hex", "metadata_fields": ["Scope", ...]}

Usage:
    python tools/snapshot-v4-atoms.py
"""

import hashlib
import json
import re
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
REGISTRY = CLAUDE_DIR / "memory" / "project-registry.json"
GLOBAL_MEMORY = CLAUDE_DIR / "memory"
OUTPUT = CLAUDE_DIR / "tests" / "fixtures" / "v4_atoms_baseline.jsonl"

# Match frontmatter-style metadata lines: "- Key: value"
_META_RE = re.compile(r"^- ([A-Za-z][\w-]*):", re.MULTILINE)


def _extract_metadata_fields(text: str) -> list:
    """Extract metadata field names from atom content."""
    return sorted(set(_META_RE.findall(text)))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _scan_atoms(mem_dir: Path) -> list:
    """Scan a memory directory for atom .md files (skip index/staging/episodic)."""
    results = []
    if not mem_dir.is_dir():
        return results

    for md in sorted(mem_dir.rglob("*.md")):
        rel = md.relative_to(mem_dir)
        parts = rel.parts

        # Skip index files, staging, episodic
        if md.name in ("MEMORY.md", "_ATOM_INDEX.md", "_INDEX.md"):
            continue
        if md.name.startswith("_"):
            continue
        if any(p.startswith("_") for p in parts[:-1]):
            continue
        if "episodic" in parts:
            continue

        try:
            text = md.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue

        results.append({
            "path": str(md).replace("\\", "/"),
            "sha256": _sha256(text),
            "metadata_fields": _extract_metadata_fields(text),
        })

    return results


def main():
    all_atoms = []

    # 1. Global atoms
    all_atoms.extend(_scan_atoms(GLOBAL_MEMORY))

    # 2. Project atoms from registry
    if REGISTRY.exists():
        try:
            registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            registry = {"projects": {}}

        for slug, info in registry.get("projects", {}).items():
            root = Path(info.get("root", ""))
            proj_mem = root / ".claude" / "memory"
            if proj_mem.is_dir() and proj_mem != GLOBAL_MEMORY:
                all_atoms.extend(_scan_atoms(proj_mem))

    # 3. Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for atom in all_atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_atoms)} atoms to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
