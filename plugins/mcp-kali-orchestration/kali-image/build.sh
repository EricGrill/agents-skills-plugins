#!/bin/bash
# Build the MCP-Kali Docker image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="${1:-mcp-kali:latest}"

echo "Building MCP-Kali Docker image: $IMAGE_NAME"
echo "This may take a while due to the size of Kali tools..."

docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"

echo ""
echo "Build complete!"
echo "Image: $IMAGE_NAME"
echo ""
echo "To use with mcp-kali server, set KALI_IMAGE=$IMAGE_NAME in your .env file"
