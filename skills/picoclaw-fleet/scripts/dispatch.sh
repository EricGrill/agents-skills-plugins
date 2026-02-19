#!/usr/bin/env bash
set -euo pipefail

# Usage: dispatch.sh <host> <user> <task> [timeout_seconds]
# Runs a one-shot PicoClaw task and returns output

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <host> <user> <task> [timeout_seconds]" >&2
  exit 1
fi

HOST="$1"
USER="$2"
TASK="$3"
TIMEOUT_SECONDS="${4:-120}"
SSH_KEY="${SSH_KEY:-}"

SSH_OPTS=("-o" "BatchMode=yes" "-o" "ConnectTimeout=8")
if [[ -n "$SSH_KEY" ]]; then
  SSH_OPTS+=("-i" "$SSH_KEY")
fi

read -r -d '' REMOTE_SCRIPT <<'EOF' || true
set -euo pipefail
TASK="$1"
TIMEOUT_SECONDS="$2"

export PATH="$HOME/.local/bin:$PATH"

if ! command -v picoclaw >/dev/null 2>&1; then
  echo "ERROR: picoclaw not installed" >&2
  exit 10
fi

if command -v timeout >/dev/null 2>&1; then
  timeout "$TIMEOUT_SECONDS" picoclaw agent -m "$TASK"
elif command -v gtimeout >/dev/null 2>&1; then
  gtimeout "$TIMEOUT_SECONDS" picoclaw agent -m "$TASK"
else
  perl -e 'alarm shift; exec @ARGV' "$TIMEOUT_SECONDS" picoclaw agent -m "$TASK"
fi
EOF

TASK_Q="$(printf '%q' "$TASK")"
TIMEOUT_Q="$(printf '%q' "$TIMEOUT_SECONDS")"
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "bash -s -- ${TASK_Q} ${TIMEOUT_Q}" <<< "$REMOTE_SCRIPT"