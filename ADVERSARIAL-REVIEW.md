# Adversarial Plugin Review: supeRpowers

**Date:** 2026-04-11
**Reviewer scope:** Plugin structure, content quality, and alignment with [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) principles.
**Plugin version:** 0.2.0

---

## Summary

The supeRpowers plugin is well-built and demonstrates strong R domain expertise. R code conventions are enforced perfectly across all 22 skills, 5 agents, and 1 rule file. Agent escalation topology is acyclic, boundaries between skills are clear, and hooks are cross-platform robust.

However, the review identified **3 high-severity**, **7 medium-severity**, and **4 low-severity** gaps when measured against the best-practice principles. None are blockers, but several represent missed opportunities for discoverability, safety, and maintainability.

---

## HIGH — Should fix before wider distribution

### H1. `rules/r-conventions.md` exceeds 150-line limit (159 lines)

**Source:** CLAUDE.md states "Rule files are ≤150 lines with no frontmatter."
**Impact:** Overly long rules consume context on every conversation turn. Rules are loaded unconditionally — they are the most expensive content per byte.
**Best practice:** "Target under 200 lines per file (60 lines achievable)" — the principle applies even more strongly to rules, which have no lazy-loading mechanism.
**Fix:** Extract the lower-priority sections (Environment-Aware Coding, Verify After Write, Function Design — lines 132-160) into a reference file loaded by relevant skills, or into a second rule file scoped more narrowly. This recovers ~28 lines and brings the file under the 150-line limit.

### H2. `r-mcp-setup` description is critically underdeveloped (169 chars)

**Source:** CLAUDE.md requires "description starts with 'Use when...' followed by third-person capability description, 5+ trigger phrases, and negative boundaries referencing sibling skills. Target 500 chars, hard limit 1024 chars."
**Current:**
```yaml
description: >
  Use when the user wants to set up MCP tools for R, connect Claude Code to a
  live R session, register R-based MCP servers, or when another skill needs
  MCP tool guidance.
```
**Missing:** Trigger phrases entirely. No negative boundaries. At 169 chars it is 331 chars short of the 500-char target.
**Best practice:** "Write skill descriptions as triggers ('when should I fire?') not summaries."
**Impact:** This skill will under-trigger. Claude's skill-matching relies on the description field for auto-discovery. Without trigger keywords, users must know the exact slash command.
**Fix:** Add explicit triggers (e.g., "set up MCP, connect R session, btw package, mcptools, live R, MCP server, register tools") and negative boundaries (e.g., "Do NOT use for general R project setup — use r-project-setup instead").

### H3. CLAUDE.md is stale — states "15 skills" but 22 exist

**Source:** CLAUDE.md line 3: "It ships 15 skills, 5 agents, and 1 rule."
**Actual:** 22 skills (15 domain + 5 workflow/cmd + r-mcp-setup + skill-auditor).
**Best practice:** "Ensure any developer can run tests successfully on first try" and "Keep codebases clean; finish migrations to prevent pattern confusion."
**Impact:** Contributors reading CLAUDE.md get an inaccurate mental model. The project structure section also doesn't mention cmd-* skills, r-mcp-setup, or skill-auditor.
**Fix:** Update the count and project structure tree to reflect the current state.

---

## MEDIUM — Improve when practical

### M1. No skill uses `context: fork` for isolated execution

**Source:** Best practice: "Use `context: fork` to run skills in isolated subagents."
**Current:** Zero of 22 skills set `context: fork` in frontmatter.
**Impact:** All skills run in the main conversation context. Heavy skills (r-clinical at 298 lines, r-performance at 300 lines) inject their full content into the primary context window and stay there for the rest of the session, consuming budget even when no longer relevant.
**Best practice (Orchestration Workflow):** The Command-Agent-Skill architecture recommends skill isolation: "Skills are preloaded: Full skill content is injected into agent's context at startup" — in a *forked* context that is discarded after use.
**Fix:** Add `context: fork` to the heavier knowledge skills (r-clinical, r-performance, r-package-dev, r-quarto, r-stats, r-tidymodels) so they run in disposable subagent contexts. The r-cmd-* workflow skills are natural orchestrators and should remain in the main context.

