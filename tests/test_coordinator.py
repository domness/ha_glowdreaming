"""Tests for BTCoordinator._async_update_data."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.glowdreaming.coordinator import BTCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed  # _UpdateFailed stub


def make_coordinator(mock_device) -> BTCoordinator:
    coord = object.__new__(BTCoordinator)
    coord._device = mock_device
    return coord


class TestAsyncUpdateData:
    @pytest.mark.asyncio
    async def test_success_calls_device_update(self, mock_device):
        coord = make_coordinator(mock_device)
        result = await coord._async_update_data()
        mock_device.update.assert_called_once()
        assert result is mock_device

    @pytest.mark.asyncio
    async def test_timeout_raises_update_failed(self, mock_device):
        mock_device.update = AsyncMock(side_effect=TimeoutError)
        coord = make_coordinator(mock_device)
        with pytest.raises(UpdateFailed, match="timed out"):
            await coord._async_update_data()

    @pytest.mark.asyncio
    async def test_bleak_error_raises_update_failed(self, mock_device):
        # BleakError is mocked as IOError in conftest
        mock_device.update = AsyncMock(side_effect=IOError("BLE failure"))
        coord = make_coordinator(mock_device)
        with pytest.raises(UpdateFailed, match="Failed getting data"):
            await coord._async_update_data()
