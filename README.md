# Automated 50-Bird Chicken Coop

This is a complete, buildable design for a **10 × 20 ft coop for 50 free-ranging hens**:
the structure, run and paddocks, water and power, plus an **ESP32 + ESPHome controller**
that integrates with **Home Assistant**. Every subsystem starts **low-tech**, and the
automation is an upgrade you can add later.

> ⚠️ **Safety and code.** This project includes **120 V mains wiring outdoors** and a
> **load-bearing structure**. The plans are detailed, but they are **not** a substitute for
> a **licensed electrician** (all 120 V work, GFCI protection, inspection) or for your
> **local building department** (permit, setbacks, snow/wind loads). The controller PCB
> itself carries only 12 V DC.

![coop exterior](construction/renders/coop-exterior.png)

| Feed & water station (filled from outside) | Inside: roosts, nest openings, trough, drinkers |
|---|---|
| ![service station](construction/renders/service-station-open.png) | ![interior](construction/renders/interior-cutaway.png) |
| **Nest bay (eggs collected from outside)** | **Controller PCB** |
| ![nest bay](construction/renders/nest-bay-open.png) | ![pcb](pcb/images/board-top.png) |

The renders are illustrative OpenSCAD models (`construction/model/`). Dimensions come from
the build plan and drawings.

**Feed, water and eggs are all serviced from outside the coop.** An exterior service station
on the east wall holds a ~350 lb gravity feed bin (it feeds an indoor trough through a wall
slot) and the 30 gal water drum (piped through the wall to the nipple line). The nest bay
lid opens from outside.

## What's here

| Folder | Contents | Checked by |
|---|---|---|
| [`PROJECT_SPEC.md`](PROJECT_SPEC.md) | Architecture, sizing, tiers, power design, **GPIO map** | consistency check |
| [`hardware/pinmap.yaml`](hardware/pinmap.yaml) | Single source of truth for GPIOs and terminals | consistency check |
| [`firmware/`](firmware/) | ESPHome configs: controller + optional ESP32-CAM | `esphome config` + full compile |
| [`pcb/`](pcb/) | KiCad 10 schematic + 2-layer board, generated from `design.py`, autorouted, Gerbers ready to order | ERC 0 · DRC 0 errors · 0 unrouted · schematic parity |
| [`3d-printing/`](3d-printing/) | 8 OpenSCAD designs → 15 STLs (sensor housings, camera, brackets, PCB plate, optional auger funnel) | `render.sh` |
| [`construction/`](construction/) | Build plan + cut list, exterior feed/water station, wiring, plumbing, run and range, 5 diagrams, 6 renders | diagrams regenerate from `pinmap.yaml` |
| [`docs/`](docs/) | [Priced parts list](docs/parts-list.md), [cost-saving measures](docs/cost-savings.md), [Home Assistant setup](docs/home-assistant.md), HA automations + dashboard | `gen_parts_list.py --check`, yamllint |
| [`tools/`](tools/) | `check_consistency.py`, `gen_parts_list.py` | CI |

## Cost (2026 estimates, see [parts list](docs/parts-list.md))

| Tier | Approx. |
|---|---:|
| Tier 1: coop, run, electric-netting paddocks, exterior feed/water station, power to the coop | ~$9.6k |
| Tier 2: full automation (controller, PCB, door actuator, water fill, sensors) | ~$0.65k |
| Optional: camera, BLE sensors, battery backup, metered auger | ~$0.2k |

The cost-saving measures in [`docs/cost-savings.md`](docs/cost-savings.md) are already applied
(about −$950 net, *after* adding the exterior station). The biggest remaining levers are a
local lumber-package quote (±30 % on lumber) and how much of the ~$900 electrician estimate
you can reduce, for example by digging the trench yourself.

## Tiers at a glance

