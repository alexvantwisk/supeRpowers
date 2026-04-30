# Contributing to supeRpowers

Thanks for your interest in supeRpowers — an R programming plugin for Claude
Code. This document describes how the project accepts contributions **right
now, during beta**. The model is intentionally narrow while the plugin is
still evolving; it will open up as things stabilise.

---

## Status: beta, single maintainer

supeRpowers is currently maintained by a single author and is in **public
beta**. The skill set, command surface, and content conventions are still
moving. Until the API and conventions settle, contribution is restricted to
**filing issues** — pull requests are not accepted yet (see
[Why no pull requests yet?](#why-no-pull-requests-yet) below).

This isn't a hostile gate. Issues are the most valuable signal at this stage:
they tell the maintainer where the plugin is rough, what's missing, and
what's actually being used in practice. If you've used the plugin on a real
project and have feedback, **please file an issue** — that's exactly what's
wanted.

---

## How to contribute right now

| You want to... | Do this |
|---|---|
| Report a bug | [Open a bug-report issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=bug_report.md) |
| Suggest a new skill, command, or agent | [Open a feature-request issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=feature_request.md) |
| Suggest content for an existing skill | [Open a skill-suggestion issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=skill_suggestion.md) |
| Report a documentation error or typo | Open a regular issue with a link to the file and line |
| Share usage feedback | Open a regular issue and tell the maintainer what worked and what didn't |
| Ask a question | Open an issue and prefix the title with `[Question]` |

Every issue is read. Most receive a response within a few days.

---

## What makes a good issue

The bar is low — please don't let it stop you filing — but issues that
include the following get triaged and resolved fastest.

### Bug reports

- **Plugin version** (`claude plugin list` output)
- **Claude Code version** (`claude --version`)
- **R version** and operating system
- **Reproducer** — a one- or two-line prompt to Claude Code that triggers the
  problem, plus what you expected vs what happened
- **Logs or output** if Claude Code returned an error or the wrong skill
  activated

### Feature / skill suggestions

- **What problem you're trying to solve.** This is the most important field.
  "I have to write a CDISC SDTM mapping every week and the plugin doesn't
  help" is more useful than "add a CDISC SDTM skill."
- **What you've tried.** Which existing skills came close, and where they
  fell short.
- **A concrete example prompt** you'd want the plugin to handle well.

### Skill content suggestions

If you want to suggest a fix or addition to an existing skill (a new
reference file, a missing example, a wrong recommendation):

- Name the skill (`r-tdd`, `r-shiny`, ...)
- Describe what's wrong or missing in plain prose
- Link to authoritative sources (CRAN docs, package vignettes, R-blogger
  articles) the maintainer can verify against

You don't need to draft the actual change — describing what should be in the
skill is enough.

---

## Why no pull requests yet?

Three reasons, all of which will go away as the plugin matures:

1. **Conventions are still settling.** The skill frontmatter format, command
   structure, and routing matrix have changed twice since 0.1.0. A PR written
   against today's conventions could be obsolete by next month, which is
   discouraging for contributors and creates merge churn.
2. **No CONTRIBUTOR-level test infrastructure.** The current test suite
   (`python tests/run_all.py`) catches structural issues but doesn't yet
   guard the *content quality* of skills. Until that's in place, accepting
   external content changes risks regressions that wouldn't be caught.
3. **Single maintainer at beta.** Reviewing PRs well takes meaningful time;
   right now that time is better spent making the plugin good enough to
   merit external contributions.

Filing an issue is *not* second-class. A clear issue describing what should
change is often more valuable than a PR — it lets the maintainer
implement the fix in a way that matches the plugin's evolving conventions
without a lengthy revision cycle.

---

## When pull requests will open

PRs will be accepted once these are in place:

- A documented **content-quality test** for skills (the `skill-auditor`
  meta-skill is the precursor; needs to be wired into CI)
- A **CONTRIBUTING-CODE.md** describing skill/command/agent contribution
  format with linting and structural checks
- A **CHANGELOG-driven release process** that doesn't require manual file
  hunting for version bumps

If you want to track this, watch the
[v1.0 milestone](https://github.com/alexvantwisk/supeRpowers/milestones)
once it's created.

---

## Code of conduct

Be respectful, be specific, and assume good intent. Discussion stays
focused on the plugin and how to make it better. Personal attacks,
discriminatory language, or off-topic disputes will result in the issue
being locked.

---

## Licensing

supeRpowers is MIT-licensed (see [LICENSE](LICENSE)). By filing an issue you
acknowledge that any content, examples, or text you include in the issue may
be used by the maintainer in the plugin under the same MIT licence.

---

## Maintainer

Alexander van Twisk — issues at
https://github.com/alexvantwisk/supeRpowers/issues
