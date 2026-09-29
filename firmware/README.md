# Firmware (ESPHome)

| File | Device |
|---|---|
| `coop-controller.yaml` | Main controller: ESP32-DevKitC-32E on the Coop Controller PCB |
| `packages/base.yaml` | WiFi/AP fallback, API (encrypted), OTA, web UI, SNTP/HA time, sun, status LED, 12 V monitor |
| `packages/door.yaml` | Pop door: relay H-bridge, reed end stops, sun-elevation schedule with a lux fallback, fault alerts |
| `packages/water.yaml` | Float-controlled fill with timeout lockout + valve watchdog, DS18B20, de-icer thermostat |
| `packages/feeder.yaml` | Scheduled auger dispensing, hopper level (JSN-SR04T), door/auger power interlock |
| `packages/lighting_fan.yaml` | Morning light supplement to the target day length, temp/RH exhaust fan |
| `packages/environment.yaml` | BME280 + BH1750 on I2C |
| `packages/security.yaml` | PIR + "night motion" |
| `packages/ble.yaml` | BLE tracker + HA Bluetooth proxy + pvvx thermometer example |
| `coop-camera.yaml` | Optional AI-Thinker ESP32-CAM |

GPIO numbers **must** match `hardware/pinmap.yaml`. Each `GPIOxx` line carries a
`# SIGNAL_NAME` comment, which `tools/check_consistency.py` verifies.

## Design rules

- **Local first.** Nothing the birds depend on needs HA or internet. `reboot_timeout: 0s`
  on the API and WiFi means the controller never reboots just because HA or WiFi is gone.
- **Fail safe.** All outputs are `ALWAYS_OFF` at boot, with gate pull-downs on the PCB.
  The door relays interlock in software, and the relay topology makes shoot-through
  impossible anyway. The valve closes on timeout and has its own watchdog. The auger has
  a 150 s cap. The float wiring convention makes a broken wire read as "don't fill".
- **Manual overrides stick** until the next scheduled transition, because the door and
  light schedulers only act on *changes* in the desired state.
- **Everything tunable is a `number`/`switch` entity** (restored across reboots), so
  thresholds change from HA or the web UI without reflashing.

## Build / flash

```bash
pip install esphome
cp secrets.example.yaml secrets.yaml      # then edit it
esphome config coop-controller.yaml       # validate
esphome run coop-controller.yaml          # compile + flash (USB first time, then OTA)
```

Verified with ESPHome 2026.9.0 (esp-idf 5.5.5): the controller uses 61 % RAM / 75 % flash,
the camera 32 % RAM / 54 % flash.
