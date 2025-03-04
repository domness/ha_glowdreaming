"""Provides the DataUpdateCoordinator."""
from __future__ import annotations

import logging
import async_timeout
from datetime import timedelta

from bleak import BleakError
from bleak.backends.device import BLEDevice

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .glowdreaming_api.device import GlowdreamingDevice
from .const import DOMAIN, DEVICE_STARTUP_TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)

class BTCoordinator(DataUpdateCoordinator):
    """Class to manage fetching generic bt data."""

    def __init__(
        self, hass: HomeAssistant, logger: logging.Logger, device: GlowdreamingDevice, ble_device: BLEDevice,
            device_name: str, base_unique_id: str | None
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Glowdreaming",
            update_interval=timedelta(seconds=30),
        )
        self._device = device
        self.ble_device = ble_device
        self.device_name = device_name
        self.base_unique_id = base_unique_id

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                await self._device.update()
        except TimeoutError as exc:
            raise UpdateFailed(
                "Connection timed out while fetching data from device"
            ) from exc
        except BleakError as exc:
            raise UpdateFailed("Failed getting data from device") from exc

        return self._device
