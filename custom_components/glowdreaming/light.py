"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_EFFECT, LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BTCoordinator
from .entity import BTEntity
from .glowdreaming_api.const import GDEffect

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
        self._effect = None
        self._attr_supported_color_modes = set()
        # self._attr_supported_features = LightEntityFeature.EFFECT
        # self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        # self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    # @property
    # def color_mode(self):
    #     return None

    # @property
    # def supported_color_modes(self):
    #     return []

    # @property
    # def supported_features(self):
    #     return SUPPORT_BRIGHTNESS | SUPPORT_EFFECT

    # @property
    # def brightness(self):
    #     return self._device.brightness

    @property
    def is_on(self) -> bool | None:
        return self._device.brightness > 0

    @property
    def effect(self):
        return self._device.effect

    # @property
    # def effect_list(self):
    #     return [e.value for e in GDEffect]

    # async def async_turn_on(self, **kwargs) -> None:
    #     """Instruct the light to turn on."""
    #     brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
    #     effect = kwargs.get(ATTR_EFFECT, self.effect)
    #     _LOGGER.debug(f"Effect changed to: {effect}")
    #     _LOGGER.debug(f"Brightness changed to: {brightness}")

    #     # value_in_range = math.ceil(scale_to_ranged_value(BRIGHTNESS_SCALE, (1,255), brightness))
    #     mapped_brightness = map_value_to_scale(brightness)
    #     _LOGGER.debug(f"Mapped brightness: {mapped_brightness}")
    #     await self._device.set_brightness(mapped_brightness, effect)

    #     # color = kwargs.get(ATTR_RGB_COLOR, self.rgb_color)
    #     # brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
    #     # # poweredOn = False
    #     # await self._device.set_color_brightness(color, brightness)
    #     # # if not self._device.power:
    #     # #     await self._device.power_on()
    #     # #     poweredOn = True
    #     # # Update this individual state, then the rest of the states
    #     self.async_write_ha_state()
    #     # # if poweredOn:
    #     # Update the rest of the data
    #     await self.coordinator.async_request_refresh()

    # async def async_turn_off(self, **kwargs) -> None:
    #     """Instruct the light to turn off."""
    #     _LOGGER.debug("Turning off light...")
    #     # if self._device.power:
    #     #     await self._device.power_off()
    #     #     # Update this individual state, then the rest of the states
    #     #     self.async_write_ha_state()
    #     #     # Update the data
    #     #     await self.coordinator.async_request_refresh()
