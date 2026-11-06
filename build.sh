#!/usr/bin/env bash
# Regenerates index.html inside a Python container: only Docker is needed locally.
# Usage: ./build.sh [DATA_DIR]
#   DATA_DIR  folder containing your notes/ (and receiving index.html).
#             Defaults to this repository (example notes).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

IMAGE="world-travels-builder"

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [DATA_DIR]" >&2
  exit 2
fi

MOUNT_ARGS=()
CMD_ARGS=()
if [[ $# -eq 1 ]]; then
  if [[ ! -d "$1" ]]; then
    echo "Error: data folder not found: $1" >&2
    exit 1
  fi
  DATA="$(realpath "$1")"
  MOUNT_ARGS=(-v "$DATA":/data)
  CMD_ARGS=(python build.py /data)
else
  DATA="$PWD"
fi

docker build -q -t "$IMAGE" . >/dev/null
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -v "$PWD":/app \
  "${MOUNT_ARGS[@]}" \
  "$IMAGE" \
  "${CMD_ARGS[@]}"
echo "Output: $DATA/index.html"
