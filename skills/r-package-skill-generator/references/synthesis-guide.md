# Synthesis & Skill Drafting Guide

How to take the four agent reports and synthesise them into a complete
skill, following the SKILL.md format documented in CLAUDE.md.

## Synthesis Checklist

### 1. Cross-Reference the Reports

Read all four reports and build a unified picture:

| API Agent says | Architecture says | Idiom says | Edge-Case says | Synthesis note |
|---|---|---|---|---|
| `fn()` takes `x` param | `fn()` calls `internal_validate()` | Use `fn()` in pipes | `fn()` fails on NA input | Core function, pipe-friendly, needs NA warning |

### 2. Resolve Conflicts

Common conflicts and how to resolve:

- **Deprecated but still shown in examples**: Check NEWS.md for the
  replacement. Mark as "teach the replacement, mention deprecated version
  as legacy."
- **Vignette uses different style than man page**: Prefer the vignette style
  (more recent, more intentional).
- **Test shows behaviour that contradicts documentation**: Trust the tests
  (they reflect actual behaviour).

### 3. Rank Functions by Importance

Not every export deserves equal coverage. Rank by:

1. Appears in vignettes and/or README (highest signal)
2. Referenced in other functions' `@seealso` or examples
3. Has a dedicated man page (vs inherited S3 method docs)
4. Complexity of usage (more complex = more guidance needed)

Mark the **top 10–15** as "essential" and everything else as "reference only."

### 4. Write the Synthesis Brief

Create `reports/synthesis.md` with this structure:

```markdown
# Synthesis Brief: {package-name}

## Package Identity
- Name, version, maintainer
- Ecosystem: tidyverse / base R / Bioconductor / other
- Primary use case in one sentence
- Class systems in use

## Core Mental Models
{2-4 key concepts a user needs before writing any code}

## Essential Functions (ranked)
1. `fn_a()` — {purpose} — {key gotcha if any}
2. `fn_b()` — {purpose}
...

## Key Patterns (from Idiom Agent)
- Pattern 1: {name} — {one-line description}
- Pattern 2: ...

## Critical Gotchas (from Edge-Case Agent)
- Gotcha 1: {trigger} → {fix}
- Gotcha 2: ...

## Ecosystem Context
- Works well with: {packages}
- Conflicts with: {packages, if any}
- Installation notes: {CRAN / Bioconductor / GitHub-only}

## Suggested Skill Structure
- SKILL.md: overview, concepts, top N functions, patterns, gotchas
- references/api-reference.md: full function catalogue
- references/patterns.md: extended workflow recipes
- references/gotchas.md: complete edge-case + error message list

## Quality Criteria for Validation
- All code examples match actual function signatures
- Examples use the package's own idioms (pipe style, NSE)
- No fabricated functions or parameters
- Gotchas include real error messages
```

### 5. Draft the Skill

Once `reports/synthesis.md` is ready, draft the skill manually using:

1. The synthesis brief as the primary context
2. All four agent reports as supplementary material
3. The `pkg-inventory.json` for structured metadata
4. The quality criteria listed in the synthesis brief
5. The SKILL.md format and conventions from CLAUDE.md

After drafting, validate with the skill-auditor to ensure compliance with
the 38-check rubric.
