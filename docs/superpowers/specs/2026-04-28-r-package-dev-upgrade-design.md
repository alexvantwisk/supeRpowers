# r-package-dev Skill Upgrade — Design Spec

**Date:** 2026-04-28
**Scope:** Depth + LLM-readability overhaul (B-scope), driven by skill-auditor findings.
**Constraint:** SKILL.md ≤300 lines, no `%>%`, all R code uses `<-`, `|>`, snake_case, double quotes.

---

## 1. Goal

Upgrade `skills/r-package-dev/` from "passing" to "best-in-class for both human and LLM consumers" by:

- Closing every gap surfaced by the 38-check skill-auditor rubric (deterministic + judgment).
- Modernizing tooling references (S7, `pak`, `air`, `lintr`, `lifecycle`, `cli`, `withr`, `usethis::use_release_issue()`).
- Tightening boundaries with sibling skills.
- Sharpening the eval.md so future audits are measurable.

This is **not** a rewrite. The skill is already strong. The upgrade strengthens depth, fills modern gaps, and makes the skill more reliably triggered and applied.

---

## 2. Current state

- **Deterministic audit:** 17/17 PASS (frontmatter, line count, gotchas, examples, sibling refs, scripts).
- **SKILL.md:** 295 / 300 lines.
- **References:** 8 files, all >280 lines, well-structured.
- **Scripts:** 6 files, all functional with error handling.
- **eval.md:** Present, 7 binary questions, 12 prompts, 11 success criteria.

### Judgment-check gaps (audit findings)

| Check | Status | Gap |
|-------|--------|-----|
| G3 edge cases | ⚠️ | Sparse `If X → do Y` conditional guidance |
| G5 ambiguity | ⚠️ | Vague phrases ("Most packages") |
| G6 scope constraints | ❌ | Only one line guards against scope creep |
| E1 I/O pairs | ⚠️ | Examples show input but not expected check/NAMESPACE output |
| V1 feedback loop | ❌ | No explicit `check → fix → recheck` named loop |
| V5 MCP qualification | ❌ | `btw_tool_*` listed without `btw:` server prefix |
| T4 success criteria | ⚠️ | Some eval criteria not strictly measurable |

### Modernization gaps (outside the rubric)

S7 not mentioned beyond "greenfield"; `usethis::use_release_issue()` workflow missing; `_PACKAGE` sentinel vs deprecated `@docType package`; `pak` for CI installs; `air` formatter; modern pkgdown bslib themes; `.lintr` config patterns; `lifecycle` for soft-deprecation; `cli` for messages; `withr` for test isolation; `vdiffr` for visual snapshot tests in packages.

---

## 3. Changes

### 3.1 SKILL.md restructure

Keep the 8 existing top-level sections. Net delta: roughly +30 high-value lines, –30 lines of redundancy. Final target ≤300 lines.

**Add at top of body (before "Package Scaffold"):**

A compact **"When to use this skill"** decision block. Lists the 5 sibling boundaries inline (r-project-setup, r-tdd, r-cmd-pkg-release, r-package-skill-generator, r-debugging) with a single-sentence delegation rule for each. Replaces the `> Boundary:` callouts currently scattered through the file.

**Strengthen Gotchas section:**

- Restructure flat table into `If you see X → do Y → verify with Z` triplets.
- Add four new gotchas:
  1. S4/S7 collation order — `@include` and DESCRIPTION `Collate:` field.
  2. Lazy data >5 MB blocks CRAN — diagnose with `tools::checkRdaFiles()`, fix with `usethis::use_data(..., compress = "xz")`.
  3. `_PACKAGE` sentinel replaces deprecated `@docType package`.
  4. `inst/extdata` for non-R data files vs `data/` for R data files.

**Add a "Scope discipline" callout (G6):**

Three-line block immediately after the Gotchas section:

```
Scope discipline (mandatory):
- Fix only the identified issue. No drive-by refactors.
- Show the minimal diff. One issue per session.
- Never re-export or rename without an explicit user request.
```

**Add a "Feedback loop" subsection (V1):**

Codify the named loop with stop conditions:

```
load_all() → test() → document() → check() → fix → repeat
```

