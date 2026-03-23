# Remediation Guide — Fixing Common Audit Failures

Per-section strategies for fixing the most common audit failures.

## Fixing Description Quality (Section D)

### Template: Rewriting a Description

**Before (weak):**
```yaml
description: Helps with data analysis tasks.
```

**After (strong):**
```yaml
description: >
  Use when performing data wrangling, cleaning, or transformation tasks.
  Provides expert guidance on tidy data pipelines, joins, reshaping, and
  type conversion using dplyr, tidyr, readr, and related packages.
  Triggers: data wrangling, data cleaning, dplyr, tidyr, mutate, filter,
  pivot, join, reshape, missing values, CSV import, column types.
  Do NOT use for statistical modeling — use r-stats instead.
  Do NOT use for performance optimization — use r-performance instead.
```

**Structure (proven in 15-skill audit):**
1. `Use when [primary trigger condition].` (opens with convention)
2. `[Third-person capability sentence.]` (what the skill provides)
3. `Triggers: [kw1], [kw2], [kw3], [kw4], [kw5+].` (5+ comma-separated keywords)
4. `Do NOT use for [territory] — use [sibling] instead.` (1+ negative boundaries)
5. Target 500 chars, hard limit 1024 chars

### Adding Negative Boundaries

List every sibling skill and explicitly exclude their territory:

```
Do NOT use for [sibling-1 territory] (use [sibling-1] instead),
[sibling-2 territory] (use [sibling-2] instead), or
[sibling-3 territory] (use [sibling-3] instead).
```

## Fixing Content Efficiency (Section C)

### Identifying Obvious Content

Ask these questions about each paragraph:
- "Does Claude already know this?" If yes, cut it.
- "Would a senior developer need this explained?" If no, cut it.
- "Is this standard library documentation?" If yes, link to official docs instead.

**Common candidates for removal:**
- Basic syntax explanations
- Standard library function signatures
- Well-known design patterns described from scratch
- Introductory context ("X is a popular framework for...")

### Trimming Strategy

1. Read the skill as if you're Claude with full training knowledge
2. Highlight every sentence that restates something Claude knows
3. Replace with the delta: what Claude should do DIFFERENTLY from its default
4. Move deep-dive content to `references/` if it exceeds 20 lines

## Fixing Gotchas (Section G)

### Template: Adding a Gotchas Section

Use the 3-column table format (proven across 15-skill audit — more scannable than paragraphs):

```markdown
## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Silent type coercion in joins | `merge()` converts factors to character without warning | Check `str()` after joins; use `dplyr::left_join()` which preserves types |
| Off-by-one in pagination | API pages start at 1, not 0; page 0 returns page 1 | Always start pagination loops at 1 |
| Encoding landmines | Excel on Windows uses CP1252, not UTF-8 | Specify `encoding = "UTF-8"` or detect with `readr::guess_encoding()` |
| Scope creep | Claude rewrites entire file when asked to fix one thing | Fix only the identified issue; show minimal diff |
```

**Rules for effective gotchas:**
- Each row is a real failure point Claude actually hits (not hypothetical)
- "Trap" column: name the specific mistake
- "Why It Fails" column: what goes wrong (one sentence)
- "Fix" column: specific action or code (not "handle appropriately")
- **Last row must be a scope constraint** (Overachiever prevention)
- Target 5-10 rows per skill

**Where to source gotchas:** Common Claude failure patterns, Stack Overflow top questions, package changelogs (breaking changes), test suites.

## Fixing Examples (Section E)

### Upgrading Prompt-Only to Input/Output Pairs

**Before (prompt only):**
```markdown
## Example Prompts
- "Clean up this CSV and show weekly totals by region"
```

**After (structured examples — proven format from 15-skill audit):**
```markdown
## Examples

### Happy Path: Cleaning messy data

**Prompt:** "Clean this CSV: fix column types, handle missing values, reshape to long"

\```r
# Input
df <- tibble(
  id = 1:3,
  q1_score = c(10, NA, 30),
  q2_score = c(40, 50, 60)
)

# Output
df |>
  pivot_longer(cols = starts_with("q"), names_to = "quarter", values_to = "score") |>
  filter(!is.na(score))
\```

### Edge Case: Join with duplicate keys

**Prompt:** "Join these tables — but one has duplicate IDs"

\```r
# Input — orders has duplicate customer_id
customers <- tibble(id = 1:3, name = c("Alice", "Bob", "Charlie"))
orders <- tibble(customer_id = c(1, 1, 2), amount = c(100, 200, 300))

# WRONG — silent row multiplication
customers |> left_join(orders, by = c("id" = "customer_id"))
# Returns 4 rows, not 3! Alice appears twice.

# CORRECT — check for duplicates first
stopifnot(!any(duplicated(orders$customer_id)))
\```

**More example prompts:**
- "Reshape this wide dataset to long format"
- "Parse dates from multiple formats in one column"
```

**Rules:** Every skill needs at minimum 1 happy path + 1 edge case with actual code. Keep 3-5 trigger prompts as a bulleted list at the end.

## Fixing Orchestration (Section O)

### Mapping Territory Boundaries

For each skill, define a one-sentence territory:

```
skill-a: Owns data import, cleaning, and reshaping.
skill-b: Owns statistical modeling and inference.
skill-c: Owns visualization and chart creation.
```

Where territories overlap, pick one owner and add explicit handoff:

```markdown
**Boundary with skill-b:** This skill handles data preparation up to
and including the analysis-ready dataset. Once the user asks to model,
test, or infer, hand off to skill-b.
```

## Fixing Testability (Section T)

### Generating Eval Criteria (Autoresearch Method)

For each skill, define 3-6 binary yes/no questions:

```markdown
## Eval Criteria

1. Does the output use the correct pipe operator (`|>` not `%>%`)? Y/N
2. Does the output include error handling for missing input? Y/N
3. Is the output under 50 lines (concise, not verbose)? Y/N
4. Does the code run without modification on the sample input? Y/N
5. Are all column names in snake_case? Y/N
```

**Rules for good eval questions:**
- Binary (yes/no), not ratings (1-10)
- Observable in the output (not subjective)
- 3-6 questions per skill (more causes gaming)
- Cover different quality dimensions (correctness, style, completeness)

### Defining Test Prompts

Pick 3+ prompts that exercise the skill's range:

```markdown
## Test Prompts

1. **Happy path:** "Clean this CSV file and show summary statistics"
2. **Edge case:** "This file has no headers and mixed delimiters"
3. **Boundary:** "Merge these two datasets and check for duplicates"
```
