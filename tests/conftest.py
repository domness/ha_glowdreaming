"""Pytest configuration: mock HA / bleak before any custom-component import."""
from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

# ---------------------------------------------------------------------------
# Minimal HA stub base classes
# ---------------------------------------------------------------------------

class _Entity:
    _attr_has_entity_name = False
    _attr_unique_id: str | None = None
    _attr_device_info: dict | None = None

    def async_write_ha_state(self) -> None:  # noqa: D102
        pass


class _CoordinatorEntity(_Entity):
    def __init__(self, *args, **kwargs) -> None:
        # First positional arg is the coordinator in both CoordinatorEntity and
        # DataUpdateCoordinator.__init__ call-sites we care about.
        if args:
            self.coordinator = args[0]

    @classmethod
    def __class_getitem__(cls, item):  # support CoordinatorEntity[T] syntax
        return cls


class _LightEntity(_Entity):
    pass


class _SensorEntity(_Entity):
    pass


class _MediaPlayerEntity(_Entity):
    pass


class _UpdateFailed(Exception):
    pass


# ---------------------------------------------------------------------------
# HA constant stubs used by the entity modules
# ---------------------------------------------------------------------------

class _ColorMode:
    ONOFF = "onoff"
    BRIGHTNESS = "brightness"


class _LightEntityFeature:
    EFFECT = 4


class _MediaPlayerState:
    PLAYING = "playing"
    OFF = "off"
    IDLE = "idle"
    PAUSED = "paused"


class _MediaPlayerDeviceClass:
    SPEAKER = "speaker"


class _MediaPlayerEntityFeature:
    VOLUME_SET = 4
    PAUSE = 1
    PLAY = 16384


ATTR_EFFECT = "effect"

# ---------------------------------------------------------------------------
# Build mock modules
# ---------------------------------------------------------------------------

ATTR_BRIGHTNESS = "brightness"

_light_mod = MagicMock()
_light_mod.LightEntity = _LightEntity
_light_mod.ATTR_BRIGHTNESS = ATTR_BRIGHTNESS
_light_mod.ATTR_EFFECT = ATTR_EFFECT
_light_mod.ColorMode = _ColorMode
_light_mod.LightEntityFeature = _LightEntityFeature

_sensor_mod = MagicMock()
_sensor_mod.SensorEntity = _SensorEntity

_mp_mod = MagicMock()
_mp_mod.MediaPlayerEntity = _MediaPlayerEntity
_mp_mod.MediaPlayerState = _MediaPlayerState
_mp_mod.MediaPlayerDeviceClass = _MediaPlayerDeviceClass
_mp_mod.MediaPlayerEntityFeature = _MediaPlayerEntityFeature

_coord_mod = MagicMock()
_coord_mod.CoordinatorEntity = _CoordinatorEntity
_coord_mod.DataUpdateCoordinator = _CoordinatorEntity
_coord_mod.UpdateFailed = _UpdateFailed

_core_mod = MagicMock()
_core_mod.callback = lambda f: f  # pass-through decorator

_bleak_exc_mod = MagicMock()
_bleak_exc_mod.BleakError = IOError  # real Exception subclass for raise/except

_bleak_mod = MagicMock()
_bleak_mod.BleakError = IOError  # coordinator imports BleakError from bleak directly

# async_timeout needs to work as an async context manager
_mock_cm = MagicMock()
_mock_cm.__aenter__ = AsyncMock(return_value=None)
_mock_cm.__aexit__ = AsyncMock(return_value=False)
_async_timeout_mod = MagicMock()
_async_timeout_mod.timeout = MagicMock(return_value=_mock_cm)

sys.modules.update({
    "homeassistant": MagicMock(),
    "homeassistant.const": MagicMock(),
    "homeassistant.core": _core_mod,
    "homeassistant.exceptions": MagicMock(),
    "homeassistant.components": MagicMock(),
    "homeassistant.components.bluetooth": MagicMock(),
    "homeassistant.components.light": _light_mod,
    "homeassistant.components.sensor": _sensor_mod,
    "homeassistant.components.media_player": _mp_mod,
    "homeassistant.config_entries": MagicMock(),
    "homeassistant.helpers": MagicMock(),
    "homeassistant.helpers.config_validation": MagicMock(),
    "homeassistant.helpers.update_coordinator": _coord_mod,
    "homeassistant.helpers.entity_platform": MagicMock(),
    "homeassistant.helpers.device_registry": MagicMock(),
    "voluptuous": MagicMock(),
    "bleak": _bleak_mod,
    "bleak.exc": _bleak_exc_mod,
    "bleak.backends": MagicMock(),
    "bleak.backends.device": MagicMock(),
    "async_timeout": _async_timeout_mod,
})

# ---------------------------------------------------------------------------
# Shared fixtures  (import pytest *after* sys.modules is patched)
# ---------------------------------------------------------------------------

import pytest  # noqa: E402

from custom_components.glowdreaming.glowdreaming_api.const import (  # noqa: E402
    GDBrightness,
    GDEffect,
    GDHumidifier,
    GDVolume,
)


@pytest.fixture
def mock_device():
    """MagicMock that mimics GlowdreamingDevice's public interface."""
    device = MagicMock()
    device.connected = True
    device.brightness = 10
    device.brightness_level = GDBrightness.LOW
    device.last_brightness = GDBrightness.LOW
    device.effect = GDEffect.SLEEP
    device.last_effect = GDEffect.SLEEP
    device.volume = 1
    device.volume_level = GDVolume.LOW
    device.humidifier = GDHumidifier.NONE
    device.humidifier_timer = 0
    device.device_lock = None
    device.mode = "test mode string"
    device.mode_hex = "0a0000010000ffff0000"
    device._sound = None
    device.set_mode = AsyncMock()
    device.update = AsyncMock()
    device.write_gatt = AsyncMock()
    device.read_gatt = AsyncMock()
    return device


@pytest.fixture
def mock_coordinator(mock_device):
    """MagicMock coordinator backed by mock_device."""
    coord = MagicMock()
    coord.data = mock_device
    coord.ble_device.address = "AA:BB:CC:DD:EE:FF"
    coord.base_unique_id = "test-unique-id"
    coord.device_name = "Glow Dreaming Test"
    coord.async_request_refresh = AsyncMock()
    return coord
