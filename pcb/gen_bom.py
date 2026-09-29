"""Grouped PCB bill of materials from design.py (CSV)."""
import csv
import sys
from collections import OrderedDict

import design


def natural(ref):
    head = ref.rstrip('0123456789')
    return head, int(ref[len(head):] or 0)


def main(out):
    groups = OrderedDict()
    for p in sorted(design.PARTS, key=lambda p: natural(p['ref'])):
        if p['group'] == 'mech':
            continue
        key = (p['value'], p['footprint'])
        g = groups.setdefault(key, {'refs': [], 'note': p['note'], 'lib': p['lib_id']})
        g['refs'].append(p['ref'])
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Qty', 'References', 'Value', 'Footprint', 'Notes'])
        for (value, fp), g in groups.items():
            w.writerow([len(g['refs']), ' '.join(g['refs']), value, fp.split(':')[1], g['note']])
    print(f'{sum(len(g["refs"]) for g in groups.values())} parts in {len(groups)} lines -> {out}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bom.csv')
