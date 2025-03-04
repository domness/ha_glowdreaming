"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Schema
from .coordinator import BTCoordinator
from .entity import GlowdreamingEntity

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: BTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingLight(coordinator)])

    # platform = entity_platform.async_get_current_platform()
    # platform.async_register_entity_service("set_mode", Schema.SET_MODE.value, "set_mode")
    # platform.async_register_entity_service("write_gatt", Schema.WRITE_GATT.value, "write_gatt")
    # platform.async_register_entity_service("read_gatt", Schema.READ_GATT.value, "read_gatt")

class GlowdreamingLight(GlowdreamingEntity, LightEntity):
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
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    @property
    def color(self):
        """Return the color of the light."""
        return self._color

    # def update(self) -> None:
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     self._light.update()
    #     self._state = self._light.is_on()
    #     self._brightness = self._light.brightness
