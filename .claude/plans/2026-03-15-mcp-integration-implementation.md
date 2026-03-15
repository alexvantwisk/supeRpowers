# MCP Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add mcptools/btw MCP server integration to supeRpowers — 1 new skill, 2 reference files, 1 shared detection script, hook enhancement, 10 skill patches, 2 agent patches, version bump.

**Architecture:** New `r-mcp-setup` skill handles onboarding + serves as MCP knowledge hub via lazy-loaded reference files. Session-start hook detects MCP availability and injects context. Existing skills check context substring to choose MCP tools or Bash fallback. Graceful degradation throughout.

**Tech Stack:** Bash (hook/detection script), Markdown (skills/agents/references), JSON (plugin.json, hook output)

**Spec:** `.claude/plans/2026-03-15-mcp-integration-design.md`

---

## Chunk 1: Infrastructure (detection script + hook enhancement)

### Task 1: Create `hooks/detect-mcp.sh`

Shared MCP detection script. Returns JSON to stdout, always exits 0.

**Files:**
- Create: `hooks/detect-mcp.sh`

- [ ] **Step 1: Create the detection script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# MCP detection helper for supeRpowers
# Used by: hooks/session-start, skills/r-mcp-setup
# Output: JSON to stdout — always exits 0
# Interface: {"mcp_registered": bool, "btw_installed": bool, "mcptools_installed": bool, "tool_groups": [...], "session_active": bool}

MCP_REGISTERED=false
BTW_INSTALLED=false
MCPTOOLS_INSTALLED=false
TOOL_GROUPS="[]"
SESSION_ACTIVE=false

# --- Check MCP server registration ---
# Look for r-btw in Claude Code MCP config files
for config_file in ".claude/settings.json" ".mcp.json"; do
    if [ -f "$config_file" ] && grep -q "r-btw" "$config_file" 2>/dev/null; then
        MCP_REGISTERED=true
        break
    fi
done

