"""Support for Glowdreaming light."""
from __future__ import annotations

import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BTCoordinator
from .entity import BTEntity
from .glowdreaming_api.const import GDBrightness, GDEffect

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: BTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingLight(coordinator)])


class GlowdreamingLight(BTEntity, LightEntity):
    """Representation of a Glowdreaming Light."""

    _attr_name = "Light"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.EFFECT

    # Maps device raw brightness values to HA 0-255 scale (3 discrete levels)
    _BRIGHTNESS_TO_HA = {10: 85, 40: 170, 100: 255}

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on (brightness > 0)."""
        if self._device.brightness is None:
            return None
        return self._device.brightness > 0

    @property
    def brightness(self) -> int | None:
        """Return brightness in 0-255 scale mapped from the 3 device levels."""
        raw = self._device.brightness
        if raw is None:
            return None
        return self._BRIGHTNESS_TO_HA.get(raw, 0)

    @property
    def effect(self) -> str | None:
        """Return the current light effect, or None when the light is off."""
        e = self._device.effect
        if e is None or e == GDEffect.NONE:
            return None
        return e

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return [e.value for e in GDEffect if e != GDEffect.NONE]

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the light, optionally with a specific effect."""
        effect_name = kwargs.get(ATTR_EFFECT)
        if effect_name:
            try:
                effect = GDEffect(effect_name)
            except ValueError:
                _LOGGER.warning("Ignoring unknown effect %r; restoring last known effect", effect_name)
                effect = self._device.last_effect or GDEffect.SLEEP
        else:
            effect = self._device.effect
            if effect is None or effect == GDEffect.NONE:
                effect = self._device.last_effect or GDEffect.SLEEP

        ha_brightness = kwargs.get(ATTR_BRIGHTNESS)
        if ha_brightness is not None:
            if ha_brightness <= 85:
                brightness = GDBrightness.LOW
            elif ha_brightness <= 170:
                brightness = GDBrightness.MEDIUM
            else:
                brightness = GDBrightness.HIGH
        else:
            brightness = self._device.brightness_level
            if brightness == GDBrightness.NONE:
                brightness = self._device.last_brightness or GDBrightness.LOW

        await self._device.set_mode(effect, brightness, self._device.volume_level, self._device.humidifier)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light (set brightness to None/off)."""
        effect = self._device.effect or GDEffect.NONE
        await self._device.set_mode(effect, GDBrightness.NONE, self._device.volume_level, self._device.humidifier)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
