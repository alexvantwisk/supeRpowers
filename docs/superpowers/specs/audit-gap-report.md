# supeRpowers Skill Audit — Gap Report

**Date:** 2026-03-23
**Rubric:** 38-check (7 sections: D, C, G, E, V, O, T)
**Skills audited:** 16
**Method:** Deterministic script (16 rubric checks) + judgment scoring (22 rubric checks)

## Summary Table

Sorted by score ascending (worst first for prioritization).

| Skill | Score | D | C | G | E | V | O | T | Top Fix |
|-------|-------|---|---|---|---|---|---|---|---------|
| r-tables | 29/38 | 7 | 6 | 6 | 3 | 2 | 2 | 4 | Fix 32 convention violations; trim obvious content |
| r-stats | 31/38 | 7 | 6 | 6 | 3 | 1 | 4 | 4 | Trim obvious content; add feedback loop |
| r-tidymodels | 31/38 | 7 | 6 | 6 | 3 | 1 | 4 | 4 | Trim obvious content; add feedback loop |
| r-quarto | 32/38 | 7 | 6 | 6 | 4 | 2 | 3 | 4 | Add feedback loop; add agent dispatch |
| r-tdd | 32/38 | 7 | 5 | 6 | 3 | 4 | 3 | 4 | Create references/ dir; add agent dispatch |
| r-visualization | 32/38 | 7 | 6 | 6 | 3 | 3 | 3 | 4 | Trim obvious content; add agent dispatch |
| r-clinical | 33/38 | 7 | 7 | 6 | 3 | 2 | 4 | 4 | Fix 16 convention violations; add feedback loop |
| r-data-analysis | 33/38 | 7 | 6 | 6 | 3 | 3 | 4 | 4 | Trim obvious content; add feedback loop |
| r-performance | 33/38 | 7 | 7 | 6 | 3 | 3 | 3 | 4 | Fix 12 convention violations; add agent dispatch |
| skill-auditor | 33/38 | 7 | 6 | 6 | 4 | 4 | 2 | 4 | Add sibling boundary with r-package-skill-generator |
| r-debugging | 34/38 | 7 | 6 | 6 | 3 | 4 | 4 | 4 | Create references/ dir; fix convention violations |
| r-shiny | 34/38 | 7 | 6 | 6 | 3 | 4 | 4 | 4 | Trim obvious content; fix convention violations |
| r-targets | 34/38 | 7 | 6 | 6 | 3 | 4 | 4 | 4 | Fix 8 convention violations; trim obvious content |
| r-package-dev | 35/38 | 7 | 7 | 6 | 4 | 3 | 4 | 4 | Add scripts/ dir |
| r-project-setup | 35/38 | 7 | 7 | 6 | 4 | 3 | 4 | 4 | Add scripts/ dir |
| r-package-skill-generator | 38/38 | 7 | 7 | 6 | 5 | 5 | 4 | 4 | None needed |

**Plugin average:** 33.1/38 (87%)
**Perfect score:** 1 skill (r-package-skill-generator)
**Below 32:** 3 skills (r-tables, r-stats, r-tidymodels)

---

## Section Averages

| Section | Avg | Perfect | Weakest |
|---------|-----|---------|---------|
| D: Description | 7.0/7 | 16/16 | (none) |
| C: Content Efficiency | 6.3/7 | 4/16 | r-tdd (5/7) |
| G: Gotchas | 6.0/6 | 16/16 | (none) |
| E: Examples | 3.3/5 | 1/16 | Most at 3/5 |
| V: Scripts & Verification | 2.9/5 | 1/16 | r-stats, r-tidymodels (1/5) |
| O: Orchestration | 3.4/4 | 10/16 | r-tables, skill-auditor (2/4) |
| T: Testability | 4.0/4 | 16/16 | (none) |

**Strongest sections:** D (100%), G (100%), T (100%)
**Weakest sections:** V (58%), E (66%)

---

## Most Common Failures

Sorted by frequency across 16 skills.

