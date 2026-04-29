# Migrate `r-cmd-*` Skills to Native Plugin Commands — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the 5 `r-cmd-*` workflow skills under `skills/` to native Claude Code plugin commands under `commands/`, drop the redundant `cmd-` infix, fix the broken structural-test infrastructure, and update all docs/hooks that referenced the old slash command names.

**Architecture:** Claude Code plugins natively support a `commands/` directory. Each `commands/<name>.md` file becomes a slash command `/<name>` (or `/<plugin>:<name>` if a name collision exists). The 5 workflow files are relocated from `skills/r-cmd-*/SKILL.md` to `commands/r-*.md` with a new minimal frontmatter (only `description`); the body content (Prerequisites / Progress Tracking / Steps / Abort Conditions / Examples) is preserved verbatim because it's the prompt the command will run. Old skill directories are deleted outright (pre-1.0, no installed users). Structural tests are simultaneously updated to drop the obsolete `plugin.json` `claude_code` glob-coverage section, which was blocking validation after the manifest schema migration.

**Tech Stack:** Markdown content files, Python 3.14 test suite (`tests/`), Claude Code CLI (`claude plugin validate`), Bash hook scripts.

**Naming map (locked in by the user):**

| Old skill                  | New command           | Slash invocation |
|----------------------------|-----------------------|------------------|
| `skills/r-cmd-tdd-cycle/`  | `commands/r-tdd-cycle.md`  | `/r-tdd-cycle`   |
| `skills/r-cmd-debug/`      | `commands/r-debug.md`      | `/r-debug`       |
| `skills/r-cmd-pkg-release/`| `commands/r-pkg-release.md`| `/r-pkg-release` |
| `skills/r-cmd-shiny-app/`  | `commands/r-shiny-app.md`  | `/r-shiny-app`   |
| `skills/r-cmd-analysis/`   | `commands/r-analysis.md`   | `/r-analysis`    |

**Decisions (no rework permitted unless flagged in user reply):**

- Command frontmatter: `description` only (filename drives the slash command name; `argument-hint` not needed — none of these take args).
- No `eval.md` for commands. Commands are explicit invocations, not intent-routed.
- Old `skills/r-cmd-*/` directories are deleted as part of the migration (no deprecation cycle).
- Body content of each command file is **identical** to the body of the corresponding SKILL.md, minus the YAML frontmatter block. The "Skill: r-tdd" / "Agent: r-code-reviewer" inline pointers stay — they tell Claude which skill/agent to dispatch when the command runs.
- Historical plan files under `docs/superpowers/plans/` (dated 2026-04-02 and earlier) are point-in-time records and **are not edited**. Only the 2026-04-01 design spec gets a SUPERSEDED banner.

---

## Phase 0 — Unblock Verification (Fix Structural Tests)

The current `tests/test_structural.py` reads `plugin.get("claude_code", {})` and validates that the (now-removed) `claude_code` block's globs cover every skill, agent, and rule. Since `.claude-plugin/plugin.json` no longer has that block (it isn't part of the current Claude Code plugin schema and was rejected by `claude plugin validate`), every glob-coverage test fails. This blocks `python tests/run_all.py` from being usable as a verification gate for the migration. We delete the obsolete section first.

### Task 0.1: Remove obsolete `claude_code` glob-coverage section from structural tests

**Files:**
- Modify: `tests/test_structural.py:145-179` (delete section "1.3 Plugin.json Glob Coverage")
- Modify: `tests/test_structural.py:267-283` (delete section "1.7 Hooks System" — also reads `claude_code.get("hooks")` which is gone; hook validity is verified by `claude plugin validate` instead)

- [ ] **Step 1: Open `tests/test_structural.py` and delete lines 145-179**

The block to delete starts at the comment `# ── 1.3 Plugin.json Glob Coverage ──` and ends just before `# ── 1.4 Reference Integrity ──`. Replace with nothing — section 1.4 directly follows section 1.2.

Exact lines to remove (verify with `sed -n '145,179p' tests/test_structural.py` first):

