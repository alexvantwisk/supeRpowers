# supeRpowers Plugin Test Suite

Adversarial test framework for the supeRpowers Claude Code marketplace plugin.

## Quick Start

```bash
cd supeRpowers
python tests/run_all.py
```

## Test Layers

### Layer 1: Structural Validation (`test_structural.py`)
Deterministic checks — no LLM needed, runs in seconds.

- YAML frontmatter format (name + description only)
- Description quality (length, triggers, boundaries)
- Line count limits (skills ≤300, agents ≤200, rules ≤150)
- Plugin.json glob coverage
- Reference file integrity (lazy-load pointers match actual files)
- R/Python script syntax validation
- Agent dispatch integrity (no broken references)
- Hooks system existence
- Eval.md coverage and quality indicators

### Layer 1b: Convention Compliance (`test_conventions.py`)
Scans all production code for R convention violations.

- No `%>%` (magrittr pipe) in production code
- No `=` assignment in R code blocks
- Base pipe `|>` used consistently in R scripts
- Double quotes preferred in R scripts

### Layer 2: Routing Matrix (`test_routing.py` + `routing_matrix.json`)
Tests whether skill descriptions correctly disambiguate overlapping domains.

42 test prompts across 9 categories:
1. Survival analysis ambiguity (r-stats vs r-clinical)
2. Regression/ML boundary (r-stats vs r-tidymodels)
3. Hypothesis test hijack (r-tdd vs r-stats)
4. Data scale ambiguity (r-data-analysis vs r-performance)
5. Package overload (r-package-dev vs r-project-setup vs r-package-skill-generator)
6. Quarto vs package vignette
7. Table vs visualization vs clinical
8. Cross-domain contamination
9. Broad trigger hijack prevention

### Layer 3: Adversarial Evals (`skills/*/eval.md`)
Per-skill evaluation files with:
- Skill-specific binary eval questions (not boilerplate)
- Happy path, edge case, AND adversarial test prompts
- Multiple boundary tests per skill (not just one)
- Harmful output prevention checks
- Measurable success criteria

## Running Individual Layers

```bash
python tests/run_all.py --layer 1     # Structural only
python tests/run_all.py --layer 1b    # Conventions only
python tests/run_all.py --layer 2     # Routing only
```

## Adding Tests

### New routing test
Add an entry to `routing_matrix.json`:
```json
{
  "id": "route-043",
  "prompt": "Your test prompt here",
  "expected_skill": "r-skill-name",
  "must_not_fire": ["competing-skill"],
  "discriminator": "why expected skill should win",
  "category": "category-name"
}
```

### New structural check
Add a check in `test_structural.py` using `suite.add(name, passed, message)`.

## Known Issues Detected

The test suite is designed to catch these known issues:
- `skill-auditor` description exceeds 1024 char limit
- `r-package-skill-generator` references 4 non-existent files
- `r-data-analysis` references 2 non-existent files (missing references/ directory)
- `r-tdd/scripts/run_coverage.R` uses `cli::` without requireNamespace guard
- `hooks/hooks.json` referenced in plugin.json but doesn't exist
- `skill-creator` referenced by 2 skills but doesn't exist as a skill
- Survival analysis routing ambiguity between r-stats and r-clinical
- "learn package" trigger in r-package-skill-generator is overly broad
