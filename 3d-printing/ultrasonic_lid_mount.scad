// JSN-SR04T waterproof ultrasonic probe mount for the feed hopper lid. It holds the probe
// vertical, pointing down at the feed, with a drip skirt so condensation runs off the
// face. Clamp ring + gasket groove seal the lid hole.
// Print: PETG, 4 perimeters, 40% infill.

$fn = 80;

probe_d = 22.6;       // JSN-SR04T transducer housing diameter (measure yours)
probe_len = 17;       // grip length
lid_hole_d = 32;      // hole saw size for the lid
flange_d = 55;
flange_t = 4;
nut_d = 45;           // clamp ring on the underside
nut_t = 5;
screw_d = 3.4;        // 3x M3 clamp screws
screw_r = 21;

module body() {
    difference() {
        union() {
            cylinder(d = flange_d, h = flange_t);
            translate([0, 0, -probe_len]) cylinder(d = lid_hole_d - 0.8, h = probe_len);
        }
        translate([0, 0, -probe_len - 1]) cylinder(d = probe_d, h = probe_len + flange_t + 2);
        // o-ring / silicone groove on the flange underside
        translate([0, 0, -0.01]) difference() { cylinder(d = 44, h = 1.2); cylinder(d = 38, h = 1.3); }
        for (a = [0, 120, 240]) rotate([0, 0, a]) translate([screw_r, 0, -1]) cylinder(d = screw_d, h = flange_t + 2);
        // gentle squeeze slits so the probe is gripped
        for (a = [0, 90, 180, 270]) rotate([0, 0, a]) translate([-0.75, probe_d / 2 - 1, -probe_len - 1]) cube([1.5, 4, probe_len - 3]);
    }
}

module clamp_ring() {
    translate([flange_d + 10, 0, 0]) difference() {
        cylinder(d = nut_d + 10, h = nut_t);
        translate([0, 0, -1]) cylinder(d = lid_hole_d, h = nut_t + 2);
        for (a = [0, 120, 240]) rotate([0, 0, a]) translate([screw_r, 0, -1]) cylinder(d = screw_d - 0.5, h = nut_t + 2);
    }
}

translate([0, 0, probe_len]) body();
clamp_ring();
