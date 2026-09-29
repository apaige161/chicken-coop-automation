// Adjustable bracket for the pop-door position reed switches (J3: DOOR_CLOSED_SW,
// DOOR_OPEN_SW). Holds a standard surface-mount reed switch (~27 x 14 x 8 mm body)
// on the door frame. The slotted holes let you fine-tune where it trips. The matching
// magnet holder screws to the door leaf.
// part = "switch" | "magnet" | "all".  Print: PETG, 100% infill (small parts).

part = "all";
$fn = 40;

sw = [28, 14.5, 8.5];     // reed switch body + clearance
magnet = [28, 14.5, 8.5]; // matching magnet body (same housing in most kits)
wall = 2;
slot_len = 12;            // adjustment travel
screw_d = 4.2;

module slotted_plate(len) {
    difference() {
        cube([len, 24, 3]);
        for (x = [6, len - 6]) hull() {
            translate([x, 4, -1]) cylinder(d = screw_d, h = 5);
            translate([x, 4 + slot_len / 2, -1]) cylinder(d = screw_d, h = 5);
        }
    }
}

module cradle(body) {
    difference() {
        cube([body[0] + 2 * wall, body[1] + 2 * wall, body[2] + wall]);
        translate([wall, wall, wall]) cube([body[0], body[1], body[2] + 1]);
        // zip-tie slots
        for (x = [wall + 5, body[0] + wall - 8]) translate([x, -1, wall + 1]) cube([3, body[1] + 2 * wall + 2, 1.8]);
        // cable exit
        translate([-1, wall + body[1] / 2 - 2.5, wall + 1]) cube([wall + 2, 5, body[2]]);
    }
}

module switch_bracket() {
    slotted_plate(sw[0] + 2 * wall + 16);
    translate([8, 24 - (sw[1] + 2 * wall), 3]) cradle(sw);
}

module magnet_holder() {
    difference() {
        union() {
            cube([magnet[0] + 2 * wall + 16, magnet[1] + 2 * wall, 3]);
            translate([8, 0, 3]) cradle(magnet);
        }
        for (x = [4, magnet[0] + 2 * wall + 12]) translate([x, (magnet[1] + 2 * wall) / 2, -1]) cylinder(d = screw_d, h = 5);
    }
}

if (part == "switch") switch_bracket();
else if (part == "magnet") magnet_holder();
else { switch_bracket(); translate([0, 34, 0]) magnet_holder(); }