### M2. No skill uses `allowed-tools` for tool scoping

**Source:** Best practice skill frontmatter field: `allowed-tools` — "Tools permitted without permission prompts."
**Impact:** Every skill has full tool access. Skills like r-mcp-setup or r-project-setup that scaffold files could benefit from pre-approved `Write`, `Edit`, `Bash` permissions to reduce permission prompt friction. Conversely, read-only reference skills (r-stats, r-visualization) don't need write access at all.
**Fix:** Audit each skill's actual tool needs. Add `allowed-tools` for workflow skills that predictably need specific tools. Consider restricting reference-only skills.

### M3. No skill uses `hooks` for safety or formatting

**Source:** Best practice: "Use on-demand hooks in skills for destruction safety and edit restrictions" and "Use PostToolUse hooks for auto-formatting to prevent CI failures."
**Impact:** Skills that generate R code (most of them) could benefit from a PostToolUse hook that runs `styler::style_file()` on written R files, or a PreToolUse hook that prevents editing files outside the project root.
**Fix:** Consider a shared PostToolUse hook for R file formatting, attached via the `hooks` frontmatter field to code-generating skills.

### M4. Agent files lack YAML frontmatter — missing configurability

**Source:** The plugin's CLAUDE.md explicitly requires "NO YAML frontmatter" for agents. However, the best-practice specification for subagents defines 16 frontmatter fields, with `name` and `description` as required.
**Impact:** Without frontmatter, agents cannot:
- Specify `model` (e.g., Haiku for the lightweight r-code-reviewer, Opus for r-statistician)
- Set `maxTurns` to prevent runaway execution
- Preload `skills` relevant to their domain
- Configure `hooks` for agent-specific safety
- Set `effort` levels appropriate to task complexity
**Note:** This is a deliberate design choice by the plugin, not an oversight. The plugin treats agent files as procedure documents dispatched by skills, not as standalone auto-invocable subagents. This works, but leaves configurability on the table.
**Fix:** If the plugin intends agents to be invocable via `Agent(agent_type)`, add YAML frontmatter. If they are purely reference documents for skills to follow as procedure, the current approach is acceptable but should be documented as an intentional deviation.

### M5. `skill-auditor` uses a third frontmatter field, breaking the "exactly two" rule

**Source:** CLAUDE.md: "YAML frontmatter with exactly two fields: `name` and `description`."
**Current:** `skill-auditor/SKILL.md` has three fields: `name`, `description`, and `disable-model-invocation: true`.
**Impact:** Internal inconsistency with project's own stated rules.
**Fix:** Either update CLAUDE.md to say "two required fields (`name`, `description`) plus optional configuration fields" or remove the `disable-model-invocation` field and find another way to prevent auto-invocation.

### M6. No `paths` field for auto-activation on file patterns

**Source:** Best practice skill frontmatter field: `paths` — "Glob patterns for auto-activation on matching files."
**Impact:** Skills could auto-activate when the user opens relevant files. For example:
- `r-shiny` could activate on `app.R`, `ui.R`, `server.R`, `mod_*.R`
- `r-quarto` could activate on `*.qmd`, `_quarto.yml`
- `r-targets` could activate on `_targets.R`
- `r-package-dev` could activate on `DESCRIPTION`, `NAMESPACE`
This would reduce reliance on the SessionStart hook for project detection.
**Fix:** Add `paths` to skills where file-pattern triggers make sense.

### M7. Seven skills lack eval.md files

**Source:** 15 of 22 skills have `eval.md` evaluation rubrics. Missing: r-cmd-analysis, r-cmd-debug, r-cmd-pkg-release, r-cmd-shiny-app, r-cmd-tdd-cycle, r-mcp-setup, skill-auditor.
**Best practice:** "Invest in product verification skills perfected over a week."
**Impact:** These skills cannot be systematically evaluated for quality regressions. The five r-cmd-* workflow skills are particularly important since they orchestrate multiple other skills — a regression in orchestration logic is harder to catch without eval criteria.
**Fix:** Add eval.md files for at least the r-cmd-* workflow skills.

