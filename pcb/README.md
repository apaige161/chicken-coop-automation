# Coop Controller PCB (KiCad)

This is a 2-layer, all through-hole carrier board for an **ESP32-DevKitC-32E**. It has 12 V
input protection, a 5 V regulator, a 2-relay H-bridge for the pop-door actuator, five
low-side MOSFET outputs, conditioned sensor inputs, and screw terminals for all field
wiring. **It carries 12 V DC only.** The 120 V SSRs and PSU live in a separate mains
enclosure (see `construction/wiring.md`).

![top](images/board-top.png)

| | |
|---|---|
| Size | 170 × 105 mm, 4× M3 holes 4 mm from each corner |
| Layers | 2 (1 oz), GND pour both sides, solid pad connections |
| Tracks | Signal 0.25 mm / 0.2 mm clearance. Power nets (`+12V`, `GND`, `M±`, `VALVE-`, `FEEDER-`, `FAN-`, `VIN_*`) 1.5 mm |
| Parts | 75 THT parts, 38 BOM lines (`fab/bom.csv`) |
| Checks | ERC 0 violations. DRC 0 errors, 0 unconnected, 0 schematic-parity issues |

## Files

| File | What it is |
|---|---|
| `design.py` | **The source.** Every part, footprint, pin→net and board position |
| `gen_schematic.py` | Writes `coop-controller.kicad_sch` from `design.py` (labels on every pin) |
| `gen_pcb.py` | Writes `coop-controller.kicad_pcb` + `.kicad_pro` (placement, net classes, outline, keep-out, pours) |
| `route.py` | Autoroutes with Freerouting (retries until 100% routed) and fills the pours |
| `gen_bom.py` | Grouped BOM → `fab/bom.csv` |
| `build.sh` | Runs everything above, plus ERC/DRC and fab exports |
| `fab/coop-controller-gerbers.zip` | **Upload this to the fab** (Gerbers + Excellon drill) |
| `fab/coop-controller-schematic.pdf` | Printable schematic |

The schematic is generated, so it's a netlist-style sheet grouped by function, with net
labels instead of drawn wires. That's deliberate: `tools/check_consistency.py` can prove it
matches `design.py` and the firmware pin map. To change the circuit, edit `design.py` and
run `bash build.sh`. Don't hand-edit the generated files, or the next build will overwrite
your changes.

## Before you order: manual checks

The layout is autorouted and passes DRC, but nobody has looked at it in the KiCad GUI yet.
Open `coop-controller.kicad_pcb` in KiCad and check:

1. **Relay pinout.** `design.py` assumes SRD pins 1 = COM, 2/5 = coil, 3 = NO, 4 = NC
   (KiCad's `SANYOU_SRD_Form_C` symbol). Confirm this on your actual relays with a
   meter before soldering.
2. **ESP32 fit.** Measure your dev board. Official Espressif DevKitC rows are 25.4 mm apart
   (fit **J21**). Many clones are 22.86 mm (fit **J22** instead). Fit only one of the two.
   Make sure the USB connector sits at the bottom (J20/J21 pin 19 end) and the antenna
   overhangs the "NO COPPER" keep-out.
3. **Terminal-block orientation.** Wire entries should face the board edges.
4. **Track routing.** Look over the Freerouting result: power-track widths, sensible
   paths, no long GND detours.
5. Run **Inspect → Design Rules Checker** once in the GUI.

## Ordering (JLCPCB / PCBWay / OSH Park)

1. Upload `fab/coop-controller-gerbers.zip`.
2. Settings: 2 layers, 1.6 mm FR-4, 1 oz copper, HASL (lead-free) or ENIG, any mask colour.
   Minimum track/space on this board is 0.25/0.2 mm, which every hobby fab handles.
3. Expect roughly **$15–30 for 5 boards** plus shipping, since it's over 100×100 mm.
4. The parts are all through-hole and commonly stocked, so hand-solder them from
   `fab/bom.csv` (Digi-Key/Mouser/LCSC). Prices are in `docs/parts-list.md`.

## Assembly order

Solder low to high: resistors, diodes, small caps, TO-92 transistors, then the pin
header/sockets (use a spare dev board to hold the sockets straight), TO-220 MOSFETs,
electrolytics, fuse holder, regulator, relays and terminal blocks last.

**Bring-up before plugging in the ESP32:**
1. Apply 12 V from a current-limited bench supply (limit to about 200 mA). Check that
   D9 lights, 5 V is on J10 pin 1, and nothing gets warm.
2. Check reverse polarity: swap the leads briefly. Nothing should happen, because D1
   blocks it.
3. Fit the ESP32, flash `firmware/coop-controller.yaml` over USB, then test each output
   from the ESPHome web UI with nothing connected. Listen for the relay clicks and check
   that the MOSFET drains pull low.

## Circuit notes

- **Door H-bridge:** K1/K2 SPDT. NC→GND, NO→+12 V, COM→motor lead. Both relays off (or
  both on) shorts the motor to itself, which brakes it. Shoot-through is impossible by
  construction. See the truth table in `PROJECT_SPEC.md`.
- **Low-side outputs:** IRLZ44N (or IRLB8721) logic-level FETs with 100 Ω gate and 100 kΩ
  pull-down resistors, so outputs stay OFF while the ESP32 boots. 1N5822 flyback diodes
  protect against the valve/motor/fan inductance. 2N7000 FETs drive the relay coils (1N4148
  flyback) and the SSR inputs (about 10 mA).
- **Inputs:** 10 kΩ pull-ups to 3.3 V plus a 100 nF cap on every long-wire input. The PIR
  has a 10 kΩ pull-down. The JSN-SR04T 5 V echo goes through a 1 k/2 k divider.
- **VIN sense:** 100 k/22 k divider into GPIO36. The firmware multiplies by 5.545.
- **Protection:** 5 A slow-blow fuse, SB560 series Schottky (reverse polarity), and a
  P6KE15CA TVS across +12 V.