| Check | Fails | Description | Fix Strategy |
|-------|-------|-------------|-------------|
| E1 | 15/16 | No code blocks in Examples section | Restructure Examples with fenced code blocks the scanner detects |
| V2 | 12/16 | No scripts/ directory | Add scripts where computation is deterministic; accept N/A for instruction-only skills |
| E5 | 10/16 | Convention violations in code blocks | Audit all code for `%>%`, `=` assignment, single quotes; fix to match r-conventions.md |
| C1 | 8/16 | Obvious content (restates standard docs) | Strip API docs Claude already knows; focus on gotchas, non-obvious patterns, opinionated guidance |
| V3 | 8/16 | No script error handling | Cascading from V2; add tryCatch/error messages to existing scripts |
| V1 | 7/16 | No feedback loop | Add verify-fix-repeat patterns for quality-critical operations |
| O2 | 5/16 | No agent dispatch lines | Add named agent handoff guidance (r-code-reviewer, r-statistician, etc.) |
| C3 | 2/16 | No references/ for long skill | Create references/ dir and offload deep-dive content |
| V5 | 2/16 | MCP tool reference issues | Use fully qualified `Server:tool_name` format |
| C7 | 1/16 | Time-sensitive content | Remove version-specific references and dates |
| O1 | 1/16 | Territory overlap | Tighten domain definition; remove overlapping content |
| O3 | 1/16 | Missing sibling boundary | Add explicit "X handles Y, this skill handles Z" |
| O4 | 1/16 | No sibling cross-references | Add sibling skill names to description |

---

## Priority Fix List

Based on impact ordering D > G > O > C > E > T > V and cross-skill frequency.

### Tier 1: High Impact, Many Skills

1. **Fix E5 convention violations (10 skills)**
   Affected: r-clinical (16), r-data-analysis (5), r-debugging (5), r-performance (12), r-shiny (4), r-stats (4), r-tables (32), r-targets (8), r-tdd (2), r-tidymodels (2), r-visualization (12)
   Action: Run `grep -rn '%>%' skills/` and fix all `%>%` to `|>`. Audit for `=` assignment, single quotes, camelCase.
   **r-tables has 32 violations — highest urgency.**

2. **Fix E1 example detection (15 skills)**
   Affected: All except r-package-skill-generator
   Root cause: Most skills DO have code in their Examples section, but the deterministic scanner counts 0. Likely a section heading format issue or code block delimiter mismatch. Investigate `score_skill.py` E1 detection logic and fix either the skills or the scanner.

3. **Trim obvious content / C1 (8 skills)**
   Affected: r-data-analysis, r-shiny, r-stats, r-tables, r-targets, r-tdd, r-tidymodels, r-visualization
   Action: Strip standard API docs (basic function syntax, common parameter tables) that Claude already knows. Replace with gotcha-dense, opinionated content.

### Tier 2: Medium Impact

4. **Add feedback loops / V1 (7 skills)**
   Affected: r-clinical, r-data-analysis, r-quarto, r-stats, r-tables, r-tidymodels, r-visualization
   Action: Add a "Verification" section with validate-fix-repeat patterns specific to each domain.

5. **Add agent dispatch lines / O2 (5 skills)**
   Affected: r-performance, r-quarto, r-tdd, r-visualization, r-tables
   Action: Add 1-2 lines naming agents and trigger conditions for handoff.

6. **Create references/ for monolithic skills (2 skills)**
   Affected: r-debugging (263 lines, no refs), r-tdd (300 lines, no refs)
   Action: Extract deep-dive content into references/ subdirectory.

### Tier 3: Low Impact / Skill-Specific

7. **skill-auditor: Add boundary with r-package-skill-generator (O3/O4)**
8. **r-quarto: Remove "Quarto 1.4+" version reference (C7)**
9. **r-tables: Tighten territory vs r-quarto and r-visualization (O1)**
10. **r-tdd: Add tryCatch to run_coverage.R (V3)**

---

## Individual Report Cards

### r-package-skill-generator — 38/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ███████ 7/7
G: Gotchas                 ██████  6/6
E: Examples                █████   5/5
V: Scripts & Verification  █████   5/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

Perfect score. No failures.

---

### r-package-dev — 35/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ███████ 7/7
G: Gotchas                 ██████  6/6
E: Examples                ████░   4/5
V: Scripts & Verification  ███░░   3/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks detected in Examples (likely parser issue) | LOW |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts to evaluate for error handling | LOW |

