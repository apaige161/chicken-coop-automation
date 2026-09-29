"""Generate coop-controller.kicad_sch from design.py.

Connectivity is made with net labels on short wire stubs at every pin, so the
schematic is a faithful, ERC-checkable netlist view of design.py. Symbols are
grouped by function on the sheet.
"""
import os
import uuid

import sexpr
from sexpr import Sym as S
import design

KICAD_SHARE = os.environ.get(
    'KICAD_SHARE', r'C:\Users\apaig\AppData\Local\Programs\KiCad\10.0\share\kicad')
PROJECT = 'coop-controller'
NS = uuid.UUID('6f1c1a52-6a8e-4a52-9b7e-1c0c0a000001')


def uid(*parts):
    """Deterministic UUIDs so regenerating doesn't churn the files."""
    return str(uuid.uuid5(NS, '/'.join(str(p) for p in parts)))


_lib_cache = {}


def load_symbol(lib_id):
    lib, name = lib_id.split(':')
    if lib not in _lib_cache:
        path = os.path.join(KICAD_SHARE, 'symbols', lib + '.kicad_sym')
        with open(path, encoding='utf-8') as f:
            tree = sexpr.parse(f.read())
        _lib_cache[lib] = {s[1]: s for s in sexpr.find(tree, 'symbol')}
    syms = _lib_cache[lib]
    sym = syms[name]
    ext = sexpr.find1(sym, 'extends')
    if ext is None:
        flat = [x for x in sym]
    else:
        parent = load_symbol(f'{lib}:{ext[1]}')
        props = {p[1]: p for p in sexpr.find(sym, 'property')}
        flat = [S('symbol'), name]
        for x in parent[2:]:
            if isinstance(x, list) and x[0] == 'property' and x[1] in props:
                flat.append(props[x[1]])
            elif isinstance(x, list) and x[0] == 'symbol':
                sub = list(x)
                sub[1] = sub[1].replace(parent[1] if isinstance(parent[1], str) else ext[1], name, 1)
                flat.append(sub)
            else:
                flat.append(x)
    return flat


def embedded(lib_id):
    sym = [x for x in load_symbol(lib_id)]
    sym[1] = lib_id
    return sym


def sym_pins(lib_id):
    """[(number, name, x, y, angle)] in symbol (y-up) coordinates."""
    out = []
    for u in sexpr.find(load_symbol(lib_id), 'symbol'):
        for p in sexpr.find(u, 'pin'):
            at = sexpr.find1(p, 'at')
            out.append((sexpr.find1(p, 'number')[1], sexpr.find1(p, 'name')[1],
                        float(at[1]), float(at[2]), int(float(at[3]))))
    return out


def effects(hide=False, justify=None):
    e = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]
    if justify:
        e.append([S('justify'), S(justify)])
    if hide:
        e.append([S('hide'), S('yes')])
    return e


def prop(name, value, x, y, hide=False):
    return [S('property'), name, value, [S('at'), x, y, 0], effects(hide)]


def snap(v, g=1.27):
    return round(round(v / g) * g, 4)