```python
    # ── 1.3 Plugin.json Glob Coverage ──────────────────────────────────────

    claude_code = plugin.get("claude_code", {})

    # Skills glob coverage
    skills_globs = claude_code.get("skills", [])
    for skill_dir in skill_dirs:
        rel_path = f"skills/{skill_dir.name}/SKILL.md"
        matched = any(fnmatch(rel_path, g) for g in skills_globs)
        suite.add(
            f"glob-covers-skill/{skill_dir.name}",
            matched,
            f"'{rel_path}' not matched by any skills glob: {skills_globs}",
        )

    # Agents glob coverage
    agents_globs = claude_code.get("agents", [])
    for agent_file in agent_files:
        rel_path = f"agents/{agent_file.name}"
        matched = any(fnmatch(rel_path, g) for g in agents_globs)
        suite.add(
            f"glob-covers-agent/{agent_file.stem}",
            matched,
            f"'{rel_path}' not matched by any agents glob: {agents_globs}",
        )

    # Rules file exists
    rules_list = claude_code.get("rules", [])
    for rule_ref in rules_list:
        rule_path = ROOT / rule_ref
        suite.add(
            f"rule-file-exists/{rule_ref}",
            rule_path.exists(),
            f"Referenced rule file does not exist: {rule_ref}",
        )

```

- [ ] **Step 2: Delete the section "1.7 Hooks System" (lines ~267-283 after the previous deletion shifts numbering)**

Exact lines to remove:

```python
    # ── 1.7 Hooks System ──────────────────────────────────────────────────

    hooks_ref = claude_code.get("hooks")
    if hooks_ref:
        hooks_path = ROOT / hooks_ref
        suite.add(
            f"hooks-config-exists",
            hooks_path.exists(),
            f"plugin.json references '{hooks_ref}' but file does not exist",
            severity="WARN",
        )
        if hooks_path.exists():
            try:
                json.loads(hooks_path.read_text(encoding="utf-8"))
                suite.add("hooks-config-valid-json", True, "")
            except json.JSONDecodeError as e:
                suite.add("hooks-config-valid-json", False, f"Invalid JSON: {e}")

```

- [ ] **Step 3: Remove the now-unused `fnmatch` import**

Search the top of `tests/test_structural.py` for `from fnmatch import fnmatch` (or `import fnmatch`) and delete that import line if it exists. Confirm with:

```bash
grep -n "fnmatch" tests/test_structural.py
```

Expected: no matches after deletion. If there are still uses elsewhere, leave the import alone.

- [ ] **Step 4: Run the test suite to confirm it now executes end-to-end**

```bash
python tests/run_all.py
```

Expected: tests run to completion (some may fail due to the 5 cmd-skills missing eval.md files — that is expected and will be resolved when those skills are deleted in later phases). The point of this step is that the suite **runs**, not that everything is green.

- [ ] **Step 5: Commit**

```bash
git add tests/test_structural.py
git commit -m "test: drop obsolete plugin.json claude_code glob-coverage tests

The claude_code wrapper was removed from .claude-plugin/plugin.json
because Claude Code's current plugin schema doesn't accept it; content
is auto-discovered from standard directories. Glob-coverage tests are
no longer meaningful, and the hook-config check is now covered by
claude plugin validate."
```

---

## Phase 1 — Pilot Migration: `r-cmd-tdd-cycle` → `/r-tdd-cycle`

This phase migrates one command end-to-end and establishes the pattern. The remaining four phases (2-5) follow the exact same shape. Do not parallelize across phases — finishing one cleanly catches mistakes before they're replicated.

### Task 1.1: Create `commands/r-tdd-cycle.md`

**Files:**
- Create: `commands/r-tdd-cycle.md`
- Read first (to copy body): `skills/r-cmd-tdd-cycle/SKILL.md`

- [ ] **Step 1: Create the `commands/` directory**

```bash
mkdir -p commands
```

- [ ] **Step 2: Write `commands/r-tdd-cycle.md` with new frontmatter + preserved body**

Frontmatter is the only thing that changes from the SKILL.md. The body — every line from `# TDD Cycle` through the end of the Examples section — is copied verbatim from `skills/r-cmd-tdd-cycle/SKILL.md`.

