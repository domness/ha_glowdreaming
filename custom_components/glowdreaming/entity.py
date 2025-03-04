"""An abstract class common to all Generic BT entities."""
from __future__ import annotations

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import device_registry as dr
from homeassistant.core import callback

from .coordinator import BTCoordinator
from .glowdreaming_api.device import GlowdreamingDevice

_LOGGER = logging.getLogger(__name__)

class BTEntity(CoordinatorEntity[BTCoordinator]):
    """Generic entity encapsulating common features of Generic BT device."""

    _device: GlowdreamingDevice
    _attr_has_entity_name = True

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device = coordinator.data
        self._address = coordinator.ble_device.address
        self._attr_unique_id = coordinator.base_unique_id
        self._attr_device_info = {
            "connections": {(dr.CONNECTION_BLUETOOTH, self._address)},
            "name": coordinator.device_name
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device = self.coordinator.data
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.connected
