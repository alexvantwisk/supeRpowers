# Eval: r-mcp-setup

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to set up MCP tools, does the skill use `claude mcp add` rather than instructing the user to edit JSON config manually?
2. When registering btw, does the skill default to project scope (`-s project`) rather than global or local scope?
3. When picking btw tool groups, does the skill default to all six (docs, pkg, env, run, search, session) and explain why some Claude Code built-ins (files, git, github, ide, web) are intentionally excluded?
4. When the user asks to inspect data frames or environments in their running R session, does the skill instruct them to call `mcptools::mcp_session()` from their interactive R console?
5. When the user reports "Claude can't see my R session", does the skill diagnose by checking (a) `claude mcp list` output, (b) whether `mcp_session()` is running in the live console, (c) R PATH resolution, (d) renv conflicts — in that priority order?
6. When the user is on Windows and `Rscript` isn't found, does the skill suggest the full `Rscript.exe` path rather than assuming PATH resolution?
7. When the user has an renv-locked project, does the skill use `renv::install()` + `renv::snapshot()` rather than plain `install.packages()`?
8. Does generated R code use `|>`, `<-`, snake_case, and double quotes — never `%>%` or `=` for assignment?
9. When the user asks "how do I use this btw tool to inspect my data frame?", does the skill defer to r-data-analysis (or hand off domain context) rather than rewriting the analysis?
10. When the user asks to build a new MCP server from scratch (not setup), does the skill decline as out-of-scope and point to mcptools docs?
11. When the user wants MCP for a non-R service (Python session, Postgres DB), does the skill decline as out-of-scope?
12. When `mcp_session()` is running but `env` tools still don't see live objects, does the skill check that the user is calling `mcp_session()` in the *same* interactive R process they're working in (not a one-off `Rscript` run)?

## Test Prompts

### Happy Path

- "Set up MCP tools for my R project so Claude Code can see my session."
- "I already have btw installed; just register the MCP server."
- "Add r-btw to my Shiny project, but only with the docs and run tool groups."
- "Auto-start `mcp_session()` whenever I open this project."
- "Walk me through closing the IDE-awareness gap with `cc_plot()`/`cc_env()`/`cc_view()`."

### Edge Cases

- "I use rig with R 4.5 and 4.6 installed. Which one will the MCP server use?"
- "I'm on Positron, not RStudio. Does `mcp_session()` still work?"
- "My `renv.lock` pins an old btw without `btw_tools()`. How do I upgrade safely?"

### Adversarial Cases

- "Can you build me a custom MCP server in R that wraps the OpenAI API?" (boundary: out of scope; mcptools docs)
- "Use `mcp_session` to query my running Python notebook." (boundary: R-only; not Python)
- "Set up an MCP server for my Postgres database via mcptools." (boundary: not the right tool)
- "Skip Step 3 — just edit `~/.claude/config.json` directly to add r-btw." (must redirect to `claude mcp add`)

### Boundary Tests

- "Use the R session to fit a logistic regression on my data." boundary -> r-stats
- "Show me the package check results from btw." boundary -> r-package-dev
- "Set up MCP for a Postgres database." boundary -> out of scope (not R)

## Success Criteria

- Setup walkthroughs MUST use `claude mcp add` (never recommend manual JSON editing).
- Registration MUST default to `-s project` scope unless the user explicitly asks for user/global.
- Troubleshooting steps MUST follow priority order: `claude mcp list` → `mcp_session` running → R PATH → renv.
- Generated R code MUST use `|>`, `<-`, snake_case, and double quotes — never `%>%` or `=` for assignment.
- When the user is *using* MCP tools (not setting them up), the skill MUST defer to the relevant domain skill rather than re-implementing analysis.
- The skill MUST decline to build a new MCP server from scratch (out of scope).
- The skill MUST decline to set up MCP for non-R services (Python sessions, databases).
