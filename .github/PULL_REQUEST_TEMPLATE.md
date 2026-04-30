## What does this PR do

<!-- One or two sentences. -->

## Linked issue

<!-- For non-trivial changes, please link the issue this PR addresses. See
CONTRIBUTING.md for the issue-first workflow. -->

Closes #

## Type of change

- [ ] New skill
- [ ] Edit / extend existing skill
- [ ] New or edited command
- [ ] New or edited agent
- [ ] Edited rule
- [ ] Documentation only (README, CONTRIBUTING, CLAUDE.md, release notes)
- [ ] Tests / CI / repo infrastructure
- [ ] Other (describe below)

## Verification

- [ ] `python tests/run_all.py` — no NEW failures
      (the 10 pre-existing structural failures documented in 0.2.0
      release notes are acceptable)
- [ ] `grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md`
      returns no output
- [ ] Frontmatter and line limits per `CLAUDE.md`
      (SKILL ≤ 300, command ≤ 200, agent ≤ 200, rule ≤ 150)
- [ ] R code uses `<-`, `|>`, snake_case, double quotes
- [ ] Routing matrix updated if I added or substantially changed a skill

## Notes for the reviewer

<!-- Anything that would help review: design rationale, edge cases, manual
testing performed, screenshots if there's a visible behavioural change. -->
