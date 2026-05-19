#!/usr/bin/env bash
set -uo pipefail

# MCP detection helper for supeRpowers
# Used by: hooks/session-start, skills/r-mcp-setup
# Output: JSON to stdout — always exits 0
# Interface: {
#   "mcp_registered": bool,         # btw/mcptools (r-btw) registered
#   "btw_installed": bool,          # btw R package available
#   "mcptools_installed": bool,     # mcptools R package available
#   "mcp_repl_installed": bool,     # mcp-repl binary on PATH
#   "mcp_repl_registered": bool,    # mcp-repl registered as MCP server
#   "tool_groups": [...]            # available btw tool groups
# }

MCP_REGISTERED=false
BTW_INSTALLED=false
MCPTOOLS_INSTALLED=false
MCP_REPL_INSTALLED=false
MCP_REPL_REGISTERED=false
TOOL_GROUPS="[]"

# --- Check MCP server registration (btw/mcptools as "r-btw") ---
for config_file in ".claude/settings.json" ".mcp.json" "${HOME}/.claude/settings.json"; do
    if [ -f "$config_file" ] && grep -q '"r-btw"' "$config_file" 2>/dev/null; then
        MCP_REGISTERED=true
        break
    fi
done

# --- Check mcp-repl registration ---
for config_file in ".claude/settings.json" ".mcp.json" "${HOME}/.claude/settings.json"; do
    if [ -f "$config_file" ] && grep -q '"mcp-repl"' "$config_file" 2>/dev/null; then
        MCP_REPL_REGISTERED=true
        break
    fi
done

# --- Check mcp-repl binary on PATH ---
if command -v mcp-repl > /dev/null 2>&1; then
    MCP_REPL_INSTALLED=true
fi

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
    TOOL_GROUPS='["docs","pkg","env","run","search","session"]'
fi

# --- Output JSON ---
cat <<EOF
{"mcp_registered":$MCP_REGISTERED,"btw_installed":$BTW_INSTALLED,"mcptools_installed":$MCPTOOLS_INSTALLED,"mcp_repl_installed":$MCP_REPL_INSTALLED,"mcp_repl_registered":$MCP_REPL_REGISTERED,"tool_groups":$TOOL_GROUPS}
EOF
