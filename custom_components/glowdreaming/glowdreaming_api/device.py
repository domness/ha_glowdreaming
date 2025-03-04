"""generic bt device"""

import asyncio
import logging
from uuid import UUID
from contextlib import AsyncExitStack

from bleak import BleakClient
from bleak.exc import BleakError
from .const import *

_LOGGER = logging.getLogger(__name__)

def get_mode_from_string(value: str):
    if value == "000000000001000000000044":
        return "Off"
    elif value == "000000010001000000040044":
        return "Sound: Low, Red: Off"
    elif value == "000000020001000000040044":
        return "Sound: Medium, Red: Off"
    elif value == "000000030001000000040044":
        return "Sound: High, Red: Off"
    elif value == "0a0000000001000000040044":
        return "Sound: Off, Red: Low"
    elif value == "280000000001000000040044":
        return "Sound: Off, Red: Medium"
    elif value == "0a0000010001000000040044":
        return "Sound: Low, Red: Low"
    elif value == "640000000001000000040044":
        return "Sound: Off, Red: High"
    elif value == "640000010001000000040044":
        return "Sound: Low, Red: High"
    elif value == "000a00000001000000040044":
        return "Sound: Off, Green: Low"
    elif value == "002800000001000000040044":
        return "Sound: Off, Green: Medium"
    elif value == "006400000001000000040044":
        return "Sound: Off, Green: High"
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

        self._mode_hex: str = "" # Temporary
        self._mode: str = "unknown" # Temporary

        self._power = None
        self._volume = None
        self._brightness = None
        self._color = None

    async def update(self):
        _LOGGER.debug("Update called")
        response = await self.read_gatt(CHAR_CHARACTERISTIC)
        self._refresh_data(response)

    async def stop(self):
        pass

    @property
    def connected(self):
        return not self._client is None

    @property
    def mode(self):
        return self._mode

    @property
    def mode_hex(self):
        return self._mode_hex

    @property
    def power(self):
        return self._power

    @property
    def sound(self) -> GDSound:
        return self._sound

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

    async def disconnect(self):
        async with self._lock:
            if self._client:
                _LOGGER.debug("Disconnecting")
                try:
                    await self._client.disconnect()
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on connect", exc_info=True)
                    raise
                except BleakError as exc:
                    _LOGGER.debug("Error on connect", exc_info=True)
                    raise
            else:
                _LOGGER.debug("Not connected, so nothing to disconnect")

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

    # async def set_mode(self, target_uuid, mode):
    #     await self.get_client()
    #     # TODO: Split all of this out into separate commands once worked out the permutations
    #     # gatt_from_mode(mode)
    #     # await self.send_command(gatt_from_mode(mode))
    #     _LOGGER.debug("Setting mode", target_uuid, mode)

    async def send_command(self, data) -> None:
        await self.write_gatt(CHAR_CHARACTERISTIC, data)
        await asyncio.sleep(0.75)
        await self.update()

    def update_from_advertisement(self, advertisement):
        pass

    def _refresh_data(self, response_data) -> None:
        _LOGGER.debug(f"Glowdreaming Hex {response_data}")
        hex_str = response_data.hex()

        self._mode_hex = hex_str
        self._mode = get_mode_from_string(hex_str)

        response = [hex(x) for x in response_data]

        # New World:
        power = bool(4 & int(response[9], 16)) # 4 is on
        volume = int(response[3], 16)

        red, green, blue = [int(x, 16) for x in response[0:3]]
        brightness = max(red, green, blue)
        red_color = 255 if red > 0 else 0
        green_color = 255 if green > 0 else 0
        blue_color = 255 if blue > 0 else 0

        self._power = power
        self._volume = volume
        self._sound = GDSound.white_noise
        self._color = (red_color, green_color, blue_color)
        self._brightness = round(255 / 100 * brightness)

        _LOGGER.debug(f"Power state is {self._power}")
        _LOGGER.debug(f"Volume state is {self._volume}")
        _LOGGER.debug(f"Sound state is {self._sound}")
        _LOGGER.debug(f"Color state is {self._color}")
        _LOGGER.debug(f"Brightness state is {self._brightness}")
