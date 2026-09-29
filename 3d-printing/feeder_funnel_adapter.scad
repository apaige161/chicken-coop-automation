// Feeder hopper -> auger tube funnel adapter.
// Bolts under a hole cut in the bottom of a 32 gal hopper (trash can / barrel) and funnels
// feed into a 2" Sch-40 PVC socket (the auger tube). The steep wall stops pellets and
// crumble from bridging.
// Print: PETG, 4 perimeters, 30% gyroid, no supports (prints upright, funnel up).

$fn = 96;

flange_d      = 170;   // flange that sits under the hopper floor
flange_t      = 5;
funnel_top_d  = 140;   // matches the hole you cut in the hopper (cut 140 mm)
wall          = 3;
funnel_h      = 70;    // ~60 deg walls. Keep >= 55 deg so feed doesn't bridge
pipe_od       = 60.3;  // 2" Sch-40 PVC OD
socket_clear  = 0.6;   // diametral clearance. PVC-cement or silicone into place
socket_depth  = 35;
bolt_d        = 5.5;   // M5 / #10 bolts through the hopper floor
bolt_n        = 6;
bolt_circle   = 155;

socket_id = pipe_od + socket_clear;

module funnel_solid() {
    union() {
        cylinder(d = flange_d, h = flange_t);
        translate([0, 0, -funnel_h])
            cylinder(d1 = socket_id + 2 * wall, d2 = funnel_top_d + 2 * wall, h = funnel_h);
        translate([0, 0, -funnel_h - socket_depth])
            cylinder(d = socket_id + 2 * wall, h = socket_depth + 0.01);
    }
}

module funnel_void() {
    translate([0, 0, -0.01]) cylinder(d = funnel_top_d, h = flange_t + 0.02);
    translate([0, 0, -funnel_h])
        cylinder(d1 = socket_id - 8, d2 = funnel_top_d, h = funnel_h + 0.02);
    // pipe socket with a 4 mm internal stop lip
    translate([0, 0, -funnel_h - socket_depth - 0.01])
        cylinder(d = socket_id, h = socket_depth - 0.01);
}

difference() {
    funnel_solid();
    funnel_void();
    for (i = [0 : bolt_n - 1])
        rotate([0, 0, i * 360 / bolt_n])
            translate([bolt_circle / 2, 0, -1]) cylinder(d = bolt_d, h = flange_t + 2);
}
