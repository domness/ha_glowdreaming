# Home Assistant - Glow Dreaming

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=domness&repository=ha_glowdreaming&category=Integration)

- Manage your Glow Dreaming device in [Home Assistant](https://home-assistant.io/).

## What it does

- Fetch the current state of your Glow Dreaming device (i.e. White Noise - Loud Volume)
- Set the state of your Glow Dreaming device

## Screenshots

<img width="391" height="592" alt="Screenshot 2025-08-07 at 22 49 04" src="https://github.com/user-attachments/assets/557f8aeb-b540-44a2-9486-2d2deaff4157" />
<img width="1106" height="783" alt="Screenshot 2025-08-07 at 22 50 01" src="https://github.com/user-attachments/assets/bb54db62-adf7-446a-ae16-955f54701691" />


## What you need

- A Glow Dreaming device with Bluetooth (App) support
- A USB Bluetooth connected to your Home Assistant setup

## Setting up the integration

- Ensure you have a Bluetooth adapter connected to your Home Assistant setup
- Select your Glow Dreaming device from the Bluetooth devices list

## Entities

The integration exposes three entities:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.glowdreaming_sensor` | Sensor | Current device state with detailed attributes |
| `light.glowdreaming_light` | Light | Control brightness and light effect |
| `media_player.glowdreaming_sound` | Media Player | Control white noise volume |

### Sensor Attributes

The sensor entity exposes the following state attributes:

| Attribute | Description |
|-----------|-------------|
| `connected` | Whether the device is currently connected via Bluetooth |
| `mode` | Current device mode (human-readable) |
| `effect` | Active light effect (`Sleep`, `Awake`, or `None`) |
| `brightness` | Current brightness level (`Low`, `Medium`, `High`, or `None`) |
| `volume` | Current volume level (`Low`, `Medium`, `High`, or `None`) |
| `humidifier` | Current humidifier mode |
| `humidifier_timer` | Remaining humidifier timer value |
| `device_lock` | Whether the physical device buttons are locked |
| `mode_hex` | Raw hex string of the last command sent |

### Light Entity

The light entity supports:
- **Brightness** — three discrete levels mapped to HA's 0–255 scale: Low (85), Medium (170), High (255)
- **Effects** — `Sleep` (red channel) or `Awake` (green channel)

### Media Player Entity

The media player entity exposes the current **White Noise** volume as a 0.0–1.0 float and reflects playback state (`playing` when volume > 0, `off` otherwise).

## Service Actions

All service actions target the `sensor.glowdreaming_sensor` entity via **Developer Tools → Actions**.

### `glowdreaming.set_mode`

Set all device parameters at once.

| Field | Required | Values |
|-------|----------|--------|
| `light_effect` | Yes | `None`, `Sleep`, `Awake` |
| `brightness` | Yes | `None`, `Low`, `Medium`, `High` |
| `volume` | Yes | `None`, `Low`, `Medium`, `High` |
| `humidifier` | Yes | `None`, `2 Hours`, `4 Hours`, `Continuous` |

### `glowdreaming.set_sleep_brightness`

Switch to Sleep (red) light effect at the specified brightness, preserving current volume and humidifier state.

| Field | Required | Values |
|-------|----------|--------|
| `brightness` | Yes | `None`, `Low`, `Medium`, `High` |

### `glowdreaming.set_awake_brightness`

Switch to Awake (green) light effect at the specified brightness, preserving current volume and humidifier state.

| Field | Required | Values |
|-------|----------|--------|
| `brightness` | Yes | `None`, `Low`, `Medium`, `High` |

### `glowdreaming.set_volume`

Set the white noise volume, preserving current light effect and humidifier state.

| Field | Required | Values |
|-------|----------|--------|
| `volume` | Yes | `None`, `Low`, `Medium`, `High` |

### `glowdreaming.set_humidifier`

Set the humidifier mode, preserving current light effect and volume state.

| Field | Required | Values |
|-------|----------|--------|
| `humidifier` | Yes | `None`, `2 Hours`, `4 Hours`, `Continuous` |

### `glowdreaming.refresh_state`

Force an immediate state refresh from the device (no parameters).

### Advanced: `glowdreaming.write_gatt` / `glowdreaming.read_gatt`

Low-level GATT access for debugging or experimentation.

| Field | Required | Description |
|-------|----------|-------------|
| `target_uuid` | Yes | GATT characteristic UUID |
| `data` | Yes (write only) | Hex string to write (e.g. `640000000000ffff0000`) |

## Issues

- Sometimes the Glow Dreaming device will disappear or fail to connect for a period of time.

