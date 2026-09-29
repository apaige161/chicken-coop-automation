#!/usr/bin/env bash
# Regenerate the Coop Controller PCB end-to-end and run all checks.
#   design.py -> schematic (+ERC) -> board (placement) -> Freerouting -> DRC -> fab outputs
# Requirements: KiCad 9/10 (kicad-cli + bundled python), Java 21+, Freerouting jar.
# Override tool paths with KICAD_BIN / FREEROUTING_JAR env vars.
set -euo pipefail
cd "$(dirname "$0")"

KICAD_BIN="${KICAD_BIN:-$HOME/AppData/Local/Programs/KiCad/10.0/bin}"
FREEROUTING_JAR="${FREEROUTING_JAR:-$HOME/.tools/freerouting.jar}"
CLI="$KICAD_BIN/kicad-cli"
KPY="$KICAD_BIN/python"
BOARD=coop-controller.kicad_pcb
SCH=coop-controller.kicad_sch

echo "== schematic"
python gen_schematic.py "$SCH"
"$CLI" sch erc --severity-all --exit-code-violations -o erc.rpt "$SCH"

echo "== board placement"
"$KPY" gen_pcb.py "$BOARD"

echo "== autoroute"
"$KPY" route.py "$BOARD" "$FREEROUTING_JAR" 2>&1 | grep -v "memory leak" || true

echo "== DRC (errors + schematic parity)"
"$CLI" pcb drc --severity-error --exit-code-violations --schematic-parity -o drc.rpt "$BOARD"

echo "== fab outputs"
rm -rf fab && mkdir -p fab/gerbers images
"$CLI" pcb export gerbers -o fab/gerbers/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts "$BOARD" >/dev/null
"$CLI" pcb export drill -o fab/gerbers/ --format excellon --excellon-separate-th "$BOARD" >/dev/null
(cd fab/gerbers && python -c "import zipfile,glob;z=zipfile.ZipFile('../coop-controller-gerbers.zip','w',zipfile.ZIP_DEFLATED);[z.write(f) for f in sorted(glob.glob('*'))]")
"$CLI" sch export pdf -o fab/coop-controller-schematic.pdf "$SCH" >/dev/null
"$CLI" pcb render --side top -w 1600 -h 1000 -o images/board-top.png "$BOARD" >/dev/null
"$CLI" pcb render --side bottom -w 1600 -h 1000 -o images/board-bottom.png "$BOARD" >/dev/null
python gen_bom.py fab/bom.csv

echo "== done: fab/coop-controller-gerbers.zip, fab/bom.csv, fab/coop-controller-schematic.pdf"
