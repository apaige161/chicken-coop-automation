# Handoff: Automated Chicken Coop Project

Session paused here at the user's request (restarting Claude Code to update). Nothing has been built yet except this folder. Resume by pasting this file's contents back to Claude, or just pointing it at this directory.

## Original goal (user's request, verbatim intent)

Build out a complete automated chicken coop system:

- Prefer **low-tech solutions** where possible, but everything should have an **upgrade path** to more automation later.
- Firmware for an **ESP32** (built-in BLE + WiFi).
- Must connect to **Home Assistant** for full control.
- **Wiring diagrams**.
- A path to a **PCB design** (Eagle or another EDA tool) so it can be fabricated.
- A path to **3D-printed parts** (enclosures/mounts/brackets) via a print service.
- **Detailed construction design for a 50-bird coop.**
- Birds should be able to **free-range most of the day**.
- **Full parts list with price breakdown.**
- **Camera(s) nice-to-have, not required.**
- Site conditions: **partially shaded**, **120V power available nearby**, **water spigot nearby**.
- User wants to give requirements once and have agents **continue implementing overnight to completion**, with **gated commits** (only commit after tests/checks pass at each step) rather than one big final commit.

## Decisions already made this session

- **Target directory:** `C:\Users\apaig\LocalCode\chicken-coop-automation` (just created, empty — no git init yet, no code written yet).
- **Project type:** Greenfield.
- **Commit strategy:** Gated commits at each completed/verified step, not a single end-of-run commit.
- **Firmware framework:** Defaulting to **ESPHome** (not raw Arduino/ESP-IDF) — local-first, integrates natively with Home Assistant, fits the "low-tech but upgradable" philosophy (start with a couple entities, add more without rewriting firmware). *User has not explicitly confirmed this — flagged as a substitution, they can redirect.*
- **PCB tool:** Defaulting to **KiCad** instead of Eagle — free, fully text/scriptable (so an agent can actually author schematic/board files), outputs standard Gerbers any fab (JLCPCB/PCBWay/OSH Park) accepts. *Also not explicitly confirmed by user — flagged as a substitution.*
- **Safety note to include prominently in deliverables:** 120V mains wiring and load-bearing structure for 50 birds need a real electrician / local-code review before construction — plans will be thorough but are not a substitute for that sign-off. This must not get silently dropped in later passes.

## Planned approach (not yet started)

1. Write a `PROJECT_SPEC.md` at the repo root myself (not delegated) covering the shared architecture so downstream agents don't produce inconsistent designs:
   - System architecture: ESP32 + ESPHome ↔ Home Assistant over WiFi (native API); BLE for a secondary low-power use case (e.g. gate/door sensor or beacon).
   - Subsystems, each with a low-tech baseline and an upgrade option:
     - Pop door (manual slide → light/schedule-triggered actuator via ESP32)
     - Feeder (gravity PVC → motorized auger dispenser)
     - Waterer (nipple bucket → level-sensed solenoid fed from the spigot, plus freeze protection)
     - Environmental sensing (temp/humidity/light — always included, reports to HA)
     - Predator/security (door sensor, optional PIR, optional camera, BLE tamper/left-open detection)
     - Supplemental lighting on the 120V circuit, relay-controlled, scheduled via HA
     - Camera as an explicitly optional add-on (ESP32-CAM secondary unit)
   - A fixed **GPIO/pin map** and component list, decided once up front, so firmware / PCB / wiring-diagram agents stay consistent with each other.
   - Power architecture: mains → stepped-down low-voltage supply for electronics; separate relay-switched 120V branch for heater/lighting; explicit call-out that outdoor 120V wiring must be GFCI-protected and code-compliant.
   - PCB deliverable scope-setting: aim for a genuinely simple, low-pin-count controller/relay-breakout board (ESP32 dev module + a handful of relay drivers + terminal blocks) since that's realistically hand-routable; schematic should be reliable, but the actual `.kicad_pcb` layout must be flagged for manual visual verification/DRC in the KiCad GUI before fabrication — Claude can't visually inspect a rendered board.
   - Coop sizing math worked out roughly already: ~4 sq ft/bird indoor for 50 birds ≈ 200 sq ft coop interior, ~1 nest box per 4–5 hens ≈ 10–13 boxes, ~8–10 inches of roost bar per bird ≈ 33–42 ft of roost total. Free-range run sizing is secondary since birds are out most of the day, but predator-proof perimeter (buried hardware-cloth apron) still matters.

2. Launch parallel domain agents (general-purpose, full tool access incl. WebSearch for current pricing), each scoped to its own subfolder to avoid merge conflicts, each given the full `PROJECT_SPEC.md` as shared context:
   - `firmware/` — ESPHome YAML config(s) implementing the subsystems above.
   - `pcb/` — KiCad schematic + best-effort board layout, BOM, connector/pin table, fab-house notes.
   - `3d-printing/` — OpenSCAD files for feeder funnel adapter, camera mount, PIR mount, BLE beacon case, weatherproof sensor enclosure.
   - `construction/` — full 50-bird coop building plan, wiring diagram, plumbing diagram (spigot → waterer), free-range run/fencing plan.
   - `docs/` (or root) — consolidated parts list & price breakdown (low-tech baseline tier vs. fully-upgraded tier), pulling current prices via web search.

3. After all agents report back: an integration/consistency pass (check firmware pin map matches PCB schematic matches wiring diagram), then gated commit(s), then a top-level README with build order.

4. Consider wrapping execution in `ecc:loop-start` / monitoring via `ecc:loop-operator` if the user wants this to survive across a long unattended stretch rather than a single session.

## Nothing has been executed yet

No git init, no PROJECT_SPEC.md, no agents launched. Safe to resume from scratch, or to change any of the flagged defaults (ESPHome, KiCad, gated-commit granularity) before work starts.
