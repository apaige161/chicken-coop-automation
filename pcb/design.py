"""Coop Controller v1.0 - circuit definition (single source for schematic + PCB).

Every part is listed with its KiCad symbol, footprint, value and a pin -> net map.
Net names for GPIO signals are the `signal` names in hardware/pinmap.yaml, and
tools/check_consistency.py verifies that the ESP32 socket pins land on those nets.

Board coordinates (mm) are measured from the board's top-left corner. Rotation is
in degrees. `None` placement means "auto-place in the given region".
"""

BOARD_W, BOARD_H = 170.0, 105.0

TB = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-{n}-5.08_1x0{n}_P5.08mm_Horizontal'
R_FP = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
C_FP = 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'
SOCKET = 'Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical'

# ESP32-DevKitC V4 (38-pin) header pin -> GPIO. Left header = J20, right = J21/J22.
# Pin 1 is the end nearest the antenna (3V3 on the left, GND on the right).
ESP_LEFT = ['3V3', 'EN', 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, 12, 'GND', 13, 'SD2', 'SD3', 'CMD', '5V']
ESP_RIGHT = ['GND', 23, 22, 'TX', 'RX', 21, 'GND', 19, 18, 5, 17, 16, 4, 0, 2, 15, 'SD1', 'SD0', 'CLK']

GPIO_NET = {
    21: 'I2C_SDA', 22: 'I2C_SCL', 4: 'ONEWIRE', 25: 'DOOR_OPEN_RLY', 26: 'DOOR_CLOSE_RLY',
    32: 'DOOR_CLOSED_SW', 33: 'DOOR_OPEN_SW', 27: 'VALVE_DRV', 13: 'FEEDER_DRV', 14: 'FAN_DRV',
    16: 'LIGHT_SSR', 17: 'HEAT_SSR', 34: 'WATER_LOW', 35: 'WATER_HIGH', 39: 'PIR',
    18: 'US_TRIG', 19: 'US_ECHO', 23: 'DOOR_BTN', 2: 'STATUS_LED', 36: 'VIN_SENSE', 5: 'SPARE_IO5',
}
SPECIAL_NET = {'3V3': '+3V3', '5V': '+5V', 'GND': 'GND'}


def esp_pins(header):
    pins = {}
    for i, p in enumerate(header, start=1):
        if isinstance(p, int):
            pins[str(i)] = GPIO_NET.get(p)   # None = unused GPIO -> no-connect
        else:
            pins[str(i)] = SPECIAL_NET.get(p)
    return pins


PARTS = []


def part(ref, lib_id, value, footprint, pins, pos=None, rot=0, group='misc', note=''):
    PARTS.append(dict(ref=ref, lib_id=lib_id, value=value, footprint=footprint,
                      pins=pins, pos=pos, rot=rot, group=group, note=note))


def tb(ref, name, nets, pos, rot):
    n = len(nets)
    part(ref, f'Connector_Generic:Conn_01x0{n}', name, TB.format(n=n),
         {str(i + 1): net for i, net in enumerate(nets)}, pos, rot, group='conn')


