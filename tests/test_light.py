"""Tests for GlowdreamingLight entity."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.light import ATTR_EFFECT  # "effect" from conftest mock

from custom_components.glowdreaming.light import GlowdreamingLight
from custom_components.glowdreaming.glowdreaming_api.const import (
    GDBrightness,
    GDEffect,
    GDHumidifier,
    GDVolume,
)


def make_light(mock_device, mock_coordinator) -> GlowdreamingLight:
    """Create a GlowdreamingLight without going through HA's __init__ stack."""
    entity = object.__new__(GlowdreamingLight)
    entity._device = mock_device
    entity.coordinator = mock_coordinator
    entity.async_write_ha_state = MagicMock()
    return entity


# ---------------------------------------------------------------------------
# is_on
# ---------------------------------------------------------------------------

class TestIsOn:
    def test_true_when_brightness_positive(self, mock_device, mock_coordinator):
        mock_device.brightness = 10
        entity = make_light(mock_device, mock_coordinator)
        assert entity.is_on is True

    def test_false_when_brightness_zero(self, mock_device, mock_coordinator):
        mock_device.brightness = 0
        entity = make_light(mock_device, mock_coordinator)
        assert entity.is_on is False

    def test_none_when_brightness_none(self, mock_device, mock_coordinator):
        mock_device.brightness = None
        entity = make_light(mock_device, mock_coordinator)
        assert entity.is_on is None


# ---------------------------------------------------------------------------
# effect property
# ---------------------------------------------------------------------------

