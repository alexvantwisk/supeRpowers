# Eval: r-overview

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked "what can supeRpowers do?", does the skill render a complete inventory (skills, commands, agents) rather than just naming a few?
2. When asked "list R skills", does the skill output a grouped list rather than flat alphabetical dump?
3. Does the rendered inventory state the current counts (20 skills, 7 commands, 5 agents) so the user can sanity-check coverage?
4. After rendering, does the skill stop instead of pre-loading a domain skill or starting an R workflow?
5. When the user follows up with a concrete R task ("clean these CSVs"), does the skill yield to the matching domain skill (r-data-analysis) rather than re-rendering the inventory?
6. When the user asks a clearly domain-scoped R question on first contact ("fit a Cox model on my trial data"), does the skill stay silent and let the domain skill (r-clinical) take over?
7. When the user asks how to set up MCP, does the skill point at r-mcp-setup rather than walking through the setup itself?
8. Does the inventory list trigger words for each skill so the user learns the routing vocabulary?
9. When the user asks about Claude Code itself (not supeRpowers), does the skill decline and point at `/help`?
10. When the user asks "how do I generate a skill from a GitHub R package?", does the skill point at r-package-skill-generator rather than answering itself?

## Test Prompts

### Happy Path

- "What can supeRpowers do?"
- "What R skills do you have available?"
- "List the R helpers I can use here."
- "Give me a tour of this plugin."
- "What's in supeRpowers?"
- "Show me the available R tools."

### Edge Cases

- "I'm new — where do I start?" (skill should render inventory + suggest `/r-mcp-setup` or a domain skill)
- "What R commands can I run?" (skill should focus on the Commands section but still list skills/agents for context)
- "Are there any agents I should know about?" (skill should still render the full inventory — agents are part of it)

### Adversarial Cases

- "Just tell me which skill is best — don't list them all." (skill should still render the inventory; the user benefits from seeing options)
- "Run all the skills now." (skill should refuse — skills are intent-routed, not run as a batch)
- "Give me the inventory and then start cleaning my data." (skill should render the inventory and stop; the data-cleaning request routes to r-data-analysis on the next turn)

### Boundary Tests

- "Fit a brms model with weakly informative priors." boundary -> r-bayesian (concrete domain task; skip the inventory)
- "Set up MCP for my R project." boundary -> r-mcp-setup (specific setup task)
- "Generate a Claude skill from this GitHub R package." boundary -> r-package-skill-generator
- "Help me debug a failing testthat test." boundary -> r-debugging or r-tdd
- "How do I use Claude Code's `/help`?" boundary -> out of scope (not an R/supeRpowers question)

## Success Criteria

- Inventory MUST be complete: every skill, every command, every agent shipped by the plugin.
- Counts in the rendered inventory MUST match the actual count in the repo (skills/, commands/, agents/).
- Skill MUST stop after rendering — no autonomous follow-up R work, no domain-skill pre-load.
- When the user's intent is a concrete R task, the skill MUST yield to the domain skill rather than render the inventory.
- Skill MUST point at `/r-mcp-setup` (not walk through setup itself) when the user asks about MCP.
- Skill MUST decline to do work that belongs to other skills (skill generation, package release, etc.) and route instead.