| Subsystem | Tier 1 (works with no electronics) | Tier 2 (controller) |
|---|---|---|
| Pop door | Guillotine door + rope/pulley | 12 V actuator, on-device sunrise/civil-dusk schedule, reed confirmation, HA alerts |
| Water | 30 gal drum in the exterior station, piped through the wall to nipples. Hose-fill from outside, or a mechanical float valve | Fail-closed solenoid, dual floats, timeout lockout, freeze-aware |
| Winter water | Insulated station + heated waterer on the GFCI outlet | DS18B20-controlled de-icer / heat cable via relay |
| Feed | ~350 lb gravity bin in the exterior station → wall slot → indoor trough, filled from outside | Ultrasonic bin level + low-feed alert. Optional metered auger |
| Light | Switch | Morning supplement to 14 h day length |
| Ventilation | Soffit/ridge/gable/windows (≥ 20 sq ft) | 12 V fan on temp/RH |
| Security | Hardware cloth, buried apron, 2-step latches, electric netting | PIR night-motion alerts, door-open-after-dark alert, optional camera |

## Build order

1. **Plan and permit.** Read `PROJECT_SPEC.md` and `construction/coop-build-plan.md`. Check
   local code, snow/wind loads and setbacks. Get a lumber quote from the cut list.
2. **Site, foundation, floor, walls, roof** (`coop-build-plan.md` §2 steps 1–9).
3. **Predator proofing and openings.** Hardware cloth everywhere, apron, doors, windows,
   nest bay, roosts.
4. **Run and paddocks** (`run-and-fencing.md`).
5. **Exterior feed & water station** (`coop-build-plan.md` §7): gravity feed bin + indoor
   trough, drum + drinker line through the wall, supply chain (`plumbing.md`).
   **Birds can move in now.** Keep them in the run for 1–2 weeks so they learn the coop is home.
6. **Power** (`wiring.md`). The electrician installs the feeder, mains box, lights and GFCI
   receptacle.
7. **Controller:** order the PCB (`pcb/fab/coop-controller-gerbers.zip`), print the parts
   (`3d-printing/stl/`), buy the Tier 2 parts, assemble and bring up the board
   (`pcb/README.md`), flash the firmware and adopt it in HA (`docs/home-assistant.md`).
8. **Commission one subsystem at a time:** door (adjust the reeds, watch a dusk close),
   then water fill, de-icer, feed-level sensor, lights, fan. Import the HA automations and
   dashboard.
9. **Optional:** camera, BLE thermometers, battery backup.

## Verify everything (what CI runs)

```bash
python tools/check_consistency.py      # pin map ↔ firmware ↔ PCB ↔ spec ↔ HA entity IDs ↔ schematic
python tools/gen_parts_list.py --check  # parts list totals are current
python construction/gen_diagrams.py     # diagrams regenerate
esphome config firmware/coop-controller.yaml
bash 3d-printing/render.sh
bash pcb/build.sh                       # needs KiCad 10 + Java + Freerouting: ERC/DRC/fab outputs
```

## Before building: check these by hand

These are the things software checks can't prove:

- [ ] **PCB:** open it in KiCad and review the autorouted layout. Confirm the SRD relay
      pinout on your parts, and your ESP32 board's row spacing (fit J21 for 25.4 mm or
      J22 for 22.86 mm). See `pcb/README.md`.
- [ ] **Firmware:** set your latitude/longitude/timezone and feeding times, and your BLE
      thermometer's MAC (or remove `packages/ble.yaml`).
- [ ] **3D parts:** measure your specific sensors and PVC and adjust the parameters in the `.scad` headers.
- [ ] **Structure:** check rafter size against your local snow load, and pull a permit if needed.
- [ ] **Electrical:** a licensed electrician does all 120 V work, with GFCI on everything.

## Design decisions

- **ESPHome** rather than Arduino/ESP-IDF: it's local-first, integrates natively with
  HA, and each entity is a few lines of YAML, which keeps the upgrade path cheap.
- **KiCad** rather than Eagle: it's free, it's scriptable (the board is generated and
  verified from `pcb/design.py`), and it outputs standard Gerbers for any fab.
- **Mains stays off the PCB.** The relay modules (or SSRs) and PSU sit in a separate
  electrician-installed box. The PCB only drives their 12 V coils/inputs.
- **Service from outside.** Feed, water and egg collection never require entering the coop,
  which cuts labour, spills and biosecurity risk.