---

## LOW — Nice to have

### L1. No `model` field in any skill for resource-appropriate routing

**Source:** Best practice: "Select Opus for plan mode and Sonnet for code implementation."
**Impact:** Lightweight skills (r-mcp-setup, r-project-setup) run on the same model as heavyweight reasoning skills (r-stats, r-clinical). Setting `model: sonnet` on reference skills and `model: opus` on statistical/clinical skills would optimize cost and speed.
**Fix:** Add `model` field to skills where the task complexity clearly warrants (or doesn't warrant) a specific model tier.

### L2. No dynamic shell output injection (`!command`) in SKILL.md files

**Source:** Best practice: "Embed `!command` in SKILL.md for dynamic shell output injection."
**Impact:** Skills could dynamically inject context like the current R version, installed packages, or renv status directly into the skill body. Currently this is handled by the SessionStart hook, which is a reasonable alternative but less granular.
**Fix:** Low priority. The hook-based approach works. Consider `!command` for skills that need very specific runtime context (e.g., r-mcp-setup checking MCP server availability).

### L3. `plugin.json` `min_version` set to `1.0.0` — may be too permissive

**Source:** Plugin uses features (hooks, skills with frontmatter fields) that may require a more recent Claude Code version.
**Impact:** Users on older versions may install the plugin and get degraded behavior without clear error messages.
**Fix:** Verify the minimum Claude Code version that supports all features used (hooks.json, skill frontmatter, agent dispatch) and update accordingly.

### L4. No `effort` field in any skill

**Source:** Best practice skill frontmatter field: `effort` — "Overrides model effort: low, medium, high, or max."
**Impact:** Simple reference lookups (r-mcp-setup, r-project-setup scaffold selection) don't need max reasoning effort, while statistical methodology selection (r-stats, r-clinical) benefits from deeper thinking.
**Fix:** Add `effort: high` or `effort: max` to complex reasoning skills; `effort: medium` to reference skills.

---

## PASS — Verified correct

These areas were explicitly checked and found to be in good standing:

| Check | Status |
|-------|--------|
| R code conventions (`\|>`, `<-`, snake_case, double quotes) | 100% compliant across all files |
| No `%>%` in skill/agent/rule content (only in eval/audit scripts) | Pass |
| All SKILL.md files have `name` + `description` frontmatter | Pass |
| Agent files have no YAML frontmatter | Pass (per project rules) |
| All skill descriptions start with "Use when..." | Pass (except r-mcp-setup — see H2) |
| Skill descriptions include negative boundaries ("Do NOT use...") | Pass (except r-mcp-setup — see H2) |
| Skill descriptions include 5+ trigger phrases | Pass (except r-mcp-setup — see H2) |
| Agent escalation topology has no circular dependencies | Pass |
| Terminal agents (r-statistician, r-dependency-manager) don't escalate | Pass |
| All skills ≤300 lines | Pass (3 at exactly 300/299 — acceptable) |
| All agents ≤200 lines | Pass (r-statistician at exactly 200) |
| Hooks are cross-platform (bash + cmd polyglot) | Pass |
| Hooks exit gracefully on missing tools (Rscript, bash) | Pass |
| JSON output escaping in hooks is correct | Pass |
| plugin.json globs match all actual files | Pass |
| Skills use progressive disclosure (references/ subdirectories) | Pass (15 of 22 have references/) |
| Skills include example prompts | Pass |
| Gotchas sections present in knowledge skills | Pass |

---

## Recommendation

The plugin is production-quality for R programming assistance. The three high-severity items (H1-H3) are straightforward to fix and should be addressed before publishing to a wider audience. The medium items (M1-M7) represent the gap between "works well" and "optimally leverages the Claude Code platform" — prioritize M1 (`context: fork`) and M2 (`allowed-tools`) for the biggest impact on context efficiency and user experience.
