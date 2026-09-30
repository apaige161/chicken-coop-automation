#!/usr/bin/env bash
# Render the illustrative coop pictures in construction/renders/ from coop_model.scad.
# Needs a desktop OpenSCAD (PNG export uses OpenGL; on headless Linux run under xvfb-run).
set -euo pipefail
cd "$(dirname "$0")"
OPENSCAD="${OPENSCAD:-$(command -v openscad || echo "$HOME/.tools/openscad-2021.01/openscad.com")}"
OUT=../renders
mkdir -p "$OUT"

# name | view | camera eye x,y,z,centre x,y,z
SHOTS=(
  "coop-exterior|exterior|540,-330,210,140,40,55"
  "coop-overview|overview|-380,-620,460,110,-40,40"
  "service-station-open|service_open|440,-70,130,258,82,44"
  "interior-cutaway|interior|150,-230,300,125,62,20"
  "interior-feed-water|interior_close|110,-60,120,215,80,20"
  "nest-bay-open|nest_open|210,330,230,150,124,40"
)

for s in "${SHOTS[@]}"; do
  IFS='|' read -r name view cam <<<"$s"
  "$OPENSCAD" -D "view=\"$view\"" --camera="$cam" --projection=p --imgsize=1600,1000 \
    --colorscheme=Tomorrow -o "$OUT/$name.png" coop_model.scad >/dev/null 2>&1
  printf "ok   %-26s %8d bytes\n" "$name" "$(wc -c <"$OUT/$name.png")"
done