Stop when: 0 errors, 0 warnings, 0 notes (CRAN target) OR user-defined acceptance criteria met.

**Qualify all MCP tool references (V5):**

`btw_tool_docs_help_page` → `btw:btw_tool_docs_help_page` (and likewise for the other two).

**Add "Modern toolchain" block:**

One line per item, pointing at `references/modern-toolchain.md`:

- `pak` — fast, parallel installs in CI
- `air` — modern Rust-based formatter, alternative to `styler`
- `lintr` — static analysis with `.lintr` config
- `lifecycle` — soft-deprecation with stage badges
- `cli` — user-facing messages, errors, progress bars
- `withr` — test cleanup and scoped state changes

### 3.2 New reference files (3)

#### `references/modern-toolchain.md` (~200 lines)

Sections: `pak` for installs (with CI snippet); `air` formatter setup and config; `lintr` config (`.lintr` examples, GitHub Action); `lifecycle` deprecation badges and stages (`experimental`, `stable`, `superseded`, `deprecated`); `cli` for messages (`cli_inform`, `cli_warn`, `cli_abort`, progress); `withr::local_*` patterns in tests.

#### `references/release-workflow.md` (~150 lines)

The `usethis::use_release_issue()` driven workflow:

1. Pre-release PR with bumped version, NEWS.md, README updates.
2. `use_release_issue()` opens a tracking issue with a checklist.
3. `devtools::release()` (or stepwise: `check()`, `submit_cran()`).
4. Post-acceptance: tag release, post-release `0.0.0.9000` bump, GitHub release notes.

Complements existing `cran-submission-checklist.md` (which covers the check gauntlet). This file covers the lifecycle around it.

#### `references/data-and-assets.md` (~150 lines)

Sections: `data/` (R data files, lazy-loaded, ≤5 MB total); `inst/extdata/` (raw files, accessed via `system.file()` / `fs::path_package()`); `R/sysdata.rda` (internal-only data); `usethis::use_data()` with `compress` and `internal` flags; `data-raw/` for reproducible data prep scripts; documentation patterns for datasets (`@format`, `@source`, `@references`).

### 3.3 Reference file enhancements

#### `class-systems-guide.md`

Promote S7 from "greenfield" to first-class. Add:

- Constructor/property/method walkthrough (`new_class`, `new_property`, `new_generic`).
- S3 → S7 migration recipe (when, how, what changes).
- S4 → S7 migration recipe (slot → property mapping, validity).
- Updated decision tree: S7 default for new code; R6 only for mutable state; S4 only for Bioconductor compatibility; S3 for one-off methods on existing classes.

#### `r-cmd-check-troubleshooting.md`

Restructure all entries into strict `Saw → Cause → Fix → Verify` quadruples. Add five modern entries:

1. `installed size of XX MB exceeds CRAN limits` — lazy data compression, vignette outputs.
2. `package requires R (>= 4.1.0)` and native `|>` — when to declare R version.
3. `Authors@R ... missing required fields` — ORCID format, role codes.
4. `Description does not end with a full stop` — exact CRAN regex.
5. `vignette engine X registered but no vignettes` — VignetteBuilder DESCRIPTION field.

#### `roxygen2-tags.md`

Add: `@inheritParams`, `@describeIn`, `@rdname`, `@family`, `@srrstats` (rOpenSci stats review), lifecycle badge patterns (`@description \\link[lifecycle]{...}`), Markdown link forms (`[fn()]`, `[pkg::fn()]`, `[topic][pkg::topic]`).

#### `cran-submission-checklist.md`

Add: resubmission protocol (what to put in `cran-comments.md` after rejection); CRAN incoming pending status reading; `R CMD check --as-cran` specific flags vs `devtools::check(cran = TRUE)`; pre-emptive responses to common reviewer asks.

### 3.4 Scripts (1 new + 2 polished)

#### New: `scripts/preflight.R`

Fast pre-check pipeline. Skips the slow `R CMD check` to support tight feedback loops:

1. `roxygen2::roxygenize()` (regenerate man/ + NAMESPACE).
2. `lintr::lint_package()` (style + smell).
3. `spelling::spell_check_package()` (typos).
4. `urlchecker::url_check()` (URL validity).

