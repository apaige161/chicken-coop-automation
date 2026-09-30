# Project Spec: Automated 50-Bird Chicken Coop

This is the shared architecture document. Firmware, PCB, wiring diagrams, 3D parts and
construction plans all follow it. If you change it, change it here first, then update
`hardware/pinmap.yaml` and run `python tools/check_consistency.py`.

> **SAFETY — READ FIRST.** This project includes 120 V AC mains wiring outdoors and a
> load-bearing structure for 50 birds plus snow and wind loads. These plans are thorough,
> but they do **not** replace a licensed electrician or a local building/code review.
> All outdoor 120 V circuits must be **GFCI protected** and installed to local code
> (NEC in the US). Have the electrical work inspected and the structure checked against
> your local snow/wind loads before you build.

## 1. Design philosophy

Every subsystem has a **Tier 1 (low-tech)** baseline that works with no electronics at all,
and a **Tier 2 (automated)** upgrade that the controller adds on top. The flock stays safe
if the controller, WiFi or Home Assistant fails:

- The pop door runs from **local sunrise/sunset logic on the ESP32**. It does not need Home
  Assistant or internet, and a physical button on the enclosure works without WiFi.
- A mechanical float valve or a manual fill still waters the birds if the solenoid fails.
- Feed and water are gravity-fed from an **exterior service station**, so a failed controller
  never stops the birds eating or drinking.

## 2. Site assumptions

| Item | Value |
|---|---|
| Flock | 50 standard-size laying hens, free-ranging most of the day |
| Shade | Partial. Put the long glazed wall facing south (north hemisphere) for winter sun, with deciduous shade in summer if you can |
| Power | 120 V outlet nearby. Run a dedicated GFCI-protected 20 A circuit to the coop |
| Water | Hose spigot nearby. Use a vacuum breaker, 25 psi regulator and a drinking-water-safe hose |

## 3. Coop sizing (50 birds)