# ---------------------------------------------------------------- connectors
# Top edge (rot 180 = wire entry faces the top edge). pos = pin 1.
TOP_Y, BOT_Y = 7.0, 98.0
tb('J1', 'PWR_IN_12V', ['VIN_RAW', 'GND'], (12 + 5.08, TOP_Y), 180)
tb('J4', 'VALVE', ['+12V', 'VALVE-'], (85 + 5.08, TOP_Y), 180)
tb('J5', 'FEEDER', ['+12V', 'FEEDER-'], (99 + 5.08, TOP_Y), 180)
tb('J14', 'FAN', ['+12V', 'FAN-'], (113 + 5.08, TOP_Y), 180)
tb('J2', 'ACTUATOR', ['M+', 'M-'], (127 + 5.08, TOP_Y), 180)
tb('J6', 'SSR_OUT', ['+12V', 'LIGHT_SSR-', '+12V', 'HEAT_SSR-'], (141 + 3 * 5.08, TOP_Y), 180)
# Bottom edge (rot 0 = wire entry faces the bottom edge).
tb('J3', 'DOOR_SW', ['DOOR_CLOSED_SW', 'DOOR_OPEN_SW', 'GND'], (12, BOT_Y), 0)
tb('J7', 'WATER_LVL', ['WATER_LOW', 'WATER_HIGH', 'GND'], (32, BOT_Y), 0)
tb('J8', 'ONEWIRE', ['+3V3', 'ONEWIRE', 'GND'], (52, BOT_Y), 0)
tb('J9', 'I2C', ['+3V3', 'I2C_SDA', 'I2C_SCL', 'GND'], (72, BOT_Y), 0)
tb('J10', 'PIR', ['+5V', 'PIR', 'GND'], (96, BOT_Y), 0)
tb('J11', 'ULTRASONIC', ['+5V', 'US_TRIG', 'US_ECHO_5V', 'GND'], (116, BOT_Y), 0)
tb('J12', 'PANEL', ['DOOR_BTN', 'GND', 'LED_PANEL', 'GND'], (140, BOT_Y), 0)
part('J13', 'Connector_Generic:Conn_01x06', 'EXPANSION',
     'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',
     {'1': '+3V3', '2': 'GND', '3': '+5V', '4': 'I2C_SDA', '5': 'I2C_SCL', '6': 'SPARE_IO5'},
     (100, 83), 90, group='conn')

# ESP32 DevKitC sockets. J21 = official 25.4 mm row spacing, J22 = 22.86 mm clones.
# Fit ONE of J21/J22 (they are wired in parallel).
ESP_X, ESP_Y = 45.0, 32.0
part('J20', 'Connector_Generic:Conn_01x19', 'ESP32_DEVKITC_LEFT', SOCKET, esp_pins(ESP_LEFT),
     (ESP_X, ESP_Y), 0, group='esp')
part('J21', 'Connector_Generic:Conn_01x19', 'ESP32_DEVKITC_RIGHT_25.4mm', SOCKET, esp_pins(ESP_RIGHT),
     (ESP_X + 25.4, ESP_Y), 0, group='esp', note='Fit for official Espressif DevKitC (25.4 mm rows)')
part('J22', 'Connector_Generic:Conn_01x19', 'ESP32_DEVKITC_RIGHT_22.86mm', SOCKET, esp_pins(ESP_RIGHT),
     (ESP_X + 22.86, ESP_Y), 0, group='esp', note='Fit instead of J21 for 22.86 mm clone boards')

# ---------------------------------------------------------------- power
part('F1', 'Device:Fuse', '5A slow-blow 5x20',
     'Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open',
     {'1': 'VIN_RAW', '2': 'VIN_FUSED'}, (6, 20), 0, group='power')
part('D1', 'Device:D_Schottky', 'SB560', 'Diode_THT:D_DO-201AD_P15.24mm_Horizontal',
     {'2': 'VIN_FUSED', '1': '+12V'}, (8, 32), 0, group='power', note='Reverse-polarity protection')
part('D2', 'Device:D_TVS', 'P6KE15CA', 'Diode_THT:D_DO-15_P10.16mm_Horizontal',
     {'1': '+12V', '2': 'GND'}, (8, 40), 0, group='power')
part('C1', 'Device:C_Polarized', '470uF 25V', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
     {'1': '+12V', '2': 'GND'}, (10, 50), 0, group='power')
part('C3', 'Device:C', '100nF', C_FP, {'1': '+12V', '2': 'GND'}, (22, 56), 0, group='power')
part('U1', 'Converter_DCDC:R-78E5.0-1.0', 'R-78E5.0-1.0', 'Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT',
     {'1': '+12V', '2': 'GND', '3': '+5V'}, (10, 64), 0, group='power',
     note='Any 7805-pinout 5 V switching regulator >= 1 A (R-78E5.0-1.0, TSR 1-2450)')
