"""Tests for GlowdreamingDevice: state parsing, command generation, tracking."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from custom_components.glowdreaming.glowdreaming_api.device import GlowdreamingDevice
from custom_components.glowdreaming.glowdreaming_api.const import (
    GDBrightness,
    GDEffect,
    GDHumidifier,
    GDSound,
    GDVolume,
)


def make_device() -> GlowdreamingDevice:
    return GlowdreamingDevice(MagicMock())


def parse(hex_str: str) -> GlowdreamingDevice:
    """Create a device and feed it a hex packet via _refresh_data."""
    d = make_device()
    d._refresh_data(bytearray.fromhex(hex_str))
    return d


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_numeric_fields_are_none(self):
        d = make_device()
        assert d.brightness is None
        assert d.volume is None
        assert d.power is None
        assert d.humidifier_timer is None

    def test_enum_fields_are_none(self):
        d = make_device()
        assert d.effect is None
        assert d.humidifier is None
        assert d.device_lock is None

    def test_tracking_fields_are_none(self):
        d = make_device()
        assert d.last_effect is None
        assert d.last_brightness is None

    def test_sound_is_none(self):
        """_sound must be initialised so the property never raises AttributeError."""
        d = make_device()
        assert d.sound is None

    def test_connected_false_without_client(self):
        d = make_device()
        assert d.connected is False


# ---------------------------------------------------------------------------
# _refresh_data – light effects
# ---------------------------------------------------------------------------

class TestRefreshDataLight:
    def test_all_off(self):
        d = parse("000000000000ffff0000")
        assert d.brightness == 0
        assert d.effect == GDEffect.NONE
        assert d.last_effect is None  # never updated while NONE

    def test_sleep_low(self):
        d = parse("0a0000000000ffff0000")
        assert d.brightness == 10
        assert d.effect == GDEffect.SLEEP
        assert d.brightness_level == GDBrightness.LOW
        assert d.last_effect == GDEffect.SLEEP
        assert d.last_brightness == GDBrightness.LOW

    def test_sleep_medium(self):
        d = parse("280000000000ffff0000")
        assert d.brightness == 40
        assert d.effect == GDEffect.SLEEP
        assert d.brightness_level == GDBrightness.MEDIUM
        assert d.last_brightness == GDBrightness.MEDIUM

    def test_sleep_high(self):
        d = parse("640000000000ffff0000")
        assert d.brightness == 100
        assert d.effect == GDEffect.SLEEP
        assert d.brightness_level == GDBrightness.HIGH
        assert d.last_brightness == GDBrightness.HIGH

    def test_awake_low(self):
        d = parse("000a00000000ffff0000")
        assert d.brightness == 10
        assert d.effect == GDEffect.AWAKE
        assert d.last_effect == GDEffect.AWAKE

    def test_awake_medium(self):
        d = parse("002800000000ffff0000")
        assert d.brightness == 40
        assert d.effect == GDEffect.AWAKE

    def test_awake_high(self):
        d = parse("006400000000ffff0000")
        assert d.brightness == 100
        assert d.effect == GDEffect.AWAKE


# ---------------------------------------------------------------------------
# _refresh_data – volume
# ---------------------------------------------------------------------------

class TestRefreshDataVolume:
    def test_off(self):
        d = parse("000000000000ffff0000")
        assert d.volume == 0
        assert d.volume_level == GDVolume.NONE

    def test_low(self):
        d = parse("000000010000ffff0000")
        assert d.volume == 1
        assert d.volume_level == GDVolume.LOW

    def test_medium(self):
        d = parse("000000020000ffff0000")
        assert d.volume == 2
        assert d.volume_level == GDVolume.MEDIUM

    def test_high(self):
        d = parse("000000030000ffff0000")
        assert d.volume == 3
        assert d.volume_level == GDVolume.HIGH


# ---------------------------------------------------------------------------
# _refresh_data – humidifier
# The parser checks byte[4] == 1 for "on", then byte[9] for mode.
# ---------------------------------------------------------------------------

class TestRefreshDataHumidifier:
    def test_off(self):
        d = parse("000000000000ffff0000")
        assert d.humidifier == GDHumidifier.NONE

    def test_2hr(self):
        # byte[4]=01 (on), byte[9]=01 → TWO
        d = parse("00000000010000780001")
        assert d.humidifier == GDHumidifier.TWO

    def test_4hr(self):
        # byte[4]=01 (on), byte[9]=02 → FOUR
        d = parse("00000000010000f00002")
        assert d.humidifier == GDHumidifier.FOUR

    def test_continuous(self):
        # byte[4]=01 (on), byte[9]=00 (neither 1 nor 2) → CONTINUOUS
        d = parse("00000000010000000000")
        assert d.humidifier == GDHumidifier.CONTINUOUS

    def test_timer_is_parsed(self):
        # byte[7] carries the remaining timer value
        d = parse("00000000010000780001")
        assert d.humidifier_timer == 0x78


# ---------------------------------------------------------------------------
# _refresh_data – bad / short data (early-return paths, no crash)
# ---------------------------------------------------------------------------

class TestRefreshDataEdgeCases:
    def test_empty_bytearray_does_not_raise(self):
        d = make_device()
        d._refresh_data(bytearray())
        assert d.brightness is None  # state unchanged

    def test_short_packet_does_not_raise(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("0a0000"))
        assert d.brightness is None  # state unchanged

    def test_none_input_does_not_raise(self):
        d = make_device()
        d._refresh_data(None)
        assert d.brightness is None  # state unchanged

    def test_short_packet_does_not_overwrite_previous_state(self):
        d = parse("0a0000000000ffff0000")  # sleep low
        assert d.effect == GDEffect.SLEEP
        d._refresh_data(bytearray.fromhex("0a00"))  # too short
        assert d.effect == GDEffect.SLEEP  # unchanged


# ---------------------------------------------------------------------------
# last_effect / last_brightness tracking
# ---------------------------------------------------------------------------

class TestTracking:
    def test_last_effect_not_cleared_by_off(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("0a0000000000ffff0000"))  # sleep low
        assert d.last_effect == GDEffect.SLEEP
        d._refresh_data(bytearray.fromhex("000000000000ffff0000"))  # off
        assert d.last_effect == GDEffect.SLEEP  # preserved

    def test_last_effect_updates_sleep_to_awake(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("0a0000000000ffff0000"))  # sleep
        d._refresh_data(bytearray.fromhex("000a00000000ffff0000"))  # awake
        assert d.last_effect == GDEffect.AWAKE

    def test_last_brightness_not_cleared_by_off(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("640000000000ffff0000"))  # high
        assert d.last_brightness == GDBrightness.HIGH
        d._refresh_data(bytearray.fromhex("000000000000ffff0000"))  # off
        assert d.last_brightness == GDBrightness.HIGH  # preserved

    def test_last_brightness_updates_low_to_high(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("0a0000000000ffff0000"))  # low
        assert d.last_brightness == GDBrightness.LOW
        d._refresh_data(bytearray.fromhex("640000000000ffff0000"))  # high
        assert d.last_brightness == GDBrightness.HIGH

    def test_last_brightness_is_enum_not_raw_int(self):
        d = make_device()
        d._refresh_data(bytearray.fromhex("280000000000ffff0000"))  # medium (40)
        assert d.last_brightness == GDBrightness.MEDIUM
        assert isinstance(d.last_brightness, GDBrightness)


# ---------------------------------------------------------------------------
# brightness_level / volume_level property mappings
# ---------------------------------------------------------------------------

class TestPropertyMappings:
    @pytest.mark.parametrize("hex_str,expected", [
        ("0a0000000000ffff0000", GDBrightness.LOW),
        ("280000000000ffff0000", GDBrightness.MEDIUM),
        ("640000000000ffff0000", GDBrightness.HIGH),
        ("000000000000ffff0000", GDBrightness.NONE),
    ])
    def test_brightness_level(self, hex_str, expected):
        d = parse(hex_str)
        assert d.brightness_level == expected

    @pytest.mark.parametrize("hex_str,expected", [
        ("000000010000ffff0000", GDVolume.LOW),
        ("000000020000ffff0000", GDVolume.MEDIUM),
        ("000000030000ffff0000", GDVolume.HIGH),
        ("000000000000ffff0000", GDVolume.NONE),
    ])
    def test_volume_level(self, hex_str, expected):
        d = parse(hex_str)
        assert d.volume_level == expected

    def test_brightness_level_unknown_raw_returns_none(self):
        d = make_device()
        d._brightness = 99  # not 10, 40, or 100
        assert d.brightness_level == GDBrightness.NONE

    def test_volume_level_unknown_raw_returns_none(self):
        d = make_device()
        d._volume = 99
        assert d.volume_level == GDVolume.NONE


# ---------------------------------------------------------------------------
# get_command_string
# ---------------------------------------------------------------------------

class TestGetCommandString:
    def test_all_off(self):
        d = make_device()
        cmd = d.get_command_string(GDEffect.NONE, GDBrightness.NONE, GDVolume.NONE, GDHumidifier.NONE)
        assert cmd == "000000000000ffff0000"

    @pytest.mark.parametrize("brightness,expected_red", [
        (GDBrightness.LOW,    "0a"),
        (GDBrightness.MEDIUM, "28"),
        (GDBrightness.HIGH,   "64"),
    ])
    def test_sleep_brightness_levels(self, brightness, expected_red):
        d = make_device()
        cmd = d.get_command_string(GDEffect.SLEEP, brightness, GDVolume.NONE, GDHumidifier.NONE)
        assert cmd[:2] == expected_red   # red byte
        assert cmd[2:4] == "00"          # green byte

    @pytest.mark.parametrize("brightness,expected_green", [
        (GDBrightness.LOW,    "0a"),
        (GDBrightness.MEDIUM, "28"),
        (GDBrightness.HIGH,   "64"),
    ])
    def test_awake_brightness_levels(self, brightness, expected_green):
        d = make_device()
        cmd = d.get_command_string(GDEffect.AWAKE, brightness, GDVolume.NONE, GDHumidifier.NONE)
        assert cmd[:2] == "00"            # red byte
        assert cmd[2:4] == expected_green  # green byte

    @pytest.mark.parametrize("volume,expected_byte", [
        (GDVolume.LOW,    "01"),
        (GDVolume.MEDIUM, "02"),
        (GDVolume.HIGH,   "03"),
        (GDVolume.NONE,   "00"),
    ])
    def test_volume_byte(self, volume, expected_byte):
        d = make_device()
        cmd = d.get_command_string(GDEffect.NONE, GDBrightness.NONE, volume, GDHumidifier.NONE)
        assert cmd[6:8] == expected_byte  # byte[3]

    @pytest.mark.parametrize("humidifier,expected_bytes", [
        (GDHumidifier.NONE,       "0000ffff"),
        (GDHumidifier.TWO,        "01000078"),
        (GDHumidifier.FOUR,       "010000f0"),
        (GDHumidifier.CONTINUOUS, "1010ffff"),
    ])
    def test_humidifier_bytes(self, humidifier, expected_bytes):
        d = make_device()
        cmd = d.get_command_string(GDEffect.NONE, GDBrightness.NONE, GDVolume.NONE, humidifier)
        assert cmd[8:16] == expected_bytes  # bytes[4–7]

    def test_documented_examples(self):
        """Spot-check the exact packets from the CLAUDE.md examples."""
        d = make_device()
        cases = [
            (GDEffect.NONE,  GDBrightness.NONE,   GDVolume.NONE,   GDHumidifier.NONE, "000000000000ffff0000"),
            (GDEffect.SLEEP, GDBrightness.LOW,     GDVolume.NONE,   GDHumidifier.NONE, "0a0000000000ffff0000"),
            (GDEffect.SLEEP, GDBrightness.MEDIUM,  GDVolume.NONE,   GDHumidifier.NONE, "280000000000ffff0000"),
            (GDEffect.SLEEP, GDBrightness.HIGH,    GDVolume.NONE,   GDHumidifier.NONE, "640000000000ffff0000"),
            (GDEffect.NONE,  GDBrightness.NONE,    GDVolume.LOW,    GDHumidifier.NONE, "000000010000ffff0000"),
            (GDEffect.NONE,  GDBrightness.NONE,    GDVolume.MEDIUM, GDHumidifier.NONE, "000000020000ffff0000"),
            (GDEffect.NONE,  GDBrightness.NONE,    GDVolume.HIGH,   GDHumidifier.NONE, "000000030000ffff0000"),
        ]
        for effect, brightness, volume, humidifier, expected in cases:
            assert d.get_command_string(effect, brightness, volume, humidifier) == expected

    def test_command_is_20_hex_chars(self):
        """All commands must represent exactly 10 bytes."""
        d = make_device()
        cmd = d.get_command_string(GDEffect.SLEEP, GDBrightness.HIGH, GDVolume.HIGH, GDHumidifier.TWO)
        assert len(cmd) == 20
