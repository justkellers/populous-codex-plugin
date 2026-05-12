#!/usr/bin/env bash
set -euo pipefail

MCP_URL="${POPULOUS_MCP_URL:-https://run.populous.app/mcp}"
BODY='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_BODY"' EXIT

if [[ -n "${POPULOUS_ACCESS_TOKEN:-}" ]]; then
  STATUS="$(
    curl -sS \
      -o "$TMP_BODY" \
      -w "%{http_code}" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${POPULOUS_ACCESS_TOKEN}" \
      --data "$BODY" \
      "$MCP_URL"
  )"
else
  STATUS="$(
    curl -sS \
      -o "$TMP_BODY" \
      -w "%{http_code}" \
      -X POST \
      -H "Content-Type: application/json" \
      --data "$BODY" \
      "$MCP_URL"
  )"
fi

case "$STATUS" in
  200)
    echo "OK: Populous MCP endpoint responded to initialize."
    ;;
  401)
    echo "OK: Populous MCP endpoint is reachable and requires bearer auth."
    ;;
  *)
    echo "Unexpected status from Populous MCP: $STATUS" >&2
    sed -n '1,20p' "$TMP_BODY" >&2
    exit 1
    ;;
esac