part('C2', 'Device:C_Polarized', '47uF 10V', 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
     {'1': '+5V', '2': 'GND'}, (10, 73), 0, group='power')
part('C4', 'Device:C', '100nF', C_FP, {'1': '+5V', '2': 'GND'}, (22, 73), 0, group='power')
part('R30', 'Device:R', '1k', R_FP, {'1': '+5V', '2': 'LED_PWR_A'}, (6, 80), 0, group='power')
part('D9', 'Device:LED', 'PWR green', 'LED_THT:LED_D3.0mm', {'2': 'LED_PWR_A', '1': 'GND'},
     (22, 80), 0, group='power')
part('R31', 'Device:R', '100k', R_FP, {'1': '+12V', '2': 'VIN_SENSE'}, (28, 48), 90, group='power')
part('R32', 'Device:R', '22k', R_FP, {'1': 'VIN_SENSE', '2': 'GND'}, (32, 48), 90, group='power')
part('C5', 'Device:C', '100nF', C_FP, {'1': 'VIN_SENSE', '2': 'GND'}, (36, 48), 90, group='power')

# ---------------------------------------------------------------- door H-bridge
for i, (k, coil, drv, com, x) in enumerate([('K1', 'K1_COIL', 'DOOR_OPEN_RLY', 'M+', 122),
                                            ('K2', 'K2_COIL', 'DOOR_CLOSE_RLY', 'M-', 146)]):
    q, d, rg, rp = f'Q{i + 1}', f'D{i + 3}', f'R{2 * i + 1}', f'R{2 * i + 2}'
    # SRD pins: 1 = COM, 2/5 = coil, 3 = NO, 4 = NC (verify on your relay with a meter).
    part(k, 'Relay:SANYOU_SRD_Form_C', 'SRD-12VDC-SL-C', 'Relay_THT:Relay_SPDT_SANYOU_SRD_Series_Form_C',
         {'5': '+12V', '2': coil, '1': com, '3': '+12V', '4': 'GND'}, (x, 23), 0, group='door')
    part(d, 'Device:D', '1N4148', 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal',
         {'1': '+12V', '2': coil}, (x, 36), 0, group='door')
    part(q, 'Transistor_FET:2N7000', '2N7000', 'Package_TO_SOT_THT:TO-92_Inline_Wide',
         {'1': 'GND', '2': f'{q}_G', '3': coil}, (x + 12, 36), 0, group='door')
    part(rg, 'Device:R', '100R', R_FP, {'1': drv, '2': f'{q}_G'}, (x, 41), 0, group='door')
    part(rp, 'Device:R', '100k', R_FP, {'1': f'{q}_G', '2': 'GND'}, (x, 46), 0, group='door')

# ---------------------------------------------------------------- 12 V MOSFET outputs
for q, d, rg, rp, drv, out, x in [('Q3', 'D5', 'R5', 'R6', 'VALVE_DRV', 'VALVE-', 80),
                                  ('Q4', 'D6', 'R7', 'R8', 'FEEDER_DRV', 'FEEDER-', 94),
                                  ('Q7', 'D7', 'R13', 'R14', 'FAN_DRV', 'FAN-', 108)]:
    part(q, 'Transistor_FET:IRLZ44N', 'IRLZ44N', 'Package_TO_SOT_THT:TO-220-3_Vertical',
         {'1': f'{q}_G', '2': out, '3': 'GND'}, (x + 2.5, 20), 0, group='outputs',
         note='Logic-level N-FET; IRLB8721 is a drop-in alternative')
    part(d, 'Device:D', '1N5822', 'Diode_THT:D_DO-201AD_P15.24mm_Horizontal',
         {'1': '+12V', '2': out}, (x + 8.5, 25), 270, group='outputs')
    part(rg, 'Device:R', '100R', R_FP, {'1': drv, '2': f'{q}_G'}, (x - 0.5, 25), 270, group='outputs')
    part(rp, 'Device:R', '100k', R_FP, {'1': f'{q}_G', '2': 'GND'}, (x + 3, 25), 270, group='outputs')

