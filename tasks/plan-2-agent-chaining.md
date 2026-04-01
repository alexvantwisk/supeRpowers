# Plan 2: Agent Chaining Protocol

## Summary

Add an `## Escalation` section to all 5 agent files, enabling agents to hand off to other agents when they encounter issues outside their expertise. Also update 5 knowledge skill descriptions with pointers to their workflow command counterparts.

**Deliverables:** 5 modified agent files + 5 modified skill descriptions (10 files total)

## Chaining Rules

1. **Max chain depth: 2** — A→B→C is the limit, no further.
2. **Always report back** — final agent includes summary of the full chain.
3. **No cycles** — A→B→A is forbidden.
4. **Explicit initiation** — only when workflow step says "escalate to" or agent's Escalation table matches.

## Chain Map

```
r-code-reviewer   → r-statistician       (stats issues in code)
r-code-reviewer   → r-dependency-manager  (dependency concerns)
r-pkg-check       → r-dependency-manager  (version conflicts)
r-pkg-check       → r-code-reviewer       (code quality findings)
r-shiny-architect → r-code-reviewer       (implementation issues)
r-statistician    → (terminal)
r-dependency-manager → (terminal)
```

Cycle check: No agent appears on both sides of a chain. r-code-reviewer receives from r-pkg-check and r-shiny-architect but only escalates to r-statistician and r-dependency-manager (neither of which escalates back). Safe.

## Agent Modifications

### Task 1: `agents/r-code-reviewer.md` (currently 100 lines)

- [ ] Insert `## Escalation` section before `## Examples` (before line 91)

**Content to insert:**
```markdown
## Escalation

When findings cross into another agent's domain, escalate rather than attempt a fix outside your expertise.

| Condition | Escalate to | Pass along |
|-----------|-------------|------------|
| Statistical methodology concern (wrong test, violated assumptions, questionable model choice) | r-statistician | Code block + specific statistical concern + data context |
| Dependency issue (version conflict, missing import, heavy package with lighter alternative) | r-dependency-manager | Package names + error messages + renv.lock excerpt if available |

When escalating, include a one-line summary of why you're handing off. The receiving agent reports back to the user with a chain summary.
```

**New line count:** ~112 lines (within 200-line limit)

---

### Task 2: `agents/r-pkg-check.md` (currently 113 lines)

- [ ] Insert `## Escalation` section before `## Examples` (before line 104)

**Content to insert:**
```markdown
## Escalation

| Condition | Escalate to | Pass along |
|-----------|-------------|------------|
| Version conflict between packages that renv cannot resolve | r-dependency-manager | Conflicting package names + version requirements + full error text |
| Code quality finding from check output (e.g., `no visible binding`, style issues in flagged files) | r-code-reviewer | File paths + specific findings from check output |

When escalating, include the relevant R CMD check output section. The receiving agent reports back with a chain summary.
```

**New line count:** ~122 lines

---

### Task 3: `agents/r-shiny-architect.md` (currently 134 lines)

- [ ] Insert `## Escalation` section before `## Examples` (before line 125)

**Content to insert:**
```markdown
## Escalation

| Condition | Escalate to | Pass along |
|-----------|-------------|------------|
| Implementation-level code quality issue (style violations, incorrect NSE usage, missing documentation) in module code | r-code-reviewer | File paths of modules with issues + specific concerns |

Architecture-level issues (reactivity design, module boundaries, performance patterns) remain with this agent. Only escalate concrete code-level findings.
```

**New line count:** ~142 lines

---

### Task 4: `agents/r-statistician.md` (currently 199 lines)

- [ ] Insert `## Escalation` section before `## Examples` (before line 187)

**Content to insert:**
```markdown
## Escalation

This is a **terminal agent** — it does not escalate to other agents. All statistical methodology questions are resolved here. If the concern crosses into pure code quality (not methodology), note this in the report for the user to address separately.
```

**New line count:** ~203 lines (slightly over 200 — may need to trim 3-4 lines from existing content, e.g., compress an example)

---

### Task 5: `agents/r-dependency-manager.md` (currently 124 lines)

- [ ] Insert `## Escalation` section before `## Examples` (before line 115)

**Content to insert:**
```markdown
## Escalation

This is a **terminal agent** — it does not escalate to other agents. All dependency, renv, and version management issues are resolved here. If a dependency problem has code-level implications beyond the dependency itself, note this in the report for the user to address separately.
```

**New line count:** ~128 lines

---

## Knowledge Skill Description Updates

Each skill gets a one-line addition at the end of its `description` field in YAML frontmatter, before the closing of the description block.

### Task 6: `skills/r-tdd/SKILL.md`

- [ ] Add to end of description (before closing `---`)

**Line to add:**
```
  For a guided Red-Green-Refactor cycle, invoke /r-cmd-tdd-cycle instead.
```

**Current description ends with:**
```
  Do NOT use for debugging existing code — use r-debugging instead.
```

**After edit:**
```
  Do NOT use for debugging existing code — use r-debugging instead.
  For a guided Red-Green-Refactor cycle, invoke /r-cmd-tdd-cycle instead.
```

---

### Task 7: `skills/r-package-dev/SKILL.md`

- [ ] Add to end of description

**Line to add:**
```
  For a guided release workflow, invoke /r-cmd-pkg-release instead.
```

---

### Task 8: `skills/r-data-analysis/SKILL.md`

- [ ] Add to end of description

**Line to add:**
```
  For a guided analysis pipeline, invoke /r-cmd-analysis instead.
```

---

### Task 9: `skills/r-shiny/SKILL.md`

- [ ] Add to end of description

**Line to add:**
```
  For a guided app scaffold workflow, invoke /r-cmd-shiny-app instead.
```

---

### Task 10: `skills/r-debugging/SKILL.md`

- [ ] Add to end of description

**Line to add:**
```
  For a guided debugging workflow, invoke /r-cmd-debug instead.
```

---

## Verification Checklist

- [ ] All 5 agents have `## Escalation` section (before Examples)
- [ ] No cycles in chain map: verify no agent escalates to an agent that escalates back
- [ ] Max depth 2 respected: no chain path exceeds A→B→C
- [ ] Terminal agents (r-statistician, r-dependency-manager) have explicit "does not escalate" marker
- [ ] All 5 knowledge skills have updated descriptions with workflow pointer
- [ ] All agent files are under 200 lines (r-statistician may need trimming)
- [ ] All skill descriptions remain under 1024 characters
- [ ] No `%>%` introduced: `grep -rn '%>%' agents/ skills/`
- [ ] Escalation tables use consistent column format: Condition | Escalate to | Pass along
