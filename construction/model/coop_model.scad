// Illustrative 3D model of the 50-bird coop (inches). Used only to render the pictures in
// construction/renders/ (see render.sh). It's a visual aid; construction/coop-build-plan.md
// is the authority for dimensions.
//
// Axes: x = east (0..240 along the 20 ft south wall), y = north (0..120), z = up.
// view = "exterior" | "service_open" | "interior" | "nest_open" | "overview"

view = "exterior";
$fn = 36;

L = 240; D = 120; T = 4;        // footprint, wall thickness
FZ = 12;                         // top of floor above grade
WH = 97;                         // wall height (8'-1")
RISE = 20;                       // 4/12 over 60"
EAVE = FZ + WH;
RZ = EAVE + RISE + 5;            // top of roof at the ridge

C_SIDING = [0.80, 0.62, 0.42];
C_TRIM   = [0.95, 0.94, 0.90];
C_ROOF   = [0.38, 0.45, 0.47];
C_FRAME  = [0.62, 0.47, 0.30];
C_MESH   = [0.45, 0.45, 0.45, 0.35];
C_GROUND = [0.52, 0.68, 0.38];
C_GRAVEL = [0.62, 0.60, 0.56];
C_WATER  = [0.25, 0.52, 0.85, 0.85];
C_DRUM   = [0.15, 0.35, 0.75];
C_FEED   = [0.86, 0.70, 0.36];
C_METAL  = [0.72, 0.74, 0.76];
C_PVC    = [0.93, 0.93, 0.93];
C_BRASS  = [0.80, 0.65, 0.25];
C_ELEC_M = [0.95, 0.80, 0.30];
C_ELEC_C = [0.55, 0.72, 0.95];
C_HEN    = [0.60, 0.33, 0.15];
C_LITTER = [0.93, 0.85, 0.62];

// service station on the east wall (north end)
SS_Y0 = 54; SS_W = 60; SS_D = 30; SS_H = 72;
BIN_Y0 = SS_Y0 + 3; BIN_W = 24;          // feed bin (inside the station)
DRUM_Y = SS_Y0 + 44;                      // drum centre (y)
OUTLET_Z = FZ + 12;                       // bin outlet / trough rim height

inside     = view == "interior" || view == "interior_close";
show_roof  = !inside;
show_south = !inside;
doors_open = view == "service_open";
lid_open   = view == "nest_open";

// ------------------------------------------------------------------ helpers
module box(p, s, c) { color(c) translate(p) cube(s); }
module mesh_panel(p, s) { color(C_MESH) translate(p) cube(s); }

module hen(p, a = 0) {
    color(C_HEN) translate(p) rotate([0, 0, a]) {
        scale([1.4, 0.8, 0.9]) sphere(r = 5);
        translate([6, 0, 4]) sphere(r = 2.6);
        color([0.85, 0.1, 0.1]) translate([7, 0, 7]) scale([0.6, 0.2, 0.6]) sphere(r = 2);
        color([0.95, 0.75, 0.2]) translate([8.8, 0, 4]) rotate([0, 90, 0]) cylinder(r1 = 0.8, r2 = 0, h = 1.6);
        translate([-6, 0, 3]) rotate([0, -40, 0]) scale([1, 0.5, 1.4]) sphere(r = 3);
    }
}

// ------------------------------------------------------------------ site
module ground() {
    color(C_GROUND) translate([-420, -420, -1]) cube([1200, 900, 1]);
    color(C_GRAVEL) translate([-12, -12, -0.5]) cube([L + 24 + SS_D, D + 24, 0.6]);
}

// ------------------------------------------------------------------ coop shell
module floor_platform() {
    for (y = [0, 57, 114]) box([0, y, 0], [L, 6, 5.5], C_FRAME);           // skids
    box([0, 0, 5.5], [L, D, FZ - 5.5], C_FRAME);                             // joists + deck
    mesh_panel([-0.5, -0.5, 0], [L + 1, 0.6, FZ]);                           // hardware-cloth skirt
}

