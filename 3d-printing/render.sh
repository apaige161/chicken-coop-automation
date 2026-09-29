#!/usr/bin/env bash
# Render every printable part to stl/. Fails if OpenSCAD reports an error or an empty mesh.
# OPENSCAD env var overrides the binary (default: openscad on PATH, then ~/.tools portable).
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-$(command -v openscad || echo "$HOME/.tools/openscad-2021.01/openscad.com")}"
mkdir -p stl

# file | part parameter (empty = default) | output name
PARTS=(
  "feeder_funnel_adapter.scad||feeder_funnel_adapter"
  "camera_mount.scad|case|camera_case"
  "camera_mount.scad|lid|camera_lid"
  "camera_mount.scad|bracket|camera_bracket"
  "pir_mount.scad||pir_housing"
  "ble_sensor_case.scad|base|ble_case_base"
  "ble_sensor_case.scad|lid|ble_case_lid"
  "sensor_radiation_shield.scad|base|shield_base"
  "sensor_radiation_shield.scad|plate|shield_louvre_x4"
  "sensor_radiation_shield.scad|top|shield_top"
  "sensor_radiation_shield.scad|spacer|shield_spacer_x12"
  "reed_switch_bracket.scad|switch|reed_switch_bracket_x2"
  "reed_switch_bracket.scad|magnet|reed_magnet_holder_x2"
  "ultrasonic_lid_mount.scad||ultrasonic_lid_mount"
  "controller_backplate.scad||controller_backplate"
)

fail=0
for entry in "${PARTS[@]}"; do
  IFS='|' read -r src part name <<<"$entry"
  args=()
  [[ -n "$part" ]] && args=(-D "part=\"$part\"")
  log=$("$OPENSCAD" "${args[@]}" -o "stl/$name.stl" "$src" 2>&1) || { echo "FAIL $name"; echo "$log"; fail=1; continue; }
  if grep -qiE "^ERROR|WARNING: Object may not be a valid 2-manifold|Current top level object is empty" <<<"$log"; then
    echo "FAIL $name"; echo "$log"; fail=1; continue
  fi
  printf "ok   %-28s %8d bytes\n" "$name" "$(wc -c <"stl/$name.stl")"
done
exit $fail
