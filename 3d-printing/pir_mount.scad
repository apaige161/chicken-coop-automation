// HC-SR501 PIR sensor housing: holds the 32 x 24 mm board with its 23 mm Fresnel dome
// poking through, and a sloped roof to shed dust and droppings. Mounts on the coop wall
// or ceiling, angled 30 deg down across the roost area.
// Print: PETG, 3 perimeters, 20% infill, back-plate down, no supports.

$fn = 64;
pcb = [32.5, 24.5];
pcb_hole_d = 2.2;       // HC-SR501 mounting holes (28 mm apart on the long axis)
pcb_hole_dx = 28;
dome_d = 23.5;
depth = 22;             // room for the pots, jumper and pins behind the board
wall = 2;
tilt = 30;

outer = [pcb[0] + 2 * wall + 2, pcb[1] + 2 * wall + 2];

module shell() {
    difference() {
        cube([outer[0], outer[1], depth]);
        translate([wall, wall, wall]) cube([outer[0] - 2 * wall, outer[1] - 2 * wall, depth]);
        // dome opening in the front face (the +z face is left open, board sits on ledges)
        translate([outer[0] / 2, outer[1] / 2, -1]) cylinder(d = dome_d, h = wall + 2);
        // wire slot
        translate([outer[0] / 2 - 4, outer[1] - wall - 1, depth - 8]) cube([8, wall + 2, 9]);
    }
    // PCB standoffs
    for (dx = [-pcb_hole_dx / 2, pcb_hole_dx / 2])
        translate([outer[0] / 2 + dx, outer[1] / 2, wall])
            difference() {
                cylinder(d = 5, h = 3);
                cylinder(d = pcb_hole_d - 0.3, h = 4);
            }
}

module wall_wedge() {
    // wedge between the housing back and the wall sets the downward tilt
    hull() {
        cube([outer[0], 0.01, depth]);
        translate([0, 0, 0]) cube([outer[0], outer[1] * sin(tilt), 0.01]);
    }
}

module back_plate() {
    difference() {
        translate([-8, 0, depth]) cube([outer[0] + 16, outer[1], 3]);
        for (x = [-4, outer[0] + 4]) translate([x, outer[1] / 2, depth - 1]) cylinder(d = 4.2, h = 6);
        translate([outer[0] / 2 - 4, outer[1] - wall - 1, depth - 1]) cube([8, wall + 2, 6]);
    }
}

// Housing + integral back plate with screw ears (print as one piece)
shell();
back_plate();
// drip roof
translate([-3, outer[1] - 1, 0]) rotate([-25, 0, 0]) cube([outer[0] + 6, 1.6, depth + 6]);