module wall_openings() {
    for (x = [36, 90, 138]) translate([x, -1, FZ + 36]) cube([24, T + 2, 36]);   // south windows
    translate([186, -1, FZ + 8]) cube([12, T + 2, 16]);                          // pop door
    translate([-1, 48, FZ + 36]) cube([T + 2, 24, 36]);                          // west window
    translate([L - T - 1, 9.6, FZ]) cube([T + 2, 36, 80]);                       // people door
    translate([78, D - T - 1, FZ + 20]) cube([156, T + 2, 14]);                  // nest openings
    translate([L - T - 1, BIN_Y0 + 3, OUTLET_Z - 4]) cube([T + 2, 18, 5]);        // feed outlet slot
}

module walls() {
    color(C_SIDING) difference() {
        union() {
            translate([0, 0, FZ]) cube([L, D, WH]);
            // gable ends
            for (x = [0, L - T]) translate([x, 0, 0]) rotate([90, 0, 90])
                linear_extrude(T) polygon([[0, EAVE], [D, EAVE], [D / 2, EAVE + RISE]]);
        }
        translate([T, T, FZ - 1]) cube([L - 2 * T, D - 2 * T, WH + RISE + 2]);
        wall_openings();
        if (!show_south) translate([-1, -1, FZ + 0.1]) cube([L + 2, T + 1.01, WH + 30]);
        // gable vents
        for (x = [-1, L - T - 1]) translate([x, D / 2 - 10, EAVE + 2]) cube([T + 2, 20, 8]);
    }
    // hardware cloth in openings + trim
    if (show_south) {
        for (x = [36, 90, 138]) {
            mesh_panel([x, 1.5, FZ + 36], [24, 0.4, 36]);
            color(C_TRIM) difference() {
                translate([x - 2, -0.6, FZ + 34]) cube([28, 0.8, 40]);
                translate([x, -1, FZ + 36]) cube([24, 2, 36]);
            }
            // hinged storm shutter propped open above the window
            color(C_SIDING * 0.9) translate([x - 1, -0.6, FZ + 73]) rotate([-60, 0, 0]) cube([26, 0.75, 20]);
        }
    }
    mesh_panel([1.5, 48, FZ + 36], [0.4, 24, 36]);
    // corner boards
    for (p = [[-0.5, -0.5], [L - 3, -0.5], [-0.5, D - 3], [L - 3, D - 3]])
        box([p[0], p[1], FZ], [3.5, 3.5, WH], C_TRIM);
    // people door (closed)
    box([L - 0.6, 9.6, FZ], [1.2, 36, 80], C_SIDING * 0.92);
    color(C_METAL) for (z = [FZ + 10, FZ + 40, FZ + 70]) translate([L + 0.6, 10, z]) cube([0.3, 10, 1.2]);
    // soffit vent strip
    for (y = show_south ? [-0.4, D - 0.2] : [D - 0.2]) mesh_panel([0, y, EAVE - 5], [L, 0.6, 5]);
}

module roof() {
    for (side = [0, 1]) color(C_ROOF)
        hull() {
            translate([-12, D / 2 - 0.1, RZ]) cube([L + 24, 0.2, 1.2]);
            translate([-12, side == 0 ? -12 : D + 12 - 0.2, RZ - 72 * RISE / 60]) cube([L + 24, 0.2, 1.2]);
        }
    // ribs
    for (side = [0, 1]) for (x = [-12 : 9 : L + 12]) color(C_ROOF * 0.85)
        hull() {
            translate([x, D / 2 - 0.1, RZ + 1]) cube([0.8, 0.2, 0.8]);
            translate([x, side == 0 ? -12 : D + 12 - 0.2, RZ + 1 - 72 * RISE / 60]) cube([0.8, 0.2, 0.8]);
        }
    color(C_METAL) translate([-12, D / 2 - 5, RZ + 1]) cube([L + 24, 10, 1.5]);   // vented ridge cap
}

