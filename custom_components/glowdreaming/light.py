"""Support for Glowdreaming light."""
from __future__ import annotations

import logging

from homeassistant.components.light import (
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
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_supported_features = LightEntityFeature.EFFECT

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
    def effect(self) -> str | None:
        """Return the current light effect."""
        return self._device.effect

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return [e.value for e in GDEffect if e != GDEffect.NONE]

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the light, optionally with a specific effect."""
        effect_name = kwargs.get(ATTR_EFFECT)
        if effect_name:
            effect = GDEffect(effect_name)
        else:
            effect = self._device.effect
            if effect is None or effect == GDEffect.NONE:
                effect = GDEffect.SLEEP

        brightness = self._device.brightness_level
        if brightness == GDBrightness.NONE:
            brightness = GDBrightness.LOW

        await self._device.set_mode(effect, brightness, self._device.volume_level, self._device.humidifier)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light (set brightness to None/off)."""
        effect = self._device.effect or GDEffect.NONE
        await self._device.set_mode(effect, GDBrightness.NONE, self._device.volume_level, self._device.humidifier)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