# --- Check R package availability (only if R is present) ---
if command -v Rscript > /dev/null 2>&1; then
    R_CHECK=$(Rscript --vanilla -e '
        btw <- requireNamespace("btw", quietly = TRUE)
        mcp <- requireNamespace("mcptools", quietly = TRUE)
        cat(btw, mcp, sep = ",")
    ' 2>/dev/null || echo "false,false")

    if echo "$R_CHECK" | grep -q "^TRUE"; then
        BTW_INSTALLED=true
    fi
    if echo "$R_CHECK" | grep -q ",TRUE$"; then
        MCPTOOLS_INSTALLED=true
    fi
fi

# --- Determine available tool groups ---
if [ "$MCP_REGISTERED" = true ] && [ "$BTW_INSTALLED" = true ]; then
    # Parse tool groups from config if possible; default to full set
    TOOL_GROUPS='["docs","pkg","env","run","search","session"]'
fi

# --- Output JSON ---
cat <<EOF
{"mcp_registered":$MCP_REGISTERED,"btw_installed":$BTW_INSTALLED,"mcptools_installed":$MCPTOOLS_INSTALLED,"tool_groups":$TOOL_GROUPS,"session_active":$SESSION_ACTIVE}
EOF
```

- [ ] **Step 2: Make executable**

Run: `chmod +x hooks/detect-mcp.sh`

- [ ] **Step 3: Verify script runs cleanly**

Run: `cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers && bash hooks/detect-mcp.sh`
Expected: JSON output like `{"mcp_registered":false,"btw_installed":false,...}` with exit code 0.

- [ ] **Step 4: Commit**

```bash
git add hooks/detect-mcp.sh
git commit -m "feat: add shared MCP detection script for hook and skill use"
```

---

### Task 2: Enhance `hooks/session-start` with MCP detection block

Add MCP detection after the existing R environment checks. Only runs when an R project is detected. Uses cached results with 5-minute TTL.

**Files:**
- Modify: `hooks/session-start` (insert after line 73, before line 75 "Build skill relevance")

- [ ] **Step 1: Add MCP detection block**

Insert this block after the `fi` on line 73 (end of "Check R environment" section), before the `# --- Build skill relevance ---` comment:

```bash
# --- Detect MCP availability (only if R project detected) ---
MCP_STATUS="not configured"
MCP_GROUPS=""

if [ "$PROJECT_TYPE" != "none" ]; then
    CACHE_FILE="/tmp/superpowers-mcp-status-${USER:-unknown}.json"
    CACHE_TTL=300  # 5 minutes

    # Use cache if fresh
    if [ -f "$CACHE_FILE" ]; then
        CACHE_AGE=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) ))
        if [ "$CACHE_AGE" -lt "$CACHE_TTL" ]; then
            MCP_JSON=$(cat "$CACHE_FILE")
        fi
    fi

    # Run detection if no cache hit
    if [ -z "${MCP_JSON:-}" ]; then
        DETECT_SCRIPT="${PLUGIN_ROOT}/hooks/detect-mcp.sh"
        if [ -f "$DETECT_SCRIPT" ]; then
            MCP_JSON=$(bash "$DETECT_SCRIPT" 2>/dev/null || echo '{"mcp_registered":false}')
            echo "$MCP_JSON" > "$CACHE_FILE" 2>/dev/null || true
        else
            MCP_JSON='{"mcp_registered":false}'
        fi
    fi

    # Parse results (lightweight — no jq dependency)
    if echo "$MCP_JSON" | grep -q '"mcp_registered":true'; then
        MCP_STATUS="available"
        # Extract tool groups for context string
        MCP_GROUPS=$(echo "$MCP_JSON" | grep -oE '"tool_groups":\[[^]]*\]' | sed 's/"tool_groups":\[//;s/\]//;s/"//g')
    fi
fi
```

- [ ] **Step 2: Add MCP context to output**

Find the line `if [ -n "$AGENTS" ]; then CONTEXT="$CONTEXT Agents: $AGENTS."; fi` (line 145) and add after it:

```bash
    # MCP status
    if [ "$MCP_STATUS" = "available" ]; then
        CONTEXT="$CONTEXT MCP: available | groups: ${MCP_GROUPS}."
    elif [ "$PROJECT_TYPE" != "none" ]; then
        CONTEXT="$CONTEXT MCP: not configured. Use the r-mcp-setup skill to enable enhanced R integration."
    fi
```

- [ ] **Step 3: Verify hook still runs cleanly**

Run: `cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers && bash hooks/session-start`
Expected: JSON output with `additionalContext` containing either "MCP: available" or "MCP: not configured".

- [ ] **Step 4: Test in a non-R directory**

Run: `cd /tmp && CLAUDE_PLUGIN_ROOT=/Users/alexandervantwisk/Desktop/Projects/supeRpowers bash /Users/alexandervantwisk/Desktop/Projects/supeRpowers/hooks/session-start`
Expected: No MCP detection runs. Output has "No R project detected."

- [ ] **Step 5: Commit**

```bash
git add hooks/session-start
git commit -m "feat: add MCP detection to session-start hook with caching"
```

---

## Chunk 2: New skill and reference files

### Task 3: Create `skills/r-mcp-setup/SKILL.md`

The main MCP onboarding and knowledge hub skill. **Use the `/writing-skills` skill** for content creation — it enforces the correct frontmatter format, line limits, and quality standards.

**Files:**
- Create: `skills/r-mcp-setup/SKILL.md`

- [ ] **Step 1: Create skill directory**

Run: `mkdir -p /Users/alexandervantwisk/Desktop/Projects/supeRpowers/skills/r-mcp-setup/references`

- [ ] **Step 2: Invoke /writing-skills to create the SKILL.md**

Use the `/writing-skills` skill with this context:

**Skill name:** `r-mcp-setup`
**Description trigger:** "Use when the user wants to set up MCP tools for R, connect Claude Code to a live R session, register R-based MCP servers, or when another skill needs MCP tool guidance."
**Target:** ≤200 lines (leave room under 300-line limit)

**Content requirements (from spec):**

The skill covers a 5-step workflow:
1. **Detection** — Run `hooks/detect-mcp.sh` or check manually: are mcptools/btw installed? Is an MCP server registered with Claude Code?
2. **Installation guidance** — `install.packages(c("mcptools", "btw"))`. Explain what each package provides.
3. **Registration (hybrid)** — Detect current config, explain what will be registered and why, ask permission, then run: `claude mcp add -s "project" r-btw -- Rscript -e "btw::btw_mcp_server(tools = btw::btw_tools(c('docs', 'pkg', 'env', 'search', 'session', 'run')))"`
4. **Session connection** — Guide user to run `mcptools::mcp_session()` in Positron. Explain: this makes the live R session discoverable so `env` tools can inspect objects. Without it, env tools see only the MCP server's empty R process. The `run` + `env` combo is where the value is.
5. **Verification** — Check tool availability after setup.

**Lazy references:**
- `Read references/mcp-tool-mappings.md for btw tool group → skill mapping and fallback commands`
- `Read references/mcp-troubleshooting.md for common setup issues`

**Agent dispatch:** None (this skill is self-contained).

**Example prompts (5):**
- "Set up MCP tools for my R project"
- "Connect Claude Code to my live R session in Positron"
- "Which btw tools should I register for package development?"
- "My MCP server isn't connecting — help me troubleshoot"
- "What's the difference between mcptools and btw?"

**Key principles to include:**
- Graceful degradation: MCP enhances but is never required
- Project-scoped registration (`-s "project"`) to avoid cross-project bleed
- R code conventions: all examples use `|>`, `<-`, double quotes, snake_case

- [ ] **Step 3: Verify skill**

Run:
```bash
wc -l skills/r-mcp-setup/SKILL.md  # Must be ≤300
head -5 skills/r-mcp-setup/SKILL.md  # Must have YAML frontmatter
grep '%>%' skills/r-mcp-setup/SKILL.md  # Must find nothing
```

- [ ] **Step 4: Commit**

```bash
git add skills/r-mcp-setup/SKILL.md
git commit -m "feat: add r-mcp-setup skill for MCP onboarding"
```

---

### Task 4: Create `skills/r-mcp-setup/references/mcp-tool-mappings.md`

Central reference mapping btw tool groups to skills with fallback commands.

**Files:**
- Create: `skills/r-mcp-setup/references/mcp-tool-mappings.md`

- [ ] **Step 1: Write the reference file**

Target: ~120-150 lines. No YAML frontmatter (reference files don't have it).

**Required content:**

**Section 1: How Skills Detect MCP Availability**
- The session-start hook injects context containing `"MCP: available"` when btw MCP tools are registered
- Skills check for this substring in their context
- Pattern: if MCP available → use btw tool; else → Bash Rscript fallback

**Section 2: Tool Group Reference (one section per group)**

For each of the 6 groups (docs, pkg, env, run, search, session), include:

| Field | Content |
|-------|---------|
| btw tool names | Full `btw_tool_*` names as Claude Code sees them |
| What it does | 1-2 sentence description |
| Skills that benefit | List from spec mapping table |
| MCP usage example | How a skill would call the tool |
| Bash fallback | Exact `Rscript -e` equivalent |

**docs group:**
- Tools: `btw_tool_docs_help_page`, `btw_tool_docs_package_help_topics`, `btw_tool_docs_vignette`, `btw_tool_docs_available_vignettes`, `btw_tool_docs_package_news`
- Benefits: All skills
- MCP: Call `btw_tool_docs_help_page(package = "dplyr", topic = "mutate")`
- Fallback: `Rscript -e 'utils::help("mutate", package = "dplyr")'`

**pkg group:**
- Tools: `btw_tool_pkg_test`, `btw_tool_pkg_check`, `btw_tool_pkg_document`, `btw_tool_pkg_coverage`
- Benefits: r-tdd, r-package-dev, r-debugging
- MCP: Call `btw_tool_pkg_test(filter = "validate")` → structured pass/fail
- Fallback: `Rscript -e 'devtools::test(filter = "validate")'` → parse console text

**env group:**
- Tools: `btw_tool_env_describe_data_frame`, `btw_tool_env_describe_environment`
- Benefits: r-data-analysis, r-debugging, r-stats, r-clinical, r-performance, r-targets
- MCP: Call `btw_tool_env_describe_data_frame(name = "my_df")` → structure, types, sample values
- Fallback: No direct equivalent (requires live session). Use `Rscript -e 'str(readRDS("data.rds"))'` for static files.
- Note: Requires `mcptools::mcp_session()` in the user's R session. Without it, env tools see only the MCP server's own empty environment.

**run group:**
- Tools: `btw_tool_run_r` (experimental)
- Benefits: r-data-analysis, r-debugging, r-stats, r-performance, r-tidymodels, r-targets
- MCP: Call `btw_tool_run_r(code = "summary(mtcars)")` → runs in the user's R session
- Fallback: `Rscript -e 'summary(mtcars)'` (runs in a fresh, isolated R process)

**search group:**
- Tools: `btw_tool_search_packages`, `btw_tool_search_package_info`
- Benefits: r-package-dev, r-project-setup, r-dependency-manager agent
- MCP: Call `btw_tool_search_packages(query = "spatial data")` → CRAN results
- Fallback: Web search or `Rscript -e 'available.packages()[grep("spatial", available.packages()[,"Package"]),]'`

**session group:**
- Tools: `btw_tool_session_check_package_installed`, `btw_tool_session_package_info`, `btw_tool_session_platform_info`
- Benefits: r-project-setup, r-dependency-manager agent
- MCP: Call `btw_tool_session_platform_info()` → R version, OS, locale
- Fallback: `Rscript -e 'sessionInfo()'`

- [ ] **Step 2: Verify reference file**

Run:
```bash
wc -l skills/r-mcp-setup/references/mcp-tool-mappings.md  # Should be ~120-150
grep '%>%' skills/r-mcp-setup/references/mcp-tool-mappings.md  # Must find nothing
head -3 skills/r-mcp-setup/references/mcp-tool-mappings.md  # Must NOT have YAML frontmatter
```

- [ ] **Step 3: Commit**

```bash
git add skills/r-mcp-setup/references/mcp-tool-mappings.md
git commit -m "feat: add MCP tool mappings reference for skill/agent use"
```

---

### Task 5: Create `skills/r-mcp-setup/references/mcp-troubleshooting.md`

Common MCP setup issues and fixes.

**Files:**
- Create: `skills/r-mcp-setup/references/mcp-troubleshooting.md`

- [ ] **Step 1: Write the troubleshooting reference**

Target: ~80-100 lines. No YAML frontmatter.

**Required sections:**

**1. MCP Server Won't Start**
- Symptom: `claude mcp list` shows server but tools aren't available
- Check: `Rscript -e "btw::btw_mcp_server()"` — does it start without error?
- Common fix: Missing btw/mcptools install → `install.packages(c("mcptools", "btw"))`
- Common fix: renv project doesn't have btw → `renv::install("btw"); renv::install("mcptools")`

**2. Windows Path Issues**
- Symptom: `Rscript` not found when MCP server starts
- Fix: Use full path to Rscript.exe in registration:
  `claude mcp add -s "project" r-btw -- "C:/Program Files/R/R-4.x.x/bin/Rscript.exe" -e "btw::btw_mcp_server(...)"`
- Alternative: Ensure R is on PATH in the shell Claude Code uses

**3. renv Conflicts**
- Symptom: MCP server can't find packages even though they're installed
- Cause: MCP server process inherits renv but btw/mcptools aren't in the renv library
- Fix: `renv::install("btw"); renv::install("mcptools"); renv::snapshot()`
- Alternative: Install to user library outside renv: `withr::with_libpaths(.Library.site[1], install.packages("btw"))`

**4. Positron Session Not Discoverable**
- Symptom: `env` tools return empty environment, `run_r` executes in wrong session
- Check: Did the user run `mcptools::mcp_session()` in their Positron console?
- Fix: Run `mcptools::mcp_session()` in the target R session
- Tip: Add to `.Rprofile` via `usethis::edit_r_profile()` for auto-start

**5. Multiple R Sessions**
- Symptom: MCP tools connect to the wrong R session
- Cause: Multiple Positron instances with `mcp_session()` running
- Fix: Use `mcptools::list_r_sessions()` and `mcptools::select_r_session()` to pick the right one

**6. Permission Denied on `claude mcp add`**
- Symptom: Registration command fails
- Fix: Ensure Claude Code is running and the user has permission to modify project config
- Alternative: Manually add to `.claude/settings.json` under `mcpServers`

- [ ] **Step 2: Verify**

Run:
```bash
wc -l skills/r-mcp-setup/references/mcp-troubleshooting.md  # ~80-100
head -3 skills/r-mcp-setup/references/mcp-troubleshooting.md  # No YAML frontmatter
```

- [ ] **Step 3: Commit**

```bash
git add skills/r-mcp-setup/references/mcp-troubleshooting.md
git commit -m "feat: add MCP troubleshooting reference"
```

---

## Chunk 3: Skill patches (10 skills) + agent patches (2 agents) + version bump

### Task 6: Patch 10 existing skills with MCP pointer

Each skill gets a 3-line MCP section appended before its Examples section. The section is identical across all skills (DRY — detail lives in the reference file).

**Files to modify:**
- `skills/r-tdd/SKILL.md` (280 lines → 283)
- `skills/r-package-dev/SKILL.md` (298 lines → 297 after trimming 1 trailing blank line, then +3 = 300)
- `skills/r-debugging/SKILL.md` (295 lines → 298)
- `skills/r-data-analysis/SKILL.md` (278 lines → 281)
- `skills/r-stats/SKILL.md` (274 lines → 277)
- `skills/r-clinical/SKILL.md` (242 lines → 245)
- `skills/r-project-setup/SKILL.md` (180 lines → 183)
- `skills/r-performance/SKILL.md` (239 lines → 242)
- `skills/r-tidymodels/SKILL.md` (209 lines → 212)
- `skills/r-targets/SKILL.md` (212 lines → 215)

- [ ] **Step 1: Determine insertion point for each skill**

For each skill, find the `## Examples` section (or the last `---` separator before examples). Insert the MCP block immediately before it.

The block to insert (exactly 5 lines including the separator):

```markdown

## MCP-Enhanced Workflow (Optional)

When btw MCP tools are available, prefer them over Bash Rscript calls. Read `skills/r-mcp-setup/references/mcp-tool-mappings.md` for tool selection and fallback logic.

```

**Special case — r-clinical:** This skill already has a `## MCP Integration (Optional)` section. Add a single line to the end of that existing section instead:

```markdown
For btw tool group mappings and Bash fallback commands, read `skills/r-mcp-setup/references/mcp-tool-mappings.md`.
```

**Special case — r-package-dev:** At 298 lines, adding 5 lines would put it at 303 (over 300). Check for trailing blank lines to trim, or collapse the block to 3 lines:

```markdown
## MCP-Enhanced Workflow (Optional)

When btw MCP tools are available, prefer them over Bash Rscript calls. Read `skills/r-mcp-setup/references/mcp-tool-mappings.md` for tool selection and fallback logic.
```

If still over 300 after trimming, remove a trailing blank line from the examples section.

- [ ] **Step 2: Apply patches to all 10 skills**

Edit each file. Use the Edit tool with exact `old_string`/`new_string` for precision.

- [ ] **Step 3: Verify all patched skills**

Run:
```bash
# Line count check — all must be ≤300
wc -l skills/r-tdd/SKILL.md skills/r-package-dev/SKILL.md skills/r-debugging/SKILL.md skills/r-data-analysis/SKILL.md skills/r-stats/SKILL.md skills/r-clinical/SKILL.md skills/r-project-setup/SKILL.md skills/r-performance/SKILL.md skills/r-tidymodels/SKILL.md skills/r-targets/SKILL.md

# No magrittr pipe
grep -rn '%>%' skills/r-tdd/ skills/r-package-dev/ skills/r-debugging/ skills/r-data-analysis/ skills/r-stats/ skills/r-clinical/ skills/r-project-setup/ skills/r-performance/ skills/r-tidymodels/ skills/r-targets/

# All still have YAML frontmatter
head -1 skills/r-tdd/SKILL.md skills/r-package-dev/SKILL.md skills/r-debugging/SKILL.md skills/r-data-analysis/SKILL.md skills/r-stats/SKILL.md skills/r-clinical/SKILL.md skills/r-project-setup/SKILL.md skills/r-performance/SKILL.md skills/r-tidymodels/SKILL.md skills/r-targets/SKILL.md
```

Expected: All ≤300 lines, no `%>%` found, all start with `---`.

- [ ] **Step 4: Commit**

```bash
git add skills/r-tdd/SKILL.md skills/r-package-dev/SKILL.md skills/r-debugging/SKILL.md skills/r-data-analysis/SKILL.md skills/r-stats/SKILL.md skills/r-clinical/SKILL.md skills/r-project-setup/SKILL.md skills/r-performance/SKILL.md skills/r-tidymodels/SKILL.md skills/r-targets/SKILL.md
git commit -m "feat: add MCP-enhanced workflow pointers to 10 skills"
```

---

### Task 7: Update 2 agents with MCP notes

Add MCP-enhanced notes to the Procedure section of r-dependency-manager and r-pkg-check.

**Files:**
- Modify: `agents/r-dependency-manager.md` (125 lines)
- Modify: `agents/r-pkg-check.md` (114 lines)

Both are well under the 200-line agent limit.

- [ ] **Step 1: Patch r-dependency-manager**

Find the `## Severity Guide` section. Insert before it:

```markdown
### MCP-Enhanced (Optional)

When btw MCP tools are available, prefer them for dependency checks:
- `btw_tool_session_check_package_installed` — structured installed-package check
- `btw_tool_session_package_info` — detailed package metadata
- `btw_tool_search_package_info` — CRAN package lookup

Read `skills/r-mcp-setup/references/mcp-tool-mappings.md` for full tool mapping and Bash fallback commands.

```

- [ ] **Step 2: Patch r-pkg-check**

Find the `## Severity Guide` section. Insert before it:

```markdown
### MCP-Enhanced (Optional)

When btw MCP tools are available, prefer them for package checks:
- `btw_tool_pkg_check` — structured R CMD check results (errors, warnings, notes as data)
- `btw_tool_pkg_document` — generate docs without console parsing
- `btw_tool_pkg_coverage` — structured coverage percentage

Read `skills/r-mcp-setup/references/mcp-tool-mappings.md` for full tool mapping and Bash fallback commands.

```

- [ ] **Step 3: Verify agents**

Run:
```bash
wc -l agents/r-dependency-manager.md agents/r-pkg-check.md  # Both must be ≤200
grep '%>%' agents/r-dependency-manager.md agents/r-pkg-check.md  # Must find nothing
head -1 agents/r-dependency-manager.md agents/r-pkg-check.md  # Must NOT have YAML frontmatter (starts with #)
```

- [ ] **Step 4: Commit**

```bash
git add agents/r-dependency-manager.md agents/r-pkg-check.md
git commit -m "feat: add MCP-enhanced notes to dependency-manager and pkg-check agents"
```

---

### Task 8: Version bump plugin.json

**Files:**
- Modify: `plugin.json`

- [ ] **Step 1: Bump version**

Change `"version": "0.2.0"` to `"version": "0.3.0"`.

- [ ] **Step 2: Verify glob patterns still match**

Run:
```bash
# New skill should be caught by existing glob
ls skills/r-mcp-setup/SKILL.md  # Must exist

# New detection script is in hooks/ — not covered by plugin.json globs (correct, it's infrastructure)
ls hooks/detect-mcp.sh  # Must exist
```

- [ ] **Step 3: Commit**

```bash
git add plugin.json
git commit -m "chore: bump version to 0.3.0 for MCP integration feature"
```

---

## Chunk 4: Final verification

### Task 9: Full verification pass

Run the complete verification checklist from CLAUDE.md.

- [ ] **Step 1: No magrittr pipe anywhere**

Run: `grep -rn '%>%' skills/ agents/ rules/`
Expected: No output (no matches).

- [ ] **Step 2: All SKILL.md files ≤300 lines with correct frontmatter**

Run:
```bash
for f in skills/*/SKILL.md; do
  lines=$(wc -l < "$f")
  has_fm=$(head -1 "$f")
  if [ "$lines" -gt 300 ]; then echo "OVER 300: $f ($lines lines)"; fi
  if [ "$has_fm" != "---" ]; then echo "NO FRONTMATTER: $f"; fi
done
```
Expected: No output (all pass).

- [ ] **Step 3: All agent files ≤200 lines with no frontmatter**

Run:
```bash
for f in agents/*.md; do
  lines=$(wc -l < "$f")
  has_fm=$(head -1 "$f")
  if [ "$lines" -gt 200 ]; then echo "OVER 200: $f ($lines lines)"; fi
  if [ "$has_fm" = "---" ]; then echo "HAS FRONTMATTER: $f"; fi
done
```
Expected: No output (all pass).

- [ ] **Step 4: Rule files ≤150 lines with no frontmatter**

Run:
```bash
for f in rules/*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 150 ]; then echo "OVER 150: $f ($lines lines)"; fi
done
```

- [ ] **Step 5: Plugin.json glob patterns match new files**

Run:
```bash
ls skills/r-mcp-setup/SKILL.md  # Matched by skills/*/SKILL.md
echo "Version:" && grep '"version"' plugin.json  # Should show 0.3.0
```

- [ ] **Step 6: Detection script runs on macOS and handles missing R**

Run:
```bash
# Test with R present
bash hooks/detect-mcp.sh

# Test with R not on PATH (simulate)
PATH=/usr/bin:/bin bash hooks/detect-mcp.sh
```
Expected: Both return valid JSON with exit code 0.

- [ ] **Step 7: Session-start hook runs end-to-end**

Run:
```bash
cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers && bash hooks/session-start
```
Expected: JSON with `additionalContext` containing MCP status line.

- [ ] **Step 8: Mark verification complete**

All checks pass. MCP integration is complete and ready for use.
