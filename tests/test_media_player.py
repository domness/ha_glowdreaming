"""Tests for GlowdreamingMediaPlayer entity."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from homeassistant.components.media_player import MediaPlayerState

from custom_components.glowdreaming.media_player import GlowdreamingMediaPlayer
from custom_components.glowdreaming.glowdreaming_api.const import GDSound


def make_player(mock_device, mock_coordinator) -> GlowdreamingMediaPlayer:
    entity = object.__new__(GlowdreamingMediaPlayer)
    entity._device = mock_device
    entity.coordinator = mock_coordinator
    entity.async_write_ha_state = MagicMock()
    return entity


# ---------------------------------------------------------------------------
# state
# ---------------------------------------------------------------------------

class TestState:
    def test_playing_when_volume_positive(self, mock_device, mock_coordinator):
        mock_device.volume = 1
        entity = make_player(mock_device, mock_coordinator)
        assert entity.state == MediaPlayerState.PLAYING

    def test_playing_at_max_volume(self, mock_device, mock_coordinator):
        mock_device.volume = 3
        entity = make_player(mock_device, mock_coordinator)
        assert entity.state == MediaPlayerState.PLAYING

    def test_off_when_volume_zero(self, mock_device, mock_coordinator):
        mock_device.volume = 0
        entity = make_player(mock_device, mock_coordinator)
        assert entity.state == MediaPlayerState.OFF

    def test_none_when_volume_none(self, mock_device, mock_coordinator):
        mock_device.volume = None
        entity = make_player(mock_device, mock_coordinator)
        assert entity.state is None


# ---------------------------------------------------------------------------
# volume_level
# ---------------------------------------------------------------------------

class TestVolumeLevel:
    def test_none_when_volume_none(self, mock_device, mock_coordinator):
        mock_device.volume = None
        entity = make_player(mock_device, mock_coordinator)
        assert entity.volume_level is None

    @pytest.mark.parametrize("raw,expected", [
        (0, 0.0),
        (1, 1 / 3),
        (2, 2 / 3),
        (3, 1.0),
    ])
    def test_volume_level_mapping(self, raw, expected, mock_device, mock_coordinator):
        mock_device.volume = raw
        entity = make_player(mock_device, mock_coordinator)
        assert pytest.approx(entity.volume_level) == expected


# ---------------------------------------------------------------------------
# source_list
# ---------------------------------------------------------------------------

class TestSourceList:
    def test_contains_white_noise(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert "White_noise" in entity.source_list

    def test_length_matches_gdsound_enum(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert len(entity.source_list) == len(GDSound)


# ---------------------------------------------------------------------------
# source
# ---------------------------------------------------------------------------

class TestSource:
    def test_none_when_sound_is_none(self, mock_device, mock_coordinator):
        mock_device._sound = None
        entity = make_player(mock_device, mock_coordinator)
        assert entity.source is None

    def test_white_noise_when_sound_set(self, mock_device, mock_coordinator):
        mock_device._sound = GDSound.WHITE_NOISE
        entity = make_player(mock_device, mock_coordinator)
        assert entity.source == "White_noise"
