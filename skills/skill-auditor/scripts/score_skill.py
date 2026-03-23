#!/usr/bin/env python3
"""Deterministic skill auditor — scores a SKILL.md against measurable checks.

Usage:
    python score_skill.py <skill_directory>
    python score_skill.py <skill_directory> --conventions <rules_file>
    python score_skill.py <skill_directory> --max-lines 300
    python score_skill.py <skill_directory> --siblings-dir ../skills --format table

Arguments:
    skill_directory   Path to the skill folder containing SKILL.md
    --conventions     Optional path to a conventions/rules file for project-specific checks
    --max-lines       Override default SKILL.md line limit (default: 500)
    --siblings-dir    Optional path to the parent skills directory for cross-skill reference checks (O4)
    --format          Output format: 'json' (default) or 'table' for human-readable text table

Output:
    JSON object to stdout (default) or human-readable table with check results, scores, and inventory.

Errors:
    Exits with code 1 and a JSON error message if skill_directory or SKILL.md is missing.
"""

import json
import os
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter fields from SKILL.md content."""
    result = {"found": False, "name": None, "description": None, "raw": "", "other_fields": []}
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return result

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return result

    result["found"] = True
    raw_fm = "\n".join(lines[1:end_idx])
    result["raw"] = raw_fm

    # Simple YAML parsing for name and description (handles multiline with >)
    current_key = None
    current_value = []

    for line in lines[1:end_idx]:
        key_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if key_match:
            if current_key:
                val = " ".join(current_value).strip()
                if current_key == "name":
                    result["name"] = val
                elif current_key == "description":
                    result["description"] = val
                else:
                    result["other_fields"].append(current_key)
            current_key = key_match.group(1)
            val_part = key_match.group(2).strip()
            if val_part == ">" or val_part == "|":
                current_value = []
            else:
                current_value = [val_part] if val_part else []
        elif current_key and line.startswith("  "):
            current_value.append(line.strip())

    if current_key:
        val = " ".join(current_value).strip()
        if current_key == "name":
            result["name"] = val
        elif current_key == "description":
            result["description"] = val
        else:
            result["other_fields"].append(current_key)

    return result


def check_name(name: str | None) -> dict:
    """Validate the name field."""
    if not name:
        return {"pass": False, "reason": "No name field found in frontmatter"}
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
        return {"pass": False, "reason": f"Name '{name}' is not valid kebab-case (lowercase, numbers, hyphens only)"}
    if len(name) > 64:
        return {"pass": False, "reason": f"Name is {len(name)} chars, max is 64"}
    return {"pass": True, "reason": f"Valid kebab-case name: '{name}'"}


def check_description(desc: str | None) -> dict:
    """Run all deterministic description checks."""
    results = {}

    if not desc:
        return {
            "D1_format": {"pass": False, "reason": "No description field found"},
            "D2_trigger_phrases": {"pass": False, "reason": "No description to check"},
            "D3_negative_boundaries": {"pass": False, "reason": "No description to check"},
            "D6_length": {"pass": False, "reason": "No description to check"},
            "D7_what_and_when": {"pass": False, "reason": "No description to check"},
        }

    # D1: Format check — "Use when..." or third-person start
    starts_use_when = desc.lower().startswith("use when")
    has_first_person = bool(re.search(r"\bI can\b|\bI will\b|\bI help\b", desc, re.IGNORECASE))
    has_second_person = bool(re.search(r"\bYou can\b|\bYou should\b", desc, re.IGNORECASE))
    results["D1_format"] = {
        "pass": starts_use_when and not has_first_person and not has_second_person,
        "reason": (
            "Starts with 'Use when...'" if starts_use_when else "Does not start with 'Use when...'"
        ) + ("; has first-person pronouns" if has_first_person else "")
        + ("; has second-person pronouns" if has_second_person else ""),
    }

    # D2: Trigger phrases — look for quoted phrases, trigger verbs, or "Triggers:" keyword list
    trigger_indicators = re.findall(r"'[^']+?'|\"[^\"]+?\"", desc)
    action_verbs = re.findall(
        r"\b(?:says?|asks?|types?|mentions?|requests?|wants?|needs?)\s+(?:to\s+)?['\"]",
        desc, re.IGNORECASE,
    )
    # Also detect "Triggers: kw1, kw2, kw3, ..." pattern
    triggers_match = re.search(r"Triggers?:\s*(.+?)(?:\.|$)", desc, re.IGNORECASE)
    trigger_keywords = []
    if triggers_match:
        trigger_keywords = [t.strip() for t in triggers_match.group(1).split(",") if t.strip()]
    has_triggers = (
        len(trigger_indicators) >= 5
        or len(action_verbs) >= 3
        or len(trigger_keywords) >= 5
    )
    results["D2_trigger_phrases"] = {
        "pass": has_triggers,
        "reason": f"Found {len(trigger_indicators)} quoted phrases, {len(action_verbs)} trigger verb patterns, {len(trigger_keywords)} keyword triggers (need 5+ in any category)",
    }

    # D3: Negative boundaries
    has_negative = bool(re.search(
        r"do\s+not\s+use|don'?t\s+use|not\s+for|never\s+use|exclude|should\s+not\s+trigger",
        desc, re.IGNORECASE,
    ))
    results["D3_negative_boundaries"] = {
        "pass": has_negative,
        "reason": "Negative boundaries found" if has_negative else "No negative boundaries detected (e.g., 'Do NOT use for...')",
    }

    # D6: Length
    char_count = len(desc)
    results["D6_length"] = {
        "pass": char_count <= 1024,
        "reason": f"{char_count} chars"
        + (" (under 500 target)" if char_count <= 500 else " (over 500 soft target)")
        + (" EXCEEDS 1024 HARD LIMIT" if char_count > 1024 else ""),
        "char_count": char_count,
        "soft_limit": char_count <= 500,
    }

    # D7: What it does AND when to use it
    has_what = bool(re.search(
        r"(?:provid|generat|creat|analyz|build|process|extract|transform|review|audit|check|help|assist|guid)",
        desc, re.IGNORECASE,
    ))
    has_when = bool(re.search(
        r"(?:use when|trigger|activat|invoke|fire|whenever|if the user)",
        desc, re.IGNORECASE,
    ))
    results["D7_what_and_when"] = {
        "pass": has_what and has_when,
        "reason": ("Includes 'what'" if has_what else "Missing 'what it does'")
        + " and "
        + ("'when'" if has_when else "missing 'when to use it'"),
    }

    return results


def check_content_efficiency(content: str, line_limit: int) -> dict:
    """Check content efficiency metrics."""
    lines = content.split("\n")
    line_count = len(lines)

    return {
        "C2_line_count": {
            "pass": line_count <= line_limit,
            "reason": f"{line_count} lines (limit: {line_limit})",
            "line_count": line_count,
        },
    }


def inventory_directory(skill_dir: Path) -> dict:
    """Inventory the skill directory structure."""
    result = {
        "has_skill_md": (skill_dir / "SKILL.md").exists(),
        "has_references": (skill_dir / "references").is_dir(),
        "has_scripts": (skill_dir / "scripts").is_dir(),
        "reference_files": [],
        "script_files": [],
        "other_files": [],
    }

    if result["has_references"]:
        for f in sorted((skill_dir / "references").iterdir()):
            if f.is_file():
                lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
                headings = [l for l in lines if re.match(r"^#{1,3}\s+", l)]
                result["reference_files"].append({
                    "name": f.name,
                    "lines": len(lines),
                    "has_toc_headings": len(headings) >= 3,
                    "over_100_lines": len(lines) > 100,
                })

    if result["has_scripts"]:
        for f in sorted((skill_dir / "scripts").iterdir()):
            if f.is_file():
                result["script_files"].append(f.name)

    for f in sorted(skill_dir.iterdir()):
        if f.is_file() and f.name != "SKILL.md":
            result["other_files"].append(f.name)

    return result


def check_reference_depth(skill_dir: Path) -> dict:
    """Check that references are one level deep (no ref-to-ref chains)."""
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return {"pass": True, "reason": "No references/ directory", "violations": []}

    violations = []
    for f in refs_dir.iterdir():
        if not f.is_file():
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        # Look for markdown links pointing to sibling reference files
        links = re.findall(r"\[.*?\]\(((?!http)[^)]+\.md)\)", content)
        for link in links:
            # Flag if linking to another file in references/
            if not link.startswith("..") and "/" not in link:
                violations.append({"file": f.name, "links_to": link})

    return {
        "pass": len(violations) == 0,
        "reason": f"{len(violations)} ref-to-ref links found" if violations else "No ref-to-ref chains",
        "violations": violations,
    }


def check_reference_tocs(skill_dir: Path) -> dict:
    """Check that reference files >100 lines have table of contents / heading structure."""
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return {"pass": True, "reason": "No references/ directory", "flagged": []}

    flagged = []
    for f in refs_dir.iterdir():
        if not f.is_file() or not f.name.endswith(".md"):
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")
        if len(lines) > 100:
            headings = [l for l in lines if re.match(r"^#{1,3}\s+", l)]
            if len(headings) < 3:
                flagged.append({"file": f.name, "lines": len(lines), "headings": len(headings)})

    return {
        "pass": len(flagged) == 0,
        "reason": f"{len(flagged)} ref files >100 lines lack heading structure" if flagged else "All long refs have headings",
        "flagged": flagged,
    }


def check_conventions(content: str, conventions_file: str | None) -> dict:
    """Run optional project-specific convention checks."""
    if not conventions_file:
        return {"checked": False, "reason": "No conventions file specified"}

    try:
        conv_content = Path(conventions_file).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return {"checked": False, "reason": f"Conventions file not found: {conventions_file}"}

    violations = []

    # Auto-detect R conventions
    if "%>%" in conv_content or "magrittr" in conv_content.lower():
        matches = [(i + 1, line.strip()) for i, line in enumerate(content.split("\n")) if "%>%" in line]
        if matches:
            violations.append({
                "rule": "No %>% (use |> instead)",
                "occurrences": len(matches),
                "first_line": matches[0][0],
            })

    if "snake_case" in conv_content.lower():
        # Check for camelCase in R code blocks
        in_code = False
        for i, line in enumerate(content.split("\n"), 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code and re.search(r"\b[a-z]+[A-Z][a-z]+\b", line):
                # Exclude common non-R camelCase (JavaScript, etc.)
                if not any(kw in line for kw in ["className", "onClick", "useState"]):
                    violations.append({
                        "rule": "Use snake_case (not camelCase)",
                        "line": i,
                        "text": line.strip()[:80],
                    })

    return {
        "checked": True,
        "conventions_file": conventions_file,
        "violations": violations,
        "pass": len(violations) == 0,
    }


def extract_code_blocks(content: str) -> list[dict]:
    """Extract fenced code blocks with their line ranges and content.

    Returns a list of dicts: {"start": int, "end": int, "lang": str, "text": str}.
    """
    blocks = []
    lines = content.split("\n")
    in_block = False
    block_start = 0
    block_lang = ""
    block_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") and not in_block:
            in_block = True
            block_start = i
            block_lang = stripped[3:].strip().lower()
            block_lines = []
        elif stripped.startswith("```") and in_block:
            blocks.append({
                "start": block_start,
                "end": i,
                "lang": block_lang,
                "text": "\n".join(block_lines),
            })
            in_block = False
            block_lines = []
        elif in_block:
            block_lines.append(line)

    return blocks


def check_gotchas_section(content: str) -> dict:
    """G1: Check for a Gotchas/Pitfalls/Common Mistakes/Anti-Patterns heading."""
    pattern = r"^#{1,2}\s+(Gotchas|Pitfalls|Common Mistakes|Anti-Patterns)"
    match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
    if match:
        return {"pass": True, "reason": f"Found heading: '{match.group(0).strip()}'"}
    return {"pass": False, "reason": "No Gotchas/Pitfalls/Common Mistakes/Anti-Patterns heading found"}


def check_example_pairs(content: str) -> dict:
    """E1: Check for 2+ code blocks in an Examples-like section."""
    lines = content.split("\n")

    # Find the start of an examples section (use LAST match — examples are at the end)
    example_section_start = None
    example_keywords = re.compile(
        r"^#{1,3}\s+.*\b(examples?|usage|demo)\b", re.IGNORECASE,
    )
    for i, line in enumerate(lines):
        if example_keywords.match(line):
            example_section_start = i

    if example_section_start is None:
        # Fall back: count code blocks near example-related text
        blocks = extract_code_blocks(content)
        example_adjacent = 0
        example_text = re.compile(
            r"\b(input|output|happy\s+path|edge\s+case|example)\b", re.IGNORECASE,
        )
        for block in blocks:
            # Check 5 lines before the block for example-related text
            context_start = max(0, block["start"] - 5)
            context = "\n".join(lines[context_start:block["start"]])
            if example_text.search(context):
                example_adjacent += 1
        if example_adjacent >= 2:
            return {"pass": True, "reason": f"{example_adjacent} code blocks near example-related text"}
        return {
            "pass": False,
            "reason": f"No Examples section found; only {example_adjacent} code blocks near example text (need 2+)",
        }

    # Count code blocks within the examples section
    # Section extends until the next heading of equal or higher level or end of file
    # Must skip lines inside fenced code blocks (R comments like `# Input` look like h1 headings)
    heading_match = re.match(r"^(#{1,3})\s+", lines[example_section_start])
    heading_level = len(heading_match.group(1)) if heading_match else 2
    section_end = len(lines)
    in_fence = False
    for i in range(example_section_start + 1, len(lines)):
        if lines[i].strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,%d})\s+" % heading_level, lines[i])
        if m:
            section_end = i
            break

    section_text = "\n".join(lines[example_section_start:section_end])
    blocks_in_section = extract_code_blocks(section_text)
    count = len(blocks_in_section)

    if count >= 2:
        return {"pass": True, "reason": f"{count} code blocks in Examples section"}
    return {"pass": False, "reason": f"Only {count} code block(s) in Examples section (need 2+)"}


def check_convention_violations(content: str) -> dict:
    """E5: Check for %>% or = assignment inside code blocks."""
    blocks = extract_code_blocks(content)
    violations = []

    for block in blocks:
        # Only check R-like code blocks (r, R, empty lang which is often R in this project)
        lang = block["lang"]
        if lang and lang not in ("r", "r,", "{r}", "{r,"):
            continue

        block_lines = block["text"].split("\n")
        # Track cumulative paren depth across lines within each code block
        # to correctly identify named arguments in multi-line function calls
        cumulative_paren_depth = 0
        for j, line in enumerate(block_lines):
            line_num = block["start"] + 1 + j + 1  # +1 for 0-index, +1 for fence line

            # Skip comment lines (they may mention %>% in explanatory text)
            stripped = line.strip()
            if stripped.startswith("#"):
                # Still update paren depth for commented-out code? No — skip entirely.
                continue

            # Check for %>%
            if "%>%" in line:
                violations.append({
                    "type": "magrittr_pipe",
                    "line": line_num,
                    "text": stripped[:80],
                })

            # Check for = used as assignment (not inside function calls)
            # Use cumulative paren depth to handle multi-line function calls
            assignment_match = re.search(r"^\s*[a-zA-Z_.][a-zA-Z0-9_.]*\s+=\s+", line)
            if assignment_match:
                # Check both single-line depth and cumulative depth
                before_eq = line[:assignment_match.end()]
                line_paren_depth = before_eq.count("(") - before_eq.count(")")
                if cumulative_paren_depth + line_paren_depth <= 0:
                    violations.append({
                        "type": "equals_assignment",
                        "line": line_num,
                        "text": stripped[:80],
                    })

            # Update cumulative paren depth for next line
            cumulative_paren_depth += line.count("(") - line.count(")")

    if not violations:
        return {"pass": True, "reason": "No convention violations in code blocks"}
    return {
        "pass": False,
        "reason": f"{len(violations)} convention violation(s) in code blocks",
        "violations": violations,
    }


def check_sibling_references(desc: str | None, siblings_dir: str | None) -> dict:
    """O4: Check if the description references sibling skill names."""
    if not siblings_dir:
        return {"pass": None, "reason": "Skipped: --siblings-dir not provided"}

    siblings_path = Path(siblings_dir).resolve()
    if not siblings_path.is_dir():
        return {"pass": None, "reason": f"Skipped: siblings directory not found: {siblings_path}"}

    if not desc:
        return {"pass": False, "reason": "No description to check for sibling references"}

    # Discover sibling skill names from */SKILL.md frontmatter
    sibling_names = []
    for child in sorted(siblings_path.iterdir()):
        skill_file = child / "SKILL.md"
        if child.is_dir() and skill_file.exists():
            try:
                fm_content = skill_file.read_text(encoding="utf-8", errors="replace")
                fm = parse_frontmatter(fm_content)
                if fm["name"]:
                    sibling_names.append(fm["name"])
            except (OSError, IOError):
                continue

    if not sibling_names:
        return {"pass": None, "reason": "No sibling skills found in --siblings-dir"}

    desc_lower = desc.lower()
    found = [name for name in sibling_names if name.lower() in desc_lower]

    if found:
        return {"pass": True, "reason": f"References {len(found)} sibling(s): {', '.join(found)}"}
    return {
        "pass": False,
        "reason": f"No sibling skill names found in description (checked {len(sibling_names)} siblings)",
    }


def check_scripts_exist(skill_dir: Path) -> dict:
    """V2: Check if scripts/ directory exists and contains at least 1 file."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return {"pass": False, "reason": "No scripts/ directory"}

    files = [f for f in scripts_dir.iterdir() if f.is_file()]
    if not files:
        return {"pass": False, "reason": "scripts/ directory exists but is empty"}

    return {"pass": True, "reason": f"scripts/ contains {len(files)} file(s)"}


