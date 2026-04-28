# supeRpowers Improvement Proposal

**Date:** 2026-04-11
**Author:** Adversarial review follow-up
**Scope:** Architecture, platform adoption, safety, developer experience
**Baseline:** v0.2.0 (22 skills, 5 agents, 1 rule, 1 hook set)

---

## Thesis

supeRpowers is a domain-expert plugin — the R knowledge is deep, the conventions are enforced, the skill boundaries are clean. What it hasn't yet done is take full advantage of the *platform* it runs on. Claude Code's skill system offers context isolation, tool scoping, model routing, lifecycle hooks, and file-pattern activation. Today the plugin uses exactly one of these (lifecycle hooks, via SessionStart). The proposals below close that gap.

Each proposal is scoped, self-contained, and ordered by expected impact on real user sessions.

---

## Proposal 1: Context Forking for Knowledge Skills

**Problem.** When a user triggers `/r-clinical` (298 lines) to answer one question about ADaM datasets, those 298 lines stay in the main context for the entire session. If they later ask about Shiny, r-shiny injects another 256 lines. By mid-session, the context window holds 1000+ lines of skill content the user may never need again.

**Solution.** Add `context: fork` to heavy, self-contained knowledge skills. This runs the skill in a disposable subagent — the skill content loads, the answer is returned, and the context is reclaimed.

**Which skills get forked:**

| Skill | Lines | Rationale |
|-------|-------|-----------|
| r-clinical | 298 | Domain-specific, rarely needed alongside other skills |
| r-performance | 300 | Distinct from daily data work, self-contained |
| r-package-dev | 300 | Long, usually invoked for dedicated package work |
| r-quarto | 299 | Publishing context, rarely mixed with analysis |
| r-tidymodels | 275 | ML pipeline is a separate workflow |
| r-targets | 287 | Pipeline setup is a focused task |
| r-project-setup | 276 | One-shot scaffolding, never needed again in-session |
| r-stats | 241 | Often dispatched for a single modeling question |
| r-package-skill-generator | 256 | Meta-tool, used once per invocation |

**Which skills stay in main context:**

| Skill | Lines | Rationale |
|-------|-------|-----------|
| r-data-analysis | 195 | Frequently referenced across a session |
| r-visualization | 259 | Called repeatedly alongside data work |
| r-debugging | 216 | Needs to see current session state and errors |
| r-shiny | 256 | Interactive development loop, state-dependent |
| r-tdd | 228 | Red-green-refactor is a multi-turn loop |
| r-tables | 226 | Often used alongside r-visualization |
| r-mcp-setup | 181 | Configuration task, needs main context tools |
| skill-auditor | 249 | Meta-tool, needs main context access |
| r-cmd-* (5 skills) | 81-104 | Orchestrators — they must stay in main context to dispatch |

**Implementation.** One frontmatter field per skill:

```yaml
---
name: r-clinical
context: fork
description: >
  ...
---
```

**Estimated context savings:** 2,330 lines of skill content moved out of the main window for typical multi-domain sessions. That's roughly 40% of total skill content.

---

## Proposal 2: File-Pattern Auto-Activation

**Problem.** The SessionStart hook detects project type once at session start. But users often work across multiple file types within a session, and the hook can't re-fire when the user opens a Quarto document inside an R package project. Skills only activate if the user knows the slash command or the description happens to match their natural language.

**Solution.** Add `paths` frontmatter to skills with obvious file-type triggers. This makes skills auto-activate when the user reads or edits matching files, without requiring the SessionStart hook or a slash command.

**Proposed mappings:**

```yaml
# r-shiny/SKILL.md
paths:
  - "app.R"
  - "ui.R"
  - "server.R"
  - "**/mod_*.R"
  - "inst/golem-config.yml"
  - "rhino.yml"

# r-quarto/SKILL.md
paths:
  - "**/*.qmd"
  - "_quarto.yml"

# r-targets/SKILL.md
paths:
  - "_targets.R"
  - "_targets/**"

# r-package-dev/SKILL.md
paths:
  - "DESCRIPTION"
  - "NAMESPACE"
  - "R/*.R"
  - "man/*.Rd"

# r-tdd/SKILL.md
paths:
  - "tests/**/*.R"
  - "tests/testthat.R"

# r-clinical/SKILL.md
paths:
  - "adam/**"
  - "sdtm/**"
  - "ADAM/**"
  - "SDTM/**"

# r-tables/SKILL.md
paths: "**/*table*.R"

# r-tidymodels/SKILL.md
paths: "**/recipe*.R"
```

