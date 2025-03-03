"""generic bt device"""

from uuid import UUID
import asyncio
import logging
from contextlib import AsyncExitStack
from enum import StrEnum

from bleak import BleakClient
from bleak.exc import BleakError

from .const import *

class GDModeCommand(StrEnum):
    """Glowdreaming Mode Command"""
    OFF = "HEX1"
    NOISE_QUIET = "HEX2"
    NOISE_MEDIUM = "HEX3"
    NOISE_LOUD = "HEX4"

_LOGGER = logging.getLogger(__name__)

def get_mode_from_string(value: str):
    if value == "000000030001000000040044":
        return "Noise: Loud"
    else:
        return "Unknown"

def gatt_from_mode(mode: str):
    if mode == "off":
        return GDModeCommand.OFF
    elif mode == "noise_quiet":
        return GDModeCommand.NOISE_QUIET
    elif mode == "noise_medium":
        return GDModeCommand.NOISE_MEDIUM
    elif mode == "noise_loud":
        return GDModeCommand.NOISE_LOUD
    else:
        return ""

class GlowdreamingDevice:
    """Generic BT Device Class"""
    def __init__(self, ble_device):
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._client_stack = AsyncExitStack()
        self._lock = asyncio.Lock()
        self._state_hex: str = ""
        self._state: str = "unknown"

        self._volume = None
        self._brightness = None
        self._color = None

    async def update(self):
        _LOGGER.debug("Update called")
        response = await self.read_gatt(CHAR_CHARACTERISTIC)
        self._refresh_data(response)

    def _refresh_data(self, response_data) -> None:
        self._state_hex = response_data.hex()
        self._state = get_mode_from_string(response_data.hex())

    async def stop(self):
        pass

    @property
    def connected(self):
        return not self._client is None

    @property
    def state(self):
        return self._state

    @property
    def state_hex(self):
        return self._state_hex

    @property
    def volume(self):
        return self._volume

    @property
    def brightness(self):
        return self._brightness

    @property
    def color(self):
        return self._color

    async def get_client(self):
        def disconnected_callback(client):
            _LOGGER.info("Disconnected callback called!")
            self._client = None

        async with self._lock:
            if not self._client:
                _LOGGER.debug("Connecting")
                try:
                    self._client = await self._client_stack.enter_async_context(
                        BleakClient(self._ble_device, timeout=60, disconnected_callback=disconnected_callback))
                    _LOGGER.debug("Made new connection")
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on connect", exc_info=True)
                    raise
                except BleakError as exc:
                    _LOGGER.debug("Error on connect", exc_info=True)
                    raise
            else:
                _LOGGER.debug("Connection reused")


    async def set_mode(self, target_uuid, mode):
        await self.get_client()
        # gatt_from_mode(mode)
        # await self.write_gatt(target_uuid, gatt_from_mode(mode))
        _LOGGER.debug("Setting mode", target_uuid, mode)

    async def write_gatt(self, target_uuid, data):
        await self.get_client()
        uuid_str = "{" + target_uuid + "}"
        uuid = UUID(uuid_str)
        data_as_bytes = bytearray.fromhex(data)
        await self._client.write_gatt_char(uuid, data_as_bytes, True)

    async def read_gatt(self, target_uuid):
        await self.get_client()
        uuid_str = "{" + target_uuid + "}"
        uuid = UUID(uuid_str)
        data = await self._client.read_gatt_char(uuid)
        _LOGGER.debug("Reading Gatt", data)
        print(data)
        self._refresh_data(data)
        return data

    def update_from_advertisement(self, advertisement):
        pass