def check_description_specificity(desc: str | None) -> dict:
    """D4: Flag overly broad trigger descriptions lacking domain-specific terms."""
    if not desc:
        return {"pass": False, "reason": "No description to check"}

    # Generic stop words that don't count as domain-specific
    generic_terms = {
        "help", "assist", "data", "code", "use", "when", "the", "a", "an", "and",
        "or", "for", "to", "in", "on", "of", "with", "is", "are", "it", "this",
        "that", "user", "need", "needs", "want", "wants", "file", "files", "do",
        "does", "not", "will", "can", "should", "would", "about", "from", "by",
        "at", "be", "been", "being", "has", "have", "had", "was", "were", "may",
        "might", "must", "shall", "could", "some", "any", "all", "no", "more",
        "most", "other", "than", "then", "also", "just", "only", "very", "too",
        "so", "if", "but", "as", "up", "out", "into", "over", "such", "like",
        "new", "make", "get", "set", "work", "working", "run", "running",
        "create", "creating", "build", "building", "provide", "providing",
        "task", "tasks", "project", "projects", "tool", "tools", "thing", "things",
        "way", "ways", "time", "good", "bad", "using", "used", "ask", "asks",
        "type", "types", "mention", "mentions", "request", "requests", "says",
        "say", "trigger", "triggers", "activate", "invoke",
    }

    # Extract words from description
    words = re.findall(r"\b[a-zA-Z]{3,}\b", desc.lower())
    domain_words = [w for w in words if w not in generic_terms]
    unique_domain = set(domain_words)

    if len(unique_domain) >= 3:
        sample = sorted(list(unique_domain))[:5]
        return {
            "pass": True,
            "reason": f"{len(unique_domain)} domain-specific terms (e.g., {', '.join(sample)})",
        }
    return {
        "pass": False,
        "reason": f"Only {len(unique_domain)} domain-specific term(s) found — description is too generic",
    }


