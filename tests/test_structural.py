"""Layer 1: Structural validation of the supeRpowers plugin.

Deterministic checks — no LLM needed. Validates frontmatter, line counts,
plugin.json coverage, reference integrity, script validity, and agent dispatch.
"""

import json
import re
from pathlib import Path

# Valid optional frontmatter fields recognized by Claude Code skill system
RECOGNIZED_OPTIONAL_FIELDS = {
    "disable-model-invocation", "argument-hint", "user-invocable",
    "allowed-tools", "model", "effort", "context", "agent", "hooks",
    "paths", "shell",
}

from conftest import (
    AGENTS_DIR,
    COMMANDS_DIR,
    CONVENTIONS_FILE,
    HOOKS_DIR,
    PLUGIN_JSON,
    RULES_DIR,
    SKILLS_DIR,
    ROOT,
    TestSuite,
    extract_agent_mentions,
    extract_reference_pointers,
    get_agent_files,
    get_command_files,
    get_rule_files,
    get_skill_dirs,
    get_skill_frontmatters,
    load_plugin_json,
    parse_frontmatter,
)


def run_structural_tests() -> TestSuite:
    suite = TestSuite("Layer 1: Structural Validation")
    frontmatters = get_skill_frontmatters()
    skill_dirs = get_skill_dirs()
    agent_files = get_agent_files()
    rule_files = get_rule_files()
    plugin = load_plugin_json()

    # ── 1.1 Frontmatter Validation ─────────────────────────────────────────

    for skill_name, fm in frontmatters.items():
        # Has frontmatter
        suite.add(
            f"frontmatter-exists/{skill_name}",
            fm["found"],
            f"No YAML frontmatter found in {skill_name}/SKILL.md",
        )
        if not fm["found"]:
            continue

        # Has name + description, and any extra fields are recognized optional fields
        unrecognized = [f for f in fm["other_fields"] if f not in RECOGNIZED_OPTIONAL_FIELDS]
        suite.add(
            f"frontmatter-fields/{skill_name}",
            len(unrecognized) == 0 and fm["name"] is not None and fm["description"] is not None,
            f"Unrecognized fields: {unrecognized}" if unrecognized else "Missing name or description",
        )

        # Name matches directory
        suite.add(
            f"name-matches-dir/{skill_name}",
            fm["name"] == skill_name,
            f"Name '{fm['name']}' != directory '{skill_name}'",
        )

        # Description starts with "Use when"
        desc = fm["description"] or ""
        suite.add(
            f"desc-starts-use-when/{skill_name}",
            desc.startswith("Use when"),
            f"Description starts with: '{desc[:30]}...'",
        )

        # Description length: 500-1024 chars
        desc_len = len(desc)
        in_range = 500 <= desc_len <= 1024
        suite.add(
            f"desc-length/{skill_name}",
            in_range,
            f"Description is {desc_len} chars (expected 500-1024)",
            severity="FAIL" if desc_len > 1024 else "WARN",
        )

        # Has trigger phrases
        has_triggers = "Trigger" in desc
        suite.add(
            f"desc-has-triggers/{skill_name}",
            has_triggers,
            "No 'Triggers:' keyword list found in description",
        )

        # Has at least 1 "Do NOT use for" boundary
        has_boundary = "Do NOT use for" in desc or "Do NOT use" in desc
        suite.add(
            f"desc-has-boundary/{skill_name}",
            has_boundary,
            "No 'Do NOT use for' boundary found in description",
        )

    # Agent files: must have YAML frontmatter with name + description matching the file stem
    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        # Frontmatter present
        suite.add(
            f"agent-frontmatter-exists/{agent_file.stem}",
            fm["found"],
            f"Agent file {agent_file.name} is missing YAML frontmatter",
        )
        if not fm["found"]:
            continue

        # Name + description fields populated
        suite.add(
            f"agent-frontmatter-fields/{agent_file.stem}",
            fm["name"] is not None and fm["description"] is not None,
            f"Agent {agent_file.name} frontmatter missing name or description",
        )

        # Name matches file stem
        suite.add(
            f"agent-name-matches-file/{agent_file.stem}",
            fm["name"] == agent_file.stem,
            f"Agent name '{fm['name']}' != file stem '{agent_file.stem}'",
        )

    # ── 1.2 Line Count Limits ──────────────────────────────────────────────

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
        suite.add(
            f"skill-line-limit/{skill_dir.name}",
            line_count <= 300,
            f"SKILL.md is {line_count} lines (max 300)",
        )

    for agent_file in agent_files:
        line_count = len(agent_file.read_text(encoding="utf-8").splitlines())
        suite.add(
            f"agent-line-limit/{agent_file.stem}",
            line_count <= 200,
            f"Agent file is {line_count} lines (max 200)",
        )

    for rule_file in rule_files:
        line_count = len(rule_file.read_text(encoding="utf-8").splitlines())
        suite.add(
            f"rule-line-limit/{rule_file.stem}",
            line_count <= 150,
            f"Rule file is {line_count} lines (max 150)",
        )

    # ── 1.3 Command Files ──────────────────────────────────────────────────

    command_files = get_command_files()

    for cmd_file in command_files:
        content = cmd_file.read_text(encoding="utf-8")

        # Frontmatter present and parseable
        has_frontmatter = content.startswith("---\n") and "\n---\n" in content[4:]
        suite.add(
            f"command-frontmatter/{cmd_file.stem}",
            has_frontmatter,
            "Command file is missing YAML frontmatter delimited by ---",
        )

        # Description field present
        if has_frontmatter:
            fm_block = content[4:].split("\n---\n", 1)[0]
            has_description = any(
                line.strip().startswith("description:")
                for line in fm_block.splitlines()
            )
            suite.add(
                f"command-has-description/{cmd_file.stem}",
                has_description,
                "Command frontmatter missing required 'description' field",
            )

        # Line limit (200 incl. frontmatter)
        line_count = content.count("\n") + 1
        suite.add(
            f"command-line-limit/{cmd_file.stem}",
            line_count <= 200,
            f"Command file is {line_count} lines (max 200)",
        )

    # ── 1.4 Reference Integrity ────────────────────────────────────────────

    for skill_dir in skill_dirs:
        pointers = extract_reference_pointers(skill_dir)
        for ref in pointers:
            ref_path = skill_dir / ref
            suite.add(
                f"ref-exists/{skill_dir.name}/{Path(ref).name}",
                ref_path.exists(),
                f"Referenced file missing: {skill_dir.name}/{ref}",
            )

    # ── 1.5 Script Validity (syntax check only) ───────────────────────────

    for skill_dir in skill_dirs:
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.exists():
            continue
        for script in scripts_dir.iterdir():
            if script.suffix == ".py":
                try:
                    compile(script.read_text(encoding="utf-8"), str(script), "exec")
                    suite.add(f"script-syntax/{skill_dir.name}/{script.name}", True, "")
                except SyntaxError as e:
                    suite.add(
                        f"script-syntax/{skill_dir.name}/{script.name}",
                        False,
                        f"Python syntax error: {e}",
                    )
            elif script.suffix == ".R":
                # Check for common issues: missing requireNamespace guards for :: calls
                content = script.read_text(encoding="utf-8")
                # Find all pkg::func calls
                pkg_calls = set(re.findall(r"(\w+)::\w+", content))
                # Find requireNamespace guards
                guarded = set(re.findall(r'requireNamespace\("(\w+)"', content))
                # Base packages that don't need guards
                base_pkgs = {"base", "utils", "stats", "methods", "grDevices", "graphics", "tools"}
                unguarded = pkg_calls - guarded - base_pkgs
                if unguarded:
                    suite.add(
                        f"script-imports/{skill_dir.name}/{script.name}",
                        False,
                        f"Uses {', '.join(sorted(unguarded))}:: without requireNamespace() guard",
                        severity="WARN",
                    )

    # ── 1.6 Agent Dispatch Integrity ───────────────────────────────────────

    existing_agents = {f.stem for f in agent_files}
    all_mentioned_agents: set[str] = set()

    for skill_dir in skill_dirs:
        mentions = extract_agent_mentions(skill_dir)
        all_mentioned_agents.update(mentions)
        for agent_name in mentions:
            suite.add(
                f"agent-exists/{skill_dir.name}/{agent_name}",
                agent_name in existing_agents,
                f"Skill '{skill_dir.name}' references agent '{agent_name}' which doesn't exist in agents/",
            )

    # Check for orphaned agents
    for agent_name in existing_agents:
        suite.add(
            f"agent-referenced/{agent_name}",
            agent_name in all_mentioned_agents,
            f"Agent '{agent_name}' is not referenced by any skill",
            severity="WARN",
        )

    # Check for "skill-creator" phantom reference
    for skill_dir in skill_dirs:
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        desc_fm = get_skill_frontmatters().get(skill_dir.name, {})
        desc = desc_fm.get("description", "") or ""
        if "skill-creator" in content.lower() or "skill-creator" in desc.lower():
            # Check if skill-creator exists as a skill
            skill_creator_exists = (SKILLS_DIR / "skill-creator" / "SKILL.md").exists()
            suite.add(
                f"phantom-ref/skill-creator/{skill_dir.name}",
                skill_creator_exists,
                f"'{skill_dir.name}' references 'skill-creator' but no such skill exists",
                severity="WARN",
            )

    # ── 1.8 Eval Coverage ─────────────────────────────────────────────────

    for skill_dir in skill_dirs:
        if skill_dir.name == "skill-auditor":
            continue  # skill-auditor is the meta-skill, eval is different
        eval_file = skill_dir / "eval.md"
        suite.add(
            f"eval-exists/{skill_dir.name}",
            eval_file.exists(),
            f"No eval.md found in {skill_dir.name}/",
        )
        if eval_file.exists():
            eval_content = eval_file.read_text(encoding="utf-8")

            # Check for adversarial cases
            has_adversarial = "adversarial" in eval_content.lower() or "Adversarial" in eval_content
            suite.add(
                f"eval-has-adversarial/{skill_dir.name}",
                has_adversarial,
                "eval.md has no adversarial test cases",
                severity="WARN",
            )

            # Check for multiple boundary tests (>=2)
            boundary_count = len(re.findall(r"boundary\s*(?:→|->|test)", eval_content, re.IGNORECASE))
            suite.add(
                f"eval-boundary-count/{skill_dir.name}",
                boundary_count >= 2,
                f"Only {boundary_count} boundary test(s) (need ≥2)",
                severity="WARN",
            )

    return suite


if __name__ == "__main__":
    suite = run_structural_tests()
    suite.print_report()