# SSR drivers (small loads: SSR input ~10 mA)
for q, rg, rp, drv, out, x in [('Q5', 'R9', 'R10', 'LIGHT_SSR', 'LIGHT_SSR-', 118),
                               ('Q6', 'R11', 'R12', 'HEAT_SSR', 'HEAT_SSR-', 142)]:
    part(q, 'Transistor_FET:2N7000', '2N7000', 'Package_TO_SOT_THT:TO-92_Inline_Wide',
         {'1': 'GND', '2': f'{q}_G', '3': out}, (x + 14, 54), 0, group='outputs')
    part(rg, 'Device:R', '100R', R_FP, {'1': drv, '2': f'{q}_G'}, (x, 54), 0, group='outputs')
    part(rp, 'Device:R', '100k', R_FP, {'1': f'{q}_G', '2': 'GND'}, (x, 59), 0, group='outputs')

# ---------------------------------------------------------------- inputs / sensors
inputs = [
    ('R15', 'DOOR_CLOSED_SW', 'C6'),
    ('R16', 'DOOR_OPEN_SW', 'C7'),
    ('R17', 'WATER_LOW', 'C8'),
    ('R18', 'WATER_HIGH', 'C9'),
    ('R19', 'DOOR_BTN', 'C10'),
]
for i, (r, net, c) in enumerate(inputs):
    part(r, 'Device:R', '10k', R_FP, {'1': '+3V3', '2': net}, (78 + i * 14, 66), 0, group='inputs')
    part(c, 'Device:C', '100nF', C_FP, {'1': net, '2': 'GND'}, (78 + i * 10, 71), 0, group='inputs',
         note='Input RC filter / ESD for long field wiring')
part('R20', 'Device:R', '10k', R_FP, {'1': 'PIR', '2': 'GND'}, (148, 66), 0, group='inputs')
part('R21', 'Device:R', '4.7k', R_FP, {'1': '+3V3', '2': 'ONEWIRE'}, (130, 71), 0, group='inputs')
part('R22', 'Device:R', '4.7k', R_FP, {'1': '+3V3', '2': 'I2C_SDA'}, (146, 71), 0, group='inputs')
part('R23', 'Device:R', '4.7k', R_FP, {'1': '+3V3', '2': 'I2C_SCL'}, (78, 76), 0, group='inputs')
part('R24', 'Device:R', '1k', R_FP, {'1': 'US_ECHO_5V', '2': 'US_ECHO'}, (92, 76), 0, group='inputs')
part('R25', 'Device:R', '2k', R_FP, {'1': 'US_ECHO', '2': 'GND'}, (106, 76), 0, group='inputs')
part('R26', 'Device:R', '330R', R_FP, {'1': 'STATUS_LED', '2': 'LED_PANEL'}, (120, 76), 0, group='inputs')

# ---------------------------------------------------------------- mechanical
for i, (x, y) in enumerate([(4, 4), (BOARD_W - 4, 4), (4, BOARD_H - 4), (BOARD_W - 4, BOARD_H - 4)]):
    part(f'H{i + 1}', 'Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', {},
         (x, y), 0, group='mech')

# Nets that get a PWR_FLAG in the schematic (driven from off-board / passive-only).
PWR_FLAG_NETS = ['VIN_RAW', 'GND', '+12V', '+3V3']

# Net classes: wide traces for load current.
POWER_NETS = ['VIN_RAW', 'VIN_FUSED', '+12V', 'GND', 'M+', 'M-', 'VALVE-', 'FEEDER-', 'FAN-']

# Antenna keep-out (no copper) above the ESP32 module's PCB antenna.
ANTENNA_KEEPOUT = (ESP_X - 4, 12.0, ESP_X + 29.4, ESP_Y - 2.0)   # x1, y1, x2, y2
