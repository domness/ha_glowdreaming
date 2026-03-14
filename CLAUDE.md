# Glow Dreaming — Home Assistant Integration

## Overview

Custom Home Assistant integration for the [Glow Dreaming](https://www.glowdreaming.com/) baby sleep aid device. Communicates over Bluetooth Low Energy (BLE) using a single GATT characteristic for both reading and writing device state.

## Architecture

```
custom_components/glowdreaming/
├── __init__.py              # Entry setup/unload; connects device on startup
├── config_flow.py           # UI config flow for BT device discovery
├── coordinator.py           # DataUpdateCoordinator; polls device every 30s
├── entity.py                # Base BTEntity (CoordinatorEntity subclass)
├── const.py                 # HA-level constants and service schemas
├── sensor.py                # Main sensor entity + all custom service actions
├── light.py                 # Light entity (brightness/effect state + control)
├── media_player.py          # Media player entity (sound/volume state)
└── glowdreaming_api/
    ├── const.py             # GATT UUID and device enums
    └── device.py            # BleakClient wrapper, GATT read/write, state parsing
```

## Bluetooth Protocol

### GATT Characteristic UUID
```
c28909e0-4d86-32a9-9143-33c7c5e6ec29
```

### Command Packet Format
Commands are 10-byte hex strings written to the characteristic:

```
{RED}{GREEN}00{VOLUME}{HUM_4_BYTES}{DEVICE_LOCK}00
 [0]  [1]  [2]  [3]      [4–7]         [8]      [9]
```

| Byte(s) | Field          | Values |
|---------|----------------|--------|
| 0       | Red (Sleep)    | `0a`=Low(10), `28`=Medium(40), `64`=High(100), `00`=Off |
| 1       | Green (Awake)  | `0a`=Low(10), `28`=Medium(40), `64`=High(100), `00`=Off |
| 2       | Blue           | Always `00` |
| 3       | Volume         | `00`=Off, `01`=Low, `02`=Medium, `03`=High |
| 4–7     | Humidifier     | See table below |
| 8       | Device lock    | `00`=unlocked, `01`=locked |
| 9       | Unused         | Always `00` |

### Humidifier Payload (bytes 4–7)

| Mode        | Hex bytes  |
|-------------|------------|
| Off         | `0000ffff` |
| 2 Hours     | `01000078` |
| 4 Hours     | `010000f0` |
| Continuous  | `1010ffff` |

### Brightness Mapping

| Level  | Raw int | Hex  |
|--------|---------|------|
| Low    | 10      | `0a` |
| Medium | 40      | `28` |
| High   | 100     | `64` |

### Light Effect Encoding

The effect is determined by which RGB channel carries the brightness value:

| Effect | Red byte | Green byte |
|--------|----------|------------|
| Sleep  | brightness_hex | `00` |
| Awake  | `00` | brightness_hex |
| None   | `00` | `00` |

### State Parsing (response bytes from read/notify)

| Byte | Field             | Interpretation |
|------|-------------------|----------------|
| 0    | Red channel       | >0 → Sleep effect active; value = raw brightness |
| 1    | Green channel     | >0 → Awake effect active; value = raw brightness |
| 3    | Volume raw        | Integer 0–3 |
| 4    | Humidifier on/off | `1`=on, `0`=off |
| 7    | Humidifier timer  | Remaining timer value |
| 9    | Power/option      | Bit 2 (`& 4`) set → power on; value `1`=2hr timer, `2`=4hr timer |

### Example Packets (from reverse-engineering comments in device.py)

| Hex string               | State |
|--------------------------|-------|
| `000000000000ffff0000`   | All off |
| `0a0000000000ffff0000`   | Sleep light — Low |
| `280000000000ffff0000`   | Sleep light — Medium |
| `640000000000ffff0000`   | Sleep light — High |
| `000000010000ffff0000`   | White noise — Low |
| `000000020000ffff0000`   | White noise — Medium |
| `000000030000ffff0000`   | White noise — High |

## Key Patterns

- **All state changes** go through `GlowdreamingDevice.set_mode()`, which always sends the full 10-byte command packet — partial updates are not supported.
- **Service actions** (set_mode, set_volume, set_humidifier, etc.) live on the `sensor` platform entity.
- **State refresh** happens after every write via `send_command()` → `update()`, which prefers BLE notifications and falls back to a direct GATT read.
- **Coordinator** polls every 30 seconds; entities update via `CoordinatorEntity._handle_coordinator_update`.

## Development Notes

- No automated test suite. Validate manually via HA developer tools → Services.
- CI uses HACS validation (`.github/workflows/hacs_action.yml`) and HA validation (`validate_with_hass.yml`).
- The `bleak` library handles all BLE operations; device connection is maintained persistently with a reconnect callback.
- `PARALLEL_UPDATES = 0` is set on platforms to serialise BT operations.
