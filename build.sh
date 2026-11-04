#!/usr/bin/env bash
# Regenerates index.html inside a Python container: only Docker is needed locally.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

IMAGE="world-travels-builder"

docker build -q -t "$IMAGE" . >/dev/null
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -v "$PWD":/app \
  "$IMAGE"
