#!/usr/bin/env bash
# render-overnight.sh
# Renders every .blend file in a queue folder, one after the other.
# Drop your scenes into the queue folder before bed, wake up to a finished pile.
#
# Usage:
#   ./render-overnight.sh path/to/queue_folder [output_root]
#
# For each blend.blend in the queue, output goes to:
#   <output_root>/<blend_basename>/####.png
#
# Settings (samples, output format) come from each .blend's own scene settings.
# Use apply_render_preset.py on each scene before queuing if you want shared defaults.

set -euo pipefail

QUEUE="${1:-}"
OUTPUT_ROOT="${2:-./renders/overnight}"

if [[ -z "${QUEUE}" || ! -d "${QUEUE}" ]]; then
  echo "Usage: $0 path/to/queue_folder [output_root]" >&2
  exit 1
fi

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
if [[ ! -x "${BLENDER}" ]]; then
  echo "Blender not found at ${BLENDER}. Edit the BLENDER path in this script." >&2
  exit 1
fi

mkdir -p "${OUTPUT_ROOT}"
MASTER_LOG="${OUTPUT_ROOT}/overnight.log"
echo "[overnight] starting at $(date)" | tee -a "${MASTER_LOG}"
echo "[overnight] queue=${QUEUE}" | tee -a "${MASTER_LOG}"
echo "[overnight] output=${OUTPUT_ROOT}" | tee -a "${MASTER_LOG}"

shopt -s nullglob
FILES=("${QUEUE}"/*.blend)
shopt -u nullglob

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "[overnight] no .blend files in queue" | tee -a "${MASTER_LOG}"
  exit 0
fi

echo "[overnight] ${#FILES[@]} file(s) queued" | tee -a "${MASTER_LOG}"

caffeinate -i bash -c '
  for BLEND in "$@"; do
    NAME="$(basename "${BLEND}" .blend)"
    OUT="'"${OUTPUT_ROOT}"'/${NAME}"
    LOG="${OUT}/render.log"
    mkdir -p "${OUT}"
    echo "[overnight] $(date) → ${NAME}" | tee -a "'"${MASTER_LOG}"'"
    "'"${BLENDER}"'" -b "${BLEND}" -o "${OUT}/####" -F PNG -x 1 -a 2>&1 | tee "${LOG}"
  done
' _ "${FILES[@]}"

echo "[overnight] done at $(date)" | tee -a "${MASTER_LOG}"
osascript -e "display notification \"Overnight queue finished (${#FILES[@]} files)\" with title \"Blender done\""
