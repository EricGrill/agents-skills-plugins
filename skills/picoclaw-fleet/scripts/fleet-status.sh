#!/usr/bin/env bash
set -euo pipefail

# Checks all hosts in picoclaw-fleet.json
# Reports: reachable/unreachable, picoclaw installed/not

CONFIG_PATH="${1:-$HOME/.openclaw/workspace/config/picoclaw-fleet.json}"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Config not found: $CONFIG_PATH" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

printf "%-16s %-22s %-12s %-12s %s\n" "NAME" "HOST" "SSH" "PICOCLAW" "DETAILS"
printf "%-16s %-22s %-12s %-12s %s\n" "----------------" "----------------------" "------------" "------------" "------------------------------"

while IFS=$'\t' read -r NAME HOST USER ARCH SSH_KEY; do
  [[ -z "$HOST" ]] && continue
  SSH_OPTS=("-o" "BatchMode=yes" "-o" "ConnectTimeout=6")
  if [[ -n "$SSH_KEY" && "$SSH_KEY" != "null" ]]; then
    SSH_OPTS+=("-i" "${SSH_KEY/#\~/$HOME}")
  fi

  if ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "echo ok" >/dev/null 2>&1; then
    SSH_STATUS="reachable"
    if ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" 'command -v picoclaw >/dev/null 2>&1 || [[ -x "$HOME/.local/bin/picoclaw" ]]' >/dev/null 2>&1; then
      PICO_STATUS="installed"
      DETAIL="ready"
    else
      PICO_STATUS="missing"
      DETAIL="run deploy.sh"
    fi
  else
    SSH_STATUS="unreachable"
    PICO_STATUS="unknown"
    DETAIL="ssh failed"
  fi

  printf "%-16s %-22s %-12s %-12s %s\n" "$NAME" "$HOST" "$SSH_STATUS" "$PICO_STATUS" "$DETAIL"
done < <(python3 - "$CONFIG_PATH" <<'PY'
import json,sys
cfg=json.load(open(sys.argv[1]))
for h in cfg.get("hosts",[]):
  print("\t".join([
    str(h.get("name","")),
    str(h.get("host","")),
    str(h.get("user","")),
    str(h.get("arch","")),
    str(h.get("ssh_key","")),
  ]))
PY
)