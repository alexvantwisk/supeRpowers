---
name: r-package-skill-generator
description: >
  Use when the user provides a GitHub link to an R package and wants to generate
  a Claude skill from it, or asks Claude to become an expert at using a specific
  R package. Automates cloning, exploration via parallel sub-agents, and
  assembly of a complete SKILL.md with references from any public R package
  repository.
  Triggers: generate skill, create skill from package, GitHub package, teach
  Claude a package from GitHub, learn package from repo, reverse-engineer package,
  package skill, analyze R package.
  Do NOT use for manually writing or editing skills — write the skill manually following the SKILL.md format in CLAUDE.md instead.
  Do NOT use for general R package development — use r-package-dev instead.
  Do NOT use for learning how to use an R package — use the relevant domain skill (r-data-analysis, r-visualization, etc.) instead.
---

# R Package Skill Generator

Turn any R package GitHub repository into a Claude skill that makes Claude an
expert at using that package.

```
GitHub URL -> Clone -> Dispatch Explore Agents -> Collect Reports
           -> Synthesise -> Draft Skill -> Review -> Output
```

**Workdir convention:** All paths below use `$WORKDIR` as a placeholder. It
defaults to a temporary directory created by `setup_workspace.py`. Override
with `--workdir` if needed.

---

## Progress Tracking

Use TaskCreate at the start of this workflow — one task per stage below. Mark each `in_progress` when starting, `completed` when artifacts are written to `$WORKDIR/reports/`.

- "Step 0: Accept input + clone repo"
- "Step 1: Scan and inventory"
- "Step 2: Dispatch exploration agents"
- "Step 3: Synthesise reports"
- "Step 4: Draft skill from synthesis"

Long-running multi-agent workflow with file artifacts in `$WORKDIR` — task state mirrors which reports have been written.

---

## Step 0 — Accept Input

The user provides a GitHub URL. Validate it:
- Must be a valid `https://github.com/{owner}/{repo}` URL
- The repo must contain a `DESCRIPTION` file with `Package:` field

```bash
python3 scripts/setup_workspace.py <URL>
# Creates $WORKDIR with pkg-source/, reports/, and pkg-inventory.json
```

If the clone fails (private repo, bad URL), tell the user and stop.

---

## Step 1 — Scan & Inventory

The setup script already runs the scanner, but you can re-run manually:

```bash
python3 scripts/scan_r_package.py $WORKDIR/pkg-source --output $WORKDIR/pkg-inventory.json
```

This produces `pkg-inventory.json` with:
- Package name, title, description, version, authors
- All exported functions (from NAMESPACE)
- File counts and sizes for R/, man/, tests/, vignettes/, src/
- Dependencies (Imports, Suggests, Depends)
- Whether S3/S4/R6 classes are present
- Vignette titles

Read the inventory before proceeding. It guides which agents to emphasise.

---

## Step 2 — Dispatch Exploration Agents

Each agent has a reference file in `agents/`. Read the relevant agent file
before dispatching or executing inline. Pass `$WORKDIR` so agents know where
to find the package source and write reports.

### Agent Dispatch Strategy

**With subagents (Claude Code):** Spawn all four agents in parallel. Each
writes its report to `$WORKDIR/reports/`. Wait for all to complete.

**Without subagents (Claude.ai):** Execute agents sequentially: API Agent
first (most critical), then Architecture, Idiom, Edge-Case. For small
packages (<20 exports), merge Architecture and Idiom into one pass.

### Agent Summaries

| Agent | Reads | Writes | Reference |
|-------|-------|--------|-----------|
| API Agent | `man/`, NAMESPACE, `R/` | `$WORKDIR/reports/api-surface.md` | `agents/api-agent.md` |
| Architecture Agent | `R/`, DESCRIPTION, NAMESPACE | `$WORKDIR/reports/architecture.md` | `agents/architecture-agent.md` |
| Idiom Agent | `R/`, vignettes/, README | `$WORKDIR/reports/idioms.md` | `agents/idiom-agent.md` |
| Edge-Case Agent | `tests/`, vignettes/, GitHub issues | `$WORKDIR/reports/edge-cases.md` | `agents/edge-case-agent.md` |

---

## Step 3 — Synthesise

After all agents complete, read all four reports and synthesise into a
single unified brief. See `references/synthesis-guide.md` for the full
checklist.

1. **Resolve contradictions** — If agents disagree, investigate and pick
   the correct interpretation.
2. **Rank by importance** — Focus on the 5-15 most-used functions (high
   cross-reference count, vignette/README mentions, non-obvious behaviour).
3. **Extract patterns** — Identify 3-5 recurring usage patterns.
4. **Collect gotchas** — Deduplicate and prioritise edge cases.

Save the synthesised brief to `$WORKDIR/reports/synthesis.md`.

**Max 2 synthesis attempts.** If synthesis produces empty or contradictory
output after 2 attempts, present partial results to the user and ask for
guidance.

---

## Step 4 — Hand Off to the Skill Creator

Draft the skill manually using the synthesis brief and the structure below,
following the SKILL.md format documented in CLAUDE.md.

Include the following context when drafting the skill:

1. **What the skill should do**: "Teach Claude to be an expert at using
   the {package-name} R package. Claude should be able to write correct,
   idiomatic code using the package, know the key functions, common
   patterns, and gotchas."

2. **Feed it the exploration reports** as source material:
   - `$WORKDIR/reports/api-surface.md`
   - `$WORKDIR/reports/architecture.md`
   - `$WORKDIR/reports/idioms.md`
   - `$WORKDIR/reports/edge-cases.md`
   - `$WORKDIR/reports/synthesis.md`
   - `$WORKDIR/pkg-inventory.json`

