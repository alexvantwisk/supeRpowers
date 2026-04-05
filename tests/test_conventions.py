"""Layer 1b: R convention compliance checks.

Scans all production content (skills/, agents/, rules/) for forbidden
patterns like %>%, = assignment, and other convention violations.
"""

import re
from pathlib import Path

from conftest import AGENTS_DIR, RULES_DIR, SKILLS_DIR, TestSuite


def _collect_md_files() -> list[Path]:
    """Collect all production markdown files (skills, agents, rules, references)."""
    files = []
    for p in SKILLS_DIR.rglob("*.md"):
        # Skip eval.md (dev-only) and anything in tests/
        if p.name == "eval.md":
            continue
        files.append(p)
    files.extend(AGENTS_DIR.glob("*.md"))
    files.extend(RULES_DIR.glob("*.md"))
    return sorted(files)


def _collect_r_scripts() -> list[Path]:
    """Collect all R scripts in skills."""
    return sorted(SKILLS_DIR.rglob("*.R"))


def _extract_r_code_blocks(content: str) -> list[tuple[int, str]]:
    """Extract R code blocks from markdown. Returns list of (start_line, code)."""
    blocks = []
    in_block = False
    block_lines: list[str] = []
    block_start = 0

    for i, line in enumerate(content.splitlines(), 1):
        if re.match(r"^```[rR]?\s*$", line) and not in_block:
            # Could be ```r or just ``` (contextual)
            in_block = True
            block_start = i
            block_lines = []
        elif line.strip() == "```" and in_block:
            in_block = False
            blocks.append((block_start, "\n".join(block_lines)))
        elif in_block:
            block_lines.append(line)

    return blocks


def _is_wrong_example_context(content: str, line_num: int) -> bool:
    """Check if a line is inside a 'WRONG' educational example."""
    lines = content.splitlines()
    # Look backwards up to 5 lines for a WRONG comment
    start = max(0, line_num - 6)
    context = "\n".join(lines[start:line_num])
    return "WRONG" in context or "wrong" in context or "DO NOT" in context or "NEVER" in context


def _is_inside_r_code_block(content: str, line_num: int) -> bool:
    """Check if a given line number is inside an R code block (```r ... ```)."""
    in_block = False
    for i, line in enumerate(content.splitlines(), 1):
        if re.match(r"^```[rR]\s*$", line):
            in_block = True
        elif line.strip() == "```" and in_block:
            in_block = False
        if i == line_num:
            return in_block
    return False


def run_convention_tests() -> TestSuite:
    suite = TestSuite("Layer 1b: Convention Compliance")

    md_files = _collect_md_files()
    r_scripts = _collect_r_scripts()

    # ── 1b.1 Forbidden %>% in production code ─────────────────────────────
    # Only flag %>% inside R code blocks (not in prose, documentation, or tables)

    magrittr_violations = []
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if "%>%" in line:
                if _is_inside_r_code_block(content, i) and not _is_wrong_example_context(content, i):
                    magrittr_violations.append(f"{f.relative_to(SKILLS_DIR.parent)}:{i}")

    for f in r_scripts:
        content = f.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if "%>%" in line:
                magrittr_violations.append(f"{f.relative_to(SKILLS_DIR.parent)}:{i}")

    suite.add(
        "no-magrittr-pipe",
        len(magrittr_violations) == 0,
        f"Found %>% at: {', '.join(magrittr_violations[:5])}"
        + (f" (+{len(magrittr_violations) - 5} more)" if len(magrittr_violations) > 5 else ""),
    )

    # ── 1b.2 Forbidden = assignment in R code blocks ─────────────────────

    # Only check inside R code blocks. Exclude:
    # - Function args: foo(x = 1), function(x = default)
    # - == / != / <= / >= comparisons
    # - Lines inside WRONG examples
    # - Lines where = is clearly inside parentheses (named args)
    assignment_violations = []

    for f in md_files:
        content = f.read_text(encoding="utf-8")
        for block_start, block in _extract_r_code_blocks(content):
            if _is_wrong_example_context(content, block_start):
                continue
            # Track cumulative paren depth across lines in the block
            paren_depth = 0
            for j, line in enumerate(block.splitlines(), block_start + 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                # If we're inside unclosed parens from a previous line, this is a continuation
                if paren_depth > 0:
                    paren_depth += line.count("(") - line.count(")")
                    continue
                # Must be a top-level assignment: identifier = value at start of line
                match = re.match(r"^(\w[\w.]*)\s*=\s+", stripped)
                if match:
                    # Count open/close parens on this line before the =
                    eq_idx = stripped.index("=")
                    before_eq = stripped[:eq_idx]
                    local_depth = before_eq.count("(") - before_eq.count(")")
                    if local_depth <= 0:
                        assignment_violations.append(f"{f.relative_to(SKILLS_DIR.parent)}:{j}")
                # Update paren depth for multi-line expressions
                paren_depth += line.count("(") - line.count(")")

    suite.add(
        "no-equals-assignment-in-codeblocks",
        len(assignment_violations) == 0,
        f"Found = assignment at: {', '.join(assignment_violations[:5])}"
        + (f" (+{len(assignment_violations) - 5} more)" if len(assignment_violations) > 5 else ""),
        severity="WARN",
    )

    # ── 1b.3 Check R scripts use <- for assignment ────────────────────────

    for f in r_scripts:
        content = f.read_text(encoding="utf-8")
        # Track paren depth to detect named args in multi-line calls
        paren_depth = 0
        top_level_eq = []
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if paren_depth > 0:
                # Inside a multi-line function call — = here is named arg
                paren_depth += line.count("(") - line.count(")")
                continue
            if re.match(r"^\w[\w.]*\s*=\s+", stripped):
                # Check if = is before any open paren on this line
                eq_idx = stripped.index("=")
                before_eq = stripped[:eq_idx]
                if before_eq.count("(") <= before_eq.count(")"):
                    top_level_eq.append(i)
            paren_depth += line.count("(") - line.count(")")

        suite.add(
            f"r-script-assignment/{f.relative_to(SKILLS_DIR)}",
            len(top_level_eq) == 0,
            f"Uses = assignment on line(s): {top_level_eq[:3]}",
            severity="WARN",
        )

    # ── 1b.4 Base pipe |> used consistently ──────────────────────────────

    for f in r_scripts:
        content = f.read_text(encoding="utf-8")
        if "%>%" in content:
            suite.add(
                f"r-script-base-pipe/{f.relative_to(SKILLS_DIR)}",
                False,
                "R script uses %>% instead of |>",
            )

    # ── 1b.5 Double quotes preferred for strings in R scripts ─────────────

    single_quote_violations = []
    for f in r_scripts:
        content = f.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Find single-quoted strings not inside double quotes
            # Simple heuristic: standalone 'string' not preceded by a word char (contractions)
            if re.search(r"(?<!\w)'[^']+?'", stripped):
                # Exclude format specifiers like '%s' and comments
                if not re.search(r"'%[sd]'", stripped):
                    single_quote_violations.append(f"{f.relative_to(SKILLS_DIR)}:{i}")

    suite.add(
        "r-scripts-double-quotes",
        len(single_quote_violations) == 0,
        f"Single-quoted strings at: {', '.join(single_quote_violations[:5])}"
        + (f" (+{len(single_quote_violations) - 5} more)" if len(single_quote_violations) > 5 else ""),
        severity="WARN",
    )

    return suite


if __name__ == "__main__":
    suite = run_convention_tests()
    suite.print_report()