New frontmatter (replaces the old skill frontmatter, lines 1-11 of `skills/r-cmd-tdd-cycle/SKILL.md`):

```markdown
---
description: Guided TDD workflow — Red, Green, Refactor, Review for R packages using testthat 3e
---
```

Then append the body from `skills/r-cmd-tdd-cycle/SKILL.md` starting at the line `# TDD Cycle` through the end of file. The full file should be the new frontmatter (3 lines) + a blank line + the body (lines 13-117 of the source SKILL.md, ~105 lines).

Exact procedure:

```bash
# 1. Write the new frontmatter
cat > commands/r-tdd-cycle.md <<'EOF'
---
description: Guided TDD workflow — Red, Green, Refactor, Review for R packages using testthat 3e
---

EOF

# 2. Append the body (everything from line 13 onward of the source SKILL.md)
tail -n +13 skills/r-cmd-tdd-cycle/SKILL.md >> commands/r-tdd-cycle.md
```

- [ ] **Step 3: Verify the new file is well-formed**

```bash
head -5 commands/r-tdd-cycle.md
wc -l commands/r-tdd-cycle.md
```

Expected `head -5`:

```
---
description: Guided TDD workflow — Red, Green, Refactor, Review for R packages using testthat 3e
---

# TDD Cycle
```

Expected line count: ~110 lines (108 body lines + 4 header lines).

- [ ] **Step 4: Validate the plugin**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed` or `Validation passed with warnings` (the kebab-case warning on plugin name is unrelated and persistent). No new errors introduced. The validator should now also list the new command file under "Validating command:" (or similar).

### Task 1.2: Delete the old skill directory

**Files:**
- Delete: `skills/r-cmd-tdd-cycle/` (whole directory)

- [ ] **Step 1: Remove the old skill directory via git**

```bash
git rm -r skills/r-cmd-tdd-cycle/
```

- [ ] **Step 2: Verify the directory is gone**

```bash
ls skills/ | grep r-cmd-tdd-cycle
```

Expected: no output (empty result).

- [ ] **Step 3: Run the test suite**

```bash
python tests/run_all.py
```

Expected: one fewer eval-coverage failure than before (because `r-cmd-tdd-cycle` was missing eval.md). 4 of the original 5 cmd-skills still fail eval coverage; that's expected until phases 2-5 delete them.

- [ ] **Step 4: Commit**

```bash
git add commands/r-tdd-cycle.md
git commit -m "refactor: migrate r-cmd-tdd-cycle skill to /r-tdd-cycle command

Moves skills/r-cmd-tdd-cycle/SKILL.md to commands/r-tdd-cycle.md as a
native plugin command. Body content is unchanged; frontmatter trimmed
to a single description line. Slash invocation: /r-tdd-cycle."
```

---

## Phase 2 — Migrate `r-cmd-debug` → `/r-debug`

Same shape as Phase 1. Repeated in full so the engineer can read tasks out of order.

### Task 2.1: Create `commands/r-debug.md`

**Files:**
- Create: `commands/r-debug.md`
- Read first: `skills/r-cmd-debug/SKILL.md`

- [ ] **Step 1: Write the file**

```bash
cat > commands/r-debug.md <<'EOF'
---
description: Guided debugging workflow — reproduce, isolate, diagnose, fix, regression test, verify
---

EOF
tail -n +12 skills/r-cmd-debug/SKILL.md >> commands/r-debug.md
```

(Source frontmatter ends at line 11, so `tail -n +12` starts the body at `# Debug`.)

- [ ] **Step 2: Verify**

```bash
head -5 commands/r-debug.md
wc -l commands/r-debug.md
```

Expected `head -5`:

```
---
description: Guided debugging workflow — reproduce, isolate, diagnose, fix, regression test, verify
---

# Debug
```

Expected line count: ~102 lines.

