"""Shared fixtures and utilities for supeRpowers plugin tests."""

import json
import os
import re
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
RULES_DIR = ROOT / "rules"
HOOKS_DIR = ROOT / "hooks"
COMMANDS_DIR = ROOT / "commands"
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
CONVENTIONS_FILE = RULES_DIR / "r-conventions.md"
ROUTING_MATRIX = Path(__file__).resolve().parent / "routing_matrix.json"

# ── Frontmatter parsing (adapted from score_skill.py) ─────────────────────────


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter fields from SKILL.md content."""
    result = {
        "found": False,
        "name": None,
        "description": None,
        "raw": "",
        "other_fields": [],
    }
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

    current_key = None
    current_value: list[str] = []

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
            if val_part in (">", "|"):
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


# ── Cached loaders ─────────────────────────────────────────────────────────────


def get_skill_dirs() -> list[Path]:
    """Return sorted list of skill directories."""
    return sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def get_skill_frontmatters() -> dict[str, dict]:
    """Return {skill_name: frontmatter_dict} for all skills."""
    result = {}
    for skill_dir in get_skill_dirs():
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        result[skill_dir.name] = fm
    return result


def get_agent_files() -> list[Path]:
    """Return sorted list of agent markdown files."""
    return sorted(AGENTS_DIR.glob("*.md"))


def get_rule_files() -> list[Path]:
    """Return sorted list of rule markdown files."""
    return sorted(RULES_DIR.glob("*.md"))


def get_command_files() -> list[Path]:
    """Return sorted list of command markdown files."""
    if not COMMANDS_DIR.exists():
        return []
    return sorted(COMMANDS_DIR.glob("*.md"))


def load_plugin_json() -> dict:
    """Load and return plugin.json."""
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))


def load_routing_matrix() -> list[dict]:
    """Load the routing test matrix."""
    return json.loads(ROUTING_MATRIX.read_text(encoding="utf-8"))


def extract_reference_pointers(skill_dir: Path) -> list[str]:
    """Extract references/*.md pointers from a SKILL.md file."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    return list(set(re.findall(r"references/[\w-]+\.md", content)))


def extract_agent_mentions(skill_dir: Path) -> list[str]:
    """Extract agent names mentioned in a SKILL.md (pattern: r-<name> agent)."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    # Matches patterns like "r-code-reviewer agent", "**r-statistician** agent"
    mentions = re.findall(r"\*{0,2}(r-[\w-]+)\*{0,2}\s+agent\b", content)
    return list(set(mentions))


def extract_trigger_phrases(description: str) -> list[str]:
    """Extract trigger phrases from a skill description's Triggers: list."""
    match = re.search(r"Triggers?:\s*(.+?)(?:Do NOT|$)", description, re.DOTALL)
    if not match:
        return []
    raw = match.group(1).strip().rstrip(".")
    return [t.strip() for t in raw.split(",") if t.strip()]


def extract_negative_boundaries(description: str) -> list[dict]:
    """Extract 'Do NOT use for...' boundaries from a description."""
    boundaries = []
    for match in re.finditer(
        r"Do NOT use for\s+(.+?)\s*(?:--?|—)\s*use\s+([\w-]+)\s+instead",
        description,
    ):
        boundaries.append({
            "excluded_topic": match.group(1).strip(),
            "redirect_to": match.group(2).strip(),
        })
    return boundaries


# ── Test result container ──────────────────────────────────────────────────────


class TestResult:
    """A single test result."""

    def __init__(self, name: str, passed: bool, message: str, severity: str = "FAIL"):
        self.name = name
        self.passed = passed
        self.message = message
        self.severity = severity  # FAIL, WARN

    def __repr__(self):
        status = "PASS" if self.passed else self.severity
        return f"[{status}] {self.name}: {self.message}"


class TestSuite:
    """Collects test results for a named layer."""

    def __init__(self, name: str):
        self.name = name
        self.results: list[TestResult] = []

    def add(self, name: str, passed: bool, message: str, severity: str = "FAIL"):
        self.results.append(TestResult(name, passed, message, severity))

    @property
    def passed(self):
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self):
        return sum(1 for r in self.results if not r.passed and r.severity == "FAIL")

    @property
    def warned(self):
        return sum(1 for r in self.results if not r.passed and r.severity == "WARN")

    @property
    def total(self):
        return len(self.results)

    def print_report(self):
        print(f"\n{'=' * 60}")
        print(f"  {self.name}")
        print(f"{'=' * 60}")
        for r in self.results:
            status = "PASS" if r.passed else r.severity
            icon = "\u2713" if r.passed else ("\u26a0" if r.severity == "WARN" else "\u2717")
            print(f"  {icon} [{status}] {r.name}")
            if not r.passed:
                print(f"         {r.message}")
        print(f"\n  Result: {self.passed}/{self.total} passed", end="")
        if self.failed:
            print(f", {self.failed} failed", end="")
        if self.warned:
            print(f", {self.warned} warnings", end="")
        print()
