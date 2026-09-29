// Louvred radiation shield (mini Stevenson screen) for the BME280 coop sensor. It keeps
// sun, radiant heat from the roof and dust off the sensor while air flows through.
// Stack N plates on 3x M3 threaded rods (or long M3 screws) with printed spacers.
// part = "plate" | "top" | "spacer" | "base" | "all"
// Print: white ASA/PETG (white matters for UV and heat), 2 perimeters, 15% infill.

part = "all";
$fn = 72;

d = 90;            // plate diameter
cone_h = 10;       // louvre drop
t = 1.6;           // plate thickness
hole_d = 22;       // centre opening for air + sensor cable
rod_d = 3.4;
rod_r = 36;
spacer_h = 12;

module rods(h) { for (a = [0, 120, 240]) rotate([0, 0, a]) translate([rod_r, 0, -1]) cylinder(d = rod_d, h = h + 2); }

module louvre(open = true) {
    difference() {
        cylinder(d1 = d, d2 = d - 2 * cone_h, h = cone_h);
        translate([0, 0, -t]) cylinder(d1 = d, d2 = d - 2 * cone_h, h = cone_h);
        if (open) cylinder(d = hole_d, h = cone_h * 3, center = true);
        rods(cone_h);
    }
    // rod bosses
    for (a = [0, 120, 240]) rotate([0, 0, a]) translate([rod_r, 0, 0])
        difference() { cylinder(d = 8, h = 3); cylinder(d = rod_d, h = 7, center = true); }
}

module base_plate() {
    // bottom plate: sensor cradle (BME280 breakout ~ 15 x 12 mm) + wall bracket arm
    difference() {
        union() {
            cylinder(d = d - 10, h = 3);
            translate([-6, -d / 2 - 30, 0]) cube([12, 40, 3]);          // arm
            translate([-15, -d / 2 - 30, 0]) cube([30, 4, 25]);         // wall flange
        }
        rods(3);
        for (z = [8, 18]) translate([-8, -d / 2 - 31, z]) rotate([-90, 0, 0]) cylinder(d = 4.2, h = 6);
        for (z = [8, 18]) translate([8, -d / 2 - 31, z]) rotate([-90, 0, 0]) cylinder(d = 4.2, h = 6);
        // air holes
        for (a = [0 : 45 : 359]) rotate([0, 0, a]) translate([22, 0, -1]) cylinder(d = 8, h = 5);
        cylinder(d = 5, h = 7, center = true);   // cable
    }
    // sensor clip posts
    for (x = [-9, 9]) translate([x, 0, 3]) difference() { cylinder(d = 4, h = 8); cylinder(d = 1.8, h = 9); }
}

module spacer() { difference() { cylinder(d = 7, h = spacer_h); cylinder(d = rod_d, h = spacer_h * 3, center = true); } }

if (part == "plate") louvre(true);
else if (part == "top") louvre(false);
else if (part == "spacer") spacer();
else if (part == "base") base_plate();
else {
    base_plate();
    translate([d + 10, 0, 0]) louvre(true);
    translate([2 * d + 20, 0, 0]) louvre(false);
    translate([0, d + 10, 0]) spacer();
}
