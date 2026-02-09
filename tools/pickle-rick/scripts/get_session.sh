#!/bin/bash
# Returns the session path for the current working directory.

set -euo pipefail

EXTENSION_DIR="$HOME/.gemini/extensions/pickle-rick"
SESSIONS_MAP="$EXTENSION_DIR/current_sessions.json"

TARGET_DIR="${1:-$PWD}"

if [[ ! -f "$SESSIONS_MAP" ]]; then
  # No sessions map exists
  exit 1
fi

# Find exact match for TARGET_DIR
SESSION_PATH=$(jq -r --arg cwd "$TARGET_DIR" '.[$cwd] // empty' "$SESSIONS_MAP")

if [[ -n "$SESSION_PATH" ]]; then
  echo "$SESSION_PATH"
else
  exit 1
fi
