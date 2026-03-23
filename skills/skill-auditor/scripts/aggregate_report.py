#!/usr/bin/env python
"""Compile multiple score_skill.py JSON outputs into a markdown gap report.

Usage:
    python aggregate_report.py <json-dir> [--output <file>]

Reads all .json files in <json-dir> (each from a score_skill.py run), recounts
passes/fails from the checks dict, groups by rubric section, and generates a
markdown report with summary table, common failures, and per-skill details.

If --output is provided, writes to file. Otherwise prints to stdout.
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# Rubric sections and their check ID prefixes
SECTIONS = ["D", "C", "G", "E", "V", "O", "T"]
SECTION_TOTALS = {"D": 7, "C": 7, "G": 6, "E": 5, "V": 5, "O": 4, "T": 4}

# Human-readable section names for the failure table
SECTION_NAMES = {
    "D": "Description Quality",
    "C": "Content Efficiency",
    "G": "Gotchas & Failure Prevention",
    "E": "Examples Quality",
    "V": "Scripts & Verification",
    "O": "Multi-Skill Orchestration",
    "T": "Testability",
}


def load_reports(json_dir: Path) -> list:
    """Load all .json files from the directory, returning parsed report dicts."""
    reports = []
    for f in sorted(json_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            if "checks" in data and "skill" in data:
                reports.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return reports


def classify_check(check_id: str) -> str | None:
    """Return the section letter for a check ID, or None if unrecognized."""
    for section in SECTIONS:
        if check_id.upper().startswith(section):
            return section
    return None


def recount_checks(checks: dict) -> dict:
    """Recount passes/fails per section from raw checks dict."""
    section_scores = {s: {"passed": 0, "failed": 0, "scored": 0} for s in SECTIONS}
    check_results = {}

    for check_id, check_data in checks.items():
        if not isinstance(check_data, dict) or "pass" not in check_data:
            continue
        section = classify_check(check_id)
        if section is None:
            continue
        passed = bool(check_data["pass"])
        check_results[check_id] = {
            "pass": passed,
            "reason": check_data.get("reason", ""),
            "section": section,
        }
        section_scores[section]["scored"] += 1
        if passed:
            section_scores[section]["passed"] += 1
        else:
            section_scores[section]["failed"] += 1

    return {"section_scores": section_scores, "check_results": check_results}


def format_section_score(scores: dict, section: str) -> str:
    """Format a section score as 'X/Y' or '-' if not scored."""
    s = scores[section]
    if s["scored"] == 0:
        return "-"
    return f"{s['passed']}/{s['scored']}"


def generate_report(reports: list) -> str:
    """Generate the full markdown report."""
    lines = []
    lines.append("# Skill Audit — Gap Report")
    lines.append("")
    lines.append(f"**Date:** {date.today().isoformat()}")
    lines.append(f"**Skills:** {len(reports)} scored")
    lines.append("")

    # Recount all reports
    skill_data = []
    all_failures = Counter()

    for report in reports:
        recounted = recount_checks(report["checks"])
        total_passed = sum(s["passed"] for s in recounted["section_scores"].values())
        total_scored = sum(s["scored"] for s in recounted["section_scores"].values())
        skill_data.append({
            "name": report["skill"],
            "section_scores": recounted["section_scores"],
            "check_results": recounted["check_results"],
            "total_passed": total_passed,
            "total_scored": total_scored,
        })
        for check_id, result in recounted["check_results"].items():
            if not result["pass"]:
                all_failures[check_id] += 1

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Skill | Score | D | C | G | E | V | O | T |")
    lines.append("|-------|-------|---|---|---|---|---|---|---|")

    for sd in sorted(skill_data, key=lambda x: x["name"]):
        score_str = f"{sd['total_passed']}/{sd['total_scored']}"
        section_strs = [format_section_score(sd["section_scores"], s) for s in SECTIONS]
        lines.append(f"| {sd['name']} | {score_str} | {' | '.join(section_strs)} |")

    lines.append("")

    # Most common failures
    lines.append("## Most Common Failures")
    lines.append("")
    if all_failures:
        lines.append("| Check | # Failing | Description |")
        lines.append("|-------|-----------|-------------|")

        for check_id, count in all_failures.most_common():
            # Find first reason from any failing skill
            desc = ""
            for sd in skill_data:
                cr = sd["check_results"].get(check_id)
                if cr and not cr["pass"]:
                    desc = cr["reason"][:80]
                    break
            lines.append(f"| {check_id} | {count} | {desc} |")
    else:
        lines.append("No failures detected.")

    lines.append("")

    # Individual results
    lines.append("## Individual Results")
    lines.append("")

    for sd in sorted(skill_data, key=lambda x: x["name"]):
        lines.append(f"### {sd['name']}")
        lines.append("")
        lines.append(f"**Score:** {sd['total_passed']}/{sd['total_scored']}")
        lines.append("")

        if not sd["check_results"]:
            lines.append("No checks scored.")
            lines.append("")
            continue

        lines.append("| Check | Result | Reason |")
        lines.append("|-------|--------|--------|")

        for check_id in sorted(sd["check_results"].keys()):
            cr = sd["check_results"][check_id]
            result_str = "PASS" if cr["pass"] else "FAIL"
            reason = cr["reason"].replace("|", "\\|")[:100]
            lines.append(f"| {check_id} | {result_str} | {reason} |")

        # Note unscored checks
        scored_sections = set()
        for check_id in sd["check_results"]:
            sec = classify_check(check_id)
            if sec:
                scored_sections.add(sec)

        unscored = [s for s in SECTIONS if sd["section_scores"][s]["scored"] == 0]
        if unscored:
            lines.append("")
            lines.append(f"*Not scored:* sections {', '.join(unscored)}")

        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python aggregate_report.py <json-dir> [--output <file>]", file=sys.stderr)
        sys.exit(1)

    json_dir = Path(sys.argv[1]).resolve()
    output_file = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        else:
            i += 1

    if not json_dir.is_dir():
        print(f"Error: Directory not found: {json_dir}", file=sys.stderr)
        sys.exit(1)

    reports = load_reports(json_dir)
    if not reports:
        print(f"Error: No valid score_skill.py JSON files found in {json_dir}", file=sys.stderr)
        sys.exit(1)

    markdown = generate_report(reports)

    if output_file:
        Path(output_file).write_text(markdown, encoding="utf-8")
        print(f"Report written to {output_file}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