// ------------------------------------------------------------------ nest bay (north)
module nest_bay() {
    y0 = D;
    color(C_SIDING * 0.95) difference() {
        translate([76, y0, FZ + 18]) cube([160, 16, 18]);
        translate([78, y0 - 1, FZ + 20]) cube([156, 16, 20]);
    }
    for (i = [0 : 12]) box([78 + i * 13 - 0.25, y0, FZ + 20], [0.5, 15, 14], C_SIDING * 0.9);
    // brackets
    for (x = [80, 156, 232]) color(C_FRAME) translate([x, y0, FZ + 18]) rotate([90, 0, 90])
        linear_extrude(2) polygon([[0, 0], [15, 0], [0, -14]]);
    // lid (hinged on the wall)
    color(C_ROOF) translate([76, y0, FZ + 36])
        rotate([lid_open ? 80 : -7, 0, 0]) cube([160, 18, 1.2]);
    if (lid_open) for (i = [0 : 11]) {
        color([0.95, 0.9, 0.75]) translate([80 + i * 13, y0 + 2, FZ + 20.5]) cube([10, 12, 2]);
        if (i % 3 == 0) color([0.97, 0.94, 0.88]) translate([85 + i * 13, y0 + 8, FZ + 23.5]) scale([1, 0.8, 0.8]) sphere(r = 1.4);
    }
}

// ------------------------------------------------------------------ pop door + ramp
module pop_door() {
    z0 = FZ + 8;
    open_h = view == "nest_open" ? 0 : 17;
    // tracks (inside face)
    for (x = [184.5, 198]) box([x, T, z0 - 1], [1.5, 1.5, 36], C_METAL);
    // leaf
    box([185.5, T + 0.2, z0 + open_h], [13, 0.6, 18], [0.95, 0.95, 0.95]);
    // actuator (vertical, above the opening)
    color([0.25, 0.25, 0.28]) translate([192, T + 3, z0 + open_h + 18]) cylinder(d = 2.2, h = 24 - open_h);
    color([0.25, 0.25, 0.28]) translate([192, T + 3, z0 + 40]) cylinder(d = 3.2, h = 22);
    color([0.8, 0.8, 0.8]) translate([192, T + 3, z0 + open_h + 18 - 2]) cylinder(d = 1.2, h = 22 - open_h);
    // ramp
    color(C_FRAME) translate([186, 0, z0]) rotate([-(90 - 35), 0, 0]) translate([0, -2, -32]) cube([12, 1.5, 32]);
}

