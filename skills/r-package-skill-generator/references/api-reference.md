# API Reference Template

Template for organizing the generated API reference file for an R package skill.
Use this structure when creating `references/api-reference.md` for a generated skill.

---

## Organization Principles

1. **Group by domain/workflow**, not alphabetically by function name
2. **Lead with the 5-10 most-used functions** in a "Core API" section
3. **Separate S3/S4 methods** from top-level functions
4. **Omit internal functions** (prefixed with `.` or not exported in NAMESPACE)
5. **Flag deprecated functions** — mention the replacement, do not document usage

---

## Template Structure

```markdown
# {package-name} API Reference

## Core Functions

| Function | Purpose | Key Arguments |
|----------|---------|---------------|
| `fn_one()` | Brief description | `arg1`, `arg2` (default: value) |
| `fn_two()` | Brief description | `arg1` |

## {Workflow Category 1} (e.g., Data Input)

### fn_one()

Brief description of what it does and when to use it.

Signature: `fn_one(data, arg1 = default, arg2 = NULL)`

Key arguments:
- `data` — input data frame or tibble
- `arg1` — what it controls (default: `value`)
- `arg2` — optional; when to use it

Returns: description of return type

Example:
\```r
result <- fn_one(df, arg1 = "value")
\```

## {Workflow Category 2} (e.g., Transformation)

[Same pattern as above]

## Class Methods (if S3/S4/R6)

### ClassName

Constructor: `ClassName$new(arg1, arg2)`

Key methods:
- `$method_one()` — what it does
- `$method_two(arg)` — what it does

Key accessors:
- `$field_name` — what it returns

## Deprecated Functions

| Function | Replacement | Since |
|----------|-------------|-------|
| `old_fn()` | `new_fn()` | v1.2.0 |
```

---

## Triage Rules for Large Packages (>100 exports)

1. **SKILL.md body:** Top 10-15 functions by vignette/README cross-reference count
2. **api-reference.md:** All non-deprecated exports, grouped by topic
3. **Omit entirely:** Internal functions (`.helper()`), re-exports from other packages
4. **Flag but do not document:** Functions with minimal documentation or no examples in `man/`

---

## Documenting Parameter Patterns

For packages with recurring parameter patterns (e.g., `.data`, `.fn`, `...`),
document the pattern once in a "Common Parameter Patterns" section rather than
repeating in every function entry.

```markdown
## Common Parameter Patterns

- **`.data`** — A data frame, data frame extension, or lazy data frame
- **`.fn`** — A function or formula (purrr-style `~ .x + 1`)
- **`...`** — Tidy selection (e.g., `starts_with("x")`, `where(is.numeric)`)
```
