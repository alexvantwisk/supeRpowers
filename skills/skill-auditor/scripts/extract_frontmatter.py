#!/usr/bin/env python
"""Extract sibling skill descriptions for orchestration analysis.

Usage:
    python extract_frontmatter.py <skills-root-dir>

Walks <skills-root>/*/SKILL.md, parses YAML frontmatter, extracts name and
description, computes pairwise keyword overlap, and flags pairs with >30%
shared words as potential territory conflicts.

Output:
    JSON to stdout with "skills" and "overlap_warnings" arrays.
"""

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract name and description from YAML frontmatter (regex-based, handles > multiline)."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {"name": None, "description": None}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {"name": None, "description": None}

    result = {"name": None, "description": None}
    current_key = None
    current_value = []

    for line in lines[1:end_idx]:
        key_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if key_match:
            if current_key in ("name", "description"):
                result[current_key] = " ".join(current_value).strip()
            current_key = key_match.group(1)
            val_part = key_match.group(2).strip()
            if val_part in (">", "|"):
                current_value = []
            else:
                current_value = [val_part] if val_part else []
        elif current_key and line.startswith("  "):
            current_value.append(line.strip())

    if current_key in ("name", "description"):
        result[current_key] = " ".join(current_value).strip()

    return result


def tokenize(text: str) -> set:
    """Split text into lowercase words, filtering short/common stopwords."""
    stopwords = {
        "a", "an", "the", "and", "or", "for", "to", "in", "of", "is", "it",
        "on", "by", "at", "as", "do", "if", "be", "use", "when", "not", "no",
        "this", "that", "with", "from", "are", "was", "has", "have", "will",
        "can", "may", "should", "would", "could", "been", "being", "its",
    }
    words = set(re.findall(r"[a-z]{3,}", text.lower()))
    return words - stopwords


def compute_overlap(words_a: set, words_b: set) -> tuple:
    """Return (overlap_pct, shared_words) between two word sets."""
    if not words_a or not words_b:
        return (0, [])
    shared = words_a & words_b
    smaller = min(len(words_a), len(words_b))
    pct = round(len(shared) / smaller * 100) if smaller > 0 else 0
    return (pct, sorted(shared))


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_frontmatter.py <skills-root-dir>", file=sys.stderr)
        sys.exit(1)

    skills_root = Path(sys.argv[1]).resolve()
    if not skills_root.is_dir():
        print(json.dumps({"error": f"Directory not found: {skills_root}"}))
        sys.exit(1)

    skills = []
    for skill_dir in sorted(skills_root.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        if fm["name"] or fm["description"]:
            skills.append({
                "name": fm["name"] or skill_dir.name,
                "description": fm["description"] or "",
            })

    # Compute pairwise overlap
    overlap_warnings = []
    for i in range(len(skills)):
        words_i = tokenize(skills[i]["description"])
        for j in range(i + 1, len(skills)):
            words_j = tokenize(skills[j]["description"])
            pct, shared = compute_overlap(words_i, words_j)
            if pct > 30:
                overlap_warnings.append({
                    "skill_a": skills[i]["name"],
                    "skill_b": skills[j]["name"],
                    "overlap_pct": pct,
                    "shared_words": shared,
                })

    output = {"skills": skills, "overlap_warnings": overlap_warnings}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
