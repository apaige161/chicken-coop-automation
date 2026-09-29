"""Cross-check the GPIO/connector map against the firmware, PCB design and spec.

hardware/pinmap.yaml is the source of truth. This fails (exit 1) if:
  * firmware uses a GPIO that is not in the pin map, or labels it with the wrong signal
  * a pin-mapped signal (other than spares) is not used by the firmware
  * the PCB ESP32 socket pin for a GPIO is not on the net named after its signal
  * a PCB connector's pins differ from the pin map
  * the GPIO table in PROJECT_SPEC.md disagrees with the pin map
  * docs/ha/*.yaml or docs/home-assistant.md reference an entity the firmware doesn't create
  * (if kicad-cli is available) the generated schematic netlist differs from pcb/design.py

Usage:  python tools/check_consistency.py
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pcb'))
import design  # noqa: E402

errors = []


def err(msg):
    errors.append(msg)
    print('  FAIL:', msg)


def load_pinmap():
    with open(os.path.join(ROOT, 'hardware', 'pinmap.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_firmware(pm):
    print('firmware vs pin map')
    by_gpio = {p['gpio']: p['signal'] for p in pm['pins']}
    files = [os.path.join(ROOT, 'firmware', 'coop-controller.yaml')] + \
        sorted(glob.glob(os.path.join(ROOT, 'firmware', 'packages', '*.yaml')))
    used = set()
    pat = re.compile(r'\bGPIO(\d+)\b(?:.*?#\s*([A-Z0-9_]+))?')
    for fn in files:
        with open(fn, encoding='utf-8') as f:
            for n, line in enumerate(f, 1):
                code = line.split('#', 1)[0]
                m = re.search(r'\bGPIO(\d+)\b', code)
                if not m:
                    continue
                gpio = int(m.group(1))
                used.add(gpio)
                rel = os.path.relpath(fn, ROOT)
                if gpio not in by_gpio:
                    err(f'{rel}:{n} uses GPIO{gpio}, which is not in hardware/pinmap.yaml')
                    continue
                full = pat.search(line)
                label = full.group(2) if full else None
                if label is None:
                    err(f'{rel}:{n} GPIO{gpio} has no "# {by_gpio[gpio]}" signal comment')
                elif label != by_gpio[gpio]:
                    err(f'{rel}:{n} GPIO{gpio} labelled {label}, pin map says {by_gpio[gpio]}')
    for p in pm['pins']:
        if p['gpio'] not in used and not p['signal'].startswith('SPARE'):
            err(f"pin map signal {p['signal']} (GPIO{p['gpio']}) is not used by the firmware")


def check_pcb(pm):
    print('PCB design vs pin map')
    parts = {p['ref']: p for p in design.PARTS}
    sockets = [('J20', design.ESP_LEFT), ('J21', design.ESP_RIGHT), ('J22', design.ESP_RIGHT)]
    for p in pm['pins']:
        found = False
        for ref, header in sockets:
            if p['gpio'] in header:
                found = True
                pin = str(header.index(p['gpio']) + 1)
                net = parts[ref]['pins'].get(pin)
                if net != p['signal']:
                    err(f"{ref} pin {pin} (GPIO{p['gpio']}) is on net {net}, expected {p['signal']}")
        if not found:
            err(f"GPIO{p['gpio']} is not on any ESP32 socket")
    for ref, c in pm['connectors'].items():
        if ref not in parts:
            err(f'connector {ref} missing from pcb/design.py')
            continue
        got = [parts[ref]['pins'].get(str(i + 1)) for i in range(len(parts[ref]['pins']))]
        if got != c['pins']:
            err(f"{ref} pins {got} != pin map {c['pins']}")
        if parts[ref]['value'].split('_')[0] != c['name'].split('_')[0]:
            err(f"{ref} named {parts[ref]['value']} on PCB but {c['name']} in pin map")
    # every signal with a connector must appear on that connector (directly or via a divider/LED net)
    via = {'US_ECHO': 'US_ECHO_5V', 'STATUS_LED': 'LED_PANEL',
           'DOOR_OPEN_RLY': 'M+', 'DOOR_CLOSE_RLY': 'M-', 'VALVE_DRV': 'VALVE-',
           'FEEDER_DRV': 'FEEDER-', 'FAN_DRV': 'FAN-', 'LIGHT_SSR': 'LIGHT_SSR-', 'HEAT_SSR': 'HEAT_SSR-'}
    for p in pm['pins']:
        ref = p['connector']
        if ref is None:
            continue
        nets = pm['connectors'][ref]['pins']
        if p['signal'] not in nets and via.get(p['signal']) not in nets:
            err(f"{p['signal']} should reach {ref} but that connector carries {nets}")


def check_spec(pm):
    print('PROJECT_SPEC.md GPIO table vs pin map')
    with open(os.path.join(ROOT, 'PROJECT_SPEC.md'), encoding='utf-8') as f:
        rows = re.findall(r'^\|\s*(\d+)\s*\|\s*([A-Z0-9_]+)\s*\|', f.read(), re.M)
    spec = {int(g): s for g, s in rows}
    pmap = {p['gpio']: p['signal'] for p in pm['pins']}
    if spec != pmap:
        for g in sorted(set(spec) | set(pmap)):
            if spec.get(g) != pmap.get(g):
                err(f'GPIO{g}: spec says {spec.get(g)}, pin map says {pmap.get(g)}')


def _slug(s):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', s.lower())).strip('_')


def check_ha_entities():
    print('Home Assistant YAML/docs entity IDs vs firmware entity names')
    names = set()
    for fn in glob.glob(os.path.join(ROOT, 'firmware', '**', '*.yaml'), recursive=True):
        with open(fn, encoding='utf-8') as f:
            for m in re.finditer(r'^\s*-?\s*name:\s*"?([^"\n#]+?)"?\s*$', f.read(), re.M):
                names.add('coop_' + _slug(m.group(1)))
    files = glob.glob(os.path.join(ROOT, 'docs', 'ha', '*.yaml')) + [os.path.join(ROOT, 'docs', 'home-assistant.md')]
    pat = re.compile(r'\b(?:cover|switch|sensor|binary_sensor|button|number)\.(coop_[a-z0-9_]+)')
    for fn in files:
        with open(fn, encoding='utf-8') as f:
            text = f.read()
        for m in pat.finditer(text):
            ent = m.group(1).rstrip('_')
            if ent not in names:
                err(f'{os.path.relpath(fn, ROOT)} references {m.group(0)}, which no firmware entity produces')


def check_schematic_netlist():
    cli = shutil.which('kicad-cli') or os.path.expanduser(
        r'~\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe')
    sch = os.path.join(ROOT, 'pcb', 'coop-controller.kicad_sch')
    if not os.path.exists(cli) or not os.path.exists(sch):
        print('schematic netlist: skipped (kicad-cli or schematic not found)')
        return
    print('schematic netlist vs pcb/design.py')
    import sexpr
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'n.net')
        subprocess.run([cli, 'sch', 'export', 'netlist', '-o', out, sch], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(out, encoding='utf-8') as f:
            tree = sexpr.parse(f.read())
    got = {}
    for n in sexpr.find(sexpr.find1(tree, 'nets'), 'net'):
        name = sexpr.find1(n, 'name')[1].lstrip('/')
        for nd in sexpr.find(n, 'node'):
            ref = sexpr.find1(nd, 'ref')[1]
            if not ref.startswith('#'):
                got[(ref, sexpr.find1(nd, 'pin')[1])] = name
    for p in design.PARTS:
        for pin, net in p['pins'].items():
            if net and got.get((p['ref'], pin)) != net:
                err(f"schematic {p['ref']}.{pin} on {got.get((p['ref'], pin))}, design says {net}")


def main():
    pm = load_pinmap()
    check_firmware(pm)
    check_pcb(pm)
    check_spec(pm)
    check_ha_entities()
    check_schematic_netlist()
    if errors:
        print(f'\n{len(errors)} consistency error(s)')
        sys.exit(1)
    print('\nOK: pin map, firmware, PCB and spec are consistent')


if __name__ == '__main__':
    main()
