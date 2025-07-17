"""generic bt device"""

import asyncio
import logging
from uuid import UUID
from contextlib import AsyncExitStack

from bleak import BleakClient
from bleak.exc import BleakError
from .const import *

_LOGGER = logging.getLogger(__name__)

# def get_mode_from_string(value: str):
#     if value == "000000000001000000000044":
#         return "Off - All"
#     elif value == "000000010001000000040044":
#         return "Sound: Low"
#     elif value == "000000020001000000040044":
#         return "Sound: Medium"
#     elif value == "000000030001000000040044":
#         return "Sound: High"
#     elif value == "0a0000000001000000040044":
#         return "Sound: Off, Sleep: Low"
#     elif value == "280000000001000000040044":
#         return "Sound: Off, Sleep: Medium"
#     elif value == "0a0000010001000000040044":
#         return "Sound: Low, Sleep: Low"
#     elif value == "640000000001000000040044":
#         return "Sound: Off, Sleep: High"
#     elif value == "640000030001000000040044":
#         return "Sound: High, Sleep: High"
#     elif value == "640000010001000000040044":
#         return "Sound: Low, Sleep: High"
#     elif value == "000a00000001000000040044":
#         return "Sound: Off, Awake: Low"
#     elif value == "002800000001000000040044":
#         return "Sound: Off, Awake: Medium"
#     elif value == "006400000001000000040044":
#         return "Sound: Off, Awake: High"
#     else:
#         return "Unknown"

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
        self._effect = None
        self._humidifier = None
        self._humidifier_timer = None
        self._device_lock = None

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
    def humidifier(self):
        return self._humidifier

    @property
    def humidifier_timer(self):
        return self._humidifier_timer

    @property
    def device_lock(self):
        return self._device_lock

    @property
    def volume_level(self) -> GDVolume:
        if self._volume is None:
            return GDVolume.NONE
        elif self._volume == 1:
            return GDVolume.LOW
        elif self._volume == 2:
            return GDVolume.MEDIUM
        elif self._volume == 3:
            return GDVolume.HIGH
        else:
            return GDVolume.NONE

    @property
    def brightness(self):
        return self._brightness

    @property
    def brightness_level(self) -> GDBrightness:
        if self._brightness is None:
            return GDBrightness.NONE
        elif self._brightness == 10:
            return GDBrightness.LOW
        elif self._brightness == 40:
            return GDBrightness.MEDIUM
        elif self._brightness == 100:
            return GDBrightness.HIGH
        else:
            return GDBrightness.NONE

    @property
    def effect(self):
        return self._effect

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
        _LOGGER.debug(f"Reading Gatt {data}")
        print(data)
        self._refresh_data(data)
        return data

    async def set_mode(self, effect: GDEffect, brightness: GDBrightness, volume: GDVolume, humidifier: GDHumidifier):
        await self.get_client()
        command = self.get_command_string(effect, brightness, volume, humidifier)
        _LOGGER.debug(f"Setting mode {command}")
        await self.send_command(command)

    def update_from_advertisement(self, advertisement):
        pass

    async def send_command(self, data) -> None:
        await self.write_gatt(CHAR_CHARACTERISTIC, data)
        await asyncio.sleep(0.75)
        await self.update()

    def _refresh_data(self, response_data) -> None:
        _LOGGER.debug(f"Glowdreaming Hex {response_data}")
        hex_str = response_data.hex()

        self._mode_hex = hex_str

        response = [hex(x) for x in response_data]

        power = bool(4 & int(response[9], 16)) # 4 is on
        volume = int(response[3], 16)

        red, green, blue = [int(x, 16) for x in response[0:3]]
        brightness = max(red, green, blue)
        if red > 0:
            effect = GDEffect.SLEEP
        elif green > 0:
            effect = GDEffect.AWAKE
        else:
            effect = GDEffect.NONE

        # Determine humidifier state based on the hex string
        humidifier_on = int(response[4], 16)
        humidifier_option = int(response[9], 16)
        humidifier_timer = int(response[7], 16)

        if humidifier_on == 1:
            if humidifier_option == 1:
                humidifier = GDHumidifier.TWO
            elif humidifier_option == 2:
                humidifier = GDHumidifier.FOUR
            else:
                humidifier = GDHumidifier.CONTINUOUS
        else:
            humidifier = GDHumidifier.NONE

        self._power = power
        self._volume = volume
        self._sound = GDSound.WHITE_NOISE
        self._effect = effect
        self._brightness = brightness
        self._humidifier = humidifier
        self._humidifier_timer = humidifier_timer
        self._device_lock = None

        self._mode = f"Power: {power}, Volume: {volume}, Brightness: {brightness}, Effect: {effect}, Humidifier: {humidifier}, Timer: {humidifier_timer}"

        _LOGGER.debug(f"Power state is {self._power}")
        _LOGGER.debug(f"Volume state is {self._volume}")
        _LOGGER.debug(f"Sound state is {self._sound}")
        _LOGGER.debug(f"Effect state is {self._effect}")
        _LOGGER.debug(f"Brightness state is {self._brightness}")
        _LOGGER.debug(f"Humidifier state is {self._humidifier}")
        _LOGGER.debug(f"Humidifier timer state is {self._humidifier_timer}")

    def get_command_string(self, effect, brightness, volume, humidifier):
        _LOGGER.debug(f"Command string for: {effect}, {brightness}, {volume}, {humidifier}")

        # 000000000000ffff0000 off
        # 0a0000000000ffff0000 red light 1
        # 280000000000ffff0000 red light 2
        # 640000000000ffff0000 red light 3
        # 000000030000ffff0000 white noise 3
        # 000000020000ffff0000 white noise 2
        # 000000010000ffff0000 white noise 1

        if volume is GDVolume.HIGH:
            volume_level = "03"
        elif volume is GDVolume.MEDIUM:
            volume_level = "02"
        elif volume is GDVolume.LOW:
            volume_level = "01"
        else:
            volume_level = "00"

        if brightness is GDBrightness.LOW:
            brightness_hex = "0a"
        elif brightness is GDBrightness.MEDIUM:
            brightness_hex = "28"
        elif brightness is GDBrightness.HIGH:
            brightness_hex = "64"
        else:
            brightness_hex = "00"

        if effect is GDEffect.AWAKE:
            red_value = "00"
            green_value = brightness_hex # change
        elif effect is GDEffect.SLEEP:
            red_value = brightness_hex # change
            green_value = "00"
        else:
            red_value = "00"
            green_value = "00"

        if humidifier is GDHumidifier.TWO:
            humidifier_value = "01000078"
        elif humidifier is GDHumidifier.FOUR:
            humidifier_value = "010000f0"
        elif humidifier is GDHumidifier.CONTINUOUS:
            humidifier_value = "1010ffff"
        else:
            humidifier_value = "0000ffff"

        device_lock = "00" # or 01 if locked

        return "{red_value}{green_value}00{volume_level}{humidifier_value}{device_lock}00".format(volume_level=volume_level, red_value=red_value, green_value=green_value, humidifier_value=humidifier_value, device_lock=device_lock)
