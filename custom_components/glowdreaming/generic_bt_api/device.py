"""generic bt device"""

from uuid import UUID
import asyncio
import logging
from contextlib import AsyncExitStack

from bleak import BleakClient
from bleak.exc import BleakError

_LOGGER = logging.getLogger(__name__)

def get_mode_from_string(value: str):
    if value == "000000030001000000040044":
        return "Noise: Loud"
    else:
        return "Unknown"

class GenericBTDevice:
    """Generic BT Device Class"""
    def __init__(self, ble_device):
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._client_stack = AsyncExitStack()
        self._lock = asyncio.Lock()
        self._bt_mode: str = ""
        self._state: str = "unknown"

    async def update(self):
        pass

    async def stop(self):
        pass

    @property
    def connected(self):
        return not self._client is None

    @property
    def state(self):
        return self._state

    # @property
    # def mode(self):
    #     return self._mode

    @property
    def bt_mode(self):
        return self._bt_mode

    async def get_client(self):
        async with self._lock:
            if not self._client:
                _LOGGER.debug("Connecting")
                try:
                    self._client = await self._client_stack.enter_async_context(BleakClient(self._ble_device, timeout=30))
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on connect", exc_info=True)
                    raise IdealLedTimeout("Timeout on connect") from exc
                except BleakError as exc:
                    _LOGGER.debug("Error on connect", exc_info=True)
                    raise IdealLedBleakError("Error on connect") from exc
            else:
                _LOGGER.debug("Connection reused")

    async def set_mode(self, target_uuid, mode):
        await self.get_client()
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
        self._bt_mode = data.hex()
        self._state = get_mode_from_string(data.hex())
        return data

    def update_from_advertisement(self, advertisement):
        pass
