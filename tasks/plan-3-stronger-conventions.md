# Plan 3: Stronger Conventions Rule

## Summary

Strengthen `rules/r-conventions.md` by tightening directive language and adding high-value missing patterns, staying within the 150-line hard limit. Currently 119 lines; budget is ~30 lines for additions.

**Deliverables:** 1 modified file (`rules/r-conventions.md`)

## Current Coverage Analysis (119 lines)

The rule currently covers:
- Pipe operator (`|>` vs `%>%`) — 8 lines + code block
- Paradigm (tidyverse-first, when to use data.table/base R) — 6 lines
- Style (formatter, linter, naming, assignment, strings, line length, spacing) — 8 lines
- Environment management (renv) — 5 lines
- R version targeting (>= 4.1.0) — 2 lines
- Package development toolchain — 8 lines
- Documentation / roxygen2 — 7 lines
- Error handling with cli — 12 lines + code block
- Tidy evaluation — 15 lines + code block
- File organization — 3 lines

**What's missing (referenced by skills but not in the rule):**
1. `vapply()` over `sapply()` when using base R (r-code-reviewer checks for this)
2. `withr::` for temporary side effects (r-tdd references this heavily)
3. `dplyr::if_else()` over base `ifelse()` with dates/types (r-code-reviewer flags this)
4. `TRUE`/`FALSE` never `T`/`F` (r-code-reviewer flags this)
5. `seq_along(x)` over `1:length(x)` (r-code-reviewer flags this)
6. Function design principles (pure functions, explicit returns)

**What uses weak language:**
- Line 21: "If existing code uses `%>%`, match it for consistency but suggest migration" — too permissive
- Line 39: "Double quotes `\"` preferred" — should be stronger

## Proposed Changes

### Change 1: Tighten weak language (net 0 lines)

**Line 21 — pipe migration:**
```
# Before
If existing code uses `%>%`, match it for consistency but suggest migration to `|>`.

# After
If existing code uses `%>%`, migrate it to `|>` when touching that code.
```

**Line 39 — strings:**
```
# Before
- **Strings:** Double quotes `"` preferred

# After
- **Strings:** Double quotes `"` always (single quotes only inside double-quoted strings)
```

### Change 2: Add Quick Reference — Anti-Patterns (add ~16 lines after File Organization)

Insert before the final line (119), at the end of the file:

```markdown

## Quick Reference — Anti-Patterns

| Never | Always |
|-------|--------|
| `sapply()` | `vapply()` or `purrr::map_*()` — type-safe |
| `ifelse()` | `dplyr::if_else()` — preserves type, strict |
| `T` / `F` | `TRUE` / `FALSE` — T and F can be overwritten |
| `1:length(x)` | `seq_along(x)` — safe when `x` is empty |
| `library()` in functions | `pkg::fn()` or `@importFrom` — explicit deps |
| `setwd()` / `rm(list=ls())` | `here::here()` / restart R session |
| `return(invisible(NULL))` at end | Just `invisible(NULL)` — implicit return |
| Modify input in place | Return new object — immutability preferred |
```

### Change 3: Add Function Design section (add ~8 lines)

Insert after the anti-patterns table:

```markdown

## Function Design

- Prefer pure functions: same inputs → same outputs, no side effects
- Use `withr::local_*()` / `withr::defer()` for temporary side effects (tempfiles, options, env vars)
- Return values explicitly; use `invisible()` for side-effect functions
- Keep functions under 50 lines; extract helpers when growing beyond that
```

## Line Budget

| Section | Lines |
|---------|-------|
| Current content | 119 |
| Anti-patterns table (header + 8 rows + blank lines) | +12 |
| Function Design (header + 4 bullets + blank line) | +7 |
| Language tightening | +0 (replacements) |
| **Total** | **138** |

138 lines — within the 150-line limit with 12 lines of buffer.

## Implementation Tasks

- [ ] **Task 1:** Tighten line 21 (pipe migration language)
- [ ] **Task 2:** Tighten line 39 (string quotes language)
- [ ] **Task 3:** Add `## Quick Reference — Anti-Patterns` table after line 118
- [ ] **Task 4:** Add `## Function Design` section after the anti-patterns table
- [ ] **Task 5:** Verify final line count is ≤ 150

## Verification Checklist

- [ ] File is ≤ 150 lines: `wc -l rules/r-conventions.md`
- [ ] No YAML frontmatter (rule files have none)
- [ ] No `%>%` in the file: `grep -n '%>%' rules/r-conventions.md` (only in the "WRONG" example)
- [ ] Imperative reference card style maintained (no prose paragraphs)
- [ ] Anti-patterns table entries don't contradict existing skills
- [ ] All new patterns are already checked by r-code-reviewer agent (alignment)
- [ ] `withr::` addition aligns with r-tdd skill's usage of `withr::local_*()` in examples
