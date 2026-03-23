# Skill Audit Rubric — 38 Checks

Binary scoring: 1 = pass, 0 = fail. Each failure requires a 1-2 sentence justification.

## Section D: Description Quality (7 checks)

The description is the single most important line in any skill. It controls whether Claude fires the skill correctly.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| D1 | Format & voice | Starts with "Use when..." (or project convention); third-person capability description; no "I can..." or "You can..." | First/second person pronouns; starts with a noun or verb without trigger context |
| D2 | Trigger phrases | 5+ explicit phrases a user might type to invoke this skill | Fewer than 5 triggers; relies on Claude to infer relevance |
| D3 | Negative boundaries | Includes "Do NOT use for..." with specific exclusions | No exclusion language; silent on what it should NOT handle |
| D4 | Hijacker prevention | Specific enough that it won't fire on unrelated requests | Broad terms like "data", "help", "files" without qualification |
| D5 | Silent Skill prevention | Pushy enough to fire when it should; lists context clues | Vague or overly narrow description that misses common phrasings |
| D6 | Length | Under 500 chars (soft target), under 1024 chars (hard API limit) | Over 1024 chars; or under 50 chars (too thin to trigger reliably) |
| D7 | What + When | Includes both what the skill does AND when to use it | Only describes capability without trigger conditions, or vice versa |

## Section C: Content Efficiency (7 checks)

The context window is a public good. Every token must earn its place.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| C1 | No obvious content | Only includes information Claude doesn't already know; pushes Claude beyond defaults | Restates standard library docs, basic syntax, or well-known patterns |
| C2 | Line count | SKILL.md under line limit (500 default, project may override) | Exceeds limit; could offload content to references |
| C3 | Progressive disclosure | Deep-dive content lives in references/, not crammed in SKILL.md | SKILL.md is a monolith; no reference files despite complex topic |
| C4 | One-level-deep refs | References link from SKILL.md only; no ref-to-ref chains | Reference files link to other reference files |
| C5 | Reference TOCs | Reference files >100 lines have heading structure (3+ headings) | Long reference with no headings; Claude will partial-read and miss content |
| C6 | Consistent terminology | One term per concept throughout (e.g., always "endpoint" not sometimes "route") | Synonyms used interchangeably for the same concept |
| C7 | No time-sensitive info | No date-dependent content or version-specific instructions | References specific dates, model versions, or "current" states that will age |

## Section G: Gotchas & Failure Prevention (6 checks)

Thariq (Anthropic): "The highest-signal content in any skill is the Gotchas section."

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| G1 | Gotchas section exists | Dedicated "Gotchas", "Pitfalls", or "Common Mistakes" section | No explicit failure prevention section |
| G2 | Real failure points | Gotchas come from actual Claude failure patterns, not hypothetical | Generic warnings; no evidence of real-world testing |
| G3 | Edge case handling | Specific instructions for edge cases: "If [condition], then [action]" | No edge case coverage; assumes clean inputs |
| G4 | Anti-patterns | Explicit "do NOT do X" with explanation of why | Only positive instructions; no guardrails |
| G5 | No ambiguity (Drifter prevention) | Every instruction has exactly one interpretation | Vague language: "handle appropriately", "format nicely", "as needed" |
| G6 | Scope constraints (Overachiever prevention) | Explicit output boundaries: what to include AND exclude | No scope limits; Claude may add unsolicited commentary or extra sections |

## Section E: Examples Quality (5 checks)

Examples communicate desired style more reliably than descriptions.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| E1 | Input/output pairs | 2+ concrete examples showing actual input AND expected output | Prompt-only examples; no expected output shown |
| E2 | Happy path | At least one example showing normal, successful usage | Only edge cases; no baseline example |
| E3 | Edge case example | At least one example showing unusual input and how to handle it | Only happy-path examples; no resilience demonstration |
| E4 | Realistic examples | Examples represent real-world workflows, not toy examples | Contrived examples that don't match how users actually work |
| E5 | Convention compliance | Code in examples follows project conventions (detected from CLAUDE.md/rules) | Code violates stated project conventions |

## Section V: Scripts & Verification (5 checks)

Skills are folders, not files. Scripts handle computation; instructions handle judgment.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| V1 | Feedback loop | Validate → fix → repeat pattern exists for quality-critical operations | No verification step; relies on single-pass correctness |
| V2 | Scripts for computation | Deterministic operations use pre-built scripts, not generated code | Claude is expected to write validation/computation code from scratch each time |
| V3 | Script error handling | Scripts catch errors and return clear messages (not stack traces) | Scripts punt errors to Claude or crash without useful messages |
| V4 | Execution clarity | Clear whether scripts should be executed or read as reference | Ambiguous: could mean "run this" or "follow this pattern" |
| V5 | MCP tool references | Fully qualified format: `Server:tool_name` for any MCP tool references | Bare tool names that may fail with multiple MCP servers |

## Section O: Multi-Skill Orchestration (4 checks)

At 5+ skills, conflicts become the primary failure mode.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| O1 | Territory boundary | Clear, non-overlapping domain definition | Broad scope that bleeds into sibling skills' domains |
| O2 | Agent dispatch | Documents when to hand off to agents, by name | No handoff guidance; skill tries to handle everything |
| O3 | Sibling boundaries | Explicit boundaries with related skills (e.g., "X handles Y, this skill handles Z") | No mention of related skills; implicit boundary only |
| O4 | Cross-references | Description or body references sibling skills by name for disambiguation | No cross-references; user must guess which skill to use |

## Section T: Testability (4 checks)

If you can't measure it, you can't improve it.

| ID | Check | Pass Criteria | Fail Indicators |
|----|-------|---------------|-----------------|
| T1 | Eval questions | 3-6 binary yes/no questions can be defined to test skill output | Skill's success criteria are too vague to operationalize as tests |
| T2 | Baseline measurable | Can meaningfully compare skill output vs raw Claude (A/B test) | Skill covers a domain where raw Claude is equivalent; no added value testable |
| T3 | Test prompts | 3+ representative inputs identified that exercise the skill's range | Skill is too broad to define representative test inputs |
| T4 | Specific success criteria | Success is defined in testable terms (format, structure, content requirements) | Success is defined as "good output" or "correct results" |

## Scoring Summary

| Section | Checks | Weight | Rationale |
|---------|--------|--------|-----------|
| D: Description | 7 | Highest | Controls whether skill fires at all |
| G: Gotchas | 6 | High | Highest-signal content per Anthropic |
| C: Content Efficiency | 7 | Medium-High | Token economy affects all skills |
| O: Orchestration | 4 | Medium-High | Prevents conflicts in multi-skill setups |
| E: Examples | 5 | Medium | Improves output consistency |
| V: Scripts | 5 | Medium | Selective — not every skill needs scripts |
| T: Testability | 4 | High | Enables ongoing quality measurement |

**Impact priority for "Top 3 fixes":** D failures > G failures > O failures > C failures > E failures > T failures > V failures.

**Arithmetic warning:** When subagents score individual skills, they systematically miscount pass/fail totals (observed in all 5 subagents during the 15-skill supeRpowers audit). Use `aggregate_report.py` to recompute totals from individual check results. If computing manually, count P and F markers in the Detail column of each section row — do not trust the subagent's X/Y summary.