**Interaction with context: fork.** When `paths` triggers a forked skill, the skill runs in isolation, answers the question, and exits — the user doesn't even notice the dispatch happened. This is the ideal UX: the right knowledge shows up automatically and doesn't linger.

---

## Proposal 3: Agent Frontmatter for Configurability

**Problem.** The five agent files are pure Markdown procedure documents. They work when skills manually dispatch to them via prose instructions, but they can't be invoked via `Agent(agent_type)` with platform-level configuration — no model selection, no turn limits, no skill preloading.

**Solution.** Add YAML frontmatter to agent files. This is the single change that unlocks the full Command-Agent-Skill orchestration pattern.

**Proposed frontmatter:**

```yaml
# agents/r-statistician.md
---
name: r-statistician
description: >
  Statistical consulting agent. Invoke for model selection, assumption
  verification, result interpretation, and methodological risk assessment.
  Covers frequentist, Bayesian, and biostatistics approaches.
model: opus
maxTurns: 15
effort: high
skills:
  - r-stats
  - r-clinical
---
```

```yaml
# agents/r-code-reviewer.md
---
name: r-code-reviewer
description: >
  Opinionated R code reviewer. Invoke to check style, correctness,
  performance, and documentation against project conventions.
model: sonnet
maxTurns: 10
effort: medium
skills:
  - r-tdd
---
```

```yaml
# agents/r-pkg-check.md
---
name: r-pkg-check
description: >
  R CMD check issue resolver. Invoke to parse check output, diagnose
  root causes, and provide usethis/devtools fix commands.
model: sonnet
maxTurns: 12
effort: medium
skills:
  - r-package-dev
---
```

```yaml
# agents/r-shiny-architect.md
---
name: r-shiny-architect
description: >
  Shiny application architecture reviewer. Invoke to evaluate module
  decomposition, reactivity, performance, and security.
model: sonnet
maxTurns: 12
effort: medium
skills:
  - r-shiny
---
```

```yaml
# agents/r-dependency-manager.md
---
name: r-dependency-manager
description: >
  renv and R dependency management expert. Invoke to audit dependencies,
  resolve conflicts, and manage Bioconductor + CRAN coexistence.
model: sonnet
maxTurns: 8
effort: medium
---
```

**Key design decisions:**

- **r-statistician gets `model: opus`** — statistical methodology selection is the one task where deeper reasoning measurably improves correctness. Everything else can run on Sonnet.
- **`maxTurns` set per agent** — prevents runaway execution. The statistician gets more turns (complex multi-step analysis), the dependency manager gets fewer (structured checklist).
- **`skills` preloaded** — agents start with the domain knowledge they need without having to discover it. The r-code-reviewer gets r-tdd preloaded because style review often leads to test recommendations.
- **No `PROACTIVELY` in descriptions** — agents should be explicitly dispatched by skills or the user, not auto-invoked.

**CLAUDE.md update required:** Change "NO YAML frontmatter" to "YAML frontmatter required" for agents, and document the expected fields.

---

## Proposal 4: PostToolUse Hook for R Code Formatting

**Problem.** When Claude writes an R file, it follows the conventions well — but not perfectly. Occasional edge cases in indentation, spacing, or line-wrapping slip through. Currently there's no automated safety net.

**Solution.** Add a PostToolUse hook that runs `styler::style_file()` on any `.R` file Claude writes or edits. This catches formatting drift the same way `prettier` or `black` would for JavaScript or Python.