3. **Suggested skill structure**:
   - SKILL.md body: package overview, core concepts, top 10-15 functions,
     common patterns, gotchas, ecosystem notes
   - `references/api-reference.md`: full function catalogue
   - `references/patterns.md`: extended workflow examples
   - `references/gotchas.md`: complete edge-case list with error messages

4. **Quality criteria**:
   - Every code example uses correct function signatures
   - Examples use the package's own idioms (pipe style, NSE patterns)
   - No fabricated functions or parameters
   - Gotchas include actual error messages for searchability
   - The skill teaches function composition, not just isolated calls

### Output Location

The generated skill should be installed to `skills/{package-name}/`.

---

## Handling Special Cases

```
Is it a meta-package (tidyverse, tidymodels)?
  YES -> Cover the opinionated workflow, not every sub-package
  NO  -> How many exported functions?
           >100 -> Focus SKILL.md on top 20; full API in references/
           <=100 -> Standard coverage

Has compiled code (src/)?
  YES -> Note platform deps, focus on R-level API, mention perf traits
  NO  -> Standard

Has Shiny components?
  YES -> Add references/shiny-integration.md
  NO  -> Standard

Is it a Bioconductor package?
  YES -> Note BiocManager::install(), document special object classes
  NO  -> Standard
```

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Generating a skill for a thin wrapper package | Package has <10 exports and trivial logic; the skill adds no value over `?pkg::fn` | Check export count in inventory first; if <10 exports with no complex patterns, advise the user it is too thin |
| Missing non-exported helpers that are key to idioms | Agents only scan NAMESPACE exports; internal helpers like `.validate_input()` shape correct usage | Have the Architecture Agent also scan `R/` for frequently called internal functions |
| Overloading skill with every function instead of primary workflows | SKILL.md becomes a copy of the man pages; too long, no insight | Rank by cross-reference count and vignette mentions; top 10-15 functions in SKILL.md, full catalog in `references/` |
| Not checking if a skill already exists for the package | Generates a duplicate skill, wasting time and creating conflicts | Search `skills/` directory for existing `r-{package-name}` before starting |
| Synthesis producing >300 lines in SKILL.md | Violates the 300-line budget; skill fails validation | Move detailed API reference, patterns, and gotchas into `references/` subdirectory |
| Fabricating functions or parameters not in the package | Agents hallucinate plausible but non-existent API surface | Cross-check every function and argument against `man/` pages and NAMESPACE |
| Skipping validation after manual drafting | Without review, the skill may violate line limits, conventions, or frontmatter format | Run the skill-auditor after drafting to validate against the 38-check rubric |

---

## Examples

### Happy Path: Generate a Skill from a GitHub URL

**Prompt:** "Generate a Claude skill for the pointblank R package: https://github.com/rstudio/pointblank"

```
Step 0 — Accept Input
  $ python3 scripts/setup_workspace.py https://github.com/rstudio/pointblank
  Created workspace: /tmp/skill-gen-pointblank/
  Cloned to: /tmp/skill-gen-pointblank/pkg-source/
  Inventory: /tmp/skill-gen-pointblank/pkg-inventory.json

Step 1 — Scan & Inventory
  Package: pointblank  Version: 0.12.1  Exports: 87
  Has vignettes: 6  Has tests: yes  Has src/: no

Step 2 — Dispatch Exploration Agents (parallel)
  API Agent       -> reports/api-surface.md     (87 exports catalogued)
  Architecture    -> reports/architecture.md     (agent/validation/reporting layers)
  Idiom Agent     -> reports/idioms.md           (pipe-based validation workflow)
  Edge-Case Agent -> reports/edge-cases.md       (common YAML config pitfalls)

Step 3 — Synthesise
  Top functions: create_agent, col_vals_gt, col_vals_between, interrogate, ...
  Key patterns: agent pipeline, YAML-driven validation, informant reports
  Gotchas: agent vs informant confusion, YAML multiline quoting

Step 4 — Draft Skill
  Output: skills/r-pointblank/SKILL.md (182 lines)
          skills/r-pointblank/references/api-reference.md
          skills/r-pointblank/references/patterns.md
```

### Edge Case: Package with >100 Exports

**Prompt:** "Generate a skill for data.table: https://github.com/Rdatatable/data.table"

```
Step 1 — Scan & Inventory
  Package: data.table  Version: 1.16.0  Exports: 214
  WARNING: >100 exports detected.

Step 2 — Agent Strategy (adapted for large API)
  API Agent focuses on top 20 functions by vignette/README cross-reference:
    [, :=, fread, fwrite, merge, setkey, .SD, .N, fifelse, ...
  Remaining 194 exports -> references/api-reference.md only.

Step 3 — Synthesise
  SKILL.md covers top 20 functions + 5 patterns + gotchas.
  Full 214-export catalogue in references/api-reference.md.
  Line count: SKILL.md = 278 lines (under 300 budget).

Step 4 — Draft Skill
  Output: skills/r-data-table/SKILL.md (278 lines)
          skills/r-data-table/references/api-reference.md (420 lines)
          skills/r-data-table/references/patterns.md
          skills/r-data-table/references/gotchas.md
```

**More example prompts:**
- "Generate a Claude skill for the gt package from its GitHub repo"
- "Teach Claude to be an expert at the polars R package"
- "Create a skill from https://github.com/tidyverse/dplyr"
