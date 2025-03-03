"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import STATE_UNKNOWN

from .const import DOMAIN, Schema
from .coordinator import GenericBTCoordinator
from .entity import GlowdreamingEntity

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: GenericBTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingSensor(coordinator)])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service("set_mode", Schema.SET_MODE.value, "set_mode")
    platform.async_register_entity_service("write_gatt", Schema.WRITE_GATT.value, "write_gatt")
    platform.async_register_entity_service("read_gatt", Schema.READ_GATT.value, "read_gatt")

class GlowdreamingSensor(GlowdreamingEntity, SensorEntity):
    """Representation of a Glowdreaming Sensor."""

    _attr_name = None

    def __init__(self, coordinator: GenericBTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)
        self._attributes = {
            "data": "UNKNOWN"
        }

    def connection_state(self):
        if self._device.connected:
            return "Connected"
        else:
            return "Disconnected"

    @property
    def is_on(self):
        return self._device.connected

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device.state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            **self._attributes,
            "connected": self.connection_state()
        }

    async def set_mode(self, target_uuid, mode):
        await self._device.set_mode(target_uuid, mode)
        self.async_write_ha_state()

    async def write_gatt(self, target_uuid, data):
        await self._device.write_gatt(target_uuid, data)
        self.async_write_ha_state()

    async def read_gatt(self, target_uuid):
        await self._device.read_gatt(target_uuid)
        self._attributes['data'] = self._device.bt_mode
        # self._attributes['mode'] = self._device.state
        self.async_write_ha_state()
