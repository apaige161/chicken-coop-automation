# Cost-Saving Measures

The rule for this list: **cheaper without adding real complexity or weakening the flock's
safety.** Section 1 is already applied to `docs/parts.csv`, so the totals in
[`parts-list.md`](parts-list.md) include it. Section 2 lists optional savings that depend
on your situation. Section 3 covers cuts that look tempting but aren't worth it.

**Net effect of section 1:** the recommended build (Tier 1 + Tier 2) went from about
**$11,190 to $10,240 (−$950)**. That's after also *adding* the ~$350 exterior feed/water
service station, which makes feed and water accessible from outside the coop.

## 1. Applied (in the parts list)

| # | Change | Saves | Why it doesn't add complexity |
|---|---|---:|---|
| 1 | **One electric-netting roll, moved between paddocks** instead of three standing rolls | ~$430 | Moving a 164 ft roll takes about 15 min every 2–4 weeks. Buy more rolls later if you want |
| 2 | **Shade sail over half the run** instead of a steel-roofed section | ~$410 | The coop is the rain shelter; the run only needs summer shade. The sail comes down for winter along with the netting |
| 3 | **Porch & floor enamel** on the PT plywood instead of sheet vinyl | ~$125 | Roll on two coats once the plywood has dried out. Just as easy to scrape under deep litter |
| 4 | **Gravel strips under the skids** instead of a full 12 × 22 ft gravel pad | ~$110 | Less digging too. The hardware-cloth skirt and apron do the rodent-proofing |
| 5 | **DIN relay modules** (12 V coil, built-in diode) instead of genuine SSRs for lights and de-icer | ~$75 | The same J6 outputs drive them, and they can't be counterfeit-shorted. SSRs stay a documented alternative |
| 6 | **Gravity feed bin + indoor trough** instead of hanging feeders + a motorized auger/hopper | ~$65 | *Fewer* parts: no motor, auger, coupler or hopper can. Feed flows as the hens eat. The auger is now an optional add-on for rationing |
| 7 | **Storm shutters from the window cut-outs** instead of polycarbonate winter panels | ~$65 | The T1-11 from the window openings becomes the shutters. Only hinges and hooks to buy |
| 8 | **Used food-grade drum** (car washes, bakeries, farm stores) instead of new | ~$25 | Rinse it well. Only buy drums that held food-grade contents |
| | *Added:* exterior feed & water service station | −$350 | The requested outside access: framing, siding, a small roof, foam, hinges and latches |

## 2. Optional: depends on your situation

| Idea | Typical saving | Notes |
|---|---:|---|
| **Get a lumber-package quote from a local yard** from the cut list in `construction/coop-build-plan.md` | 10–15 % of ~$4.5k lumber ≈ $450–650 | Local yards often beat big-box prices on full packages and deliver for free |
| **Dig the feeder-cable trench yourself.** The electrician only does terminations, the mains box and the inspection | $200–400 of the $900 labour estimate | Ask your electrician first; many are happy to do this. Call 811 before digging |
| **Reclaimed metal roofing or siding** | $300–900 | Check it for rust-through and sharp edges. Only fine if it's sound |
| **Skip the exhaust fan** (J14) in mild climates | ~$32 | The soffit + ridge + window ventilation (≥ 20 sq ft) is enough on its own in most climates |
| **ESP32 clone board** instead of the official DevKitC | ~$5 | The PCB has the J22 socket row for 22.86 mm clones |
| **Stage Tier 2.** Build Tier 1 now and add the controller in a later season | Spreads ~$650 | Every Tier 1 part stays in use when Tier 2 is added |
| **Skip the camera and BLE sensors** | ~$90 | Purely optional |

## 3. Not recommended (false economies)

- **Chicken wire instead of ½" hardware cloth.** Raccoons tear it and weasels pass through.
  One predator night costs more than the whole mesh budget.
- **Skipping the GFCI or the electrician** on the 120 V side. That's a safety and code issue.
- **Lighter rafters, or no rafter ties.** Structural. Check against your snow load.
- **Cheap no-name SSRs** (counterfeit "Fotek"). They fail shorted. Use genuine SSRs or the
  relay modules.
- **Garden hose for drinking water.** It leaches lead/BPA. The drinking-water hose is about $65.
- **PLA for outdoor printed parts.** It warps in a hot coop within a season. PETG costs about the same.
