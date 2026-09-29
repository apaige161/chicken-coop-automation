"""Generate coop-controller.kicad_pcb from design.py (run with KiCad's bundled python).

Places footprints, assigns nets, sets net classes, draws the outline, adds the antenna
keep-out and ground pours. Routing is done afterwards by route.py (Freerouting).
"""
import json
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402
from gen_schematic import uid, KICAD_SHARE  # noqa: E402

OX, OY = 50.0, 50.0   # board origin on the KiCad page (mm)
MM = pcbnew.FromMM


def pt(x, y):
    return pcbnew.VECTOR2I(MM(OX + x), MM(OY + y))


def write_project(path):
    """Minimal .kicad_pro carrying design rules + net classes."""
    pro = {
        "board": {"design_settings": {
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2},
            "rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.6,
                      "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.5,
                      "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25},
            "track_widths": [0.0, 0.4, 1.0, 1.5], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}],
        }},
        "meta": {"filename": os.path.basename(path), "version": 3},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.8,
                 "via_drill": 0.4, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
                 "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647},
                {"name": "Power", "clearance": 0.3, "track_width": 1.5, "via_diameter": 1.2,
                 "via_drill": 0.6, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
                 "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 0},
            ],
            "meta": {"version": 4},
            "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in design.POWER_NETS],
        },
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[uid('root'), "Root"]],
    }
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pro, f, indent=2)


def load_fp(fpid):
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(KICAD_SHARE, 'footprints', lib + '.pretty'), name)
    if fp is None:
        raise RuntimeError('footprint not found: ' + fpid)
    return fp


def add_line(board, a, b, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(a)
    s.SetEnd(b)
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    board.Add(s)


def rect_outline(x1, y1, x2, y2):
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]:
        chain.Append(pt(x, y))
    chain.SetClosed(True)
    return chain


def add_zone(board, net, layer, x1, y1, x2, y2, priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.Outline().AddOutline(rect_outline(x1, y1, x2, y2))
    z.SetLocalClearance(MM(0.4))
    z.SetMinThickness(MM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)   # solid: robust on a 2-layer THT board
    z.SetThermalReliefGap(MM(0.5))
    z.SetThermalReliefSpokeWidth(MM(0.6))
    z.SetAssignedPriority(priority)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)
    return z


def add_keepout(board, x1, y1, x2, y2):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.SetZoneName('ESP32 antenna keep-out')
    z.Outline().AddOutline(rect_outline(x1, y1, x2, y2))
    board.Add(z)


def add_text(board, text, x, y, size=1.5, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    board.Add(t)


def main(out):
    pro = os.path.splitext(out)[0] + '.kicad_pro'
    write_project(pro)
    board = pcbnew.NewBoard(out)

    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for p in design.PARTS:
        fp = load_fp(p['footprint'])
        fp.SetReference(p['ref'])
        fp.SetValue(p['value'])
        if p['group'] == 'mech':
            fp.Reference().SetVisible(False)
        fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', p['ref'])))
        fp.SetOrientationDegrees(p['rot'])
        fp.SetPosition(pt(*p['pos']))
        if p['ref'] == 'J22':
            # J21/J22 are alternative sockets sharing space by design: drop J22's courtyard.
            for item in list(fp.GraphicalItems()):
                if item.GetLayer() == pcbnew.F_CrtYd:
                    fp.Remove(item)
            fp.SetAllowMissingCourtyard(True)
        for pad in fp.Pads():
            n = p['pins'].get(pad.GetNumber())
            if n:
                pad.SetNet(net(n))
        board.Add(fp)

    # Outline
    w, h = design.BOARD_W, design.BOARD_H
    for a, b in [((0, 0), (w, 0)), ((w, 0), (w, h)), ((w, h), (0, h)), ((0, h), (0, 0))]:
        add_line(board, pt(*a), pt(*b))

    add_keepout(board, *design.ANTENNA_KEEPOUT)

    # Ground pour on both layers (filled after routing).
    add_zone(board, net('GND'), pcbnew.B_Cu, 0.5, 0.5, w - 0.5, h - 0.5)
    add_zone(board, net('GND'), pcbnew.F_Cu, 0.5, 0.5, w - 0.5, h - 0.5)

    add_text(board, 'COOP CONTROLLER v1.0', 62, 83, 2.0)
    add_text(board, '12V DC ONLY - NO MAINS ON THIS BOARD', 62, 86.5, 1.2)
    add_text(board, 'ESP32 ANTENNA - NO COPPER', 58, 21, 1.2)
    add_text(board, 'Fit J21 (25.4mm) OR J22 (22.86mm clone)', 62, 89, 1.0)

    board.Save(out)
    print(f'placed {len(design.PARTS)} footprints, {len(nets)} nets -> {out}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'coop-controller.kicad_pcb')