// ------------------------------------------------------------------ interior
module interior() {
    color(C_LITTER) translate([T, T, FZ]) cube([L - 2 * T, D - 2 * T, 4]);
    // poop board + roosts (west end)
    box([9.6, T, FZ + 24], [62.4, D - 2 * T, 0.75], [0.85, 0.85, 0.82]);
    for (y = [T, D - T - 1.5]) box([9.6, y, FZ], [2, 1.5, 24], C_FRAME);
    for (i = [0 : 4]) box([15.6 + i * 13.2 - 1.75, T, FZ + 38], [3.5, D - 2 * T, 1.5], C_FRAME);
    for (x = [12, 70]) for (y = [T, D - T - 3.5]) box([x, y, FZ + 24], [1.5, 3.5, 14], C_FRAME);
    // hens on the roosts / floor
    for (p = [[15.6, 25], [15.6, 60], [28.8, 40], [42, 85], [55.2, 30], [68.4, 70]]) hen([p[0], p[1], FZ + 44], 90);
    for (p = [[120, 40, 0], [150, 55, 60], [200, 72, 180], [205, 60, 200], [135, 75, 20], [100, 30, 250]])
        hen([p[0], p[1], FZ + 9], p[2]);
    // indoor feed trough fed through the wall from the exterior bin
    trough();
    // nipple drinker line: through the east wall at y = 99, west to x = 180, south to y = 70, west to x = 120
    color(C_PVC) {
        translate([180, 99, FZ + 14]) rotate([0, 90, 0]) cylinder(d = 1.05, h = L - T - 180 + 2);
        translate([180, 70, FZ + 14]) rotate([-90, 0, 0]) cylinder(d = 1.05, h = 29);
        translate([120, 70, FZ + 14]) rotate([0, 90, 0]) cylinder(d = 1.05, h = 60);
        for (x = [125 : 12 : 175]) color([0.9, 0.2, 0.2]) translate([x, 70, FZ + 12.2]) cylinder(d = 0.6, h = 1.4);
        for (x = [188 : 12 : 230]) color([0.9, 0.2, 0.2]) translate([x, 99, FZ + 12.2]) cylinder(d = 0.6, h = 1.4);
    }
    // controller + mains boxes, east wall, north end, 5 ft up
    box([L - T - 5, 96, FZ + 56], [5, 16, 12], C_ELEC_M);
    box([L - T - 4.5, 78, FZ + 56], [4.5, 14, 10], C_ELEC_C);
    color([0.4, 0.4, 0.4]) translate([L - T - 2, 88, FZ + 20]) cylinder(d = 1, h = 36);  // conduit
    // lights
    for (x = [72, 168]) color([1, 0.95, 0.7]) translate([x, 60, EAVE - 6]) sphere(r = 2.5);
    // PIR over the roosts
    box([80, 58, EAVE - 8], [3, 4, 3], [0.95, 0.95, 0.95]);
}

module trough() {
    x0 = L - T - 14;
    color(C_METAL) difference() {
        translate([x0, BIN_Y0 + 1, FZ + 2]) cube([14, 22, OUTLET_Z - FZ - 2]);
        translate([x0 + 1, BIN_Y0 + 2, FZ + 5]) cube([12.5, 20, 20]);
    }
    color(C_FEED) translate([x0 + 1, BIN_Y0 + 2, FZ + 5]) cube([12.5, 20, OUTLET_Z - FZ - 8]);
    // anti-waste wire grill
    color([0.3, 0.3, 0.3]) for (y = [BIN_Y0 + 3 : 2.5 : BIN_Y0 + 22]) translate([x0 + 1, y, OUTLET_Z - 0.5]) cube([12.5, 0.3, 0.3]);
}

// ------------------------------------------------------------------ exterior feed + water service station
module service_station() {
    x0 = L; y0 = SS_Y0;
    // base blocks
    for (y = [y0 + 2, y0 + SS_W - 10]) box([x0 + 2, y, 0], [26, 8, FZ], [0.6, 0.6, 0.6]);
    // shell (back = coop wall), insulated
    color(C_SIDING) difference() {
        translate([x0, y0, FZ - 2]) cube([SS_D, SS_W, SS_H]);
        translate([x0 - 1, y0 + 1.5, FZ]) cube([SS_D - 0.5, SS_W - 3, SS_H - 4]);
        translate([x0 + SS_D - 2, y0 + 1.5, FZ]) cube([3, SS_W - 3, SS_H - 4]);   // door opening
        if (doors_open) translate([x0 + 0.5, y0 - 1, FZ - 3]) cube([SS_D, 3, SS_H + 2]);   // cut-away side
    }
    // lean-to roof
    color(C_ROOF) hull() {
        translate([x0 - 1, y0 - 3, FZ + SS_H + 8]) cube([1, SS_W + 6, 1]);
        translate([x0 + SS_D + 4, y0 - 3, FZ + SS_H - 4]) cube([1, SS_W + 6, 1]);
    }
    // two doors on the east face
    for (i = [0, 1]) {
        hy = i == 0 ? y0 + 1.5 : y0 + SS_W - 1.5;
        color(C_SIDING * 0.92) translate([x0 + SS_D, hy, FZ])
            rotate([0, 0, doors_open ? (i == 0 ? -100 : 100) : 0])
                translate([0, i == 0 ? 0 : -(SS_W - 3) / 2, 0]) cube([0.9, (SS_W - 3) / 2, SS_H - 4]);
    }
    if (!doors_open) color(C_METAL) translate([x0 + SS_D + 0.9, y0 + SS_W / 2 - 2, FZ + 36]) cube([0.6, 4, 2]);
    feed_bin();
    water_drum();
}