Top 3 Fixes: (1) Add scripts/ with R CMD check helper, (2) Investigate E1 detection, (3) Consider testing subsection content before r-tdd handoff.

---

### r-project-setup — 35/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ███████ 7/7
G: Gotchas                 ██████  6/6
E: Examples                ████░   4/5
V: Scripts & Verification  ███░░   3/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks detected in Examples | LOW |
| V2 | No scripts/ directory | MEDIUM |
| V3 | No scripts for error handling | LOW |

Top 3 Fixes: (1) Add validate-scaffold.R script, (2) Investigate E1 detection, (3) Fix .Rproj template BuildType inconsistency.

---

### r-debugging — 34/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ████░   4/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C3 | 263-line monolith with no references/ directory | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 5 convention violations | MEDIUM |
| V2 | No scripts/ directory | LOW |

Top 3 Fixes: (1) Create references/ and offload gotchas table + browser commands, (2) Fix 5 convention violations, (3) Add scripts/ with reprex template.

---

### r-shiny — 34/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ████░   4/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Restates standard Shiny docs (reactivity table, bslib functions) | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 4 convention violations | LOW |
| V2 | No scripts/ directory | LOW |

Top 3 Fixes: (1) Strip obvious reactivity/bslib docs, (2) Fix 4 convention violations, (3) Add expected output annotations to examples.

---

### r-targets — 34/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ████░   4/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Core Workflow Commands and Target Formats tables restate standard docs | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 8 convention violations | MEDIUM |
| V2 | No scripts/ directory | LOW |

Top 3 Fixes: (1) Fix 8 convention violations, (2) Condense obvious command/format tables, (3) Investigate E1 detection.

---

### r-clinical — 33/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ███████ 7/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ██░░░   2/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 16 convention violations | HIGH |
| V1 | No feedback loop for regulatory-grade work | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |

Top 3 Fixes: (1) Fix 16 convention violations, (2) Add verification loop for CDISC compliance, (3) Investigate E1 detection.

---

### r-data-analysis — 33/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ███░░   3/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Restates standard dplyr/tidyr/stringr docs | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 5 convention violations | LOW |
| V1 | No feedback loop (verify row counts, types after transforms) | MEDIUM |
| V2 | No scripts/ directory | LOW |

Top 3 Fixes: (1) Strip obvious API docs, (2) Add verification steps for joins/transforms, (3) Fix 5 convention violations.

---

### r-performance — 33/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ███████ 7/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ███░░   3/5
O: Orchestration           ███░    3/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 12 convention violations | HIGH |
| O2 | No agent dispatch lines | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |

Top 3 Fixes: (1) Fix 12 convention violations, (2) Add agent dispatch to r-code-reviewer, (3) Investigate E1 detection.

---

### skill-auditor — 33/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ████░   4/5
V: Scripts & Verification  ████░   4/5
O: Orchestration           ██░░    2/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks in Examples (prompt-only examples) | MEDIUM |
| C7 | "38-check" count hardcoded in 4 places | LOW |
| O3 | No boundary with r-package-skill-generator | MEDIUM |
| O4 | No sibling skill names in description | MEDIUM |
| V5 | Tool references without fully qualified format | LOW |

Top 3 Fixes: (1) Add input/output example showing sample report card, (2) Add sibling boundary with r-package-skill-generator, (3) Parameterize check count.

---

### r-quarto — 32/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ████░   4/5
V: Scripts & Verification  ██░░░   2/5
O: Orchestration           ███░    3/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| E1 | 0 code blocks detected in Examples | LOW |
| C7 | "Quarto 1.4+" version reference in yaml-config-cheatsheet.md | LOW |
| V1 | No feedback loop for rendered output | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |
| O2 | No agent dispatch lines | MEDIUM |

Top 3 Fixes: (1) Add agent dispatch lines, (2) Add render-verify-fix feedback loop, (3) Remove version-specific references.

---

### r-tdd — 32/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      █████░░ 5/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ████░   4/5
O: Orchestration           ███░    3/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Core Expectations restates standard testthat docs | MEDIUM |
| C3 | 300-line monolith with no references/ directory | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 2 convention violations | LOW |
| O2 | No agent dispatch to r-code-reviewer or r-pkg-check | MEDIUM |
| V3 | run_coverage.R lacks tryCatch | LOW |

