#!/usr/bin/env bash
# new-gig.sh
# Scaffolds a standard gig folder structure. Run once at the start of every gig.
#
# Usage:
#   ./new-gig.sh <gig-name> [parent-dir]
#
# Example:
#   ./new-gig.sh 2026-05-22_warehouse_brisbane ~/Desktop/Gigs
#
# Creates:
#   <parent-dir>/<gig-name>/
#     00_reference/       — stage photos, brief, BPM notes
#     01_svg/             — traced SVGs
#     02_blender/         — .blend files
#     03_renders/         — Blender output (cameras/, layers/)
#         cameras/
#         layers/
#     04_ae/              — After Effects projects + exported MOVs
#     05_resolume/        — final clips ready to drop into Resolume
#     06_deliverables/    — anything you give to the client/venue
#     README.md           — gig brief template

set -euo pipefail

NAME="${1:-}"
PARENT="${2:-${HOME}/Desktop/Gigs}"

if [[ -z "${NAME}" ]]; then
  echo "Usage: $0 <gig-name> [parent-dir]" >&2
  echo "Example: $0 2026-05-22_warehouse_brisbane ~/Desktop/Gigs" >&2
  exit 1
fi

ROOT="${PARENT}/${NAME}"
if [[ -d "${ROOT}" ]]; then
  echo "Folder already exists: ${ROOT}" >&2
  exit 1
fi

mkdir -p "${ROOT}/00_reference"
mkdir -p "${ROOT}/01_svg"
mkdir -p "${ROOT}/02_blender"
mkdir -p "${ROOT}/03_renders/cameras"
mkdir -p "${ROOT}/03_renders/layers"
mkdir -p "${ROOT}/04_ae"
mkdir -p "${ROOT}/05_resolume"
mkdir -p "${ROOT}/06_deliverables"

cat > "${ROOT}/README.md" <<EOF
# ${NAME}

## Gig brief
- Date:
- Venue:
- Artist / DJ:
- Set length:
- Track BPM range:
- Projection setup (1080 / ultrawide / 4K / multi-surface):
- Frame rate (50 / 60):

## Folder layout
- \`00_reference/\` — stage photos, briefs, anything from the client.
- \`01_svg/\` — traced SVGs (one per layer category: bg / stage / lights / performer).
- \`02_blender/\` — .blend files. Use \`apply_render_preset.py\` + \`loop_length_calculator.py\` before rendering.
- \`03_renders/\` — Blender outputs. \`cameras/\` for per-camera, \`layers/\` for Resolume layer comps.
- \`04_ae/\` — After Effects projects + intermediate MOVs.
- \`05_resolume/\` — final HAP/DXV clips ready to drag into Resolume's clip browser.
- \`06_deliverables/\` — anything you hand off (preview MP4s, contact sheets).

## Render commands

\`\`\`bash
# Per-camera render
~/Desktop/00\\ -\\ Aidxn/blender-helper/cli/render-cameras.sh 02_blender/main.blend 03_renders/cameras

# Layer render (Resolume comp)
~/Desktop/00\\ -\\ Aidxn/blender-helper/cli/render-layers.sh 02_blender/main.blend 03_renders/layers

# Transcode PNG sequences to HAP Alpha for Resolume
for d in 03_renders/layers/*/; do
  ~/Desktop/00\\ -\\ Aidxn/blender-helper/cli/transcode-to-hap.sh "\$d" 50 hap_alpha
done
\`\`\`

## Pre-gig checklist
- [ ] Track BPM confirmed
- [ ] Loop lengths set (\`loop_length_calculator.py\`)
- [ ] All layers rendered with alpha
- [ ] Clips transcoded to HAP / DXV3
- [ ] Resolume comp built and BPM-synced
- [ ] Tested on the actual projection resolution
- [ ] Backup drive packed
EOF

echo "[new-gig] created ${ROOT}"
echo "[new-gig] README at ${ROOT}/README.md"
open "${ROOT}" 2>/dev/null || true
