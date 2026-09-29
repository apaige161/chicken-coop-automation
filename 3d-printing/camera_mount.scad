// ESP32-CAM (AI-Thinker, 27 x 40.5 mm) weather hood + tilting wall mount.
// part = "case" | "lid" | "bracket" | "all" (layout for preview)
// Print: PETG or ASA (UV), 3 perimeters, 20% infill. Case prints lens-side down.
// Hardware: 2x M3x12 + nuts (lid), 1x M4x20 + nyloc (tilt pivot), 2x wood screws (bracket).

part = "all";
$fn = 48;

board = [27.2, 40.7];    // ESP32-CAM PCB + clearance
board_t = 12;            // PCB + camera + ESP32 shield + headers
wall = 2.2;
lens_d = 9;              // OV2640 lens barrel clearance
lens_y = 40.7 - 10.5;    // lens centre from the bottom edge of the PCB (antenna end up)
hood = 12;               // rain hood over the lens
cable_d = 6;             // USB/5 V cable gland hole

inner = [board[0] + 1, board[1] + 1, board_t];
outer = [inner[0] + 2 * wall, inner[1] + 2 * wall, inner[2] + wall];

module case_body() {
    difference() {
        union() {
            cube(outer);
            // rain hood above the lens
            translate([0, lens_y + wall + lens_d / 2 + 1, 0])
                difference() {
                    translate([0, 0, -hood]) cube([outer[0], wall, hood]);
                }
            // pivot ear
            translate([outer[0] / 2 - 5, outer[1] - 4, outer[2]])
                difference() {
                    cube([10, 4, 12]);
                    translate([5, -1, 7]) rotate([-90, 0, 0]) cylinder(d = 4.3, h = 6);
                }
        }
        translate([wall, wall, wall]) cube([inner[0], inner[1], inner[2] + 1]);
        // lens window
        translate([outer[0] / 2, wall + lens_y, -1]) cylinder(d = lens_d, h = wall + 2);
        // cable hole at the bottom (drip loop exits downward)
        translate([outer[0] / 2, -1, wall + inner[2] / 2]) rotate([-90, 0, 0]) cylinder(d = cable_d, h = wall + 2);
        // lid screw holes
        for (x = [wall / 2 + 0.2, outer[0] - wall / 2 - 0.2])
            translate([x, outer[1] / 2, outer[2] - 8]) cylinder(d = 2.5, h = 9);
        // flash LED window (GPIO4 LED sits ~ lens_y - 16)
        translate([outer[0] / 2 + 6, wall + lens_y - 16, -1]) cylinder(d = 5, h = wall + 2);
    }
}

module lid() {
    difference() {
        union() {
            cube([outer[0], outer[1], 2]);
            translate([wall + 0.3, wall + 0.3, 2]) cube([inner[0] - 0.6, inner[1] - 0.6, 2]);
        }
        for (x = [wall / 2 + 0.2, outer[0] - wall / 2 - 0.2])
            translate([x, outer[1] / 2, -1]) cylinder(d = 3.3, h = 6);
    }
}

module bracket() {
    difference() {
        union() {
            cube([30, 4, 40]);                           // wall plate
            translate([10, 0, 30]) cube([10, 22, 4]);     // arm
            translate([10, 18, 30]) cube([2.5, 4, 16]);   // fork cheek
            translate([17.5, 18, 30]) cube([2.5, 4, 16]);
        }
        for (z = [8, 24]) translate([15, -1, z]) rotate([-90, 0, 0]) cylinder(d = 4.5, h = 6);
        translate([5, 20, 41]) rotate([0, 90, 0]) cylinder(d = 4.3, h = 20);
    }
}

if (part == "case") case_body();
else if (part == "lid") lid();
else if (part == "bracket") bracket();
else {
    case_body();
    translate([outer[0] + 10, 0, 0]) lid();
    translate([2 * outer[0] + 20, 0, 0]) bracket();
}
