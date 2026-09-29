// Mounting back-plate for the Coop Controller PCB (170 x 105 mm, M3 holes 4 mm in from
// each corner) inside an IP65 ABS/polycarbonate junction box, 250 x 200 mm or larger.
// Standoffs lift the PCB 8 mm. Slots on the plate match most boxes' internal bosses;
// or just drill the plate to suit.
// Print: PETG/ASA, 3 perimeters, 20% infill. Fits a 256 mm bed diagonally if needed.

$fn = 40;

pcb = [170, 105];
hole_inset = 4;
standoff_h = 8;
standoff_d = 7;
m3_pilot = 2.6;          // self-tapping M3, or use a heat-set insert (4.2 mm hole)
plate = [200, 130, 3];
box_boss_pitch = [180, 110];   // mounting slots for the box bosses (adjust to your box)

difference() {
    union() {
        // ribbed plate (lighter than solid)
        difference() {
            cube(plate);
            for (x = [20 : 20 : plate[0] - 20]) for (y = [18 : 20 : plate[1] - 18])
                translate([x, y, -1]) cylinder(d = 12, h = plate[2] + 2, $fn = 6);
        }
        // frame around the cut-outs
        difference() { cube(plate); translate([6, 6, -1]) cube([plate[0] - 12, plate[1] - 12, plate[2] + 2]); }
        // standoffs
        ox = (plate[0] - pcb[0]) / 2; oy = (plate[1] - pcb[1]) / 2;
        for (x = [hole_inset, pcb[0] - hole_inset]) for (y = [hole_inset, pcb[1] - hole_inset])
            translate([ox + x, oy + y, 0]) cylinder(d = standoff_d, h = plate[2] + standoff_h);
    }
    ox = (plate[0] - pcb[0]) / 2; oy = (plate[1] - pcb[1]) / 2;
    for (x = [hole_inset, pcb[0] - hole_inset]) for (y = [hole_inset, pcb[1] - hole_inset])
        translate([ox + x, oy + y, 1]) cylinder(d = m3_pilot, h = plate[2] + standoff_h);
    // box mounting slots
    for (sx = [-1, 1]) for (sy = [-1, 1])
        translate([plate[0] / 2 + sx * box_boss_pitch[0] / 2, plate[1] / 2 + sy * box_boss_pitch[1] / 2, -1])
            hull() { translate([-3, 0, 0]) cylinder(d = 4.5, h = 5); translate([3, 0, 0]) cylinder(d = 4.5, h = 5); }
}