Top 3 Fixes: (1) Create references/ and offload testing patterns, (2) Add agent dispatch lines, (3) Add tryCatch to run_coverage.R.

---

### r-visualization — 32/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ███░░   3/5
O: Orchestration           ███░    3/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Majority restates standard ggplot2 API docs | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 12 convention violations | HIGH |
| O2 | No agent dispatch lines | MEDIUM |
| V1 | No feedback loop for iterative refinement | MEDIUM |
| V2 | No scripts/ directory | LOW |

Top 3 Fixes: (1) Strip standard ggplot2 docs, focus on journal themes/gotchas, (2) Fix 12 convention violations, (3) Add agent dispatch and verification loop.

---

### r-stats — 31/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  █░░░░   1/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Core model-fitting sections restate standard R library docs | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | 4 convention violations | LOW |
| V1 | No feedback loop for assumption checking | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |
| V5 | No MCP tool references | LOW |

Top 3 Fixes: (1) Strip standard model-fitting syntax, (2) Add assumption-checking feedback loop, (3) Fix 4 convention violations.

---

### r-tidymodels — 31/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  █░░░░   1/5
O: Orchestration           ████    4/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Restates standard tidymodels API docs | MEDIUM |
| E1 | Only 1 code block in Examples (need 2+) | MEDIUM |
| E5 | 2 convention violations | LOW |
| V1 | No feedback loop for pipeline validation | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |
| V5 | No MCP tool references | LOW |

Top 3 Fixes: (1) Strip obvious API docs, (2) Add pipeline verification loop, (3) Add second worked example.

---

### r-tables — 29/38

```
D: Description Quality     ███████ 7/7
C: Content Efficiency      ██████░ 6/7
G: Gotchas                 ██████  6/6
E: Examples                ███░░   3/5
V: Scripts & Verification  ██░░░   2/5
O: Orchestration           ██░░    2/4
T: Testability             ████    4/4
```

| Check | Finding | Impact |
|-------|---------|--------|
| C1 | Bulk restates gt/gtsummary API docs | MEDIUM |
| E1 | 0 code blocks detected in Examples | LOW |
| E5 | **32 convention violations** — worst in plugin | **HIGH** |
| O1 | Territory bleeds into r-quarto (integration section) and r-visualization (sparklines) | MEDIUM |
| O2 | No agent dispatch lines | MEDIUM |
| V1 | No feedback loop for table output quality | MEDIUM |
| V2 | No scripts/ directory | LOW |
| V3 | No scripts for error handling | LOW |

Top 3 Fixes: (1) Fix 32 convention violations immediately, (2) Remove Quarto integration section from references to fix O1 overlap, (3) Add agent dispatch and verification loop.

---

## Overlap Warnings

| Pair | Overlap % | Risk | Status |
|------|-----------|------|--------|
| r-stats / r-tidymodels | 40% | HIGH | Managed — explicit boundaries in both descriptions |
| r-tables / r-visualization | 39% | MEDIUM | r-tables bleeds into viz territory (sparklines, data bars) |
| r-package-dev / r-tdd | 31% | LOW | Managed — explicit boundaries in both descriptions |
| r-quarto / r-tables | 31% | MEDIUM | r-tables references have Quarto integration section |

---

## Methodology Notes

- **Deterministic checks** ran via `score_skill.py` with `--conventions rules/r-conventions.md --max-lines 300 --siblings-dir skills/`
- **Judgment checks** scored by 16 parallel subagents (4 batches of 4), each reading full SKILL.md + references + rubric
- **Scores recounted** from individual P/F check results per rubric warning about subagent arithmetic
- **E1 systematic failure** (15/16 FAIL) likely reflects a scanner detection issue rather than genuinely absent examples — most skills DO have code in their Examples section. Recommend investigating `score_skill.py` E1 logic before mass-fixing skills.
- **V2/V3 failures** are expected for instruction-only R skills. Only 4 skills legitimately benefit from scripts: r-package-skill-generator (has them), r-tdd (has them), skill-auditor (has them), and r-package-dev/r-project-setup (candidates for addition).
