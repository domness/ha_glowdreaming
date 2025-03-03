"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Schema
from .coordinator import GenericBTCoordinator
from .entity import GlowdreamingEntity

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

def get_state_from_string(value: str):
    if value == "000000030001000000040044":
        return "Noise: Loud"
    else:
        return "Unknown"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: GenericBTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingSensor(coordinator)])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service("write_gatt", Schema.WRITE_GATT.value, "write_gatt")
    platform.async_register_entity_service("read_gatt", Schema.READ_GATT.value, "read_gatt")


class GlowdreamingSensor(GlowdreamingEntity, SensorEntity):
    """Representation of a Glowdreaming Sensor."""

    _attr_name = None

    def __init__(self, coordinator: GenericBTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)
        self._native_value = ""
        self._attributes = {
            "data": "UNKNOWN",
            "mode": "Unknown"
        }

    @property
    def is_on(self):
        return self._device.connected

    @property
    def native_value(self):
        return self._native_value

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    async def write_gatt(self, target_uuid, data):
        await self._device.write_gatt(target_uuid, data)
        self.async_write_ha_state()

    async def read_gatt(self, target_uuid):
        gatt_value = await self._device.read_gatt(target_uuid)
        self._attributes['data'] = gatt_value.hex()
        self._attributes['mode'] = get_state_from_string(gatt_value.hex())
        self.async_write_ha_state()
