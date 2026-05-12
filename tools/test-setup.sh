#!/bin/bash
# Test setup.sh against a variety of inputs.
set -u

SETUP_SH="${1:-}"
if [ -z "$SETUP_SH" ] || [ ! -f "$SETUP_SH" ]; then
  echo "Usage: $0 /absolute/path/to/setup.sh"
  exit 1
fi

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/subvault-setup-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

PASS=0
FAIL=0

# File paths reach Python through env vars, so any character is allowed.
py_json_valid() {
  SUBVAULT_TEST_FILE="$1" python3 -c \
    "import json,os; json.load(open(os.environ['SUBVAULT_TEST_FILE']))" \
    2>/dev/null
}

run_test() {
  local name="$1" key="$2" expect_exit="$3"
  local home="$TEST_ROOT/$name"
  mkdir -p "$home/.cursor"
  mkdir -p "$home/Library/Application Support/Claude"
  mkdir -p "$home/.config/Claude"

  local actual_exit
  HOME="$home" "$SETUP_SH" "$key" >"$home/stdout.txt" 2>"$home/stderr.txt"
  actual_exit=$?

  if [ "$actual_exit" = "$expect_exit" ]; then
    PASS=$((PASS+1))
    printf "  \033[32m✓\033[0m %s (exit=%s)\n" "$name" "$actual_exit"
  else
    FAIL=$((FAIL+1))
    printf "  \033[31m✗\033[0m %s (got exit=%s, expected %s)\n" "$name" "$actual_exit" "$expect_exit"
    echo "    stdout: $(cat "$home/stdout.txt")"
    echo "    stderr: $(cat "$home/stderr.txt")"
  fi
}

verify_json_valid() {
  local file="$1" name="$2"
  if py_json_valid "$file"; then
    PASS=$((PASS+1))
    printf "  \033[32m✓\033[0m %s — valid JSON\n" "$name"
  else
    FAIL=$((FAIL+1))
    printf "  \033[31m✗\033[0m %s — INVALID JSON\n" "$name"
    [ -f "$file" ] && cat "$file"
  fi
}

verify_contains() {
  local file="$1" needle="$2" name="$3"
  if grep -q -- "$needle" "$file"; then
    PASS=$((PASS+1))
    printf "  \033[32m✓\033[0m %s contains expected: %s\n" "$name" "$needle"
  else
    FAIL=$((FAIL+1))
    printf "  \033[31m✗\033[0m %s missing: %s\n" "$name" "$needle"
    [ -f "$file" ] && cat "$file"
  fi
}

echo "================================================================"
echo "  setup.sh test suite"
echo "================================================================"

echo ""
echo "--- TEST: rejection of invalid prefix ---"
run_test "bad-prefix" "bogus_key_12345" 1
run_test "empty-key"  ""                1

echo ""
echo "--- TEST: simple key writes valid JSON to both Cursor + Claude ---"
run_test "simple" "sv_live_a1b2c3d4e5f6" 0
verify_json_valid "$TEST_ROOT/simple/.cursor/mcp.json" "Cursor config (simple)"
verify_json_valid "$TEST_ROOT/simple/Library/Application Support/Claude/claude_desktop_config.json" "Claude config (simple)"
verify_contains  "$TEST_ROOT/simple/.cursor/mcp.json" "sv_live_a1b2c3d4e5f6" "Cursor key present"
verify_contains  "$TEST_ROOT/simple/.cursor/mcp.json" "Bearer" "Cursor 'Bearer' prefix"

echo ""
echo "--- TEST: pathological keys (quote, dollar, backslash, newline) ---"
run_test "single-quote"    "sv_live_with'quote"       0
run_test "dollar-sign"     "sv_live_with\$dollar"     0
run_test "backslash"       "sv_live_with\\backslash"  0
run_test "newline-attempt" $'sv_live_with\nnewline'   0
verify_contains "$TEST_ROOT/single-quote/.cursor/mcp.json" "with'quote"  "single-quote round-trip"
verify_contains "$TEST_ROOT/dollar-sign/.cursor/mcp.json"  "with.dollar" "dollar-sign round-trip (regex .)"

echo ""
echo "--- TEST: existing config preserved, SubVault merged in ---"
home="$TEST_ROOT/merge"
mkdir -p "$home/.cursor"
echo '{"mcpServers":{"another-tool":{"command":"foo"}},"custom-setting":42}' > "$home/.cursor/mcp.json"
HOME="$home" "$SETUP_SH" sv_live_merger >/dev/null 2>&1
verify_json_valid "$home/.cursor/mcp.json" "merged Cursor config"
verify_contains  "$home/.cursor/mcp.json" "another-tool"   "preserved 'another-tool'"
verify_contains  "$home/.cursor/mcp.json" "subvault"       "added subvault"
verify_contains  "$home/.cursor/mcp.json" "custom-setting" "preserved top-level setting"

echo ""
echo "--- TEST: idempotency — re-running updates the SubVault entry only ---"
HOME="$TEST_ROOT/merge" "$SETUP_SH" sv_live_merger_v2 >/dev/null 2>&1
verify_json_valid "$TEST_ROOT/merge/.cursor/mcp.json" "after re-run"
verify_contains  "$TEST_ROOT/merge/.cursor/mcp.json" "sv_live_merger_v2" "key was updated"
verify_contains  "$TEST_ROOT/merge/.cursor/mcp.json" "another-tool"      "other servers still present"

echo ""
echo "--- TEST: corrupted existing config is preserved, not clobbered ---"
home="$TEST_ROOT/corrupt"
mkdir -p "$home/.cursor"
echo 'NOT VALID JSON {{{ ' > "$home/.cursor/mcp.json"
HOME="$home" "$SETUP_SH" sv_live_safe >/dev/null 2>"$home/stderr.txt" || true
if grep -q "NOT VALID JSON" "$home/.cursor/mcp.json"; then
  PASS=$((PASS+1)); printf "  \033[32m✓\033[0m corrupt config preserved on parse error\n"
else
  FAIL=$((FAIL+1)); printf "  \033[31m✗\033[0m corrupt config was clobbered!\n"
fi

echo ""
echo "================================================================"
printf "  Results: \033[32m%d passed\033[0m, \033[31m%d failed\033[0m\n" "$PASS" "$FAIL"
echo "================================================================"
[ "$FAIL" = 0 ]