def check_description_length_min(desc: str | None) -> dict:
    """D5: Check that description is >= 100 characters to avoid Silent Skill risk."""
    if not desc:
        return {"pass": False, "reason": "No description field found"}

    length = len(desc)
    if length >= 100:
        return {"pass": True, "reason": f"Description is {length} chars (minimum 100)"}
    return {"pass": False, "reason": f"Description is only {length} chars (minimum 100 — Silent Skill risk)"}


def check_progressive_disclosure(content: str, skill_dir: Path) -> dict:
    """C3: If SKILL.md >150 lines and no references/ directory, fail."""
    line_count = len(content.split("\n"))
    has_refs = (skill_dir / "references").is_dir()

    if line_count <= 150:
        return {"pass": True, "reason": f"{line_count} lines (<=150, no references required)"}
    if has_refs:
        return {"pass": True, "reason": f"{line_count} lines with references/ directory for progressive disclosure"}
    return {
        "pass": False,
        "reason": f"{line_count} lines but no references/ directory — long skills should offload detail to references",
    }


def format_table(report: dict) -> str:
    """Format the report as a human-readable text table."""
    lines = []
    skill_name = report["skill"]
    score = report["deterministic_score"]
    checks = report["checks"]

    # Determine overall status
    pass_count, total_count = score.split("/")
    overall = "PASS" if pass_count == total_count else "FAIL"

    lines.append(f"{skill_name}  {score}  {overall}")

    for check_name, check_data in checks.items():
        if not isinstance(check_data, dict) or "pass" not in check_data:
            continue
        passed = check_data["pass"]
        if passed is None:
            status = "SKIP"
        elif passed:
            status = "PASS"
        else:
            status = "FAIL"
        reason = check_data.get("reason", "")
        lines.append(f"  {check_name:<28s} {status:<4s}  {reason}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: score_skill.py <skill_directory> [--conventions <file>] [--max-lines N] [--siblings-dir <path>] [--format json|table]"}))
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    conventions_file = None
    max_lines = 500
    siblings_dir = None
    output_format = "json"

    # Parse optional args
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--conventions" and i + 1 < len(args):
            conventions_file = args[i + 1]
            i += 2
        elif args[i] == "--max-lines" and i + 1 < len(args):
            max_lines = int(args[i + 1])
            i += 2
        elif args[i] == "--siblings-dir" and i + 1 < len(args):
            siblings_dir = args[i + 1]
            i += 2
        elif args[i] == "--format" and i + 1 < len(args):
            output_format = args[i + 1]
            if output_format not in ("json", "table"):
                print(json.dumps({"error": f"Invalid format '{output_format}', must be 'json' or 'table'"}))
                sys.exit(1)
            i += 2
        else:
            i += 1

    if not skill_dir.is_dir():
        print(json.dumps({"error": f"Skill directory not found: {skill_dir}"}))
        sys.exit(1)

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(json.dumps({"error": f"SKILL.md not found in {skill_dir}"}))
        sys.exit(1)

    content = skill_md.read_text(encoding="utf-8", errors="replace")

    # Run all checks
    frontmatter = parse_frontmatter(content)
    name_check = check_name(frontmatter["name"])
    desc_checks = check_description(frontmatter["description"])
    efficiency = check_content_efficiency(content, max_lines)
    directory = inventory_directory(skill_dir)
    ref_depth = check_reference_depth(skill_dir)
    ref_tocs = check_reference_tocs(skill_dir)
    conventions = check_conventions(content, conventions_file)

    # New checks
    gotchas = check_gotchas_section(content)
    example_pairs = check_example_pairs(content)
    conv_violations = check_convention_violations(content)
    sibling_refs = check_sibling_references(frontmatter["description"], siblings_dir)
    scripts_exist = check_scripts_exist(skill_dir)
    specificity = check_description_specificity(frontmatter["description"])
    desc_len_min = check_description_length_min(frontmatter["description"])
    progressive = check_progressive_disclosure(content, skill_dir)

    # Compute deterministic score
    deterministic_checks = {}
    deterministic_checks["name_valid"] = name_check
    deterministic_checks.update(desc_checks)
    deterministic_checks["D4_specificity"] = specificity
    deterministic_checks["D5_description_length_min"] = desc_len_min
    deterministic_checks.update(efficiency)
    deterministic_checks["C3_progressive_disclosure"] = progressive
    deterministic_checks["C4_ref_depth"] = ref_depth
    deterministic_checks["C5_ref_tocs"] = ref_tocs
    deterministic_checks["G1_gotchas_section"] = gotchas
    deterministic_checks["E1_example_pairs"] = example_pairs
    deterministic_checks["E5_convention_violations"] = conv_violations
    deterministic_checks["O4_sibling_references"] = sibling_refs
    deterministic_checks["V2_scripts_exist"] = scripts_exist

    # Score: count passes, exclude checks with pass=None (skipped)
    pass_count = sum(
        1 for v in deterministic_checks.values()
        if isinstance(v, dict) and v.get("pass") is True
    )
    total_count = sum(
        1 for v in deterministic_checks.values()
        if isinstance(v, dict) and "pass" in v and v["pass"] is not None
    )

    report = {
        "skill": skill_dir.name,
        "skill_path": str(skill_dir),
        "deterministic_score": f"{pass_count}/{total_count}",
        "checks": deterministic_checks,
        "frontmatter": {
            "found": frontmatter["found"],
            "name": frontmatter["name"],
            "description_preview": (frontmatter["description"] or "")[:200],
            "description_length": len(frontmatter["description"] or ""),
            "other_fields": frontmatter["other_fields"],
        },
        "directory": directory,
        "conventions": conventions,
    }

    if output_format == "table":
        print(format_table(report))
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
