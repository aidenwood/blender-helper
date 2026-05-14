#!/usr/bin/env bash
# render-cameras.sh
# Renders every camera in a .blend file to its own output folder.
# Wraps scripts/batch_render_cameras.py for headless overnight use.
#
# Usage:
#   ./render-cameras.sh path/to/scene.blend [output_root]
#
# Output structure:
#   <output_root>/<camera_name>/####.png
#
# macOS will stay awake during the render (caffeinate -i) and ping a
# notification when done.

set -euo pipefail

BLEND="${1:-}"
OUTPUT_ROOT="${2:-./renders/cameras}"

if [[ -z "${BLEND}" || ! -f "${BLEND}" ]]; then
  echo "Usage: $0 path/to/scene.blend [output_root]" >&2
  exit 1
fi

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
if [[ ! -x "${BLENDER}" ]]; then
  echo "Blender not found at ${BLENDER}. Edit the BLENDER path in this script." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${SCRIPT_DIR}/scripts/batch_render_cameras.py"

mkdir -p "${OUTPUT_ROOT}"
LOG="${OUTPUT_ROOT}/render-cameras.log"

echo "[render-cameras] blend=${BLEND}"
echo "[render-cameras] output=${OUTPUT_ROOT}"
echo "[render-cameras] log=${LOG}"

BHELPER_OUTPUT_ROOT="${OUTPUT_ROOT}" caffeinate -i \
  "${BLENDER}" -b "${BLEND}" -P "${PY}" 2>&1 | tee "${LOG}"

osascript -e "display notification \"Cameras rendered to ${OUTPUT_ROOT}\" with title \"Blender done\""
echo "[render-cameras] done."
