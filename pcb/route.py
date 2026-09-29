"""Autoroute coop-controller.kicad_pcb with Freerouting, then pour the ground planes.

Run with KiCad's python:  python route.py [board] [freerouting.jar]
Needs Java 21+ and the Freerouting jar (https://github.com/freerouting/freerouting).
Freerouting is not deterministic, so this retries until every connection is routed.
"""
import os
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_ATTEMPTS = 8


def route_once(board_path, jar):
    board = pcbnew.LoadBoard(board_path)
    for t in list(board.GetTracks()):
        board.Remove(t)
    dsn = os.path.splitext(board_path)[0] + '.dsn'
    ses = os.path.splitext(board_path)[0] + '.ses'
    # Hide copper pours during export so Freerouting routes GND with real tracks
    # (otherwise it assumes the plane connects everything and leaves islands).
    zones = [board.GetArea(i) for i in range(board.GetAreaCount())]
    pours = [z for z in zones if not z.GetIsRuleArea()]
    for z in pours:
        board.Remove(z)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit('DSN export failed')
    for z in pours:
        board.Add(z)
    cmd = ['java', '-jar', jar, '-de', dsn, '-do', ses, '-mp', '100', '--gui.enabled=false']
    subprocess.run(cmd, check=True, cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not pcbnew.ImportSpecctraSES(board, ses):
        raise SystemExit('SES import failed')
    for f in (dsn, ses):
        if os.path.exists(f):
            os.remove(f)
    board.BuildConnectivity()
    return board, board.GetConnectivity().GetUnconnectedCount(False)


def main(board_path, jar):
    with open(board_path, encoding='utf-8') as f:
        pristine = f.read()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        with open(board_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(pristine)
        board, unrouted = route_once(board_path, jar)
        print(f'attempt {attempt}: {unrouted} unrouted connection(s)', flush=True)
        if unrouted == 0:
            break
    else:
        raise SystemExit('could not fully route after %d attempts' % MAX_ATTEMPTS)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(board_path)
    print('routed + zones filled ->', board_path)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'coop-controller.kicad_pcb'),
         sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/.tools/freerouting.jar'))
