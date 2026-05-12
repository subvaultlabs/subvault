#!/bin/bash
# SubVault — Install MCP server config for Claude Desktop, Cursor, and VS Code.
# Usage: curl -fsSL https://subvault.ai/setup.sh | bash -s YOUR_API_KEY

set -euo pipefail

KEY="${1:-}"
if [ -z "$KEY" ]; then
  echo "Usage: curl -fsSL https://subvault.ai/setup.sh | bash -s YOUR_API_KEY"
  exit 1
fi

if [[ ! "$KEY" =~ ^sv_live_ ]]; then
  echo "Error: API key must start with sv_live_"
  exit 1
fi

if [ "$(id -u)" = "0" ]; then
  echo "Error: don't run this as root. SubVault config files belong in your own home directory."
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required."
  exit 1
fi

URL="https://mcp.subvault.ai/mcp"
CONFIGURED=0

# Python helper. Two modes:
#   SUBVAULT_MODE=render → print a complete {"<wrapper>":{"subvault":...}} snippet on stdout
#   SUBVAULT_MODE=merge  → merge SubVault into the config file at SUBVAULT_FILE
# Values pass through env vars so the API key doesn't have to be escape-safe.
run_helper() {
  SUBVAULT_URL="$URL" \
  SUBVAULT_KEY="$KEY" \
  SUBVAULT_MODE="$1" \
  SUBVAULT_WRAPPER="${2:-}" \
  SUBVAULT_FILE="${3:-}" \
  SUBVAULT_NAME="${4:-}" \
  python3 -c '
import json, os, sys

entry = {
    "type": "http",
    "url": os.environ["SUBVAULT_URL"],
    "headers": {"Authorization": "Bearer " + os.environ["SUBVAULT_KEY"]},
}

mode    = os.environ["SUBVAULT_MODE"]
wrapper = os.environ["SUBVAULT_WRAPPER"]

if mode == "render":
    print(json.dumps({wrapper: {"subvault": entry}}, indent=2))
    sys.exit(0)

if mode == "merge":
    path = os.environ["SUBVAULT_FILE"]
    name = os.environ["SUBVAULT_NAME"]
    try:
        with open(path) as f:
            cfg = json.load(f)
        action = "Updated"
    except FileNotFoundError:
        cfg = {}
        action = "Created"
    except json.JSONDecodeError:
        sys.stderr.write(
            f"  Error: {path} is not valid JSON; leaving it untouched.\n"
            f"  Fix the file by hand, then re-run.\n"
        )
        sys.exit(2)
    cfg.setdefault(wrapper, {})["subvault"] = entry
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"  {action} {name} config")
    sys.exit(0)

sys.stderr.write(f"  Error: unknown helper mode {mode!r}\n")
sys.exit(3)
'
}

merge_config() {
  local file="$1" wrapper="$2" name="$3"
  mkdir -p "$(dirname "$file")"
  run_helper merge "$wrapper" "$file" "$name" && CONFIGURED=$((CONFIGURED+1))
}

echo ""
echo "  SubVault — configuring MCP servers"
echo ""

# Claude Desktop
if [ "$(uname)" = "Darwin" ]; then
  CLAUDE_CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
  CLAUDE_CFG="$HOME/.config/Claude/claude_desktop_config.json"
fi
if [ -d "$(dirname "$CLAUDE_CFG")" ]; then
  merge_config "$CLAUDE_CFG" "mcpServers" "Claude Desktop"
else
  echo "  — Claude Desktop not found (skipped)"
fi

# Cursor
CURSOR_CFG="$HOME/.cursor/mcp.json"
if [ -d "$HOME/.cursor" ]; then
  merge_config "$CURSOR_CFG" "mcpServers" "Cursor"
else
  echo "  — Cursor not found (skipped)"
fi

# VS Code — MCP config is per-project, so print the snippet to paste instead
# of writing a config file we can't locate. Wrapper key is "servers" here, not
# "mcpServers".
if command -v code &>/dev/null 2>&1; then
  echo ""
  echo "  VS Code detected — paste this into .vscode/mcp.json in your project:"
  echo ""
  run_helper render servers | /usr/bin/sed 's/^/  /'
  echo ""
  CONFIGURED=$((CONFIGURED+1))
else
  echo "  — VS Code not found (skipped)"
fi

echo ""
if [ "$CONFIGURED" -gt 0 ]; then
  echo "  Done. Restart your AI tools to pick up the new config."
  echo ""
  echo "  Then try: \"remember what I've been working on\""
  echo "  Or after a useful chat: \"vault this\""
else
  echo "  No supported tools found. Set it up by hand:"
  echo "    https://subvault.ai/docs/setup"
fi
echo ""
