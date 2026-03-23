#!/usr/bin/env python
"""Post-batch validation — checks all SKILL.md files meet quality constraints.

Usage:
    python verify_batch.py <skill-dir-or-skills-root> [--all] [--max-lines 300] [--conventions <file>]

Modes:
    Single skill: python verify_batch.py skills/r-stats --max-lines 300
    All skills:   python verify_batch.py skills/ --all --max-lines 300

Output:
    Human-readable pass/fail summary table. Exit code 0 if all pass, 1 if any fail.
"""

import re
import sys
from pathlib import Path


def parse_frontmatter_fields(content: str) -> dict:
    """Check whether frontmatter contains name and description fields."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {"found": False, "has_name": False, "has_description": False}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {"found": False, "has_name": False, "has_description": False}

    fm_block = "\n".join(lines[1:end_idx])
    return {
        "found": True,
        "has_name": bool(re.search(r"^name:", fm_block, re.MULTILINE)),
        "has_description": bool(re.search(r"^description:", fm_block, re.MULTILINE)),
    }


def has_gotchas_heading(content: str) -> bool:
    """Check for a Gotchas/Pitfalls heading (case-insensitive)."""
    return bool(re.search(r"^#{1,3}\s+(?:gotchas|pitfalls|common\s+mistakes)", content, re.IGNORECASE | re.MULTILINE))


def has_pipe_violations(content: str) -> bool:
    """Check for %>% in code blocks, excluding gotcha table warnings."""
    in_code = False
    in_gotcha = False
    for line in content.split("\n"):
        heading_match = re.match(r"^#{1,3}\s+(.*)", line)
        if heading_match:
            heading_text = heading_match.group(1).strip().lower()
            in_gotcha = any(w in heading_text for w in ("gotcha", "pitfall", "common mistake"))
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code and not in_gotcha and "%>%" in line:
            return True
    return False


def check_snake_case(content: str) -> bool:
    """Return True if camelCase violations found in code blocks."""
    in_code = False
    for line in content.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code and re.search(r"\b[a-z]+[A-Z][a-z]+\b", line):
            if not any(kw in line for kw in ("className", "onClick", "useState")):
                return True
    return False


def validate_skill(skill_dir: Path, max_lines: int, conventions_file: str | None) -> dict:
    """Validate a single SKILL.md and return results dict."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"name": skill_dir.name, "error": "SKILL.md not found"}

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    line_count = len(content.split("\n"))
    fm = parse_frontmatter_fields(content)
    fm_ok = fm["found"] and fm["has_name"] and fm["has_description"]
    gotchas_ok = has_gotchas_heading(content)
    pipe_ok = not has_pipe_violations(content)
    lines_ok = line_count <= max_lines

    failures = []
    if not lines_ok:
        failures.append("line count")
    if not fm_ok:
        failures.append("frontmatter")
    if not gotchas_ok:
        failures.append("gotchas")
    if not pipe_ok:
        failures.append("%>%")

    snake_ok = True
    if conventions_file:
        try:
            conv = Path(conventions_file).read_text(encoding="utf-8", errors="replace")
            if "snake_case" in conv.lower() and check_snake_case(content):
                snake_ok = False
                failures.append("snake_case")
        except FileNotFoundError:
            pass

    return {
        "name": skill_dir.name,
        "lines": line_count,
        "fm_ok": fm_ok,
        "gotchas_ok": gotchas_ok,
        "pipe_ok": pipe_ok,
        "snake_ok": snake_ok,
        "lines_ok": lines_ok,
        "passed": len(failures) == 0,
        "failures": failures,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_batch.py <skill-dir-or-skills-root> [--all] [--max-lines 300] [--conventions <file>]")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()
    scan_all = "--all" in sys.argv
    max_lines = 300
    conventions_file = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--max-lines" and i + 1 < len(args):
            max_lines = int(args[i + 1])
            i += 2
        elif args[i] == "--conventions" and i + 1 < len(args):
            conventions_file = args[i + 1]
            i += 2
        elif args[i] == "--all":
            i += 1
        else:
            i += 1

    # Determine skill directories to check
    if scan_all:
        skill_dirs = sorted(d for d in target.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    else:
        if (target / "SKILL.md").exists():
            skill_dirs = [target]
        else:
            print(f"Error: No SKILL.md found in {target}")
            sys.exit(1)

    if not skill_dirs:
        print(f"Error: No skill directories found in {target}")
        sys.exit(1)

    results = [validate_skill(d, max_lines, conventions_file) for d in skill_dirs]

    # Print summary table
    name_w = max(len(r["name"]) for r in results)
    name_w = max(name_w, len("Skill"))

    header = f"{'Skill':<{name_w}}  Lines  FM   Gotchas  %>%   Status"
    print(header)
    print("-" * len(header))

    any_fail = False
    for r in results:
        if "error" in r:
            print(f"{r['name']:<{name_w}}  -      -    -        -     ERROR ({r['error']})")
            any_fail = True
            continue
        fm_str = "OK" if r["fm_ok"] else "FAIL"
        gotchas_str = "OK" if r["gotchas_ok"] else "FAIL"
        pipe_str = "OK" if r["pipe_ok"] else "FAIL"
        if r["passed"]:
            status = "PASS"
        else:
            any_fail = True
            status = "FAIL (" + ", ".join(r["failures"]) + ")"
        print(f"{r['name']:<{name_w}}  {r['lines']:>5}  {fm_str:<4} {gotchas_str:<8} {pipe_str:<5} {status}")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
