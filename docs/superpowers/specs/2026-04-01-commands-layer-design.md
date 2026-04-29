# Commands Layer — Workflow Skills for supeRpowers

**Date:** 2026-04-01  
**Status:** SUPERSEDED 2026-04-29 — Claude Code plugins do support a native `commands/` directory; the 5 `r-cmd-*` skills have been migrated to `commands/r-*.md`. See `docs/superpowers/plans/2026-04-29-cmd-skills-to-commands-migration.md` for the migration plan.  
**Scope:** Add 5 workflow command skills, agent chaining protocol, updated skill/agent descriptions

## Context

The supeRpowers plugin has 16 knowledge skills and 5 agents, but no explicit workflow orchestration. Users must know which skill to invoke and manually sequence multi-step R development processes. The best practices pattern from the Claude Code community advocates "commands" — explicit entry points that orchestrate multi-step workflows by coordinating skills and agents.

Since Claude Code plugin.json does not support a separate `commands` key, workflow commands are implemented as skills with a distinct naming convention (`r-cmd-*`).

## Architecture

### Two Skill Types

```
skills/
├── Knowledge skills (existing 16)     ← "What to know"
│   r-data-analysis/SKILL.md
│   r-tdd/SKILL.md
│   ...
│
└── Workflow skills (new 5)            ← "What to do"
    r-cmd-tdd-cycle/SKILL.md
    r-cmd-pkg-release/SKILL.md
    r-cmd-analysis/SKILL.md
    r-cmd-shiny-app/SKILL.md
    r-cmd-debug/SKILL.md
```

### Naming Convention

- Workflow skills: `/r-cmd-<workflow>` — signals "this does something"
- Knowledge skills: `/r-<domain>` — signals "this knows something"
- The `cmd` infix provides instant visual/semantic separation

### Interaction Model

```
User invokes /r-cmd-tdd-cycle
  → Workflow skill provides step-by-step procedure
  → Each step references a knowledge skill for domain expertise
  → Steps dispatch to agents for specialized review/analysis
  → Agents can chain to other agents (escalation)
```

Workflow skills are short (100-150 lines) and procedural. They do not duplicate knowledge — they reference it via skill pointers.

## Command Inventory

| Command | Orchestrates | Skills Referenced | Agents Dispatched |
|---------|-------------|-------------------|-------------------|
| **r-cmd-tdd-cycle** | Red, Green, Refactor, Review | r-tdd, r-debugging | r-code-reviewer |
| **r-cmd-pkg-release** | Check, Test, Document, Build, Submit | r-package-dev, r-tdd | r-pkg-check, r-dependency-manager, r-code-reviewer |
| **r-cmd-analysis** | Import, Clean, Explore, Model, Visualize | r-data-analysis, r-visualization, r-stats | r-statistician |
| **r-cmd-shiny-app** | Scaffold, Module, Wire, Test, Review | r-project-setup, r-shiny, r-tdd | r-shiny-architect, r-code-reviewer |
| **r-cmd-debug** | Reproduce, Isolate, Diagnose, Fix, Verify | r-debugging, r-tdd | r-code-reviewer |

### Deliberately Excluded

- **No r-cmd-quarto** — Quarto workflows are too varied (document vs slides vs book vs website) to fit one command.
- **No r-cmd-clinical** — Clinical workflows are domain-specific, vary by company/protocol; better served by the knowledge skill.
- **No r-cmd-targets** — Pipeline setup is already well-covered by the r-targets skill's procedural nature.

## Command File Format

Each workflow skill follows this structure:

```markdown
---
name: r-cmd-<workflow>
description: >
  Use when [trigger]. Orchestrates [skill list] with [agent list].
  Invoke directly as /r-cmd-<workflow>.
  Do NOT use for [boundary] — use [sibling] instead.
---

# <Workflow Title>

## Prerequisites
- [What must be true before starting]

## Steps

### Step 1: <Phase name>
**Skill:** `r-<knowledge-skill>`
**Action:** [What to do]
**Gate:** [What must be true before proceeding]

### Step 2: <Phase name>
**Skill:** `r-<knowledge-skill>`
**Agent:** `r-<agent>` — dispatch when [condition]
**Action:** [What to do]
**Gate:** [What must be true before proceeding]

### Step 3: <Phase name>
**Agent:** `r-<agent>` → escalate to `r-<other-agent>` when [condition]
**Action:** [What to do]
**Gate:** [What must be true before proceeding]

## Abort Conditions
- [When to stop and re-assess rather than push forward]

## Examples
### Example: <Typical scenario>
**Prompt:** "..."
**Flow:** Step 1 → Step 2 → Step 3 → Done
```

