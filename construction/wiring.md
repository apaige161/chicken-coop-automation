# Electrical Wiring

> **120 V AC SAFETY: READ FIRST.** Wet, dusty, ammonia-laden outdoor buildings are the
> harshest place you can put mains wiring. **Have a licensed electrician install and
> inspect everything on the 120 V side** (feeder, breaker, GFCI, mains enclosure, relay load
> wiring, lights, receptacles) to your local code (NEC Articles 210, 225, 300, 547 in
> the US). Every 120 V circuit to the coop **must be GFCI protected**. This document
> describes the intended design so you and your electrician share one plan. It is **not**
> a substitute for them.

![wiring](diagrams/wiring-diagram.svg)

## 1. Architecture

There are two separate enclosures, and they are never combined:

| Enclosure | Contents | Voltage |
|---|---|---|
| **Mains box.** NEMA 4X / IP65 polycarbonate or fibreglass, DIN rail, about 300 × 250 × 150 mm | 2-pole 20 A DIN breaker, GFCI receptacle (unless GFCI at the panel), Mean Well **HDR-100-12N** 12 V PSU, **relay 1** (lights), **relay 2** (de-icer / heat cable), ground bar | 120 V AC in, 12 V DC out |
| **Controller box.** IP65 ABS, about 250 × 200 × 100 mm | Coop Controller PCB on the printed back-plate, cable glands on the bottom face only, door push-button + status LED on the lid | 12 V DC and below |

Mount both boxes on the east wall inside the coop, at the north end, 5 ft up, out of peck
and splash range. That puts them directly behind the exterior feed & water station, so
the float, probe, valve and feed-level cables are only a few feet long. They pass through
the wall in a sealed gland.
Run all cables in PVC conduit or sealed flexible conduit (rodents chew cable).

## 2. Feeder to the coop (electrician)

- Use a **dedicated 20 A circuit** from the house panel with a **GFCI breaker** (or a
  20 A breaker plus a GFCI device as the first thing in the coop).
- The cable is **UF-B 12/2 with ground**, direct burial, or THWN in PVC conduit. Burial
  depth for a residential 120 V, ≤ 20 A, GFCI-protected branch circuit is **12"**
  (NEC 300.5, Table, column 4). Deeper is fine. Use conduit wherever it's exposed above
  grade.
- Voltage drop: 12 AWG is fine up to about 100 ft at the ~6 A this coop actually draws.
  Go to 10 AWG beyond that.
- Enter the mains box from the bottom through a listed fitting. Put a disconnect inside
  the coop (the DIN breaker) so you can isolate the coop locally.

## 3. Mains box wiring (electrician)

| From | To | Conductor |
|---|---|---|
| Feeder L / N / G | 2-pole DIN breaker L / N, ground bar | 12 AWG |
| Breaker L / N | GFCI receptacle line side | 12 AWG |
| Breaker L / N | PSU L / N, PSU ⏚ to ground bar | 14 AWG |
| Breaker **L** | Relay 1 COM → relay 1 NO → **light fixture hot** | 14 AWG |
| Breaker **L** | Relay 2 COM → relay 2 NO → **de-icer receptacle hot** (single weatherproof outlet in the station) | 14 AWG |
| Breaker N | lights neutral, de-icer receptacle neutral | 14 / 12 AWG |
| Ground bar | every fixture, receptacle, metal box, PSU ⏚ | green / bare |

- **The relays only switch the HOT conductor.** Neutral and ground are never switched.
- **Default: DIN-rail relay modules** with a 12 V DC coil, 6 A / 250 V AC contacts, a status
  LED and a **built-in coil suppression diode** (e.g. Finder 38.51.7.012.0050 or equivalent,
  about $16 each). They cost about a third as much as genuine SSRs, dissipate no heat, and
  can't be counterfeit-shorted like cheap "Fotek" SSRs. Two 9 W LED bulbs and a 250 W
  de-icer + 36 W heat cable (≈ 2.4 A) are well inside the rating. **Keep the relay-2 load
  ≤ 500 W.** If your module has no built-in diode, fit a 1N4007 across A1/A2 (cathode
  to A1) to protect the PCB's 2N7000 driver.
- Alternative: zero-cross SSRs (input 3–32 V DC, ≥ 10 A / ≥ 25 A output). Use genuine
  Crydom/Omron/Carlo Gavazzi parts only. The PCB drives either type unchanged.
- Relay 2 failing welded or open is fail-safe either way, because the de-icer has its own
  thermostat.
- The de-icer itself must be thermostatically controlled. The controller is an extra
  layer, not the only protection against overheating.

## 4. 12 V DC from the PSU to the controller

