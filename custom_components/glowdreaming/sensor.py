"""Support for Glowdreaming sensor."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Schema
from .coordinator import BTCoordinator
from .entity import BTEntity
from .glowdreaming_api.const import *

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Glowdreaming device based on a config entry."""
    coordinator: BTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GlowdreamingSensor(coordinator)])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service("write_gatt", Schema.WRITE_GATT.value, "write_gatt")
    platform.async_register_entity_service("read_gatt", Schema.READ_GATT.value, "read_gatt")
    platform.async_register_entity_service("set_mode", Schema.SET_MODE.value, "set_mode")
    platform.async_register_entity_service("set_sleep_brightness", Schema.SET_SLEEP_BRIGHTNESS.value, "set_sleep_brightness")
    platform.async_register_entity_service("set_awake_brightness", Schema.SET_AWAKE_BRIGHTNESS.value, "set_awake_brightness")
    platform.async_register_entity_service("set_volume", Schema.SET_VOLUME.value, "set_volume")

class GlowdreamingSensor(BTEntity, SensorEntity):
    """Representation of a Glowdreaming Sensor."""

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._name = "Sensor"
        self._attributes = {
            "mode_hex": "UNKNOWN"
        }

    def connection_state(self):
        if self._device.connected:
            return "Connected"
        else:
            return "Disconnected"

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._device.connected

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device._mode

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            **self._attributes,
            "connected": self.connection_state(),
            "volume": self._device.volume,
            "effect": self._device.effect,
            "brightness": self._device.brightness,
            "humidifier": self._device.humidifier,
            "humidifier_timer": self._device.humidifier_timer,
            "device_lock": self._device.device_lock,
            "mode": self._device._mode,
            "mode_hex": self._device._mode_hex
        }

    async def set_mode(self, light_effect, brightness, volume, humidifier):
        _LOGGER.debug("Setting effect to %s, brightness to %s, volume to %s, and humidifier to %s", light_effect, brightness, volume, humidifier)

        gd_effect = GDEffect(light_effect)
        gd_brightness = GDBrightness(brightness)
        gd_volume = GDVolume(volume)
        gd_humidifier = GDHumidifier(humidifier)

        await self._device.set_mode(gd_effect, gd_brightness, gd_volume, gd_humidifier)

        self.async_write_ha_state()

    async def set_awake_brightness(self, brightness):
        _LOGGER.debug("Setting awake brightness to %s", brightness)

        gd_effect = GDEffect.AWAKE
        gd_brightness = GDBrightness(brightness)
        gd_volume = self._device.volume_level
        gd_humidifier = self._device.humidifier

        await self._device.set_mode(gd_effect, gd_brightness, gd_volume, gd_humidifier)

        self.async_write_ha_state()

    async def set_sleep_brightness(self, brightness):
        _LOGGER.debug("Setting sleep brightness to %s", brightness)

        gd_effect = GDEffect.SLEEP
        gd_brightness = GDBrightness(brightness)
        gd_volume = self._device.volume_level
        gd_humidifier = self._device.humidifier

        await self._device.set_mode(gd_effect, gd_brightness, gd_volume, gd_humidifier)

        self.async_write_ha_state()

    async def set_volume(self, volume):
        _LOGGER.debug("Setting volume to %s", volume)

        gd_effect = self._device.effect
        gd_brightness = self._device.brightness_level
        gd_volume = GDVolume(volume)
        gd_humidifier = self._device.humidifier

        await self._device.set_mode(gd_effect, gd_brightness, gd_volume, gd_humidifier)

        self.async_write_ha_state()

    async def write_gatt(self, target_uuid, data):
        await self._device.write_gatt(target_uuid, data)
        self.async_write_ha_state()

    async def read_gatt(self, target_uuid):
        await self._device.read_gatt(target_uuid)
        self._attributes['mode_hex'] = self._device._mode_hex
        self.async_write_ha_state()