### Format Decisions

- **Gates between steps** — each step has an explicit condition that must pass before moving on. Prevents barreling through a broken pipeline.
- **Agent escalation syntax** — `r-code-reviewer → r-statistician when [condition]` makes chaining explicit.
- **Abort conditions** — when to stop the workflow entirely rather than continuing.
- **100-150 line target** — workflow skills stay lean. No knowledge duplication.
- **No Gotchas section** — workflows reference knowledge skills that already have Gotchas.

## Agent Chaining Protocol

### Mechanism

Each agent gets a new `## Escalation` section (before Examples) listing conditions for handoff:

```markdown
## Escalation

| Condition | Escalate to | Pass along |
|-----------|-------------|------------|
| Statistical assumption violation found | r-statistician | Finding details + code context |
| Dependency conflict blocking resolution | r-dependency-manager | Package list + error output |
```

### Chaining Rules

1. **Max chain depth: 2** — Agent A to Agent B is fine. A to B to C is the limit. No unbounded chains.
2. **Always report back** — the final agent reports to the user, including a summary of the full chain.
3. **No cycles** — A to B to A is forbidden. If B finds something for A, it reports the finding and the user/workflow decides.
4. **Chain initiation is explicit** — agents only chain when a workflow skill's step says "escalate to" or when the agent's own Escalation table matches. Knowledge skills do not trigger chains.

### Chain Map

```
r-code-reviewer   → r-statistician       (stats issues in code)
r-code-reviewer   → r-dependency-manager  (dependency concerns)
r-pkg-check       → r-dependency-manager  (version conflicts)
r-pkg-check       → r-code-reviewer       (code quality findings)
r-shiny-architect → r-code-reviewer       (implementation issues)
r-statistician    → (terminal — no escalation)
r-dependency-manager → (terminal — no escalation)
```

Two terminal agents (statistician, dependency-manager) anchor chains.

## Discovery and Routing

### Description Patterns

Workflow skills start with `Use when starting...` to signal intent-to-act:

```yaml
# Workflow
description: "Use when starting a TDD cycle..."

# Knowledge
description: "Use when working with test-driven development..."
```

### Overlap Prevention

Each workflow skill's description includes a boundary referencing its knowledge counterpart:

```yaml
# r-cmd-tdd-cycle
description: >
  ...Do NOT use for testthat API guidance without a full cycle — use r-tdd instead.
```

Each knowledge skill gets a one-line addition pointing to its workflow:

```yaml
# r-tdd (updated)
description: >
  ...For a guided Red-Green-Refactor cycle, use /r-cmd-tdd-cycle instead.
```

## Changes to Existing Files

### Knowledge Skills Updated (5 files)

One-line description addition pointing to the corresponding workflow command:

| Skill | Addition |
|-------|----------|
| r-tdd | "For a guided Red-Green-Refactor cycle, use /r-cmd-tdd-cycle instead." |
| r-package-dev | "For a guided release workflow, use /r-cmd-pkg-release instead." |
| r-data-analysis | "For a guided analysis pipeline, use /r-cmd-analysis instead." |
| r-shiny | "For a guided app scaffold workflow, use /r-cmd-shiny-app instead." |
| r-debugging | "For a guided debugging workflow, use /r-cmd-debug instead." |

### Agent Files Updated (5 files)

New `## Escalation` section (4-8 lines each):

| Agent | Escalation targets |
|-------|-------------------|
| r-code-reviewer | r-statistician, r-dependency-manager |
| r-pkg-check | r-dependency-manager, r-code-reviewer |
| r-shiny-architect | r-code-reviewer |
| r-statistician | (none — terminal) |
| r-dependency-manager | (none — terminal) |

### Unchanged

- r-conventions.md — no changes
- plugin.json — no changes (existing glob discovers new skills)
- hooks/ — no changes (lower priority, separate effort)

## Deliverables

1. 5 new workflow skill files (`skills/r-cmd-*/SKILL.md`)
2. 5 updated knowledge skill descriptions (one-line addition each)
3. 5 updated agent files (new Escalation section each)
4. Total: 15 files touched (5 new, 10 modified)
