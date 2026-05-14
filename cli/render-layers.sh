#!/usr/bin/env bash
# render-layers.sh
# Renders each top-level collection in a .blend as its own image sequence
# with alpha — one clip per Resolume layer.
# Wraps scripts/batch_render_collections_as_layers.py.
#
# Usage:
#   ./render-layers.sh path/to/scene.blend [output_root]
#
# Output structure:
#   <output_root>/<collection_name>/####.png  (RGBA)

set -euo pipefail

BLEND="${1:-}"
OUTPUT_ROOT="${2:-./renders/layers}"

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
PY="${SCRIPT_DIR}/scripts/batch_render_collections_as_layers.py"

mkdir -p "${OUTPUT_ROOT}"
LOG="${OUTPUT_ROOT}/render-layers.log"

echo "[render-layers] blend=${BLEND}"
echo "[render-layers] output=${OUTPUT_ROOT}"
echo "[render-layers] log=${LOG}"

BHELPER_OUTPUT_ROOT="${OUTPUT_ROOT}" caffeinate -i \
  "${BLENDER}" -b "${BLEND}" -P "${PY}" 2>&1 | tee "${LOG}"

osascript -e "display notification \"Layers rendered to ${OUTPUT_ROOT}\" with title \"Blender done\""
echo "[render-layers] done."