| From | To | Cable |
|---|---|---|
| PSU +V | Controller **J1 VIN_RAW** | 16/2 outdoor, in conduit between boxes |
| PSU −V | Controller **J1 GND** | 〃 |

The PCB has its own 5 A fuse, reverse-polarity diode and TVS. Set the PSU trim pot to
12.5 V if you add the backup battery (optional, see below).

### Optional battery backup (Tier 2+)

A 12 V 7 Ah SLA battery on a float charger, diode-ORed (Schottky, 10 A) with the PSU
output, keeps the door, sensors and WiFi running through an outage: about 0.25 A average,
so over 24 h. The firmware reports `12V Supply Voltage` and raises `12V Supply Low` below
11.5 V.

## 5. Controller terminals: field wiring

This comes from `hardware/pinmap.yaml`, so it always matches the PCB and firmware.

| Terminal | Pins | Connects to | Cable / notes |
|---|---|---|---|
| **J1 PWR_IN** | VIN_RAW, GND | PSU +V / −V | 16/2 |
| **J2 ACTUATOR** | M+, M− | Linear actuator red (M+), black (M−) | 16/2 outdoor. If the door moves the wrong way, swap the two leads |
| **J3 DOOR_SW** | DOOR_CLOSED_SW, DOOR_OPEN_SW, GND | Reed switch at the closed position, reed switch at the open position, common | 18/5 sprinkler wire (direct-burial rated, cheap, colour-coded) |
| **J4 VALVE** | +12V, VALVE− | Solenoid valve coil (either way round) | 18/2 |
| **J5 FEEDER** | +12V, FEEDER− | **Optional** metered-auger gear motor | Unused with the default gravity feed bin. 16/2 if fitted |
| **J6 SSR_OUT** | +12V, LIGHT_SSR−, +12V, HEAT_SSR− | Relay 1 **A1** / **A2**, relay 2 **A1** / **A2** (or SSR + / −) | 18/4. The only cable between the two boxes besides J1 |
| **J7 WATER_LVL** | WATER_LOW, WATER_HIGH, GND | Low float, high float, common | 18/5 sprinkler wire. Mount the floats so the contact **closes when the water is below the float** |
| **J8 ONEWIRE** | +3V3, ONEWIRE, GND | DS18B20 probe red, yellow, black | The probe's own lead, extended with Cat5e if needed (≤ 10 m) |
| **J9 I2C** | +3V3, I2C_SDA, I2C_SCL, GND | BME280 and BH1750 boards (in parallel) | Cat5e: SDA+GND on one pair, SCL+3V3 on another. **Keep under 2 m** |
| **J10 PIR** | +5V, PIR, GND | HC-SR501 VCC, OUT, GND | 18/3 or Cat5e. Set the PIR jumper to "H" (retrigger) |
| **J11 ULTRASONIC** | +5V, US_TRIG, US_ECHO_5V, GND | JSN-SR04T 5V, Trig, Echo, GND | Cat5e, ≤ 3 m |
| **J12 PANEL** | DOOR_BTN, GND, LED_PANEL, GND | Lid push-button (NO), status LED (anode on LED_PANEL; 330 Ω is on the PCB) | Short leads inside the box |
| **J13 EXPANSION** | +3V3, GND, +5V, SDA, SCL, IO5 | Future sensors (ammonia, second BME280…) | 2.54 mm header |
| **J14 FAN** | +12V, FAN− | 12 V exhaust fan / bilge blower | 18/2 |

### Load current budget (12 V)

| Load | Typical | When |
|---|---|---|
| Controller + ESP32 + sensors | 0.25 A | always |
| Door actuator | 2–3 A (stall ≤ 5 A, stopped by internal limits) | about 25 s, twice a day |
| Optional feeder auger | 1–2 A | 20 s, twice a day if fitted. **The firmware won't run it while the door is moving** |
| Solenoid valve | 0.5 A | while filling |
| Exhaust fan | 0.3–1 A | hot/humid periods |
| Relay coils | 2 × ~20 mA (SSR inputs ≈ 10 mA) | |

The worst realistic simultaneous load is about 4.5 A, within the 7.5 A PSU and the
PCB's 5 A slow-blow fuse.

## 6. Installation practice

- Seal every cable entry: glands on the bottom faces, with a **drip loop** below each.
- Keep 12 V and 120 V in separate conduits, or at least 12" apart where they run in parallel.
- Use ferrules on stranded wire in the screw terminals. Label both ends of every cable
  with its terminal (e.g. "J7-1 WATER_LOW").
- Fix sensor cables along the rafters or ties, never where birds can perch on them or
  peck them.
- **Commissioning:** with the PCB powered but the field devices disconnected, toggle each
  output from the ESPHome web UI and confirm it at the terminal with a meter. Then
  connect the devices one at a time.
- Test the GFCI monthly with its TEST button.