Exits non-zero on any failure, prints grouped per-stage summaries, runs in <30 s on most packages. Complements (does not replace) `check_package.R` and `release_checklist.R`.

#### Polish: `release_checklist.R`

- Add `--with-revdep` flag that runs `revdepcheck::revdep_check()`.
- Add platform-check summary (which OSes were tested).
- Group output by phase with horizontal rules.

#### Polish: `audit_deps.R`

Add detection: `Suggests` packages used unconditionally (without `requireNamespace()` guard) — CRAN policy violation. Output flagged file:line locations.

### 3.5 eval.md sharpening (T4)

Replace soft success criteria with measurable ones:

- Happy-path roxygen response MUST include **all five** of: `@param` for every argument; `@returns`; `@examples`; `@export`; an explicit `devtools::document()` invocation.
- CRAN-readiness response MUST include **all five** of: `check(cran = TRUE)` (or `R CMD check --as-cran`); `urlchecker`; `spelling::spell_check_package`; `cran-comments.md`; `NEWS.md`.
- NAMESPACE conflict response MUST mention **at least two** of: selective `@importFrom`, `pkg::fn()`, `usethis::use_import_from()`, package-level conflict resolution.

Add two new test prompts:

1. *S4 → S7 migration:* "I have an S4 class hierarchy with three classes and want to migrate to S7. Walk me through the migration."
2. *Release issue flow:* "Open a release issue using `usethis::use_release_issue()` and walk me through the checklist for a 0.4.0 minor release."

### 3.6 Sibling boundaries — explicit table

In SKILL.md "When to use" block:

| Boundary | Sibling | Rule |
|----------|---------|------|
| Initial project scaffold only | `r-project-setup` | Defer there |
| Test authoring, TDD cycle | `r-tdd` | Defer there |
| Interactive guided release | `r-cmd-pkg-release` | Invoke that command |
| Generate a skill FROM a package | `r-package-skill-generator` | Defer there |
| Debug package source code | `r-debugging` | Defer there |

This skill owns: development loop, documentation, NAMESPACE, dependencies, class systems, vignettes/pkgdown, R CMD check, CRAN submission, CI/CD.

---

## 4. Verification

Each batch of changes must pass all four gates before commit:

1. `python skills/skill-auditor/scripts/score_skill.py skills/r-package-dev --siblings-dir skills --conventions rules/r-conventions.md --max-lines 300` — score must remain 17/17.
2. `python skills/skill-auditor/scripts/verify_batch.py skills --all --max-lines 300` — file size limits across the project.
3. `grep -rn '%>%' skills/r-package-dev --exclude=eval.md` — must return no matches.
4. `python tests/run_all.py` — full plugin test suite passes.

After all batches: re-read SKILL.md end-to-end as if seeing it fresh; verify no broken cross-references, dangling lazy-load pointers, or contradictions.

---

## 5. Out of scope

- New agents — existing two (`r-pkg-check`, `r-dependency-manager`) are sufficient.
- Bioconductor submission workflow.
- `pkgcheck` / rOpenSci editorial review tooling.
- R6 → S7 migration recipe (R6 is for mutable state; rarely migrated).
- Performance profiling within packages — covered by `r-performance`.

---

## 6. Implementation order

Suggested sequencing for the implementation plan:

1. **SKILL.md decision block + sibling boundary table** (smallest unit, immediately improves trigger reliability).
2. **MCP qualification fix + Modern toolchain block** in SKILL.md.
3. **Strengthen Gotchas + add Scope discipline + Feedback loop subsection.**
4. **New `references/modern-toolchain.md`.**
5. **New `references/release-workflow.md`.**
6. **New `references/data-and-assets.md`.**
7. **Enhance existing references** (`class-systems-guide.md` → S7 promotion; `r-cmd-check-troubleshooting.md` → quadruple format; `roxygen2-tags.md` additions; `cran-submission-checklist.md` resubmission protocol).
8. **New `scripts/preflight.R`.**
9. **Polish existing scripts** (`release_checklist.R`, `audit_deps.R`).
10. **Sharpen `eval.md`** with measurable criteria + two new prompts.
11. **Final verification gauntlet** (all four gates).

Each step ends with the four-gate verification. Any failure → fix before proceeding.
