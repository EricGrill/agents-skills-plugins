#!/usr/bin/env bash
set -euo pipefail

# Usage: deploy.sh <host> <user> <arch> [ssh_key]
# Deploys PicoClaw to a remote host

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <host> <user> <arch> [ssh_key]" >&2
  exit 1
fi

HOST="$1"
USER="$2"
ARCH_RAW="$3"
SSH_KEY="${4:-}"

API_KEY_ENV="${API_KEY_ENV:-ANTHROPIC_API_KEY}"
PROVIDER="${PROVIDER:-anthropic}"
API_KEY="${!API_KEY_ENV:-}"

if [[ -z "$API_KEY" ]]; then
  echo "Error: $API_KEY_ENV is not set in local environment." >&2
  exit 1
fi

case "${ARCH_RAW,,}" in
  amd64|x86_64) ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  riscv64) ARCH="riscv64" ;;
  *)
    echo "Unsupported architecture: $ARCH_RAW (expected amd64|arm64|riscv64)" >&2
    exit 1
    ;;
esac

SSH_OPTS=("-o" "BatchMode=yes" "-o" "ConnectTimeout=8")
if [[ -n "$SSH_KEY" ]]; then
  SSH_OPTS+=("-i" "$SSH_KEY")
fi

echo "[deploy] Resolving latest PicoClaw release for arch=$ARCH ..."
LATEST_TAG="$(curl -fsSL https://api.github.com/repos/EricGrill/picoclaw/releases/latest | grep -m1 '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')"
if [[ -z "$LATEST_TAG" ]]; then
  echo "Failed to resolve latest PicoClaw tag from GitHub API." >&2
  exit 1
fi

BINARY_CANDIDATES=(
  "picoclaw-linux-${ARCH}"
  "picoclaw-${ARCH}-linux"
  "picoclaw-${ARCH}"
)

REMOTE_TMP="/tmp/picoclaw"

# Build remote probe/download script.
read -r -d '' REMOTE_SCRIPT <<'EOF' || true
set -euo pipefail
TAG="$1"
ARCH="$2"
PROVIDER="$3"
API_KEY_ENV="$4"
API_KEY="$5"

mkdir -p "$HOME/.local/bin" "$HOME/.picoclaw"

pick_url() {
  local base="https://github.com/EricGrill/picoclaw/releases/download/${TAG}"
  local c
  for c in "picoclaw-linux-${ARCH}" "picoclaw-${ARCH}-linux" "picoclaw-${ARCH}"; do
    if curl -fsI "${base}/${c}" >/dev/null 2>&1; then
      echo "${base}/${c}"
      return 0
    fi
  done
  return 1
}

URL="$(pick_url)" || {
  echo "Could not find compatible binary asset for ${ARCH} in ${TAG}" >&2
  exit 2
}

curl -fsSL "$URL" -o "$HOME/.local/bin/picoclaw"
chmod +x "$HOME/.local/bin/picoclaw"

cat > "$HOME/.picoclaw/.env" <<ENV
PROVIDER=${PROVIDER}
${API_KEY_ENV}=${API_KEY}
ENV
chmod 600 "$HOME/.picoclaw/.env"

if ! grep -q 'HOME/.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
if ! grep -q 'HOME/.local/bin' "$HOME/.zshrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi

export PATH="$HOME/.local/bin:$PATH"
set +e
picoclaw onboard >/tmp/picoclaw-onboard.log 2>&1
ONBOARD_RC=$?
set -e

if [[ $ONBOARD_RC -ne 0 ]]; then
  echo "Warning: picoclaw onboard exited with code $ONBOARD_RC"
  cat /tmp/picoclaw-onboard.log
else
  echo "picoclaw onboard complete"
fi

echo "deployed"
EOF

echo "[deploy] Deploying to ${USER}@${HOST} (tag=${LATEST_TAG}) ..."
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "bash -s -- '$LATEST_TAG' '$ARCH' '$PROVIDER' '$API_KEY_ENV' '$API_KEY'" <<< "$REMOTE_SCRIPT"

echo "[deploy] Success: ${HOST} ready."