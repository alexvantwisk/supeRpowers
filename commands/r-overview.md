---
description: Print an inventory of every supeRpowers skill, command, and agent — a directory of available R helpers
---

# Overview

Print a concise, grouped directory of every skill, command, and agent shipped
by the supeRpowers plugin so the user can locate the right tool for their
next R task.

## What to Do

**Skill:** `r-overview`

Invoke the `r-overview` skill and render the inventory it produces verbatim.
The skill keeps its content in lockstep with the actual files in `skills/`,
`commands/`, and `agents/`, so this command stays accurate as the plugin
evolves.

After rendering, **stop**. Do not begin any R workflow, do not dispatch any
agent, and do not pre-load any domain skill. Wait for the user's next
message — at that point the matching domain skill activates from intent (or
the user invokes another command explicitly).

## Abort Conditions

- The user follows up with a concrete R task — yield to the matching domain
  skill (`r-data-analysis`, `r-stats`, `r-bayesian`, etc.) rather than
  re-rendering the inventory.
- The user asks about Claude Code itself (not supeRpowers) — point at
  Claude Code's `/help` instead.

## Examples

- `/r-overview` — full inventory
- `/r-overview` after `/r-mcp-setup` — quick orientation once MCP is wired up
- `/r-overview` for a teammate new to the plugin