| Parameter | Rule of thumb | Design value |
|---|---|---|
| Indoor floor area | 4 sq ft/bird | **10 ft × 20 ft = 200 sq ft** |
| Nest boxes | 1 per 4–5 hens | **12 boxes** in one row (12"W × 12"H × 14"D), exterior bay on the north wall, floor 20" up, so all boxes sit below the 36–40" roosts |
| Roost length | 8–10 in/bird | **5 bars × 9 ft = 45 ft** (10.8 in/bird), spanning the 9'-5" interior width |
| Ventilation | ~1 sq ft per 10 sq ft floor | **≥20 sq ft** of screened soffit, gable and window openings |
| Pop door | 1 per ~50 birds | **12" W × 16" H**, vertical guillotine, 12 V 18"-stroke actuator |
| Secure run (bad-weather days) | ~10 sq ft/bird | **20 ft × 25 ft = 500 sq ft**, roofed or netted |
| Feed | ~0.25 lb/bird/day | **~12.5 lb/day** (~90 lb/week) |
| Water | ~0.12–0.25 gal/bird/day | **6–12 gal/day**. A 30 gal reservoir lasts 2.5–5 days |
| Feed + water access | Fill without entering the coop | **Exterior service station** on the east wall (5 ft × 30 in × 6 ft): ~350 lb gravity feed bin + 30 gal drum, both filled from outside |

## 4. System architecture

```
                      +-------------------- Home Assistant ---------------------+
                      |  dashboards, overrides, notifications, history          |
                      +--------------------------+------------------------------+
                                                 | ESPHome native API (WiFi, encrypted)
          BLE (passive)                          |
 [BLE thermometer(s)] ~~~~~~~~~~~~~~>  +---------+-----------+      optional     +-------------+
 (nest box / brooder)                  |  Coop Controller    |  <--- WiFi ---->  | ESP32-CAM   |
                                       |  ESP32-DevKitC-32E  |                   | (camera)    |
                                       |  on Coop Ctrl PCB   |                   +-------------+
                                       +--+--+--+--+--+--+--+
     12 V DC loads:  door actuator (2-relay H-bridge), water solenoid, 12 V fan, (optional feed auger)
     Low-voltage in: door reeds, water floats, DS18B20, BME280, BH1750, PIR, ultrasonic, button
     Relay/SSR out:  relay 1 -> 120 V coop lights, relay 2 -> 120 V de-icer (mains stays OFF the PCB)
```

- **Firmware:** ESPHome (YAML). It is local-first and integrates natively with Home Assistant.
  The coop logic (door schedule, water fill, freeze protection, lighting, feeding) runs on
  the device. Home Assistant supervises and can override.
- **BLE:** The controller runs `esp32_ble_tracker` passively to read BLE thermometers such
  as the Xiaomi LYWSD03MMC with pvvx firmware in the nest boxes or brooder. It also works
  as a Home Assistant **Bluetooth proxy**, so more BLE sensors can be added later without
  new hardware.
- **Camera (optional):** A separate ESP32-CAM node running ESPHome, or any RTSP/ONVIF
  camera added to Home Assistant directly.

## 5. Power architecture

```
House panel --[20 A GFCI breaker]-- UF-B 12/2 (buried per code) --> Coop weatherproof mains box
   Mains box (NEMA 4X / IP65), DIN rail:
     - 2-pole disconnect / 20 A breaker
     - GFCI receptacle (if not GFCI at panel)
     - Mean Well HDR-100-12N (12 V 7.5 A DIN PSU) ---> 12 V to controller box
     - Relay 1: DIN relay module, 12 VDC coil, 6 A (or SSR) -> coop LED lights
     - Relay 2: same                                       -> water de-icer / heat cable (<= 500 W)
   Optional: 12 V 7 Ah SLA battery + float charger for door backup during power cuts
```

- The **controller PCB carries 12 V DC and below only.** It switches the relay coils (or SSR
  inputs) on the low side. The relays, PSU and all 120 V conductors live in a separate
  mains enclosure. Use relay modules with a built-in suppression diode.
- 12 V input: 5 A fuse → reverse-polarity Schottky → TVS → loads. 5 V comes from an
  onboard switching regulator (7805-footprint module). The ESP32 dev board takes 5 V on
  its `5V` pin and makes 3.3 V itself.

## 6. Controller GPIO map (single source of truth: `hardware/pinmap.yaml`)

Board: **ESP32-DevKitC-32E** (38-pin, ESP32-WROOM-32E). Strapping pins (0, 2, 5, 12, 15)
are avoided or used only in boot-safe ways. GPIO 34/35/36/39 are input-only and have no
internal pull-ups, so the PCB provides external 10 kΩ pull-ups.

| GPIO | Signal | Dir | Connector | Notes |
|---|---|---|---|---|
| 21 | I2C_SDA | I/O | J9 | BME280 (0x76), BH1750 (0x23). 4.7 kΩ pull-ups on PCB |
| 22 | I2C_SCL | O | J9 | |
| 4 | ONEWIRE | I/O | J8 | DS18B20 in the water reservoir. 4.7 kΩ pull-up |
| 25 | DOOR_OPEN_RLY | O | J2 (via K1) | Relay K1: actuator M+ to +12 V (extend = open) |
| 26 | DOOR_CLOSE_RLY | O | J2 (via K2) | Relay K2: actuator M− to +12 V (retract = close) |
| 32 | DOOR_CLOSED_SW | I | J3 | Reed switch to GND, pulled up |
| 33 | DOOR_OPEN_SW | I | J3 | Reed switch to GND, pulled up |
| 27 | VALVE_DRV | O | J4 | Low-side MOSFET, 12 V NC solenoid valve |
| 13 | FEEDER_DRV | O | J5 | Low-side MOSFET, optional 12 V metered-auger motor |
| 14 | FAN_DRV | O | J14 | Low-side MOSFET, 12 V exhaust fan (may blip at boot; harmless) |
| 16 | LIGHT_SSR | O | J6 | Low-side MOSFET → relay 1 coil / SSR1 input (120 V lights) |
| 17 | HEAT_SSR | O | J6 | Low-side MOSFET → relay 2 coil / SSR2 input (120 V de-icer) |
| 34 | WATER_LOW | I | J7 | Float switch to GND, ext. 10 kΩ pull-up, RC filter |
| 35 | WATER_HIGH | I | J7 | Float switch to GND, ext. 10 kΩ pull-up, RC filter |
| 39 | PIR | I | J10 | HC-SR501 output (3.3 V logic), 10 kΩ pull-down |
| 18 | US_TRIG | O | J11 | JSN-SR04T feed-bin level ultrasonic trigger |
| 19 | US_ECHO | I | J11 | 5 V echo through a 1 kΩ/2 kΩ divider |
| 23 | DOOR_BTN | I | J12 | Panel push button to GND (manual door toggle) |
| 2 | STATUS_LED | O | J12 | Onboard LED + panel LED (330 Ω) |
| 36 | VIN_SENSE | ADC | — | 12 V rail through 100 kΩ/22 kΩ divider (battery/PSU health) |
| 5 | SPARE_IO5 | I/O | J13 | Expansion header. Strapping pin: do not pull low at boot |

**Door H-bridge truth table** (K1/K2 are SPDT; NC→GND, NO→+12 V, COM→motor lead):

| K1 | K2 | M+ | M− | Result |
|---|---|---|---|---|
| off | off | GND | GND | Stopped (dynamic brake) |
| on | off | +12 V | GND | Extend → **door opens** |
| off | on | GND | +12 V | Retract → **door closes** |
| on | on | +12 V | +12 V | Stopped (no shoot-through possible) |

The firmware still interlocks K1/K2. The actuator's built-in limit switches are the
primary end stop. The reed switches and a 30 s runtime timeout are secondary.

## 7. Subsystems

| Subsystem | Tier 1 (low-tech) | Tier 2 (automated) |
|---|---|---|
| Pop door | Manual guillotine door + rope/pulley and latch | 12 V linear actuator, sunrise/sunset + lux logic on-device, reed confirmation, HA alert if not closed 30 min after sunset |
| Feeder | ~350 lb gravity bin in the exterior station, feeding an indoor trough through a wall slot, filled from outside | Ultrasonic feed-level sensor + low-feed alert. Optional metered auger on J5 for rationing |
| Water | 30 gal drum in the exterior station, piped through the wall to nipples/cups, hose-filled from outside | 12 V NC solenoid from spigot, low/high float fill control with max-runtime and leak lockout |
| Freeze protection | Insulated station + heated bucket by hand | DS18B20 water temp → relay 2 de-icer/heat cable, HA freeze alerts |
| Lighting | Manual switch | Relay 1 adds morning light to keep 14 h of daylight in winter |
| Ventilation | Screened soffit/gable/window openings | 12 V exhaust fan on temperature/humidity thresholds |
| Environment | Min/max thermometer | BME280 (T/RH/P), BH1750 lux, BLE thermometers, HA history |
| Security | Hardware cloth, buried apron, latches | Door reeds, PIR night alerts, optional camera, electric poultry netting for range area |

## 8. Repository layout

| Path | Contents |
|---|---|
| `hardware/pinmap.yaml` | GPIO/connector source of truth |
| `firmware/` | ESPHome configs: `coop-controller.yaml`, `coop-camera.yaml`, packages |
| `pcb/` | KiCad project (generated by `pcb/generate.py`), BOM, fab notes, Gerbers |
| `3d-printing/` | OpenSCAD sources + print/service notes |
| `construction/` | Coop build plan, cut list, wiring and plumbing diagrams, run/fencing plan |
| `docs/` | Parts list and price breakdown, Home Assistant setup, build order |
| `tools/` | Consistency checks, BOM tooling |

## 9. Verification gates

Each step is committed only after its checks pass:

1. `esphome config` passes for every firmware YAML.
2. `python tools/check_consistency.py` passes: the pin map matches the firmware, PCB netlist and docs.
3. KiCad ERC/DRC via `kicad-cli` runs clean, with only documented waivers.
4. OpenSCAD renders every part to STL without errors.
5. The BOM totals regenerate from CSV without diffs.
