# Handoff / Status

**Status: complete (design package v1.0).** The original goals in the first session's
handoff are all implemented and verified. See `README.md` for the build order and the
"Before building: check these by hand" list.

## Done
- Spec + single-source pin map (`PROJECT_SPEC.md`, `hardware/pinmap.yaml`)
- ESPHome firmware: controller + optional camera. Validated and compiled (ESPHome 2026.9)
- KiCad PCB generated from `pcb/design.py`, autorouted (Freerouting). ERC/DRC clean, Gerbers + BOM
- 8 OpenSCAD parts → 15 STLs
- Construction plan, cut list, wiring/plumbing/run docs, 5 generated diagrams
- Priced parts list (2026 estimates), Home Assistant docs/automations/dashboard
- `tools/check_consistency.py` + GitHub Actions CI

## Decisions that stand (the user can redirect)
- ESPHome instead of raw Arduino/ESP-IDF, KiCad instead of Eagle.
- Mains stays off the PCB (separate electrician-installed mains box with SSRs + PSU).

## Needs a human
- Review the autorouted PCB in the KiCad GUI before ordering. Confirm the relay pinout and
  the ESP32 row spacing.
- Electrician for all 120 V work. Local permit and snow/wind-load check for the structure.
- Site-specific firmware substitutions (lat/long/timezone, feeding times, BLE MAC).