class Sheet:
    def __init__(self):
        self.items = []
        self.lib_ids = []
        self.root = uid('root')

    def add_symbol(self, ref, lib_id, value, footprint, x, y, pin_nets, in_bom=True):
        if lib_id not in self.lib_ids:
            self.lib_ids.append(lib_id)
        pins = sym_pins(lib_id)
        s = [S('symbol'), [S('lib_id'), lib_id], [S('at'), x, y, 0], [S('unit'), 1],
             [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes' if in_bom else 'no')],
             [S('on_board'), S('yes')], [S('dnp'), S('no')], [S('uuid'), uid('sym', ref)],
             prop('Reference', ref, x + 2.54, y - 6.35 if pins else y - 2.54),
             prop('Value', value, x + 2.54, y + 6.35 if pins else y + 2.54),
             prop('Footprint', footprint, x, y, hide=True),
             prop('Datasheet', '~', x, y, hide=True)]
        for num, *_ in pins:
            s.append([S('pin'), num, [S('uuid'), uid('pin', ref, num)]])
        s.append([S('instances'), [S('project'), PROJECT,
                                   [S('path'), '/' + self.root, [S('reference'), ref], [S('unit'), 1]]]])
        self.items.append(s)
        # Stubs + labels / no-connects
        for num, name, px, py, ang in pins:
            ex, ey = snap(x + px), snap(y - py)
            out = (ang + 180) % 360     # direction pointing away from the symbol body
            dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[out]
            net = pin_nets.get(num, None) if pin_nets is not None else None
            if net is None:
                self.items.append([S('no_connect'), [S('at'), ex, ey], [S('uuid'), uid('nc', ref, num)]])
                continue
            lx, ly = snap(ex + dx * 2.54), snap(ey + dy * 2.54)
            self.items.append([S('wire'), [S('pts'), [S('xy'), ex, ey], [S('xy'), lx, ly]],
                               [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
                               [S('uuid'), uid('w', ref, num)]])
            self.label(net, lx, ly, out, uid('lbl', ref, num))
        return len(pins)

    def label(self, net, x, y, direction, u):
        just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[direction]
        self.items.append([S('label'), net, [S('at'), x, y, direction],
                           [S('fields_autoplaced'), S('yes')], effects(justify=just), [S('uuid'), u]])

    def text(self, t, x, y, size=2.0):
        self.items.append([S('text'), t, [S('exclude_from_sim'), S('no')], [S('at'), x, y, 0],
                           [S('effects'), [S('font'), [S('size'), size, size]], [S('justify'), S('left')]],
                           [S('uuid'), uid('text', t[:40], x, y)]])

    def dump(self, path):
        tree = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'coop_gen'],
                [S('generator_version'), '9.0'], [S('uuid'), self.root], [S('paper'), 'A1'],
                [S('title_block'), [S('title'), 'Coop Controller'], [S('rev'), '1.0'],
                 [S('comment'), 1, 'Generated by pcb/gen_schematic.py from pcb/design.py - do not hand-edit'],
                 [S('comment'), 2, 'Low voltage (12 V DC) only. Mains/SSRs live in a separate enclosure.']],
                [S('lib_symbols')] + [embedded(l) for l in self.lib_ids]]
        tree += self.items
        tree.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
        tree.append([S('embedded_fonts'), S('no')])
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(sexpr.dumps(tree) + '\n')


GROUP_TITLES = [
    ('power', 'POWER INPUT: 12 V in, fuse, reverse polarity, TVS, 5 V regulator, VIN sense'),
    ('esp', 'ESP32-DevKitC-32E SOCKETS (fit J21 OR J22)'),
    ('door', 'POP DOOR ACTUATOR: 2-relay H-bridge (K1 open / K2 close)'),
    ('outputs', '12 V LOW-SIDE OUTPUTS: valve, feeder, fan, SSR drivers'),
    ('inputs', 'INPUT CONDITIONING: pull-ups, RC filters, echo divider'),
    ('conn', 'FIELD CONNECTORS'),
    ('mech', 'MECHANICAL'),
]


def main(out):
    sh = Sheet()
    y = 25.4
    for group, title in GROUP_TITLES:
        parts = [p for p in design.PARTS if p['group'] == group]
        sh.text(title, 20.32, y)
        y += 12.7
        x = 38.1
        row_h = 0.0
        for p in parts:
            pins = sym_pins(p['lib_id'])
            ys = [-pp[3] for pp in pins] or [0]
            xs = [pp[2] for pp in pins] or [0]
            h = max(ys) - min(ys) + 12.7
            w = max(xs) - min(xs) + 50.8
            if x + w > 800:
                x = 38.1
                y += row_h + 12.7
                row_h = 0
            sx, sy = snap(x - min(xs) + 22.86, 2.54), snap(y - min(ys) + 5.08, 2.54)
            sh.add_symbol(p['ref'], p['lib_id'], p['value'], p['footprint'], sx, sy, p['pins'])
            x += w
            row_h = max(row_h, h)
        y += row_h + 20.32
    fx = 38.1
    for net in design.PWR_FLAG_NETS:
        sh.add_symbol(f'#FLG_{net}', 'power:PWR_FLAG', 'PWR_FLAG', '', snap(fx, 2.54), snap(y, 2.54),
                      {'1': net}, in_bom=False)
        fx += 30.48
    sh.dump(out)


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else 'coop-controller.kicad_sch')
