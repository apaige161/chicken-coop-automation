# Water: Spigot to Drinkers

![plumbing](diagrams/plumbing-diagram.svg)

Demand: 50 hens drink about **6 gal/day** in mild weather and up to **12 gal/day** in
heat. A **30 gal** food-grade drum holds 2.5–5 days, which is enough buffer that the
automation is a convenience rather than a single point of failure.

The drum and all pressurised plumbing live in the **exterior feed & water service station**
on the east wall (`coop-build-plan.md` §7). You can fill and service it from outside, and
the only water that enters the coop is the unpressurised gravity line to the drinkers.

![service station](renders/service-station-open.png)

## Supply chain (from the house spigot)

| # | Part | Why |
|---|---|---|
| 1 | Existing hose spigot (frost-free if you have one) | Source |
| 2 | **Hose-bib vacuum breaker** (ASSE 1011) | Required backflow protection: stops coop water siphoning back into the house supply |
| 3 | Brass Y-valve with shut-offs | Keeps one port for your garden hose |
| 4 | **Pressure regulator, 25 psi**, ¾" GHT | Protects the solenoid, float and fittings. Low pressure is also gentler if a float sticks |
| 5 | Inline screen filter (40–100 mesh) | Sediment clogs nipples and pilot valves |
| 6 | **Drinking-water-safe hose** (lead-free, NSF-61) | Garden hose leaches lead/BPA. Bury it 12" in a trench, or run it in foam pipe insulation, up to the station |
| 7 | **12 V normally-closed solenoid valve**, ½" brass, pilot-operated (min. about 3 psi), mounted inside the station | Tier 2. Fails **closed** on power or controller failure |
| 8 | Drum inlet: ½" bulkhead fitting in the lid or high on the side | |
| 9 | Overflow: ¾" bulkhead 2" below the rim, PVC through the station floor, draining **away from the station** | If a float or valve ever sticks, the water goes onto the ground outside, never into the litter |
| 10 | Outlet: ¾" bulkhead near the bottom, then a ball valve, then ¾" PVC **through the coop wall at 14"** to the drinker line | The only pipe that enters the coop, and it's unpressurised |

## Drinkers (inside the coop)

- The ¾" PVC line enters through the east wall and runs west, then turns to run through
  the middle of the floor (see the floor plan). It carries **10+ horizontal nipples**
  (1 per 5–6 birds) or **cup drinkers** (1 cup per 8–10 birds) at the birds' head height,
  about 12–14" for standard layers. Horizontal nipples drip less than vertical ones and
  suit a gravity drum.
- The drum sits on an **18" block stand** in the station. Its bottom is then about 30"
  above grade, and the nipple line is about 26" above grade (floor ≈ 12" + 14"), so there's
  enough head (≈ 0.3–1 psi) to feed the line. Keep the line level, or falling slightly
  away from the drum.
- Screen the drum's lid vent (mosquitoes) and keep the drum opaque or painted (algae).

## Level sensing (Tier 2)

| Sensor | Position | Terminal |
|---|---|---|
| LOW float | ~⅓ full | J7 WATER_LOW |
| HIGH float | ~2" below the overflow | J7 WATER_HIGH |
| DS18B20 probe | Hanging at mid-depth, away from the de-icer | J8 ONEWIRE |

Use vertical side-mount or top-mount reed float switches (PP body, food-safe). Install
them so the **contact closes when the water is BELOW the float**. With that convention a
broken wire reads "not below", so the firmware never opens the valve on a dead sensor.
The sensor cables run through a sealed gland in the station wall straight to the
controller, which sits on the other side of the same wall, inside the coop.

### Firmware behaviour (`firmware/packages/water.yaml`)

- Water drops below LOW: the valve opens (if `Water Auto Fill` is on and there's no lockout).
- The valve closes when the level reaches HIGH.
- If HIGH isn't reached within `Water Max Fill Time` (default 10 min), the valve closes and
  **Water Fill Lockout** latches, and HA notifies you. Likely causes are a leak, supply
  turned off, a frozen hose or a stuck float. Fix the cause, then press
  `Water Fill Lockout Reset`.
- A separate watchdog closes the valve after max-fill + 1 minute, even if you opened it by hand.
- **No filling when the water is at or below 1 °C.** The hose is probably frozen.
- `Water Float Fault` fires if LOW says "below" while HIGH says "above", which is
  physically impossible.

## Winter / freeze protection

The drum is outdoors in a cabinet, so plan for this:

1. **Station insulation:** line the drum side and the roof of the station with 1" rigid
   foam, and keep the doors closed (weather-stripped). The drum's thermal mass plus the
   de-icer does the rest.
2. **Drum:** put a **plastic-safe, thermostatic** floating or submersible de-icer (250 W)
   on **relay 2** (J6 HEAT). The firmware turns it on below 3 °C water temperature and off
   above 6 °C. If the probe fails, it falls back to coop air below 2 °C.
3. **Pipe and drinker line:** wrap self-regulating heat cable (≈ 3 W/ft) on the short
   exposed pipe between the drum and the wall and along the indoor nipple line, under foam
   insulation. Plug it into the same relay-2 outlet with a rated splitter (total well under
   the 6 A relay and receptacle ratings).
4. **Supply hose:** the easiest approach is to disconnect and drain it when nights go below
   freezing, and fill the drum by hand through the lid every 3–4 days. It's right there
   behind the station doors. The alternative is a heated drinking-water hose on a separate
   GFCI outlet.
5. **Low-tech fallback:** two heated 3 gal poultry waterers on the GFCI receptacle inside
   the coop.

## Tier 1 (no electronics)

Skip items 7–8 and the floats. Either fill the drum by hose through the lid every 3–4 days
(open the station, fill, close; no need to enter the coop), or fit a **mechanical
stock-tank float valve** fed through the same vacuum breaker, regulator and filter. That
gives you automatic filling with no electricity at all. Tier 2 then adds the solenoid in
front of it as a **leak-protection master valve** controlled by the floats.
