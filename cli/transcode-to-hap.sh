#!/usr/bin/env bash
# transcode-to-hap.sh
# Converts a PNG image sequence (RGBA) to a HAP / HAP Alpha .mov for Resolume.
# Requires FFmpeg built with HAP codec support (the standard Homebrew build has it).
#
# Usage:
#   ./transcode-to-hap.sh path/to/sequence_folder [fps] [variant]
#
# variant:
#   hap          — colour only, no alpha. Smallest file.
#   hap_alpha    — colour + alpha. Most common for VJ layers.   (default)
#   hap_q        — higher quality, no alpha. Larger file.
#   hap_q_alpha  — higher quality + alpha. Largest. Use FFmpeg's built-in;
#                  for true HAP Q Alpha you may still need AfterCodecs/HAPpy.
#
# Output goes next to the input folder: <folder_name>.mov
#
# Tip: run on overnight Blender output:
#   for d in renders/layers/*/; do ./transcode-to-hap.sh "$d" 50 hap_alpha; done

set -euo pipefail

INPUT="${1:-}"
FPS="${2:-50}"
VARIANT="${3:-hap_alpha}"

if [[ -z "${INPUT}" || ! -d "${INPUT}" ]]; then
  echo "Usage: $0 path/to/sequence_folder [fps] [variant]" >&2
  echo "  variant: hap | hap_alpha | hap_q | hap_q_alpha" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null; then
  echo "FFmpeg not installed. brew install ffmpeg" >&2
  exit 1
fi

case "${VARIANT}" in
  hap)         CODEC_ARGS=(-c:v hap -format hap) ;;
  hap_alpha)   CODEC_ARGS=(-c:v hap -format hap_alpha) ;;
  hap_q)       CODEC_ARGS=(-c:v hap -format hap_q) ;;
  hap_q_alpha) CODEC_ARGS=(-c:v hap -format hap_q_alpha) ;;
  *)           echo "Unknown variant '${VARIANT}'" >&2; exit 1 ;;
esac

INPUT="${INPUT%/}"
NAME="$(basename "${INPUT}")"
OUTPUT="$(dirname "${INPUT}")/${NAME}.mov"

# Find numbering pattern by sampling the first file.
FIRST="$(find "${INPUT}" -maxdepth 1 -type f \( -name '*.png' -o -name '*.tif' -o -name '*.tiff' -o -name '*.exr' \) | sort | head -n 1 || true)"
if [[ -z "${FIRST}" ]]; then
  echo "No image files in ${INPUT}" >&2
  exit 1
fi
EXT="${FIRST##*.}"
# Common Blender output: 0001.png, 0002.png — assume 4-digit. If not, edit %04d.
PATTERN="${INPUT}/%04d.${EXT}"

echo "[transcode] ${INPUT} → ${OUTPUT}  (${VARIANT} @ ${FPS}fps)"

ffmpeg -y \
  -framerate "${FPS}" \
  -i "${PATTERN}" \
  "${CODEC_ARGS[@]}" \
  "${OUTPUT}"

echo "[transcode] done → ${OUTPUT}"
