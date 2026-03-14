#!/usr/bin/env python3
"""Atom Health Check — 原子記憶依賴健康度檢查工具

Usage:
  python atom-health-check.py --validate-refs   檢查 Related 完整性
  python atom-health-check.py --stale-check     列出 Last-used > 60 天的 atoms
  python atom-health-check.py --report          生成完整健康報告
  python atom-health-check.py --report --json   JSON 格式輸出
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_ROOT = Path.home() / ".claude" / "memory"
SKIP_FILES = {"MEMORY.md", "SPEC_Atomic_Memory_System.md"}
SKIP_DIRS = {"_distant", "_staging", "_vectordb", "episodic"}
# Central hub atoms — skip reverse-link warnings for these
CENTRAL_HUBS = {"decisions", "spec"}


def parse_memory_index(root: Path) -> dict[str, str]:
    """Parse MEMORY.md to build alias→stem mapping (e.g. spec→SPEC_Atomic_Memory_System)."""
    index_path = root / "MEMORY.md"
    aliases = {}
    if not index_path.exists():
        return aliases
    text = index_path.read_text(encoding="utf-8")
    # Match table rows: | alias | path | ...
    for m in re.finditer(r"\|\s*(\S+)\s*\|\s*([\w/.-]+\.md)\s*\|", text):
        alias = m.group(1).strip()
        filepath = m.group(2).strip()
        stem = Path(filepath).stem
        if alias != stem:
            aliases[alias] = stem
    return aliases


def find_atoms(root: Path) -> dict[str, Path]:
    """Recursively find all .md atom files, return {name: path}."""
    atoms = {}
    for md in root.rglob("*.md"):
        if md.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in md.relative_to(root).parts):
            continue
        name = md.stem
        atoms[name] = md
    return atoms


def parse_frontmatter(path: Path) -> dict:
    """Parse atom frontmatter fields into a dict."""
    text = path.read_text(encoding="utf-8")
    fm = {}

    # Detect Claude-native frontmatter (--- delimited YAML)
    yaml_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if yaml_match:
        for line in yaml_match.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        fm["_format"] = "claude-native"
        return fm

    # Detect atom-style frontmatter (- Key: Value lines at top)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^-\s+(.+?):\s+(.+)$", line)
        if m:
            fm[m.group(1)] = m.group(2)
        elif line.startswith("##"):
            break
    fm["_format"] = "atom"
    return fm


def parse_related(fm: dict) -> list[str]:
    """Extract Related atom names from frontmatter."""
    raw = fm.get("Related", "")
    if not raw or raw.strip() == "(none)":
        return []
    names = [n.strip().removesuffix(".md") for n in raw.split(",")]
    return [n for n in names if n]


def resolve_ref(ref: str, atoms: dict[str, Path], aliases: dict[str, str]) -> str | None:
    """Resolve a Related reference to an atom name. Returns atom name or None."""
    if ref in atoms:
        return ref
    # Check if ref is a MEMORY.md alias
    if ref in aliases:
        stem = aliases[ref]
        if stem in atoms:
            return stem
        # Alias target might be in SKIP_FILES but still valid on disk
        for md in MEMORY_ROOT.rglob(f"{stem}.md"):
            return stem
    # Check reverse alias (stem mentioned but alias is canonical)
    for alias, stem in aliases.items():
        if ref == stem and alias in atoms:
            return alias
    # Last resort: check if file exists on disk (covers SKIP_FILES entries)
    for md in MEMORY_ROOT.rglob(f"{ref}.md"):
        return ref
    return None


def validate_refs(atoms: dict[str, Path], aliases: dict[str, str] | None = None) -> list[dict]:
    """Check that all Related references point to existing atoms."""
    aliases = aliases or {}
    issues = []
    for name, path in sorted(atoms.items()):
        fm = parse_frontmatter(path)
        related = parse_related(fm)
        for ref in related:
            if resolve_ref(ref, atoms, aliases) is None:
                issues.append({
                    "atom": name,
                    "missing_ref": ref,
                    "file": str(path),
                })
    return issues


def check_reverse_refs(atoms: dict[str, Path], aliases: dict[str, str] | None = None) -> list[dict]:
    """Check bidirectional Related consistency."""
    aliases = aliases or {}
    # Build adjacency with resolved names
    adj: dict[str, list[str]] = {}
    for name, path in atoms.items():
        fm = parse_frontmatter(path)
        raw_refs = parse_related(fm)
        resolved = []
        for ref in raw_refs:
            r = resolve_ref(ref, atoms, aliases)
            resolved.append(r if r else ref)
        adj[name] = resolved

    issues = []
    for name, refs in adj.items():
        for ref in refs:
            if ref in CENTRAL_HUBS:
                continue
            # Also check aliases of ref in CENTRAL_HUBS
            if ref in aliases and aliases[ref] in CENTRAL_HUBS:
                continue
            if ref in adj and name not in adj[ref]:
                # Check if name is reachable via alias
                name_aliases = [a for a, s in aliases.items() if s == name]
                if not any(a in adj.get(ref, []) for a in name_aliases):
                    issues.append({
                        "atom_a": name,
                        "atom_b": ref,
                        "direction": f"{name} → {ref} exists, but {ref} → {name} missing",
                    })
    return issues


def stale_check(atoms: dict[str, Path], days: int = 60) -> list[dict]:
    """Find atoms with Last-used older than threshold."""
    cutoff = datetime.now() - timedelta(days=days)
    stale = []
    for name, path in sorted(atoms.items()):
        fm = parse_frontmatter(path)
        last_used = fm.get("Last-used", "")
        if not last_used:
            continue
        try:
            dt = datetime.strptime(last_used.strip(), "%Y-%m-%d")
            if dt < cutoff:
                age = (datetime.now() - dt).days
                stale.append({
                    "atom": name,
                    "last_used": last_used.strip(),
                    "days_ago": age,
                    "file": str(path),
                })
        except ValueError:
            pass
    return stale


def full_report(atoms: dict[str, Path], aliases: dict[str, str] | None = None) -> dict:
    """Generate complete health report."""
    aliases = aliases or {}
    report = {
        "generated": datetime.now().isoformat(),
        "total_atoms": len(atoms),
        "aliases": aliases,
        "atoms": [],
        "broken_refs": validate_refs(atoms, aliases),
        "missing_reverse_refs": check_reverse_refs(atoms, aliases),
        "stale_atoms": stale_check(atoms),
    }

    for name, path in sorted(atoms.items()):
        fm = parse_frontmatter(path)
        related = parse_related(fm)
        entry = {
            "name": name,
            "file": str(path.relative_to(MEMORY_ROOT)),
            "format": fm.get("_format", "unknown"),
            "confidence": fm.get("Confidence", "—"),
            "last_used": fm.get("Last-used", "—"),
            "confirmations": fm.get("Confirmations", "—"),
            "related": related,
            "issues": [],
        }

        # Check for missing standard fields
        if fm.get("_format") == "atom":
            if not fm.get("Last-used"):
                entry["issues"].append("missing Last-used")
            if not fm.get("Confirmations"):
                entry["issues"].append("missing Confirmations")
            if not fm.get("Trigger"):
                entry["issues"].append("missing Trigger")
        elif fm.get("_format") == "claude-native":
            entry["issues"].append("claude-native format (no Last-used/Confirmations/Related)")

        report["atoms"].append(entry)

    return report


def print_text_report(report: dict):
    """Pretty-print the report."""
    print(f"=== Atom Health Report ({report['generated'][:10]}) ===")
    print(f"Total atoms: {report['total_atoms']}\n")

    # Per-atom status
    print("── Atom Status ──")
    for a in report["atoms"]:
        status = "✅" if not a["issues"] else "⚠️"
        related_str = ", ".join(a["related"]) if a["related"] else "(none)"
        print(f"  {status} {a['name']}")
        print(f"     File: {a['file']} | Confidence: {a['confidence']}")
        print(f"     Last-used: {a['last_used']} | Confirmations: {a['confirmations']}")
        print(f"     Related: {related_str}")
        if a["issues"]:
            print(f"     Issues: {', '.join(a['issues'])}")
        print()

    # Broken refs
    if report["broken_refs"]:
        print("── Broken References ──")
        for b in report["broken_refs"]:
            print(f"  ❌ {b['atom']} → {b['missing_ref']} (not found)")
        print()
    else:
        print("── Broken References: None ✅ ──\n")

    # Reverse refs
    if report["missing_reverse_refs"]:
        print("── Missing Reverse References ──")
        for r in report["missing_reverse_refs"]:
            print(f"  ⚠️ {r['direction']}")
        print()
    else:
        print("── Reverse References: All OK ✅ ──\n")

    # Stale
    if report["stale_atoms"]:
        print("── Stale Atoms (>60 days) ──")
        for s in report["stale_atoms"]:
            print(f"  🕐 {s['atom']} — last used {s['last_used']} ({s['days_ago']}d ago)")
        print()
    else:
        print("── Stale Atoms: None ✅ ──\n")

    # Summary
    issues_count = (
        len(report["broken_refs"])
        + len(report["missing_reverse_refs"])
        + len(report["stale_atoms"])
        + sum(1 for a in report["atoms"] if a["issues"])
    )
    if issues_count == 0:
        print("🎉 All atoms healthy!")
    else:
        print(f"⚠️ {issues_count} issue(s) found.")


def main():
    parser = argparse.ArgumentParser(description="Atom Health Check")
    parser.add_argument("--validate-refs", action="store_true", help="Check Related references exist")
    parser.add_argument("--stale-check", action="store_true", help="List atoms with Last-used > 60 days")
    parser.add_argument("--stale-days", type=int, default=60, help="Stale threshold in days (default: 60)")
    parser.add_argument("--report", action="store_true", help="Full health report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--memory-root", type=str, default=None, help="Override memory root path")
    args = parser.parse_args()

    global MEMORY_ROOT
    if args.memory_root:
        MEMORY_ROOT = Path(args.memory_root)

    if not MEMORY_ROOT.exists():
        print(f"Error: {MEMORY_ROOT} does not exist", file=sys.stderr)
        sys.exit(1)

    atoms = find_atoms(MEMORY_ROOT)
    aliases = parse_memory_index(MEMORY_ROOT)

    if not any([args.validate_refs, args.stale_check, args.report]):
        parser.print_help()
        sys.exit(0)

    if args.validate_refs:
        broken = validate_refs(atoms, aliases)
        reverse = check_reverse_refs(atoms, aliases)
        if args.json:
            print(json.dumps({"broken_refs": broken, "missing_reverse_refs": reverse}, indent=2, ensure_ascii=False))
        else:
            if broken:
                for b in broken:
                    print(f"❌ {b['atom']} → {b['missing_ref']} (not found)")
            else:
                print("✅ All Related references valid.")
            if reverse:
                print()
                for r in reverse:
                    print(f"⚠️ {r['direction']}")
            else:
                print("✅ All reverse references OK.")

    elif args.stale_check:
        stale = stale_check(atoms, args.stale_days)
        if args.json:
            print(json.dumps(stale, indent=2, ensure_ascii=False))
        elif stale:
            for s in stale:
                print(f"🕐 {s['atom']} — {s['last_used']} ({s['days_ago']}d ago)")
        else:
            print(f"✅ No atoms older than {args.stale_days} days.")

    elif args.report:
        report = full_report(atoms, aliases)
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print_text_report(report)


if __name__ == "__main__":
    main()
