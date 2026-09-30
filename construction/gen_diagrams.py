"""Generate the construction diagrams (SVG) for the 50-bird coop.

    python construction/gen_diagrams.py

Outputs to construction/diagrams/. The wiring diagram's terminal list is read from
hardware/pinmap.yaml so it can't drift from the PCB and firmware. Every SVG is
checked for well-formed XML after writing.
"""
import os
import xml.dom.minidom

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'diagrams')

INK = '#1f2933'
MUTED = '#616e7c'
WOOD = '#c89f68'
WALL = '#8d6e4a'
WIRE_12V = '#d64545'
WIRE_GND = '#1f2933'
WIRE_SIG = '#2f6fbd'
WIRE_AC = '#b8860b'
WATER = '#2186c4'
GREEN = '#3f9142'
FILL = '#f5f7fa'
FONT = 'font-family="Helvetica, Arial, sans-serif"'


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
                      self._text(20, 34, title, 22, weight='bold')]

    @staticmethod
    def _esc(s):
        return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _text(self, x, y, s, size=12, anchor='start', color=INK, weight='normal', rotate=None):
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ''
        return (f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" fill="{color}" '
                f'text-anchor="{anchor}" font-weight="{weight}"{tr}>{self._esc(s)}</text>')

    def text(self, *a, **k):
        self.parts.append(self._text(*a, **k))

    def rect(self, x, y, w, h, fill='none', stroke=INK, sw=1.5, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def poly(self, pts, fill='none', stroke=INK, sw=1.5, close=True, dash=None):
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.parts.append(f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, x, y, r, fill='none', stroke=INK, sw=1.5):
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def box(self, x, y, w, h, title, lines=(), fill=FILL, stroke=INK, size=12):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=6)
        self.text(x + 8, y + 18, title, size + 1, weight='bold')
        for i, l in enumerate(lines):
            self.text(x + 8, y + 36 + i * (size + 4), l, size - 1, color=MUTED)

    def dim(self, x1, y1, x2, y2, label, off=0, size=12):
        """Dimension line with end ticks and a centred label."""
        if y1 == y2:
            y = y1 + off
            self.line(x1, y, x2, y, MUTED, 1)
            for x in (x1, x2):
                self.line(x, y - 5, x, y + 5, MUTED, 1)
            self.text((x1 + x2) / 2, y - 5, label, size, 'middle', MUTED)
        else:
            x = x1 + off
            self.line(x, y1, x, y2, MUTED, 1)
            for y in (y1, y2):
                self.line(x - 5, y, x + 5, y, MUTED, 1)
            self.text(x - 6, (y1 + y2) / 2, label, size, 'middle', MUTED, rotate=-90)

    def legend(self, x, y, items):
        for i, (color, label, dash) in enumerate(items):
            yy = y + i * 18
            self.line(x, yy, x + 30, yy, color, 3, dash)
            self.text(x + 38, yy + 4, label, 11)

    def save(self, name):
        body = '\n'.join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}">\n{body}\n</svg>\n')
        path = os.path.join(OUT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(svg)
        xml.dom.minidom.parseString(svg)   # gate: must be well-formed
        print('wrote', os.path.relpath(path, ROOT))


# --------------------------------------------------------------------------- wiring
FIELD = {
    'J1': ('12 V DC from PSU (mains box)', '16/2 outdoor, fused 5 A on PCB'),
    'J2': ('Linear actuator, 12 V, 18" stroke', '16/2 outdoor. Red = M+ (extend/open)'),
    'J3': ('Door reed switches (closed, open)', '18/5 sprinkler wire, common = GND'),
    'J4': ('Water solenoid valve, 12 V NC', '18/2. Polarity-free coil'),
    'J5': ('OPTIONAL metered auger motor, 12 V', '16/2. Unused with the gravity feed bin'),
    'J6': ('Relay module 1 A1/A2 (lights), relay 2 (de-icer)', '18/4. +12V to A1, switched pin to A2'),
    'J7': ('Float switches (low, high) in the drum', '18/5 sprinkler wire, common = GND'),
    'J8': ('DS18B20 waterproof probe (drum)', 'Red 3V3, yellow DATA, black GND'),
    'J9': ('BME280 + BH1750 (I2C) in radiation shield', 'Cat5e, keep under 2 m'),
    'J10': ('HC-SR501 PIR (roost area)', '18/3'),
    'J11': ('JSN-SR04T ultrasonic (feed bin lid)', 'Cat5e / 22/4'),
    'J12': ('Panel: door push-button + status LED', 'On enclosure lid'),
    'J13': ('Expansion header (3V3, GND, 5V, SDA, SCL, IO5)', 'Future sensors'),
    'J14': ('12 V exhaust fan (gable)', '18/2'),
}


def wire_color(pin):
    if pin in ('+12V', 'VIN_RAW', 'M+', 'M-'):
        return WIRE_12V
    if pin == 'GND':
        return WIRE_GND
    return WIRE_SIG


def wiring(pm):
    rows = sum(14 * len(c['pins']) + 18 for c in pm['connectors'].values())
    s = Svg(1500, 460 + 80 + rows + 40, 'Coop electrical wiring diagram (see construction/wiring.md)')
    s.text(20, 56, 'SAFETY: 120 V work must be GFCI protected and done/inspected by a licensed electrician '
           'to local code. The controller PCB carries 12 V DC only.', 13, color='#c0392b', weight='bold')

    # --- mains side
    s.box(20, 80, 230, 90, 'House panel', ['20 A GFCI breaker (dedicated)', 'or 20 A breaker + GFCI at coop'])
    s.line(250, 125, 330, 125, WIRE_AC, 4)
    s.text(20, 190, 'Feed: UF-B 12/2 w/G, buried per NEC 300.5', 10, color=WIRE_AC)
    s.rect(330, 80, 420, 330, fill='#fffaf0', stroke=WIRE_AC, sw=2, rx=8)
    s.text(340, 100, 'MAINS ENCLOSURE (NEMA 4X / IP65, DIN rail), inside coop, 5 ft up', 13, weight='bold')
    s.box(345, 115, 180, 60, 'Disconnect / 20 A', ['2-pole DIN breaker'], fill='#fff')
    s.box(545, 115, 190, 60, 'GFCI receptacle', ['service outlet (tools, brooder)'], fill='#fff')
    s.box(345, 190, 180, 70, 'PSU Mean Well', ['HDR-100-12N, 12 V 7.5 A', 'L / N / PE in, +V / -V out'], fill='#fff')
    s.box(545, 190, 190, 70, 'Relay 1 (lights)', ['DIN module, 12 VDC coil, 6 A', 'switches HOT only (or SSR)'], fill='#fff')
    s.box(545, 275, 190, 70, 'Relay 2 (de-icer)', ['DIN module, 12 VDC coil, 6 A', 'switches HOT only (or SSR)'], fill='#fff')
    s.box(345, 275, 180, 70, 'Ground bar', ['all PE + metal parts bonded'], fill='#fff')
    s.text(345, 370, 'L = black (hot)  N = white  PE = green/bare', 11, color=MUTED)
    s.text(345, 388, 'Lights & de-icer on their own outdoor-rated cords/boxes', 11, color=MUTED)

    s.box(800, 110, 230, 70, 'Coop LED lights', ['2x 9 W A19 in jelly-jar', 'wet-location fixtures'])
    s.line(735, 225, 770, 225, WIRE_AC, 3)
    s.line(770, 225, 770, 145, WIRE_AC, 3)
    s.line(770, 145, 800, 145, WIRE_AC, 3)
    s.box(800, 280, 230, 70, 'Water de-icer / heated base', ['250-500 W, thermostatic', 'plugged into the relay-2 outlet'])
    s.line(735, 310, 800, 310, WIRE_AC, 3)

    # 12 V to controller
    s.line(435, 260, 435, 460, WIRE_12V, 3)
    s.text(442, 440, '+12 V / GND to J1', 11, color=WIRE_12V)

    # SSR control back from controller
    s.poly([(700, 460), (700, 425), (760, 425), (760, 330), (735, 330)], stroke=WIRE_SIG, sw=2, close=False, dash='6,3')
    s.poly([(680, 460), (680, 418), (752, 418), (752, 245), (735, 245)], stroke=WIRE_SIG, sw=2, close=False, dash='6,3')
    s.text(560, 440, 'J6: relay coils (12 V)', 11, color=WIRE_SIG)

    # optional battery
    s.box(20, 205, 290, 90, 'Optional backup (Tier 2+)', ['12 V 7 Ah SLA + float charger', 'diode-OR onto PSU output', 'door keeps working in outages'],
          fill='#f0fff4', stroke=GREEN)

    # --- controller
    cx, cy, cw, ch = 330, 460, 420, rows + 80
    s.rect(cx, cy, cw, ch, fill='#eef6ff', stroke=WIRE_SIG, sw=2, rx=8)
    s.text(cx + 10, cy + 22, 'CONTROLLER ENCLOSURE (IP65), Coop Controller PCB v1.0', 13, weight='bold')
    s.text(cx + 10, cy + 40, 'ESP32-DevKitC-32E + ESPHome. Cable glands on the bottom face only', 11, color=MUTED)

    y = cy + 70
    for ref in sorted(pm['connectors'], key=lambda r: int(r[1:])):
        c = pm['connectors'][ref]
        dev, cable = FIELD[ref]
        n = len(c['pins'])
        blk_h = 14 * n + 10
        s.rect(cx + 250, y, 150, blk_h, fill='#ffffff', stroke=INK, sw=1.2, rx=3)
        s.text(cx + 256, y + 13, f'{ref} {c["name"]}', 11, weight='bold')
        for i, pin in enumerate(c['pins']):
            py = y + 24 + i * 14 - 4
            s.circle(cx + 400, py, 3, fill='#ffffff')
            s.text(cx + 394, py + 4, pin, 10, 'end', MUTED)
            s.line(cx + 403, py, 1060, py, wire_color(pin), 2 if pin != 'GND' else 1.5)
        # field device box
        s.rect(1060, y - 2, 420, blk_h + 4, fill=FILL, stroke=INK, sw=1, rx=4)
        s.text(1068, y + 13, dev, 11, weight='bold')
        s.text(1068, y + 27, cable, 10, color=MUTED)
        y += blk_h + 8
    s.text(cx + 10, cy + 110, 'Field wiring', 12, weight='bold')
    s.text(cx + 10, cy + 128, 'Terminals: 5.08 mm screw,', 11, color=MUTED)
    s.text(cx + 10, cy + 144, '16-26 AWG. Ferrules on', 11, color=MUTED)
    s.text(cx + 10, cy + 160, 'stranded wire.', 11, color=MUTED)
    s.text(cx + 10, cy + 186, 'Drip loop every cable', 11, color=MUTED)
    s.text(cx + 10, cy + 202, 'below the gland.', 11, color=MUTED)
    s.text(cx + 10, cy + 228, 'Run low-voltage wiring', 11, color=MUTED)
    s.text(cx + 10, cy + 244, 'in PVC conduit or at', 11, color=MUTED)
    s.text(cx + 10, cy + 260, 'least 12" away from', 11, color=MUTED)
    s.text(cx + 10, cy + 276, 'mains cables.', 11, color=MUTED)

    s.legend(20, 360, [(WIRE_AC, '120 V AC (licensed electrician)', None), (WIRE_12V, '+12 V DC / motor', None),
                       (WIRE_GND, 'GND / common', None), (WIRE_SIG, 'Signal / control', None),
                       (WIRE_SIG, 'Relay/SSR control (12 V)', '6,3')])
    s.box(20, 480, 290, 160, 'Rules', ['Mains and 12 V in SEPARATE boxes', 'GFCI upstream of everything',
                                       'Bond all metal to ground', 'UF-B / THWN in conduit outdoors',
                                       'Rodent-proof: conduit + gland seals', 'Label every cable both ends',
                                       'Turn off breaker before servicing'])
    s.save('wiring-diagram.svg')


# --------------------------------------------------------------------------- plumbing
def plumbing():
    s = Svg(1400, 640, 'Water supply: spigot to reservoir (see construction/plumbing.md)')
    y = 200
    parts = [
        ('Hose spigot', ['existing, frost-free', 'preferred']),
        ('Vacuum breaker', ['hose-bib backflow', 'preventer (required)']),
        ('Y-valve + shutoff', ['keep 1 port for', 'the garden hose']),
        ('Pressure regulator', ['25 psi, 3/4" GHT', '(protects valve/floats)']),
        ('Inline filter', ['40-100 mesh', 'screen filter']),
        ('Drinking-water hose', ['lead-free, 5/8"', 'bury 12" or run in', 'foam pipe insulation']),
    ]
    x = 20
    for i, (t, l) in enumerate(parts):
        s.box(x, y, 185, 90, t, l)
        if i < len(parts) - 1:
            s.line(x + 185, y + 45, x + 215, y + 45, WATER, 5)
        x += 215
    # into coop
    s.line(20 + 5 * 215 + 92, y + 90, 20 + 5 * 215 + 92, 380, WATER, 5)
    s.box(1060, 380, 200, 90, '12 V NC solenoid', ['1/2" brass, pilot type', 'VALVE (J4) opens it', 'fails CLOSED'], stroke=WIRE_SIG)
    s.line(1060, 425, 900, 425, WATER, 5)
    # drum
    s.rect(600, 330, 300, 250, fill='#e8f4fb', stroke=INK, sw=2, rx=10)
    s.text(610, 352, '30 gal drum in the EXTERIOR service', 12, weight='bold')
    s.text(610, 368, 'station (18" stand, insulated side)', 12, weight='bold')
    s.rect(603, 430, 294, 147, fill='#bfe3f5', stroke='none')
    s.line(603, 430, 897, 430, WATER, 2, '5,3')
    # floats
    s.line(640, 380, 640, 470, INK, 1.5)
    s.circle(640, 470, 9, fill='#fff')
    s.text(655, 474, 'LOW float (J7) -> start fill', 11)
    s.line(700, 360, 700, 410, INK, 1.5)
    s.circle(700, 410, 9, fill='#fff')
    s.text(715, 404, 'HIGH float (J7) -> stop fill', 11)
    s.line(840, 360, 840, 540, INK, 1.5)
    s.rect(835, 540, 10, 25, fill='#555', stroke='none')
    s.text(760, 556, 'DS18B20 (J8)', 11, 'end')
    s.text(610, 520, 'de-icer (relay 2) in winter', 11, color=MUTED)
    # overflow
    s.line(897, 360, 960, 360, WATER, 3)
    s.line(960, 360, 960, 620, WATER, 3, '6,4')
    s.text(968, 600, '3/4" overflow to outside', 11, color=MUTED)
    s.text(968, 614, '(drains to grade, away from the station)', 11, color=MUTED)
    # outlet to nipples
    s.line(600, 560, 300, 560, WATER, 4)
    s.line(300, 560, 300, 600, WATER, 4)
    s.line(120, 600, 480, 600, WATER, 4)
    for xx in range(140, 480, 40):
        s.line(xx, 600, xx, 612, INK, 2)
    s.text(120, 630, '3/4" PVC through the coop wall -> drinker line inside, 10+ horizontal nipples/cups, 12-14" high',
           11, color=MUTED)
    s.box(20, 380, 520, 150, 'Tier 1 (low-tech)', [
        'Skip the solenoid: fill the drum by hand with the hose,',
        'or fit a MECHANICAL float valve (stock-tank type)',
        'fed by the same regulator/filter chain.',
        '30 gal lasts 2.5-5 days for 50 birds.',
        'Tier 2 adds the solenoid + floats + DS18B20 (this drawing).'], fill='#f0fff4', stroke=GREEN)
    s.text(20, 90, 'Winter: disconnect and drain the hose below freezing (the firmware also refuses to fill '
           'when the water is near 0 C).', 12, color='#c0392b')
    s.text(20, 108, 'Hand-fill the drum from outside through the station doors, or use a heated drinking-water hose.', 12, color='#c0392b')
    s.save('plumbing-diagram.svg')


# --------------------------------------------------------------------------- floor plan
def floor_plan():
    k = 42          # px per ft
    ox, oy = 110, 170
    W, D = 20, 10   # ft (east-west, north-south)
    s = Svg(ox + W * k + 480, oy + D * k + 170, 'Coop floor plan: 10 ft x 20 ft (200 sq ft) + exterior feed/water station, north up')

    def P(x, y):
        return ox + x * k, oy + y * k

    x0, y0 = P(0, 0)
    s.rect(x0, y0, W * k, D * k, fill='#fbf7ef', stroke=WALL, sw=8)
    s.dim(x0, y0 + D * k, x0 + W * k, y0 + D * k, "20'-0\" outside", 78)
    s.dim(x0, y0, x0, y0 + D * k, "10'-0\"", -60)

    # roosts (west end): 4 bars, 10 ft long, running N-S, 16" apart, over a poop board
    px, py = P(0.8, 0.5)
    s.rect(px, py, 5.2 * k, 9 * k, fill='#efe6d6', stroke=MUTED, sw=1, dash='4,3')
    s.text(px + 6, py + 9 * k - 8, 'poop board @ 24" (PDZ/sand)', 11, color=MUTED)
    for i in range(5):
        rx = px + (0.5 + i * 1.1) * k
        s.rect(rx - 4, py + 4, 8, 9 * k - 30, fill=WOOD, stroke=WALL, sw=1)
    s.text(px + 6, py + 16, 'ROOSTS: 5 x 9 ft 2x4 (wide face up)', 12, weight='bold')
    s.text(px + 6, py + 32, '@ 36" high, 13" apart, 45 ft total', 11, color=MUTED)

    # nest boxes (north wall, exterior rollout bay)
    nx, ny = P(6.5, -1.25)
    s.rect(nx, ny, 13 * k, 1.25 * k, fill='#fff3d6', stroke=WALL, sw=2)
    for i in range(1, 12):
        s.line(nx + i * 13 * k / 12, ny, nx + i * 13 * k / 12, ny + 1.25 * k, WALL, 1)
    s.text(nx + 13 * k / 2, ny - 8, '12 NEST BOXES (single row, 12x12x14" deep), exterior bay, floor 20" up, hinged lid outside', 11, 'middle')

    # people door (east wall)
    dx, dy = P(20, 6.2)
    s.rect(dx - 6, dy, 12, 3 * k, fill='#ffffff', stroke=INK, sw=1.5)
    s.poly([(dx, dy), (dx - 3 * k, dy), (dx, dy + 3 * k)], stroke=MUTED, sw=1, close=False, dash='4,3')
    s.text(dx + 12, dy + 1.5 * k, '36" door (east)', 11)

    # pop door (south wall)
    pdx, pdy = P(15.5, 10)
    s.rect(pdx, pdy - 6, 1.0 * k, 12, fill='#ffe08a', stroke=INK)
    s.text(pdx + 0.5 * k, pdy + 26, 'POP DOOR 12"x16"', 11, 'middle', weight='bold')
    s.text(pdx + 0.5 * k, pdy + 40, 'actuator above (inside), ramp to run', 10, 'middle', MUTED)

    # windows (south) and vents
    for wx in (3, 7.5, 11.5):
        a, b = P(wx, 10)
        s.rect(a, b - 5, 2 * k, 10, fill='#cfe8ff', stroke=INK, sw=1)
    s.text(P(7.5, 10)[0], P(0, 10)[1] + 26, '24"x36" windows: 1/2" hardware cloth + hinged storm shutters', 10, 'start', MUTED)
    a, b = P(0, 5)
    s.rect(a - 5, b - k, 10, 2 * k, fill='#cfe8ff', stroke=INK, sw=1)
    s.text(a + 10, b + 4 + k * 1.3, 'window (west)', 10, 'start', MUTED)

    # exterior feed + water service station (east wall, north end)
    sx, sy = P(20, 0.5)
    s.rect(sx + 4, sy, 2.5 * k, 5 * k, fill='#f3ead9', stroke=WALL, sw=3)
    s.text(sx + 1.25 * k + 4, sy - 8, 'SERVICE STATION (outside)', 11, 'middle', weight='bold')
    bx, by = P(20.2, 3.25)
    s.rect(bx, by, 2.1 * k, 2.0 * k, fill='#f3e3c3', stroke=INK)
    s.text(bx + 1.05 * k, by + 0.9 * k, 'FEED BIN', 10, 'middle', weight='bold')
    s.text(bx + 1.05 * k, by + 0.9 * k + 13, '~350 lb', 9, 'middle', MUTED)
    dcx, dcy = P(21.25, 1.83)
    s.circle(dcx, dcy, 0.83 * k, fill='#d6ecfa')
    s.text(dcx, dcy + 4, '30 gal DRUM', 9, 'middle', weight='bold')
    s.text(P(22.7, 0)[0] + 10, P(0, 2.2)[1], 'doors open', 10, 'start', MUTED)
    s.text(P(22.7, 0)[0] + 10, P(0, 2.2)[1] + 14, 'from outside', 10, 'start', MUTED)
    # indoor trough fed through the wall
    tx, ty = P(18.6, 3.3)
    s.rect(tx, ty, 1.1 * k, 1.8 * k, fill='#f3e3c3', stroke=INK)
    s.text(tx - 6, ty + 0.9 * k + 4, 'trough', 10, 'end', MUTED)
    s.line(P(19.7, 0)[0], P(0, 4.2)[1], P(20.2, 0)[0], P(0, 4.2)[1], '#b07b2c', 4)
    # drinker line from the drum through the wall
    pts = [P(20.4, 1.75), P(15, 1.75), P(15, 4.2), P(10, 4.2)]
    s.poly(pts, stroke=WATER, sw=4, close=False)
    s.text(P(10, 4.2)[0], P(0, 4.2)[1] + 16, 'nipple/cup line (heat cable in winter)', 10, 'start', MUTED)
    # electrical boxes (inside, east wall, 5 ft up)
    ex, ey = P(19.4, 0.6)
    s.rect(ex, ey, 14, 0.9 * k, fill='#fff3b0', stroke=WIRE_AC, sw=2)
    s.text(ex - 6, ey + 14, 'mains box (5 ft up)', 10, 'end', WIRE_AC)
    s.rect(ex, ey + 1.0 * k, 14, 0.8 * k, fill='#dcecff', stroke=WIRE_SIG, sw=2)
    s.text(ex - 6, ey + 1.0 * k + 14, 'controller', 10, 'end', WIRE_SIG)
    for lx in (6, 14):
        a, b = P(lx, 5)
        s.circle(a, b, 8, fill='#fffbe6', stroke=WIRE_AC)
    s.text(P(6, 5)[0] + 12, P(0, 5)[1] + 4, 'light', 10, 'start', WIRE_AC)
    a, b = P(2.5, 5)
    s.text(a, b + 70, 'PIR aimed over roosts', 10, 'start', MUTED)
    s.text(P(20, 0)[0] + 16, P(0, -0.5)[1], 'gable fan (J14) above', 10, 'start', MUTED)

    # compass + notes
    cx0, cy0 = ox + W * k + 250, oy + 30
    s.poly([(cx0, cy0 - 22), (cx0 - 9, cy0 + 8), (cx0 + 9, cy0 + 8)], fill=INK)
    s.text(cx0, cy0 + 26, 'N', 14, 'middle', weight='bold')
    notes = ['Floor: 3/4" PT plywood, porch enamel,', '  8-12" deep-litter pine shavings',
             'Ventilation >= 20 sq ft: full soffit +', '  ridge vent + 3 windows + gables,',
             '  all 1/2" hardware cloth', 'Roosts higher than nest boxes',
             '  (boxes 18-24" off floor)', 'Keep feed/water out from under roosts',
             '4 sq ft/bird indoors = 200 sq ft',
             'Feed + water filled from OUTSIDE:', '  gravity bin -> wall slot -> trough,', '  drum -> wall -> nipple line']
    for i, n in enumerate(notes):
        s.text(ox + W * k + 190, oy + 90 + i * 17, n, 11, color=MUTED)
    s.save('coop-floor-plan.svg')


# --------------------------------------------------------------------------- elevations
def elevations():
    k = 30
    s = Svg(1500, 620, 'Coop elevations: 4/12 gable roof, 8 ft walls, floor ~12 in. up on skids')
    g = 520   # ground line y

    # ---- south (front) elevation
    ox = 60
    floor_h, wall_h, rise, over = 1.0, 8.08, 20 / 12, 1.0
    L = 20
    s.line(ox - 30, g, ox + (L + 1) * k + 30, g, MUTED, 1)
    y_floor = g - floor_h * k
    y_top = y_floor - wall_h * k
    s.rect(ox, y_floor, L * k, floor_h * k * 0.0 + 6, fill=WOOD, stroke=WALL)
    for sx in (0.5, 10, 19.5):
        s.rect(ox + sx * k - 8, y_floor + 6, 16, floor_h * k - 6, fill='#9c7a4d', stroke=WALL, sw=1)
    s.rect(ox, y_top, L * k, wall_h * k, fill='#f3ead9', stroke=WALL, sw=3)
    s.poly([(ox - over * k, y_top), (ox + (L + over) * k, y_top), (ox + (L + over) * k, y_top - 10),
            (ox - over * k, y_top - 10)], fill='#9aa5b1', stroke=INK)
    for wx in (3, 7.5, 11.5):
        s.rect(ox + wx * k, y_top + 2 * k, 2 * k, 3 * k, fill='#cfe8ff', stroke=INK)
    s.rect(ox + 15.5 * k, y_floor - (8 / 12 + 16 / 12) * k, 1 * k, 16 / 12 * k, fill='#ffe08a', stroke=INK)
    s.poly([(ox + 15.5 * k, y_floor - 8 / 12 * k), (ox + 14 * k, g)], stroke=WOOD, sw=4, close=False)
    s.text(ox + 16.6 * k, y_floor - 1.3 * k, 'pop door + ramp', 11)
    s.rect(ox + 0.5 * k, y_top + 0.3 * k, L * k - k, 0.5 * k, fill='none', stroke=MUTED, sw=1, dash='3,3')
    s.text(ox + 10 * k, y_top + 0.7 * k, 'soffit vent strip (hardware cloth) full length', 10, 'middle', MUTED)
    s.dim(ox, g + 10, ox + L * k, g + 10, "20'-0\"", 20)
    s.dim(ox + L * k + 20, y_top, ox + L * k + 20, g, "~9'-1\" to eave", 30)
    s.text(ox + L * k / 2, y_top - 30, 'SOUTH (FRONT) ELEVATION', 14, 'middle', weight='bold')

    # ---- east (end) section
    ox2 = 900
    D = 10
    s.line(ox2 - 40, g, ox2 + (D + 1) * k + 60, g, MUTED, 1)
    y_floor = g - floor_h * k
    y_top = y_floor - wall_h * k
    ridge_y = y_top - rise * 5 / 1.667 * k * 0 - (5 * 4 / 12) * k
    s.rect(ox2 - 4, y_floor, D * k + 8, 6, fill=WOOD, stroke=WALL)
    for sx in (0.25, 5, 9.75):
        s.rect(ox2 + sx * k - 8, y_floor + 6, 16, floor_h * k - 6, fill='#9c7a4d', stroke=WALL, sw=1)
    s.poly([(ox2, y_floor), (ox2, y_top), (ox2 + D / 2 * k, ridge_y), (ox2 + D * k, y_top), (ox2 + D * k, y_floor)],
           fill='#f3ead9', stroke=WALL, sw=3)
    s.poly([(ox2 - over * k, y_top + over * 4 / 12 * k), (ox2 + D / 2 * k, ridge_y - 8),
            (ox2 + (D + over) * k, y_top + over * 4 / 12 * k)], stroke=INK, sw=5, close=False)
    s.rect(ox2 + D / 2 * k - 14, ridge_y - 14, 28, 8, fill='#9aa5b1', stroke=INK, sw=1)
    s.text(ox2 + D / 2 * k, ridge_y - 22, 'ridge vent', 10, 'middle', MUTED)
    # viewed from the east: south is on the LEFT, north on the RIGHT
    # people door (south end of the east wall)
    s.rect(ox2 + 0.8 * k, y_floor - 80 / 12 * k, 3 * k, 80 / 12 * k, fill='#ffffff', stroke=INK)
    s.text(ox2 + 2.3 * k, y_floor - 3 * k, '36"x80"', 10, 'middle', MUTED)
    # exterior feed + water service station (north end, in front of the wall)
    st_x0, st_x1 = ox2 + 4.5 * k, ox2 + 9.5 * k
    st_top = y_floor - 72 / 12 * k
    s.rect(st_x0, st_top, st_x1 - st_x0, y_floor - st_top + floor_h * k, fill='#e9dcc4', stroke=WALL, sw=2)
    s.poly([(st_x0 - 6, st_top - 4), (st_x1 + 6, st_top - 4), (st_x1 + 6, st_top - 12), (st_x0 - 6, st_top - 12)],
           fill='#9aa5b1', stroke=INK, sw=1)
    s.line((st_x0 + st_x1) / 2, st_top + 4, (st_x0 + st_x1) / 2, y_floor, WALL, 1.5)
    s.text((st_x0 + st_x1) / 2, st_top + 2.2 * k, 'FEED + WATER', 10, 'middle', weight='bold')
    s.text((st_x0 + st_x1) / 2, st_top + 2.2 * k + 13, 'service station', 10, 'middle', MUTED)
    s.text((st_x0 + st_x1) / 2, st_top + 2.2 * k + 26, '(2 doors, fill from here)', 9, 'middle', MUTED)
    # nest bay (north side = right in this view)
    s.rect(ox2 + D * k, y_floor - 3.6 * k, 1.5 * k, 2.2 * k, fill='#fff3d6', stroke=WALL, sw=2)
    s.text(ox2 + D * k + 1.6 * k, y_floor - 3.9 * k, 'nest bay', 10, 'start', MUTED)
    # gable vent + fan
    s.rect(ox2 + 4.2 * k, y_top - 0.9 * k, 1.6 * k, 0.8 * k, fill='#cfe8ff', stroke=INK)
    s.text(ox2 + 6 * k, y_top + 0.9 * k, 'gable vent + 12 V fan (above)', 10, 'start', MUTED)
    s.dim(ox2, g + 10, ox2 + D * k, g + 10, "10'-0\"", 20)
    s.dim(ox2 + D * k + 40, ridge_y, ox2 + D * k + 40, g, "~10'-9\" ridge", 30)
    s.dim(ox2 - 60, y_floor, ox2 - 60, g, '~12"', 0)
    s.text(ox2 + D * k / 2, ridge_y - 44, 'EAST (END) ELEVATION (south on the left)', 14, 'middle', weight='bold')
    s.text(60, 580, 'Framing: 4x6 PT skids on 4" compacted gravel; 2x6 PT floor joists 16" o.c.; 2x4 studs 16" o.c.; '
           '2x6 rafters 24" o.c. with collar ties; 2x4 purlins 24" o.c.; 29 ga ribbed steel roofing.', 11, color=MUTED)
    s.text(60, 598, 'Check rafter size/spacing against your local ground snow load before building (see coop-build-plan.md).',
           11, color='#c0392b')
    s.save('coop-elevations.svg')


# --------------------------------------------------------------------------- site plan
def site_plan():
    k = 7   # px per ft
    s = Svg(1300, 900, 'Site plan: coop, secure run and rotational free-range paddocks (not to exact scale)')
    ox, oy = 520, 250
    # coop 20x10
    s.rect(ox, oy, 20 * k, 10 * k, fill='#f3ead9', stroke=WALL, sw=3)
    s.text(ox + 10 * k, oy + 5 * k + 4, 'COOP', 12, 'middle', weight='bold')
    # run 25 x 20 south of coop
    rx, ry = ox - 2.5 * k, oy + 10 * k
    s.rect(rx, ry, 25 * k, 20 * k, fill='#eef7ee', stroke=GREEN, sw=3)
    s.text(rx + 12.5 * k, ry + 9 * k, 'SECURE RUN', 12, 'middle', weight='bold')
    s.text(rx + 12.5 * k, ry + 9 * k + 15, '20 x 25 ft (500 sq ft)', 10, 'middle', MUTED)
    s.text(rx + 12.5 * k, ry + 9 * k + 29, 'netted, 24" apron', 10, 'middle', MUTED)
    # range gates on three sides
    for gx, gy, gw, gh in [(rx + 25 * k - 4, ry + 8 * k, 8, 3 * k), (rx + 11 * k, ry + 20 * k - 4, 3 * k, 8),
                           (rx - 4, ry + 8 * k, 8, 3 * k)]:
        s.rect(gx, gy, gw, gh, fill='#ffe08a', stroke=INK)
    # paddocks (60 x 35 ft each, electric netting)
    pads = [('PADDOCK A', 720, 180), ('PADDOCK B', 380, 510), ('PADDOCK C', 40, 250)]
    for name, x, y in pads:
        s.rect(x, y, 60 * k, 35 * k, fill='none', stroke=GREEN, sw=2, dash='10,6')
        s.text(x + 30 * k, y + 17 * k, name, 13, 'middle', GREEN, 'bold')
        s.text(x + 30 * k, y + 17 * k + 16, '~164 ft electric poultry netting', 10, 'middle', MUTED)
        s.text(x + 30 * k, y + 17 * k + 30, '2-4 weeks per rotation', 10, 'middle', MUTED)
    # utilities
    hx, hy = 60, 70
    s.box(hx, hy, 180, 60, 'House', ['120 V panel, hose spigot'])
    s.poly([(hx + 180, hy + 22), (ox + 19 * k, hy + 22), (ox + 19 * k, oy)], stroke=WIRE_AC, sw=3, close=False)
    s.text(ox + 19 * k + 8, hy + 60, 'UF-B 12/2 (GFCI),', 11, color=WIRE_AC)
    s.text(ox + 19 * k + 8, hy + 74, 'trench per code', 11, color=WIRE_AC)
    s.poly([(hx + 180, hy + 44), (ox + 12 * k, hy + 44), (ox + 12 * k, oy)], stroke=WATER, sw=3, close=False, dash='8,4')
    s.text(ox + 12 * k - 8, hy + 70, 'drinking-water hose', 11, 'end', WATER)
    s.text(ox + 12 * k - 8, hy + 84, '(seasonal)', 11, 'end', WATER)
    # shade tree (west of the coop)
    s.circle(420, 185, 50, fill='#dff0d8', stroke=GREEN)
    s.text(420, 182, 'deciduous shade', 10, 'middle', GREEN)
    s.text(420, 196, '(summer shade)', 10, 'middle', MUTED)
    # compass
    s.poly([(1230, 90), (1221, 120), (1239, 120)], fill=INK)
    s.text(1230, 140, 'N', 14, 'middle', weight='bold')
    notes = ['Long glazed wall faces SOUTH for winter sun; partial shade from the west/south-west in summer.',
             'Set the coop on high, well-drained ground. Keep the run 50+ ft from wells/streams (check local rules).',
             'Free-range most of the day: rotate paddocks every 2-4 weeks so the ground recovers (~0.25-0.5 acre total).',
             'Birds return to the coop at dusk; the auto door closes at civil dusk (sun -6 deg) and alerts HA if not closed.',
             'Electric netting keeps out dogs, foxes and coyotes by day. It does NOT stop hawks, so leave shrubs/cover.']
    for i, n in enumerate(notes):
        s.text(40, 800 + i * 18, n, 12, color=MUTED)
    s.save('site-plan.svg')


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(ROOT, 'hardware', 'pinmap.yaml'), encoding='utf-8') as f:
        pm = yaml.safe_load(f)
    for ref in pm['connectors']:
        assert ref in FIELD, f'wiring diagram has no field-device entry for {ref}'
    wiring(pm)
    plumbing()
    floor_plan()
    elevations()
    site_plan()


if __name__ == '__main__':
    main()
