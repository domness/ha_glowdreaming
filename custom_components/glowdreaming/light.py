"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging
import math

from homeassistant.components.light import (SUPPORT_BRIGHTNESS, SUPPORT_EFFECT, ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ColorMode, PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import value_to_brightness
from homeassistant.util.percentage import percentage_to_ranged_value

from .const import DOMAIN, Schema
from .coordinator import BTCoordinator
from .entity import BTEntity
from .glowdreaming_api.const import GDEffect

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0
BRIGHTNESS_SCALE = (1, 100)

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
        self._effect = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def color_mode(self):
        return None

    @property
    def supported_color_modes(self):
        return []

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_EFFECT

    @property
    def brightness(self):
        return value_to_brightness(BRIGHTNESS_SCALE, self._device.brightness)

    @property
    def is_on(self) -> bool | None:
        """Return true if brightness is greater than zero"""
        return self._device.brightness > 0

    @property
    def effect(self):
        return self._device.effect

    @property
    def effect_list(self):
        return [e.value for e in GDEffect]

    # def update(self) -> None:
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     self._light.update()
    #     self._state = self._light.is_on()
    #     self._brightness = self._light.brightness

    async def async_turn_on(self, **kwargs) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
        value_in_range = math.ceil(percentage_to_ranged_value(BRIGHTNESS_SCALE, brightness))
        _LOGGER.debug(f"Value in range: {value_in_range}")
        await self._device.set_brightness(value_in_range)

        # color = kwargs.get(ATTR_RGB_COLOR, self.rgb_color)
        # brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
        # # poweredOn = False
        # await self._device.set_color_brightness(color, brightness)
        # # if not self._device.power:
        # #     await self._device.power_on()
        # #     poweredOn = True
        # # Update this individual state, then the rest of the states
        self.async_write_ha_state()
        # # if poweredOn:
        # Update the rest of the data
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Instruct the light to turn off."""
        _LOGGER.debug("Turning off light...")
        # if self._device.power:
        #     await self._device.power_off()
        #     # Update this individual state, then the rest of the states
        #     self.async_write_ha_state()
        #     # Update the data
        #     await self.coordinator.async_request_refresh()
