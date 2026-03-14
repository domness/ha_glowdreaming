"""Tests for GlowdreamingSensor entity and its service methods."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from custom_components.glowdreaming.sensor import GlowdreamingSensor
from custom_components.glowdreaming.glowdreaming_api.const import (
    GDBrightness,
    GDEffect,
    GDHumidifier,
    GDVolume,
)


def make_sensor(mock_device, mock_coordinator) -> GlowdreamingSensor:
    entity = object.__new__(GlowdreamingSensor)
    entity._device = mock_device
    entity.coordinator = mock_coordinator
    entity.async_write_ha_state = MagicMock()
    return entity


# ---------------------------------------------------------------------------
# native_value
# ---------------------------------------------------------------------------

class TestNativeValue:
    def test_returns_device_mode(self, mock_device, mock_coordinator):
        mock_device.mode = "Power: True, Volume: 1, Brightness: 10"
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.native_value == mock_device.mode

    def test_returns_none_when_mode_none(self, mock_device, mock_coordinator):
        mock_device.mode = None
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.native_value is None


# ---------------------------------------------------------------------------
# extra_state_attributes
# ---------------------------------------------------------------------------

class TestExtraStateAttributes:
    def test_expected_keys_present(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        attrs = entity.extra_state_attributes
        for key in ("connected", "volume", "effect", "brightness", "humidifier",
                    "humidifier_timer", "device_lock", "mode", "mode_hex"):
            assert key in attrs, f"missing key: {key}"

    def test_no_duplicate_mode_hex(self, mock_device, mock_coordinator):
        """mode_hex should appear exactly once (sourced from device, not _attributes)."""
        entity = make_sensor(mock_device, mock_coordinator)
        attrs = entity.extra_state_attributes
        assert list(attrs.keys()).count("mode_hex") == 1

    def test_mode_hex_reflects_device(self, mock_device, mock_coordinator):
        mock_device.mode_hex = "640000030000ffff0000"
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.extra_state_attributes["mode_hex"] == "640000030000ffff0000"

    def test_connected_when_device_connected(self, mock_device, mock_coordinator):
        mock_device.connected = True
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.extra_state_attributes["connected"] == "Connected"

    def test_disconnected_when_device_not_connected(self, mock_device, mock_coordinator):
        mock_device.connected = False
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.extra_state_attributes["connected"] == "Disconnected"


# ---------------------------------------------------------------------------
# connection_state helper
# ---------------------------------------------------------------------------

class TestConnectionState:
    def test_connected_string(self, mock_device, mock_coordinator):
        mock_device.connected = True
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.connection_state() == "Connected"

    def test_disconnected_string(self, mock_device, mock_coordinator):
        mock_device.connected = False
        entity = make_sensor(mock_device, mock_coordinator)
        assert entity.connection_state() == "Disconnected"


# ---------------------------------------------------------------------------
# Service: set_mode
# ---------------------------------------------------------------------------

class TestSetMode:
    @pytest.mark.asyncio
    async def test_delegates_to_device(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_mode("Sleep", "High", "Medium", "None")
        mock_device.set_mode.assert_called_once_with(
            GDEffect.SLEEP, GDBrightness.HIGH, GDVolume.MEDIUM, GDHumidifier.NONE
        )

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_mode("Sleep", "Low", "None", "None")
        entity.async_write_ha_state.assert_called()


# ---------------------------------------------------------------------------
# Service: set_sleep_brightness
# ---------------------------------------------------------------------------

class TestSetSleepBrightness:
    @pytest.mark.asyncio
    async def test_uses_sleep_effect_and_preserves_volume_humidifier(self, mock_device, mock_coordinator):
        mock_device.volume_level = GDVolume.HIGH
        mock_device.humidifier = GDHumidifier.CONTINUOUS
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_sleep_brightness("Medium")
        mock_device.set_mode.assert_called_once_with(
            GDEffect.SLEEP, GDBrightness.MEDIUM, GDVolume.HIGH, GDHumidifier.CONTINUOUS
        )


# ---------------------------------------------------------------------------
# Service: set_awake_brightness
# ---------------------------------------------------------------------------

class TestSetAwakeBrightness:
    @pytest.mark.asyncio
    async def test_uses_awake_effect_and_preserves_volume_humidifier(self, mock_device, mock_coordinator):
        mock_device.volume_level = GDVolume.LOW
        mock_device.humidifier = GDHumidifier.TWO
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_awake_brightness("High")
        mock_device.set_mode.assert_called_once_with(
            GDEffect.AWAKE, GDBrightness.HIGH, GDVolume.LOW, GDHumidifier.TWO
        )


# ---------------------------------------------------------------------------
# Service: set_volume
# ---------------------------------------------------------------------------

class TestSetVolume:
    @pytest.mark.asyncio
    async def test_preserves_effect_and_brightness(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.SLEEP
        mock_device.brightness_level = GDBrightness.HIGH
        mock_device.humidifier = GDHumidifier.NONE
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_volume("High")
        mock_device.set_mode.assert_called_once_with(
            GDEffect.SLEEP, GDBrightness.HIGH, GDVolume.HIGH, GDHumidifier.NONE
        )


# ---------------------------------------------------------------------------
# Service: set_humidifier
# ---------------------------------------------------------------------------

class TestSetHumidifier:
    @pytest.mark.asyncio
    async def test_preserves_effect_and_brightness(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.AWAKE
        mock_device.brightness_level = GDBrightness.MEDIUM
        mock_device.volume_level = GDVolume.LOW
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.set_humidifier("2 Hours")
        mock_device.set_mode.assert_called_once_with(
            GDEffect.AWAKE, GDBrightness.MEDIUM, GDVolume.LOW, GDHumidifier.TWO
        )


# ---------------------------------------------------------------------------
# Service: refresh_state
# ---------------------------------------------------------------------------

class TestRefreshState:
    @pytest.mark.asyncio
    async def test_calls_device_update(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.refresh_state()
        mock_device.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.refresh_state()
        entity.async_write_ha_state.assert_called()


# ---------------------------------------------------------------------------
# Service: write_gatt / read_gatt
# ---------------------------------------------------------------------------

class TestGattServices:
    @pytest.mark.asyncio
    async def test_write_gatt_delegates(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.write_gatt("some-uuid", "deadbeef")
        mock_device.write_gatt.assert_called_once_with("some-uuid", "deadbeef")

    @pytest.mark.asyncio
    async def test_read_gatt_delegates(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.read_gatt("some-uuid")
        mock_device.read_gatt.assert_called_once_with("some-uuid")

    @pytest.mark.asyncio
    async def test_read_gatt_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_sensor(mock_device, mock_coordinator)
        await entity.read_gatt("some-uuid")
        entity.async_write_ha_state.assert_called()
