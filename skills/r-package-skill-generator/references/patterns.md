# Workflow Patterns Template

Template for documenting idiomatic usage patterns extracted from an R package.
Use this structure when creating `references/patterns.md` for a generated skill.

---

## What Makes a Good Pattern

A pattern is a **reusable sequence of function calls** that accomplishes a
common task. Good patterns:

1. Appear in vignettes, README, or multiple test files
2. Combine 2+ functions from the package in a specific order
3. Have a clear input → transformation → output shape
4. Demonstrate the package author's intended idiom

---

## Pattern Template

```markdown
### Pattern: {Descriptive Name}

**When to use:** One sentence describing the use case.

**Input:** What the user starts with (data type, shape).

**Output:** What the user gets (data type, shape).

\```r
# Step 1: Setup
data <- setup_function(input)

# Step 2: Transform
result <- data |>
  package_fn_one(arg = "value") |>
  package_fn_two()

# Step 3: Extract result
final <- extract_function(result)
\```

**Variations:**
- For grouped data, wrap in `.by` or `group_by()`
- For large data, consider `lazy_version()` instead
```

---

## Pattern Categories

Organize patterns into these standard categories:

### 1. Quick Start
The simplest end-to-end usage — what goes in the README "Getting Started" section.
One pattern, 5-10 lines of code.

### 2. Data Input/Output
Reading data into the package's expected format and writing results out.

### 3. Core Workflow
The 3-5 most common multi-step operations. These are the patterns most users need.

### 4. Advanced Composition
Combining multiple package features, integration with other packages (ggplot2,
dplyr, etc.), or non-obvious function chaining.

### 5. Debugging/Inspection
Patterns for inspecting intermediate state, validating inputs, or diagnosing
unexpected output.

---

## Extraction Process

1. **Scan vignettes** — each vignette section usually demonstrates one pattern
2. **Scan README examples** — the README "Usage" section shows the author's
   preferred quick-start pattern
3. **Scan test files** — `tests/testthat/test-*.R` files show edge-case patterns
4. **Cross-reference** — functions that appear together across multiple sources
   form the strongest patterns
5. **Prioritize** — rank by frequency of appearance across sources

---

## Conventions for Generated Pattern Code

- Use `|>` (never `%>%`)
- Use `<-` for assignment (never `=`)
- Use `snake_case` for all identifiers
- Use double quotes for strings
- Include comments explaining each step
- Show realistic (not toy) data shapes