**Implementation:**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/format-r-file\" \"$CLAUDE_FILE_PATH\"",
            "async": true
          }
        ]
      }
    ]
  }
}
```

**`hooks/format-r-file`:**

```bash
#!/usr/bin/env bash
set -euo pipefail
file="$1"
[[ "$file" == *.R ]] || exit 0
command -v Rscript >/dev/null 2>&1 || exit 0
Rscript --vanilla -e "styler::style_file('$file')" 2>/dev/null || true
exit 0
```

**Design notes:**
- `async: true` — formatting runs in parallel, doesn't block Claude's next turn.
- Only fires on `.R` files — ignores Markdown, YAML, JSON, etc.
- Graceful fallback — if Rscript or styler isn't available, exits silently.
- Operates on the file path from the tool result, not a hardcoded path.

**Bonus: PreToolUse hook for `%>%` prevention.** A lighter alternative — a PreToolUse hook on Write/Edit that scans the content for `%>%` and returns a warning message. This catches the violation before it's written rather than formatting after.

---

## Proposal 5: Effort and Model Routing

**Problem.** All 22 skills run at the same reasoning effort and on the same model. A quick "what's the ggplot2 syntax for a boxplot?" question gets the same computational budget as "design a group-sequential clinical trial with adaptive randomization."

**Solution.** Add `effort` and `model` fields where the task complexity clearly warrants differentiation.

**Proposed routing:**

| Skill | model | effort | Rationale |
|-------|-------|--------|-----------|
| r-clinical | opus | high | Regulatory accuracy is non-negotiable |
| r-stats | opus | high | Model selection requires deep reasoning |
| r-package-skill-generator | opus | high | Synthesizing a skill from an entire package |
| r-performance | sonnet | high | Profiling analysis needs care but not max depth |
| r-package-dev | sonnet | medium | Mostly structured knowledge, not reasoning |
| r-data-analysis | sonnet | medium | Pattern matching, not novel reasoning |
| r-visualization | sonnet | medium | Syntax-heavy, not reasoning-heavy |
| r-mcp-setup | sonnet | low | Procedural setup steps |
| r-project-setup | sonnet | low | Scaffolding from templates |
| r-cmd-* (all 5) | *(inherit)* | *(inherit)* | Orchestrators inherit from parent |

Skills not listed above: leave unset (inherit from session defaults).

---

## Proposal 6: Fix r-mcp-setup Description

**Problem.** At 169 characters with no trigger phrases and no negative boundaries, r-mcp-setup is effectively invisible to auto-discovery.

**Proposed replacement:**

```yaml
description: >
  Use when setting up MCP tools for R, connecting Claude Code to a live R
  session via mcptools and btw, registering R-based MCP servers, or when
  another skill references MCP tool guidance. Provides step-by-step setup
  for project-scoped MCP registration, live session connection via
  mcp_session(), and tool group configuration.
  Triggers: set up MCP, connect R session, mcptools, btw, MCP server,
  register R tools, live R session, MCP not working, btw tools, claude mcp.
  Do NOT use for general R project setup — use r-project-setup instead.
  Do NOT use for package development workflow — use r-package-dev instead.
```

This hits 550 chars, includes 10 trigger phrases, and has 2 negative boundaries.

---

## Proposal 7: `allowed-tools` for Workflow Skills

**Problem.** The r-cmd-* workflow skills predictably need Bash (to run R code), Write (to create files), Edit (to modify code), and Read (to check results). Every invocation triggers multiple permission prompts that interrupt the guided flow.

**Solution.** Pre-approve expected tools in the frontmatter:

```yaml
# r-cmd-analysis
allowed-tools: Read,Edit,Write,Bash(Rscript*),Bash(cat*)

# r-cmd-tdd-cycle
allowed-tools: Read,Edit,Write,Bash(Rscript*),Bash(devtools::test*)

# r-cmd-pkg-release
allowed-tools: Read,Edit,Write,Bash(Rscript*),Bash(R CMD*)

# r-cmd-shiny-app
allowed-tools: Read,Edit,Write,Bash(Rscript*),Bash(golem::*)

