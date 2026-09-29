"""Render docs/parts.csv into docs/parts-list.md with per-category and per-tier totals.

    python tools/gen_parts_list.py           # write docs/parts-list.md
    python tools/gen_parts_list.py --check   # exit 1 if the committed file is stale
"""
import csv
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'docs', 'parts.csv')
OUT = os.path.join(ROOT, 'docs', 'parts-list.md')

TIERS = OrderedDict([
    ('base', 'Tier 1: coop, run, low-tech equipment and power to the coop'),
    ('auto', 'Tier 2: automation (controller, door, water, feed, sensors)'),
    ('opt', 'Optional add-ons (camera, BLE sensors, battery backup)'),
])


def money(v):
    return f'${v:,.0f}'


def render(rows):
    out = ['# Parts List and Price Breakdown', '',
           '> Generated from `docs/parts.csv` by `tools/gen_parts_list.py`. Edit the CSV, not this file.',
           '> Prices are **2026 USD estimates** (big-box lumber yard / Digi-Key / Amazon-class retail) and',
           '> vary by region, and lumber by ±30 %. Get a local lumber quote from the cut list in',
           '> `construction/coop-build-plan.md`. Tools, tax and delivery are not included.', '']
    totals = OrderedDict((t, 0.0) for t in TIERS)
    body = []
    for tier, title in TIERS.items():
        trows = [r for r in rows if r['tier'] == tier]
        body += [f'## {title}', '']
        cats = OrderedDict()
        for r in trows:
            cats.setdefault(r['category'], []).append(r)
        for cat, items in cats.items():
            sub = sum(r['ext'] for r in items)
            body += [f'### {cat}: {money(sub)}', '',
                     '| Item | Spec | Qty | Unit | Total | Notes |', '|---|---|---:|---:|---:|---|']
            for r in items:
                q = r['qty']
                qs = f'{q:g}'
                body.append(f"| {r['item']} | {r['spec']} | {qs} | ${r['unit']:,.2f} | {money(r['ext'])} | {r['notes']} |")
            body.append('')
        totals[tier] = sum(r['ext'] for r in trows)
    out += ['## Summary', '', '| Tier | Total |', '|---|---:|']
    for tier, title in TIERS.items():
        out.append(f'| {title} | **{money(totals[tier])}** |')
    out.append(f"| **Tier 1 + Tier 2 (recommended build)** | **{money(totals['base'] + totals['auto'])}** |")
    out.append(f'| Everything | {money(sum(totals.values()))} |')
    structure = sum(r['ext'] for r in rows if r['tier'] == 'base' and r['category'] in ('Floor', 'Walls', 'Roof'))
    fence = sum(r['ext'] for r in rows if r['category'] == 'Run & fencing')
    out += ['', f"Where the money goes: floor, wall and roof framing, siding and steel are "
            f"{structure / totals['base']:.0%} of Tier 1, and the run plus electric-netting paddocks "
            f"another {fence / totals['base']:.0%}. The whole automation tier adds only "
            f"{totals['auto'] / totals['base']:.0%} on top of Tier 1.", '']
    out += body
    return '\n'.join(out).rstrip() + '\n'


def load():
    rows = []
    with open(SRC, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['tier'] not in TIERS:
                raise SystemExit(f"unknown tier {r['tier']!r} for {r['item']}")
            r['qty'] = float(r['qty'])
            r['unit'] = float(r['unit_price'])
            r['ext'] = r['qty'] * r['unit']
            rows.append(r)
    return rows


def main():
    text = render(load())
    if '--check' in sys.argv:
        with open(OUT, encoding='utf-8') as f:
            if f.read() != text:
                print('docs/parts-list.md is stale: run python tools/gen_parts_list.py')
                sys.exit(1)
        print('OK: docs/parts-list.md is up to date')
        return
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote', os.path.relpath(OUT, ROOT))


if __name__ == '__main__':
    main()
