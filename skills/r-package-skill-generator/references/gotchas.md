# Gotchas Extraction Template

Template for identifying and documenting common failure points from an R package.
Use this structure when creating `references/gotchas.md` for a generated skill.

---

## Gotcha Table Format

Use this table format consistently across all generated skills:

```markdown
| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Short description of what the user does wrong | Why this causes a problem (error message, silent wrong result, or performance issue) | The correct approach with code snippet |
```

---

## Sources for Gotcha Discovery

### 1. GitHub Issues (Highest Signal)

Search for issues labeled `bug`, `question`, or `help wanted`. Focus on:
- Issues with 3+ thumbs up (common pain point)
- Issues that were closed with a workaround, not a fix
- Recurring questions in different issues

### 2. Stack Overflow

Search `[r] [package-name]` sorted by votes. The top-voted questions reveal
the most common confusion points.

### 3. Package Test Suite

Look in `tests/testthat/` for:
- Tests with names containing "error", "fail", "edge", "corner", "warn"
- `expect_error()` calls — these document known failure modes
- `expect_warning()` calls — these document expected warnings

### 4. Package NEWS/Changelog

Breaking changes between versions create gotchas for users on older versions
or following outdated tutorials.

### 5. Vignette Warnings

Authors often include "Note:" or "Warning:" blocks in vignettes documenting
non-obvious behavior.

---

## Gotcha Categories

### Type 1: Silent Wrong Results
The code runs without error but produces incorrect output. **Highest priority.**

Example: Forgetting `family = binomial` in `glm()` silently fits a linear model.

### Type 2: Confusing Error Messages
The code fails, but the error message does not point to the actual cause.

Example: "object not found" when the real issue is data masking in dplyr.

### Type 3: Performance Traps
The code works correctly but is orders of magnitude slower than necessary.

Example: Growing a vector with `c(result, x)` inside a loop.

### Type 4: API Confusion
Two similar functions or arguments that users mix up.

Example: `predict(type = "response")` vs `predict(type = "link")` in GLMs.

### Type 5: Scope/Side Effects
Functions that modify state in unexpected ways.

Example: `data.table::setDT()` mutates the original data frame in the caller's scope.

---

## Prioritization

1. **Silent wrong results** — always include; users cannot detect these without help
2. **Confusing errors with 3+ GitHub issues** — high frequency, high frustration
3. **Performance traps on common operations** — users hit these on real-world data
4. **API confusion between popular functions** — prevents wasted debugging time
5. **Scope/side effects** — include when the side effect is genuinely surprising

---

## Quality Checks

- Every gotcha must have a **concrete "Fix" column** with working code
- Include the **actual error message** when applicable (improves searchability)
- Avoid hypothetical gotchas — only document traps that appear in issues/SO/tests
- Limit to 8-12 gotchas per skill — prioritize ruthlessly
- Use project R conventions: `|>`, `<-`, `snake_case`, double quotes