- [ ] **Step 3: Validate**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed with warnings`. No new errors.

### Task 2.2: Delete old skill directory + commit

- [ ] **Step 1: Remove**

```bash
git rm -r skills/r-cmd-debug/
```

- [ ] **Step 2: Run tests**

```bash
python tests/run_all.py
```

Expected: 3 remaining eval-coverage failures for cmd-skills.

- [ ] **Step 3: Commit**

```bash
git add commands/r-debug.md
git commit -m "refactor: migrate r-cmd-debug skill to /r-debug command"
```

---

## Phase 3 — Migrate `r-cmd-pkg-release` → `/r-pkg-release`

### Task 3.1: Create `commands/r-pkg-release.md`

**Files:**
- Create: `commands/r-pkg-release.md`
- Read first: `skills/r-cmd-pkg-release/SKILL.md`

- [ ] **Step 1: Write the file**

```bash
cat > commands/r-pkg-release.md <<'EOF'
---
description: Guided R package release workflow — audit deps, test, document, R CMD check, version bump, review, submit
---

EOF
tail -n +13 skills/r-cmd-pkg-release/SKILL.md >> commands/r-pkg-release.md
```

(Source frontmatter ends at line 12, so `tail -n +13` starts the body at `# Package Release`.)

- [ ] **Step 2: Verify**

```bash
head -5 commands/r-pkg-release.md
wc -l commands/r-pkg-release.md
```

Expected `head -5`:

```
---
description: Guided R package release workflow — audit deps, test, document, R CMD check, version bump, review, submit
---

# Package Release
```

Expected line count: ~88 lines.

- [ ] **Step 3: Validate**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed with warnings`.

### Task 3.2: Delete + commit

- [ ] **Step 1: Remove**

```bash
git rm -r skills/r-cmd-pkg-release/
```

- [ ] **Step 2: Run tests**

```bash
python tests/run_all.py
```

Expected: 2 remaining eval-coverage failures.

- [ ] **Step 3: Commit**

```bash
git add commands/r-pkg-release.md
git commit -m "refactor: migrate r-cmd-pkg-release skill to /r-pkg-release command"
```

---

## Phase 4 — Migrate `r-cmd-shiny-app` → `/r-shiny-app`

### Task 4.1: Create `commands/r-shiny-app.md`

**Files:**
- Create: `commands/r-shiny-app.md`
- Read first: `skills/r-cmd-shiny-app/SKILL.md`

- [ ] **Step 1: Write the file**

```bash
cat > commands/r-shiny-app.md <<'EOF'
---
description: Guided Shiny app workflow — scaffold, design modules, wire reactivity, test, architecture review
---

EOF
tail -n +13 skills/r-cmd-shiny-app/SKILL.md >> commands/r-shiny-app.md
```

(Source frontmatter ends at line 12, so `tail -n +13` starts the body at `# Shiny App`.)

- [ ] **Step 2: Verify**

```bash
head -5 commands/r-shiny-app.md
wc -l commands/r-shiny-app.md
```

Expected `head -5`:

```
---
description: Guided Shiny app workflow — scaffold, design modules, wire reactivity, test, architecture review
---

# Shiny App
```

Expected line count: ~96 lines.

- [ ] **Step 3: Validate**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed with warnings`.

### Task 4.2: Delete + commit

- [ ] **Step 1: Remove**

```bash
git rm -r skills/r-cmd-shiny-app/
```

- [ ] **Step 2: Run tests**

```bash
python tests/run_all.py
```

Expected: 1 remaining eval-coverage failure.

- [ ] **Step 3: Commit**

```bash
git add commands/r-shiny-app.md
git commit -m "refactor: migrate r-cmd-shiny-app skill to /r-shiny-app command"
```

---

## Phase 5 — Migrate `r-cmd-analysis` → `/r-analysis`

### Task 5.1: Create `commands/r-analysis.md`

**Files:**
- Create: `commands/r-analysis.md`
- Read first: `skills/r-cmd-analysis/SKILL.md`

- [ ] **Step 1: Write the file**

```bash
cat > commands/r-analysis.md <<'EOF'
---
description: Guided data analysis pipeline — import, clean, explore, model, visualize, report
---

