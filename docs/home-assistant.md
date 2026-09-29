# Home Assistant Setup

The coop controller is an **ESPHome** device. Home Assistant finds it automatically and
gets full control of it. The coop never *depends* on HA, though: all the scheduling and
safety logic runs on the ESP32.

## 1. Flash the firmware

1. Install ESPHome: the ESPHome Device Builder add-on in HA, or
   `pip install esphome` on a PC.
2. Copy `firmware/secrets.example.yaml` to `firmware/secrets.yaml` and fill in your WiFi
   details. Generate the two API keys with the one-liner in the file.
3. Edit the `substitutions:` at the top of `firmware/coop-controller.yaml`: **latitude,
   longitude, timezone** (these drive the sunrise/sunset door and lights), the feeding
   hours, and the hopper depth.
4. The first flash goes over USB: `esphome run firmware/coop-controller.yaml`. After that,
   updates go over WiFi (OTA, encrypted with the API key).
5. **Windows users:** if compiling fails with `c++config.h` / path-length errors, set
   `ESPHOME_ESP_IDF_PREFIX=C:\esphidf` and run from PowerShell or cmd, not Git Bash.

If WiFi isn't configured or is out of range, the device starts a setup access point
called **Coop-Controller-Setup** (captive portal). Its local web UI
(`http://coop-controller.local`, user `admin`) controls everything without HA.

## 2. Add it to Home Assistant

Go to Settings → Devices & services. The **ESPHome: Coop** device should appear as
"Discovered". Click **Configure** and paste the `api_encryption_key`.

## 3. Entities

| Entity | What it does |
|---|---|
| `cover.coop_pop_door` | Open/close/stop the pop door (endstop cover with reed-switch feedback) |
| `switch.coop_door_auto_mode` | On-device sunrise/sunset schedule. Turn it off for a manual day |
| `number.coop_door_open_sun_elevation` / `…_close_sun_elevation` | Open when the sun is ≥ +2°, close at ≤ −6° (civil dusk) |
| `number.coop_door_earliest_open` | Don't open before this hour (default 06:30), to keep predators at dawn out |
| `switch.coop_water_auto_fill`, `button.coop_water_fill_now`, `button.coop_water_fill_lockout_reset` | Water fill control |
| `number.coop_water_max_fill_time` | Fill timeout before lockout (default 10 min) |
| `switch.coop_water_de_icer`, `switch.coop_de_icer_auto`, `number.coop_de_icer_on_below` / `…_off_above` | Freeze protection (3 °C on / 6 °C off) |
| `switch.coop_feeder_auto_schedule`, `button.coop_dispense_feed_now`, `number.coop_feeder_run_time` | Auger feeding (07:00 and 15:00 by default) |
| `switch.coop_coop_light`, `switch.coop_light_auto_winter_supplement`, `number.coop_target_day_length` | Morning light supplement up to 14 h of daylight |
| `switch.coop_exhaust_fan`, `switch.coop_fan_auto`, `number.coop_fan_on_above` | Ventilation fan |
| `sensor.coop_coop_temperature` / `_humidity` / `_pressure`, `sensor.coop_outdoor_light`, `sensor.coop_water_temperature`, `sensor.coop_feed_level` | Telemetry |
| `binary_sensor.coop_door_fault`, `…_door_open_after_dark`, `…_water_fill_lockout`, `…_water_float_fault`, `…_water_freeze_risk`, `…_feed_low`, `…_12v_supply_low`, `…_night_motion` | Problems. Hook these to notifications |
| `sensor.coop_nest_box_temperature` (BLE) | From the pvvx BLE thermometer, if fitted |

The controller also acts as a **Bluetooth proxy**, so other BLE devices near the coop
(BTHome door/gate sensors, more thermometers) appear in HA without any firmware changes.

## 4. Automations and dashboard

- `docs/ha/automations.yaml` has a problem alert (any fault sensor → phone push), a
  night-motion alert, a controller-offline alert, an evening "door didn't close" check,
  and an auto-mode re-enable at 03:00.
- `docs/ha/dashboard.yaml` is a ready-made dashboard (door tile, status glance, gauges,
  48 h climate graph, controls). Paste it into a new dashboard's raw config editor.

Replace `notify.notify` with your phone's notifier (`notify.mobile_app_<name>`).

## 5. Camera (optional)

- **ESP32-CAM:** flash `firmware/coop-camera.yaml` (board `esp32cam`). It appears as
  `camera.coop_camera_…`, and you can add a `picture-entity` card.
- **Better option:** an outdoor PoE or WiFi camera with IR and RTSP/ONVIF (Reolink, Amcrest
  and similar) through HA's ONVIF / Generic Camera integration. Frigate NVR can add
  person/animal detection later.

## 6. Upgrade path

| Now | Later |
|---|---|
| On-device schedule | HA automations for vacation mode, egg-count logging, weather-aware door times |
| 1 PIR | Camera + Frigate object detection (fox, raccoon, hawk) |
| Manual range gates | Second actuator on expansion header IO5 (J13) for a run → paddock gate |
| BME280 | Ammonia sensor (e.g. MQ-137 via ADS1115 on the J13 I2C) for litter management |
| Mains only | Battery backup (see `construction/wiring.md`), later solar |
