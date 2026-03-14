# Glow Dreaming HA Integration — Agent Guide

## Summary

Home Assistant custom integration for the Glow Dreaming BLE baby sleep device. Python/async, using `bleak` for BLE and the standard HA `DataUpdateCoordinator` pattern.

## Key Files

| File | Purpose |
|------|---------|
| `glowdreaming_api/device.py` | BLE device driver — GATT read/write, state parsing |
| `glowdreaming_api/const.py` | GATT UUID + enums (GDEffect, GDBrightness, GDVolume, GDHumidifier) |
| `sensor.py` | All custom HA service actions (set_mode, set_volume, etc.) |
| `light.py` | Light entity — brightness + effect display and control |
| `media_player.py` | Sound/volume state display |
| `coordinator.py` | DataUpdateCoordinator, 30s poll interval |
| `entity.py` | Base `BTEntity` — shared unique_id, device_info, availability |

## Bluetooth Protocol (brief)

- **GATT UUID**: `c28909e0-4d86-32a9-9143-33c7c5e6ec29`
- **Command format**: 10-byte hex string — `{RED}{GREEN}00{VOLUME}{HUM_4_BYTES}{LOCK}00`
- **Brightness levels**: `0a`=Low(10), `28`=Medium(40), `64`=High(100)
- **Volume levels**: `00`=Off, `01`=Low, `02`=Medium, `03`=High
- **Effect**: Red channel=Sleep, Green channel=Awake
- See `CLAUDE.md` for full protocol tables.

## Conventions

- All device mutations go through `GlowdreamingDevice.set_mode()` — always pass full state (effect, brightness, volume, humidifier).
- `send_command()` writes GATT then calls `update()` to refresh state.
- Entities extend `BTEntity`; `_device` is set from `coordinator.data`.
- `PARALLEL_UPDATES = 0` on all platforms.

## Validation

```bash
# HACS action validation (via GitHub Actions)
# .github/workflows/hacs_action.yml
# .github/workflows/validate_with_hass.yml
```

No local test suite — validate manually in HA or via CI workflows.

## Change Guidelines

- No breaking changes to existing entity unique_ids or service action names.
- Service schemas are in `const.py` (`Schema` enum).
- Device enums (`GDEffect`, `GDBrightness`, `GDVolume`, `GDHumidifier`) are the canonical values used in all service calls and state reads.