EOF
tail -n +12 skills/r-cmd-analysis/SKILL.md >> commands/r-analysis.md
```

(Source frontmatter ends at line 11, so `tail -n +12` starts the body at `# Analysis Pipeline`.)

- [ ] **Step 2: Verify**

```bash
head -5 commands/r-analysis.md
wc -l commands/r-analysis.md
```

Expected `head -5`:

```
---
description: Guided data analysis pipeline — import, clean, explore, model, visualize, report
---

# Analysis Pipeline
```

Expected line count: ~96 lines.

- [ ] **Step 3: Validate**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed with warnings`.

### Task 5.2: Delete + commit

- [ ] **Step 1: Remove**

```bash
git rm -r skills/r-cmd-analysis/
```

- [ ] **Step 2: Run tests**

```bash
python tests/run_all.py
```

Expected: zero eval-coverage failures attributable to cmd-skills (all 5 are gone). Other failures, if any, are unrelated and pre-existing.

- [ ] **Step 3: Commit**

```bash
git add commands/r-analysis.md
git commit -m "refactor: migrate r-cmd-analysis skill to /r-analysis command"
```

---

## Phase 6 — Update `hooks/session-start` to point at new command names

The session-start hook recommends `/r-cmd-*` slash commands when it detects an R project type. Those names no longer resolve. We update each reference to the new `/r-*` form.

### Task 6.1: Update hook script

**Files:**
- Modify: `hooks/session-start` (4 references)

- [ ] **Step 1: Identify the lines**

```bash
grep -n "r-cmd-" hooks/session-start
```

Expected to match lines 94, 97, 109, and 133 (numbering may have drifted; the grep gives canonical locations).

- [ ] **Step 2: Replace each occurrence**

Concrete substitutions to make (apply each via Edit tool or `sed -i ''` on macOS):

| Old text | New text |
|----------|----------|
| `/r-cmd-pkg-release` | `/r-pkg-release` |
| `/r-cmd-tdd-cycle`   | `/r-tdd-cycle`   |
| `/r-cmd-shiny-app`   | `/r-shiny-app`   |
| `/r-cmd-analysis`    | `/r-analysis`    |
| `/r-cmd-debug`       | `/r-debug`       |
| `/r-cmd-* workflow skills` | `/r-* commands` |

The last substitution updates the catch-all guidance text. Run `grep -n "r-cmd-" hooks/session-start` after editing — expected zero matches.

- [ ] **Step 3: Smoke-test the hook script**

```bash
bash hooks/session-start <<< '{}' 2>&1 | head -30
```

Expected: the script runs without error and emits its usual JSON-ish context block. Visually scan the output for any `/r-cmd-` strings — there should be none.

- [ ] **Step 4: Commit**

```bash
git add hooks/session-start
git commit -m "chore(hooks): point session-start at new /r-* command names"
```

---

## Phase 7 — Update CLAUDE.md

The project guide at `CLAUDE.md` documents the directory layout, the content formats, and the verification checklist. None of those mention `commands/` yet. Sections to update:

1. Project structure ASCII tree — add `commands/` entry
2. The "Workflow command skills" sub-bullet under Skills — remove (these are no longer skills)
3. New "Commands (`commands/*.md`)" content-format section
4. New "Adding a new command" section
5. Verification checklist — add a line for command files

### Task 7.1: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace the project structure block**

Find the block currently containing (around line 9):

```
.claude-plugin/
  plugin.json            # Plugin manifest (name, version, author, license)
hooks/                   # Session lifecycle hooks
  ...
skills/                  # Skills (SKILL.md + optional references/, scripts/, eval.md)
  Domain skills:
    r-data-analysis/       r-visualization/       r-tdd/
    ...
  Workflow command skills (user-invoked via /<name>):
    r-cmd-analysis/        r-cmd-debug/           r-cmd-pkg-release/
    r-cmd-shiny-app/       r-cmd-tdd-cycle/
  Meta skills:
    skill-auditor/
agents/                  # Shared agents (YAML frontmatter required)
  ...
```

Replace the "Workflow command skills" sub-block with a top-level `commands/` entry:

```
.claude-plugin/
  plugin.json            # Plugin manifest (name, version, author, license)
hooks/                   # Session lifecycle hooks
  hooks.json             # SessionStart hook configuration
  session-start          # R project detection script
  detect-mcp.sh          # MCP server detection helper
  run-hook.cmd           # Cross-platform wrapper
rules/                   # Foundation rules (loaded into every R conversation)
  r-conventions.md       # Base pipe |>, tidyverse-first, style guide
commands/                # Slash commands (user-invoked via /<name>)
  r-analysis.md          r-debug.md             r-pkg-release.md
  r-shiny-app.md         r-tdd-cycle.md
skills/                  # Skills (SKILL.md + optional references/, scripts/, eval.md)
  Domain skills:
    r-data-analysis/       r-visualization/       r-tdd/
    r-debugging/           r-package-dev/         r-shiny/
    r-stats/               r-clinical/            r-tables/
    r-quarto/              r-performance/         r-package-skill-generator/
    r-project-setup/       r-tidymodels/          r-targets/
    r-mcp-setup/
  Meta skills:
    skill-auditor/
agents/                  # Shared agents (YAML frontmatter required)
  r-code-reviewer.md     r-statistician.md      r-pkg-check.md
  r-shiny-architect.md   r-dependency-manager.md
docs/                    # Reference documentation (e.g. docs/superpowers/)
tests/                   # Routing, structural, and convention test suites
```

- [ ] **Step 2: Add a "Commands" content-format section**

Insert a new section between the "### Skills" and "### Agents" subsections under `## Content Formats`:

```markdown
### Commands (`commands/*.md`)

- YAML frontmatter with a single field: `description` (one-line, shown in `/` autocomplete)
- Filename (without `.md`) is the slash command name (e.g. `commands/r-tdd-cycle.md` → `/r-tdd-cycle`)
- Body is the prompt that runs when the user invokes the command
- Max 200 lines (including frontmatter)
- May reference skills and agents inline ("Skill: r-tdd", "Agent: r-code-reviewer") to delegate domain knowledge
```

- [ ] **Step 3: Add an "Adding a new command" section**

Insert between "## Adding a New Skill" and "## Adding a New Agent":

```markdown
## Adding a New Command

1. Create `commands/<name>.md` with frontmatter `description: <one-line summary>`
2. Body is the prompt that runs on `/<name>` — Prerequisites, Progress Tracking, Steps, Abort Conditions, Examples
3. Reference skills and agents inline (e.g. `**Skill:** r-tdd`) so Claude dispatches them at the right step
4. Keep under 200 lines (including frontmatter)
5. No eval.md — commands are explicit invocations, not intent-routed
```

- [ ] **Step 4: Update the verification checklist**

Replace this block:

```markdown
- [ ] No `%>%` in skills/, agents/, rules/ (excluding `eval.md` files)
- [ ] SKILL.md files are ≤300 lines with correct frontmatter
- [ ] Agent files are ≤200 lines with `name` + `description` frontmatter
- [ ] Rule files are ≤150 lines with no frontmatter
- [ ] All R code uses `<-`, `|>`, snake_case, double quotes
- [ ] `claude plugin validate .` passes (warnings acceptable)
- [ ] Tests pass: `python tests/run_all.py`
```

with:

```markdown
- [ ] No `%>%` in skills/, commands/, agents/, rules/ (excluding `eval.md` files)
- [ ] SKILL.md files are ≤300 lines with correct frontmatter
- [ ] Command files are ≤200 lines with `description` frontmatter
- [ ] Agent files are ≤200 lines with `name` + `description` frontmatter
- [ ] Rule files are ≤150 lines with no frontmatter
- [ ] All R code uses `<-`, `|>`, snake_case, double quotes
- [ ] `claude plugin validate .` passes (warnings acceptable)
- [ ] Tests pass: `python tests/run_all.py`
```

- [ ] **Step 5: Update the convention-grep hint**

Find this block (under "## R Code Conventions"):

```bash
grep -rn '%>%' skills/ agents/ rules/ --exclude=eval.md
```

Replace with:

```bash
grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md
```

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): document commands/ directory and update layout"
```

---

## Phase 8 — Update tests for command discovery

The structural test suite currently has no concept of `commands/`. We add a section that mirrors the SKILL.md frontmatter checks for command files: each must have valid YAML frontmatter with a `description` field, and each must be ≤200 lines.

### Task 8.1: Add command-file checks to test_structural.py

**Files:**
- Modify: `tests/conftest.py` (add `COMMANDS_DIR` constant + `get_command_files()`)
- Modify: `tests/test_structural.py` (add a new section "1.X Command Files")

- [ ] **Step 1: Add the command path constants to `tests/conftest.py`**

After the existing `AGENTS_DIR` / `RULES_DIR` constants near the top of the file, add:

```python
COMMANDS_DIR = ROOT / "commands"
```

After the existing `get_agent_files()` / `get_rule_files()` helpers near the bottom, add:

```python
def get_command_files() -> list[Path]:
    """Return sorted list of command markdown files."""
    if not COMMANDS_DIR.exists():
        return []
    return sorted(COMMANDS_DIR.glob("*.md"))
```

- [ ] **Step 2: Write the failing test first (TDD)**

Open `tests/test_structural.py` and add this new section after section 1.2 (rule files), before section 1.4 (Reference Integrity):

```python
    # ── 1.3 Command Files ──────────────────────────────────────────────────

    from conftest import get_command_files
    command_files = get_command_files()

    for cmd_file in command_files:
        # Frontmatter present and parseable
        content = cmd_file.read_text(encoding="utf-8")
        has_frontmatter = content.startswith("---\n") and "\n---\n" in content[4:]
        suite.add(
            f"command-frontmatter/{cmd_file.stem}",
            has_frontmatter,
            f"Command file is missing YAML frontmatter delimited by ---",
        )

        # Description field present
        if has_frontmatter:
            fm_block = content.split("\n---\n", 2)[0][4:]  # between the two --- delimiters
            has_description = any(line.strip().startswith("description:") for line in fm_block.splitlines())
            suite.add(
                f"command-has-description/{cmd_file.stem}",
                has_description,
                f"Command frontmatter missing required 'description' field",
            )

        # Line limit (200 incl. frontmatter)
        line_count = content.count("\n") + 1
        suite.add(
            f"command-line-limit/{cmd_file.stem}",
            line_count <= 200,
            f"Command file is {line_count} lines (max 200)",
        )
```

(Note: this section uses `1.3` because the old `1.3 Plugin.json Glob Coverage` was deleted in Phase 0. Adjust numbering only if other sections were also renumbered.)

- [ ] **Step 3: Run tests — confirm new checks pass for the 5 commands**

```bash
python tests/run_all.py
```

Expected: `command-frontmatter/r-tdd-cycle`, `command-has-description/r-tdd-cycle`, `command-line-limit/r-tdd-cycle` all PASS, plus the same three for the other four commands. 15 new passing checks total.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_structural.py
git commit -m "test(structural): add frontmatter/line-limit checks for commands/"
```

---

## Phase 9 — Mark old design spec as superseded

The original commands-layer spec at `docs/superpowers/specs/2026-04-01-commands-layer-design.md` was written under the (then-correct or assumed-correct) belief that plugins didn't support a `commands/` key. That premise no longer holds. We mark it superseded with a banner pointing at this plan.

### Task 9.1: Add SUPERSEDED banner to the design spec

**Files:**
- Modify: `docs/superpowers/specs/2026-04-01-commands-layer-design.md` (add banner immediately after the H1 title)

- [ ] **Step 1: Insert the banner**

Open the file. Find the existing first-level heading and the metadata block underneath:

```markdown
# Commands Layer — Workflow Skills for supeRpowers

**Date:** 2026-04-01
**Status:** Approved
**Scope:** ...
```

Replace `**Status:** Approved` with:

```markdown
**Status:** SUPERSEDED 2026-04-29 — Claude Code plugins do support a native `commands/` directory; the 5 `r-cmd-*` skills have been migrated to `commands/r-*.md`. See `docs/superpowers/plans/2026-04-29-cmd-skills-to-commands-migration.md` for the migration plan.
```

(Leave the rest of the document intact as a historical record of the original reasoning.)

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-04-01-commands-layer-design.md
git commit -m "docs: mark 2026-04-01 commands-layer spec as superseded"
```

---

## Phase 10 — Final Validation

### Task 10.1: Full validation pass

- [ ] **Step 1: Plugin validates with no errors**

```bash
claude plugin validate /Users/alexandervantwisk/Desktop/Projects/supeRpowers
```

Expected: `Validation passed with warnings`. The only acceptable warning is the kebab-case warning on the plugin name (`supeRpowers` is intentional R branding). Any other warning is a regression.

- [ ] **Step 2: Test suite is green**

```bash
python tests/run_all.py
```

Expected: 0 failures. Treat any failure as a blocker — do not proceed.

- [ ] **Step 3: Convention check is clean**

```bash
grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md
```

Expected: no matches.

- [ ] **Step 4: Confirm no lingering `r-cmd-` references in active project files**

```bash
grep -rn "r-cmd-" CLAUDE.md README.md hooks/ tests/ rules/ skills/ commands/ agents/ 2>/dev/null
```

Expected: no matches. Historical files under `docs/superpowers/specs/` and `docs/superpowers/plans/` are allowed to retain references — they are point-in-time records.

### Task 10.2: Smoke test in a fresh Claude Code session

- [ ] **Step 1: Add this directory as a marketplace (one-time)**

```bash
claude plugin marketplace add /Users/alexandervantwisk/Desktop/Projects/supeRpowers --scope user
```

(Skip if already added in a prior session.)

- [ ] **Step 2: Install the plugin**

```bash
claude plugin install supeRpowers@supeRpowers
```

- [ ] **Step 3: Open a fresh session in an R project (or any directory) and verify**

In the new Claude Code session:

1. Type `/r-` and confirm autocompletion lists: `/r-analysis`, `/r-debug`, `/r-pkg-release`, `/r-shiny-app`, `/r-tdd-cycle`.
2. Run `/r-tdd-cycle` with no arguments and confirm Claude responds with the TDD-cycle workflow content (Prerequisites, Steps, etc.).
3. Trigger the session-start hook by reloading the session and confirm the recommended commands list mentions the new names (no `/r-cmd-*` strings).

- [ ] **Step 4: Final commit (if any cleanup edits surfaced)**

If steps 1-3 surface any issue (e.g. a description that's awkward in autocomplete), fix and commit. Otherwise this phase has no commit.

---

## Self-Review Notes

The plan covers:

- ✅ All 5 cmd-skills migrated (Phases 1-5)
- ✅ Old skill directories deleted (Phases 1-5, Step 2 of each)
- ✅ Hook references updated (Phase 6)
- ✅ Documentation updated (Phase 7)
- ✅ Structural test infrastructure repaired (Phase 0) and extended with command checks (Phase 8)
- ✅ Old design spec marked superseded (Phase 9)
- ✅ Final validation gate (Phase 10)

Items deliberately not in scope:

- Historical plan files under `docs/superpowers/plans/` are not edited; they record decisions at the time they were made.
- The `r-cmd-` mentions inside `docs/superpowers/specs/2026-04-28-r-package-dev-upgrade-design.md` and `2026-04-28-r-shiny-upgrade-design.md` are left alone (historical specs).
- README.md is not edited — current content was already verified to contain no `/r-cmd-*` references.
- The kebab-case naming concern on `supeRpowers` itself is unrelated and stays as-is unless a future user explicitly chooses to publish to the public claude.ai marketplace.
- No new features. No refactoring of any other skill or agent file.

Type-consistency check:

- New command names used in Phase 6/7 hook + CLAUDE.md updates match the file paths created in Phases 1-5: `/r-tdd-cycle`, `/r-debug`, `/r-pkg-release`, `/r-shiny-app`, `/r-analysis`. No drift.
- Test helper `get_command_files()` (Phase 8) reads from `COMMANDS_DIR = ROOT / "commands"`, matching the directory created in Phase 1.