module feed_bin() {
    x0 = L + 2; x1 = L + SS_D - 3; y0 = BIN_Y0; w = BIN_W; top = FZ + 54;
    // plywood bin: sloped floor falls from the front (x1) to the outlet at the wall
    color([0.86, 0.74, 0.55]) difference() {
        translate([x0, y0, OUTLET_Z - 4]) cube([x1 - x0, w, top - OUTLET_Z + 4]);
        translate([x0 + 0.75, y0 + 0.75, OUTLET_Z - 4 + 0.01]) cube([x1 - x0 - 1.5, w - 1.5, top]);
        if (doors_open) translate([x0 - 1, y0 - 1, OUTLET_Z - 3]) cube([x1 - x0 + 2, 1.8, top]);   // cut-away side
    }
    // sloped floor (45 deg) + feed
    color([0.86, 0.74, 0.55]) translate([x0, y0, OUTLET_Z - 4]) rotate([90, 0, 0]) translate([0, 0, -w])
        linear_extrude(w) polygon([[0, 0], [x1 - x0, 0], [x1 - x0, x1 - x0], [0, 0.75]]);
    color(C_FEED) translate([x0 + 0.75, y0 + 0.75, OUTLET_Z - 4]) rotate([90, 0, 0]) translate([0, 0, -(w - 1.5)])
        linear_extrude(w - 1.5) polygon([[0, 1], [x1 - x0 - 1.5, x1 - x0 - 0.5], [x1 - x0 - 1.5, 34], [0, 34]]);
    // hinged lid with the ultrasonic level sensor
    color([0.80, 0.68, 0.50]) translate([x0 - 0.5, y0 - 0.5, top]) rotate([0, doors_open ? -35 : 0, 0])
        cube([x1 - x0 + 1, w + 1, 0.75]);
    color([0.2, 0.2, 0.2]) translate([(x0 + x1) / 2, y0 + w / 2, top + (doors_open ? 9 : 0.75)]) cylinder(d = 3, h = 1.5);
    // outlet slide gate
    color(C_METAL) translate([x0 + 0.2, y0 + 3, OUTLET_Z - 4]) cube([0.3, 18, 8]);
}

module water_drum() {
    x = L + SS_D / 2; y = DRUM_Y;
    // block stand
    for (dy = [-6, 2]) box([x - 8, y + dy, FZ], [16, 4, 18], [0.62, 0.62, 0.6]);
    color(C_DRUM) translate([x, y, FZ + 18]) cylinder(d = 20, h = 29);
    color(C_DRUM * 0.8) translate([x, y, FZ + 47]) cylinder(d = 19, h = 1);
    // supply: hose up the station wall -> brass solenoid -> drum lid
    color([0.1, 0.4, 0.2]) translate([x + 10, y + 7, 0]) cylinder(d = 1.2, h = FZ + 54);
    color(C_BRASS) translate([x + 7, y + 5, FZ + 50]) cube([4, 4, 4]);
    color(C_PVC) translate([x + 3, y + 3, FZ + 52]) rotate([0, 90, 0]) cylinder(d = 0.9, h = 5);
    // overflow + outlet to the drinker line through the wall
    color(C_PVC) translate([x - 10, y, FZ + 44]) rotate([0, -90, 0]) cylinder(d = 1.05, h = 6);
    color(C_PVC) translate([L - 2, y + 1, FZ + 14]) rotate([0, 90, 0]) cylinder(d = 1.05, h = 8);
    color(C_PVC) translate([x - 6, y + 1, FZ + 14]) cylinder(d = 1.05, h = 6);
    color([0.2, 0.2, 0.2]) translate([x, y, FZ + 49]) cylinder(d = 1.5, h = 2);   // float/probe gland
    // foam insulation panel behind the drum (north end)
    color([0.35, 0.55, 0.85, 0.6]) translate([L + 1, SS_Y0 + SS_W - 2.6, FZ]) cube([SS_D - 3, 1, SS_H - 4]);
}

