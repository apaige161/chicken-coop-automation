// Vented, peck-proof case for a Xiaomi LYWSD03MMC BLE thermometer (pvvx firmware), for
// the nest-box row or brooder. Slots let air through but are narrow enough to stop
// beaks, and a keyhole on the back hangs it on a screw.
// Print: PETG, 3 perimeters, 20% infill, no supports. Snap lid.

part = "all";   // "base" | "lid" | "all"
$fn = 48;

sensor = [43.5, 43.5, 13.5];   // LYWSD03MMC body + clearance
wall = 2;
slot_w = 2.5;
slot_pitch = 6;
inner = sensor;
outer = [inner[0] + 2 * wall, inner[1] + 2 * wall, inner[2] + wall];

module vents(len, n) {
    for (i = [0 : n - 1]) translate([i * slot_pitch, 0, 0]) cube([slot_w, len, 50]);
}

module base() {
    difference() {
        cube(outer);
        translate([wall, wall, wall]) cube([inner[0], inner[1], inner[2] + 1]);
        // side vent slots (all four walls)
        n = floor((inner[0] - 6) / slot_pitch);
        for (r = [0, 90, 180, 270])
            translate([outer[0] / 2, outer[1] / 2, 0]) rotate([0, 0, r])
                translate([-n * slot_pitch / 2, outer[1] / 2 - wall - 1, wall + 3])
                    vents(wall + 2, n);
        // keyhole on the back (floor)
        translate([outer[0] / 2, outer[1] * 0.7, -1]) cylinder(d = 8, h = wall + 2);
        translate([outer[0] / 2 - 2, outer[1] * 0.45, -1]) cube([4, outer[1] * 0.25, wall + 2]);
        // snap grooves
        for (y = [wall + 0.01, outer[1] - wall - 0.8])
            translate([wall, y, outer[2] - 3]) cube([inner[0], 0.8, 1.2]);
    }
}

module lid() {
    difference() {
        union() {
            cube([outer[0], outer[1], 1.6]);
            translate([wall + 0.25, wall + 0.25, 1.6]) difference() {
                cube([inner[0] - 0.5, inner[1] - 0.5, 4]);
                translate([1.6, 1.6, -1]) cube([inner[0] - 3.7, inner[1] - 3.7, 6]);
            }
            // snap bumps
            for (y = [wall + 0.25 - 0.6, outer[1] - wall - 0.25])
                translate([wall + 4, y, 3.4]) cube([inner[0] - 8, 0.6, 1]);
        }
        // viewing window so the display is readable
        translate([outer[0] / 2 - 14, outer[1] / 2 - 11, -1]) cube([28, 22, 4]);
    }
}

if (part == "base") base();
else if (part == "lid") lid();
else { base(); translate([outer[0] + 8, 0, 0]) lid(); }