class TestEffectProperty:
    def test_returns_none_when_device_effect_is_none(self, mock_device, mock_coordinator):
        mock_device.effect = None
        entity = make_light(mock_device, mock_coordinator)
        assert entity.effect is None

    def test_returns_none_when_device_effect_is_gdeffect_none(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.NONE
        entity = make_light(mock_device, mock_coordinator)
        assert entity.effect is None

    def test_returns_sleep(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.SLEEP
        entity = make_light(mock_device, mock_coordinator)
        assert entity.effect == GDEffect.SLEEP

    def test_returns_awake(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.AWAKE
        entity = make_light(mock_device, mock_coordinator)
        assert entity.effect == GDEffect.AWAKE


# ---------------------------------------------------------------------------
# effect_list
# ---------------------------------------------------------------------------

class TestEffectList:
    def test_excludes_none(self, mock_device, mock_coordinator):
        entity = make_light(mock_device, mock_coordinator)
        assert GDEffect.NONE not in entity.effect_list
        assert "None" not in entity.effect_list

    def test_contains_sleep_and_awake(self, mock_device, mock_coordinator):
        entity = make_light(mock_device, mock_coordinator)
        assert GDEffect.SLEEP in entity.effect_list
        assert GDEffect.AWAKE in entity.effect_list

    def test_current_effect_always_in_list(self, mock_device, mock_coordinator):
        """When the light is on, the current effect must be present in effect_list."""
        for active_effect in (GDEffect.SLEEP, GDEffect.AWAKE):
            mock_device.effect = active_effect
            entity = make_light(mock_device, mock_coordinator)
            assert entity.effect in entity.effect_list


# ---------------------------------------------------------------------------
# async_turn_on
# ---------------------------------------------------------------------------

class TestTurnOn:
    @pytest.mark.asyncio
    async def test_explicit_sleep_effect(self, mock_device, mock_coordinator):
        mock_device.brightness_level = GDBrightness.LOW
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on(**{ATTR_EFFECT: GDEffect.SLEEP})
        mock_device.set_mode.assert_called_once_with(
            GDEffect.SLEEP, GDBrightness.LOW, mock_device.volume_level, mock_device.humidifier
        )

    @pytest.mark.asyncio
    async def test_explicit_awake_effect(self, mock_device, mock_coordinator):
        mock_device.brightness_level = GDBrightness.MEDIUM
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on(**{ATTR_EFFECT: GDEffect.AWAKE})
        mock_device.set_mode.assert_called_once_with(
            GDEffect.AWAKE, GDBrightness.MEDIUM, mock_device.volume_level, mock_device.humidifier
        )

    @pytest.mark.asyncio
    async def test_no_effect_uses_current_when_on(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.AWAKE
        mock_device.brightness_level = GDBrightness.HIGH
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.AWAKE

    @pytest.mark.asyncio
    async def test_restores_last_effect_when_off(self, mock_device, mock_coordinator):
        """After turn-off (effect=NONE), turn-on must restore last_effect."""
        mock_device.effect = GDEffect.NONE
        mock_device.last_effect = GDEffect.AWAKE
        mock_device.brightness_level = GDBrightness.LOW
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.AWAKE

    @pytest.mark.asyncio
    async def test_falls_back_to_sleep_when_no_last_effect(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.NONE
        mock_device.last_effect = None
        mock_device.brightness_level = GDBrightness.LOW
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.SLEEP

    @pytest.mark.asyncio
    async def test_invalid_effect_falls_back_to_last_effect(self, mock_device, mock_coordinator):
        mock_device.last_effect = GDEffect.AWAKE
        mock_device.brightness_level = GDBrightness.LOW
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on(**{ATTR_EFFECT: "NotARealEffect"})
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.AWAKE

    @pytest.mark.asyncio
    async def test_invalid_effect_falls_back_to_sleep_without_last(self, mock_device, mock_coordinator):
        mock_device.last_effect = None
        mock_device.brightness_level = GDBrightness.LOW
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on(**{ATTR_EFFECT: "NotARealEffect"})
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.SLEEP

    @pytest.mark.asyncio
    async def test_restores_last_brightness_when_off(self, mock_device, mock_coordinator):
        mock_device.brightness_level = GDBrightness.NONE
        mock_device.last_brightness = GDBrightness.HIGH
        mock_device.effect = GDEffect.SLEEP
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[1] == GDBrightness.HIGH

    @pytest.mark.asyncio
    async def test_defaults_to_low_brightness_when_no_last(self, mock_device, mock_coordinator):
        mock_device.brightness_level = GDBrightness.NONE
        mock_device.last_brightness = None
        mock_device.effect = GDEffect.SLEEP
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[1] == GDBrightness.LOW

    @pytest.mark.asyncio
    async def test_uses_current_brightness_when_on(self, mock_device, mock_coordinator):
        mock_device.brightness_level = GDBrightness.MEDIUM
        mock_device.effect = GDEffect.SLEEP
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        args = mock_device.set_mode.call_args[0]
        assert args[1] == GDBrightness.MEDIUM

    @pytest.mark.asyncio
    async def test_requests_coordinator_refresh(self, mock_device, mock_coordinator):
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        mock_coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_on()
        entity.async_write_ha_state.assert_called()


# ---------------------------------------------------------------------------
# async_turn_off
# ---------------------------------------------------------------------------

class TestTurnOff:
    @pytest.mark.asyncio
    async def test_sends_none_brightness(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.SLEEP
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_off()
        args = mock_device.set_mode.call_args[0]
        assert args[1] == GDBrightness.NONE

    @pytest.mark.asyncio
    async def test_preserves_current_effect_in_command(self, mock_device, mock_coordinator):
        mock_device.effect = GDEffect.AWAKE
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_off()
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.AWAKE

    @pytest.mark.asyncio
    async def test_uses_none_effect_when_device_effect_is_none(self, mock_device, mock_coordinator):
        mock_device.effect = None
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_off()
        args = mock_device.set_mode.call_args[0]
        assert args[0] == GDEffect.NONE

    @pytest.mark.asyncio
    async def test_requests_coordinator_refresh(self, mock_device, mock_coordinator):
        entity = make_light(mock_device, mock_coordinator)
        await entity.async_turn_off()
        mock_coordinator.async_request_refresh.assert_called_once()