// ------------------------------------------------------------------ run (south)
module run() {
    x0 = -30; x1 = L + 30; y1 = -240; h = 78;
    posts = [for (x = [x0 : 100 : x1]) [x, y1]];
    for (x = [x0 : 100 : x1 + 1]) box([x, y1, 0], [3.5, 3.5, h], C_FRAME);
    for (y = [y1 : 80 : 0]) { box([x0, y, 0], [3.5, 3.5, h], C_FRAME); box([x1, y, 0], [3.5, 3.5, h], C_FRAME); }
    // rails
    box([x0, y1, h - 3.5], [x1 - x0 + 3.5, 3.5, 3.5], C_FRAME);
    for (x = [x0, x1]) box([x, y1, h - 3.5], [3.5, -y1, 3.5], C_FRAME);
    // mesh
    mesh_panel([x0, y1 + 1.5, 0], [x1 - x0 + 3.5, 0.3, h - 4]);
    for (x = [x0 + 1.5, x1 + 1.5]) mesh_panel([x, y1, 0], [0.3, -y1, h - 4]);
    // shade sail over the half nearest the coop
    if (view == "overview") color([0.9, 0.9, 0.85, 0.55]) translate([x0, -120, h + 2]) cube([x1 - x0 + 3.5, 120, 0.4]);
    // gate
    box([x1 + 1, -140, 2], [1.5, 30, 60], C_FRAME);
    // hens ranging in the run
    for (p = [[40, -60, 30], [70, -150, 200], [150, -90, 120], [200, -180, 300], [110, -200, 45]]) hen([p[0], p[1], 5], p[2]);
}

// ------------------------------------------------------------------ scene
ground();
floor_platform();
walls();
if (show_roof) roof();
nest_bay();
pop_door();
if (inside || view == "service_open") interior();
service_station();
if (view == "overview" || view == "exterior") run();
if (view == "service_open") labels_service();
if (view == "interior") labels_interior();

// ------------------------------------------------------------------ labels
module label(p, t, a = 0, size = 2.2) {
    color([0.1, 0.1, 0.1]) translate(p) rotate([90, 0, a]) linear_extrude(0.2) text(t, size = size, font = "Liberation Sans:style=Bold");
}
module labels_service() {
    label([L + 4, SS_Y0 - 3, FZ + 60], "FEED BIN ~350 lb", 0);
    label([L + 4, SS_Y0 - 3, FZ + 56.5], "sloped floor -> wall slot", 0, 1.6);
    label([L + 4, SS_Y0 - 3, FZ + 3], "slide gate + slot to indoor trough", 0, 1.6);
    label([L + SS_D + 2, DRUM_Y - 12, FZ + 66], "30 gal WATER DRUM", 90);
    label([L + SS_D + 2, DRUM_Y - 12, FZ + 62.5], "floats, DS18B20, de-icer inside", 90, 1.6);
    label([L + SS_D + 2, DRUM_Y + 2, FZ + 57], "12V valve", 90, 1.6);
}
module labels_interior() {
    label([20, 20, FZ + 60], "ROOSTS 5 x 9 ft over poop board", 0, 3.5);
    label([100, 112, FZ + 48], "12 NEST BOX OPENINGS", 0, 3.5);
    label([128, 104, FZ + 4.5], "NIPPLE LINE", 0, 3);
    label([196, 88, FZ + 20], "TROUGH", 0, 3);
}