# r-cmd-debug
allowed-tools: Read,Edit,Write,Bash(Rscript*)
```

**Key constraint:** Only scope to the specific Bash patterns the workflow needs. Do not blanket-allow `Bash(*)`. The user still gets prompted for anything outside the declared patterns.

---

## Proposal 8: Trim r-conventions.md Below 150 Lines

**Problem.** At 159 lines, the rules file exceeds the 150-line limit. Rules are loaded into *every* conversation — they are the costliest content per line in the entire plugin.

**Solution.** Extract lines 132-160 (Environment-Aware Coding, Verify After Write, Function Design) into a new file: `rules/r-conventions-mcp.md`. Load it conditionally — either as a second rule file or as a reference from r-mcp-setup.

**Concrete split:**

**Keep in r-conventions.md (lines 1-131, 131 lines):** Pipe, Paradigm, Style, Environment Management, R Version, Package Dev Toolchain, Documentation, Error Handling, Tidy Evaluation, File Organization, Anti-Patterns table.

**Move to r-conventions-mcp.md (lines 132-160, 28 lines):** Environment-Aware Coding (MCP tool usage), Verify After Write, Function Design.

The moved content is MCP-specific or applies only to non-trivial code generation — it doesn't need to be in every conversation.

---

## Proposal 9: Sync CLAUDE.md With Reality

**Changes needed:**

1. **Line 3:** "15 skills" → "22 skills" and list the categories (15 domain knowledge + 5 workflow orchestrators + r-mcp-setup + skill-auditor).
2. **Project structure tree:** Add r-cmd-* skills, r-mcp-setup, skill-auditor, and the nested agents/scripts in r-package-skill-generator.
3. **Content Formats > Skills:** Update "exactly two fields" to "two required fields (`name`, `description`) plus optional platform fields (`context`, `model`, `effort`, `allowed-tools`, `paths`, `hooks`, `disable-model-invocation`)."
4. **Content Formats > Agents:** If Proposal 3 is adopted, update from "NO YAML frontmatter" to document the expected frontmatter fields.
5. **Verification Checklist:** Add checks for `context: fork` on appropriate skills and `allowed-tools` scoping.

---

## Proposal 10: Eval Coverage for Workflow Skills

**Problem.** The five r-cmd-* workflow skills and r-mcp-setup have no eval.md rubrics. These are the skills where regression is hardest to detect — orchestration logic is about sequencing and gating, not just content accuracy.

**Proposed eval dimensions for r-cmd-* skills:**

1. Does the workflow follow the stated step sequence?
2. Does each step invoke the correct sub-skill?
3. Are gate conditions checked before advancing?
4. Are abort conditions triggered when appropriate?
5. Does the workflow produce output matching the expected format?
6. Does the workflow correctly dispatch to agents when needed?
7. Does all generated code follow r-conventions.md?

**Proposed eval dimensions for r-mcp-setup:**

1. Does the setup follow the 5-step sequence?
2. Are btw tool groups correctly identified?
3. Is the `claude mcp add` command syntactically correct?
4. Is the user asked for permission before modifying config?
5. Does verification check server connectivity?

---

## Proposal 11: A `stop` Hook for Work Verification

**Problem.** When Claude finishes a task dispatched by a workflow skill, there's no automated check that the output actually works. The user has to manually verify.

**Solution.** A Stop hook that nudges continuation when the task involved writing R code but no verification step was observed.

**Implementation concept:**

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/verify-nudge\"",
            "async": false
          }
        ]
      }
    ]
  }
}
```

The `verify-nudge` script checks whether:
- R files were written during the session (track via a temp marker file updated by the PostToolUse hook)
- No `Rscript` or `devtools::test` command was observed after the last write

If both conditions are true, return a nudge: `"R files were written but not verified. Consider running the code or tests before finishing."`

This aligns with the "Verify After Write" convention currently buried in r-conventions.md.

---

## Implementation Priority

| Phase | Proposals | Effort | Impact |
|-------|-----------|--------|--------|
| **Phase 1: Quick wins** | P6 (mcp-setup description), P8 (trim rules), P9 (sync CLAUDE.md) | 1-2 hours | Fixes all high-severity review findings |
| **Phase 2: Platform adoption** | P1 (context fork), P5 (effort/model), P7 (allowed-tools) | 3-4 hours | Major context efficiency + UX improvement |
| **Phase 3: Auto-discovery** | P2 (paths), P3 (agent frontmatter) | 3-4 hours | Plugin feels intelligent, not just responsive |
| **Phase 4: Safety net** | P4 (format hook), P11 (verify nudge) | 2-3 hours | Catches convention drift automatically |
| **Phase 5: Test coverage** | P10 (eval files) | 2-3 hours | Regression safety for orchestration skills |

Phase 1 is non-controversial and should ship immediately. Phase 2 delivers the biggest user-facing improvement. Phase 3 makes the plugin feel like it understands your project. Phases 4 and 5 are insurance policies — they prevent quality from degrading as the plugin grows.
