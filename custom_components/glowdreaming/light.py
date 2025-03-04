"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ColorMode, PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Schema
from .coordinator import BTCoordinator
from .entity import BTEntity

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: BTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingLight(coordinator)])

class GlowdreamingLight(BTEntity, LightEntity):
    """Representation of a Glowdreaming Light."""

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._name = "Light"
        self._state = None
        self._brightness = None
        self._color = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def color_mode(self):
        return ColorMode.RGB

    @property
    def supported_color_modes(self):
        return [ColorMode.RGB]

    @property
    def brightness(self):
        return self._device.brightness

    @property
    def rgb_color(self):
        return self._device.color

    @property
    def is_on(self) -> bool | None:
        """Return true if brightness is greater than zero"""
        return self._device.brightness > 0

    @property
    def color(self):
        """Return the color of the light."""
        return self._color

    @property
    def rgb_color(self):
        return self._device.color

    # def update(self) -> None:
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     self._light.update()
    #     self._state = self._light.is_on()
    #     self._brightness = self._light.brightness
