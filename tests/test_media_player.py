"""Tests for GlowdreamingMediaPlayer entity."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, AsyncMock

from homeassistant.components.media_player import MediaPlayerState, MediaPlayerEntityFeature, MediaType

from custom_components.glowdreaming.media_player import GlowdreamingMediaPlayer
from custom_components.glowdreaming.glowdreaming_api.const import GDSound, GDVolume


def make_player(mock_device, mock_coordinator) -> GlowdreamingMediaPlayer:
    entity = object.__new__(GlowdreamingMediaPlayer)
    entity._device = mock_device
    entity.coordinator = mock_coordinator
    entity.async_write_ha_state = MagicMock()
    entity._last_volume = GDVolume.LOW
    return entity


# ---------------------------------------------------------------------------
# supported_features
# ---------------------------------------------------------------------------

class TestSupportedFeatures:
    def test_has_volume_set(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert entity._attr_supported_features & MediaPlayerEntityFeature.VOLUME_SET

    def test_has_pause(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert entity._attr_supported_features & MediaPlayerEntityFeature.PAUSE

    def test_has_play(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert entity._attr_supported_features & MediaPlayerEntityFeature.PLAY


class TestMediaContentType:
    def test_content_type_is_music(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert entity._attr_media_content_type == MediaType.MUSIC

    def test_media_title_is_set(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert entity._attr_media_title is not None


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

    def test_idle_when_volume_zero(self, mock_device, mock_coordinator):
        mock_device.volume = 0
        entity = make_player(mock_device, mock_coordinator)
        assert entity.state == MediaPlayerState.IDLE

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
# source_list / source
# ---------------------------------------------------------------------------

class TestSourceList:
    def test_contains_white_noise(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert "White_noise" in entity.source_list

    def test_length_matches_gdsound_enum(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        assert len(entity.source_list) == len(GDSound)


class TestSource:
    def test_none_when_sound_is_none(self, mock_device, mock_coordinator):
        mock_device._sound = None
        entity = make_player(mock_device, mock_coordinator)
        assert entity.source is None

    def test_white_noise_when_sound_set(self, mock_device, mock_coordinator):
        mock_device._sound = GDSound.WHITE_NOISE
        entity = make_player(mock_device, mock_coordinator)
        assert entity.source == "White_noise"


# ---------------------------------------------------------------------------
# async_media_pause  (turns sound off, saves last volume)
# ---------------------------------------------------------------------------

class TestMediaPause:
    @pytest.mark.asyncio
    async def test_calls_set_mode_with_volume_none(self, mock_device, mock_coordinator):
        mock_device.volume_level = GDVolume.HIGH
        entity = make_player(mock_device, mock_coordinator)
        await entity.async_media_pause()
        mock_device.set_mode.assert_called_once_with(
            mock_device.effect,
            mock_device.brightness_level,
            GDVolume.NONE,
            mock_device.humidifier,
        )

    @pytest.mark.asyncio
    async def test_saves_last_volume_before_muting(self, mock_device, mock_coordinator):
        mock_device.volume_level = GDVolume.HIGH
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.LOW
        await entity.async_media_pause()
        assert entity._last_volume == GDVolume.HIGH

    @pytest.mark.asyncio
    async def test_does_not_overwrite_last_volume_when_already_none(self, mock_device, mock_coordinator):
        """If volume_level is already NONE, _last_volume should not be overwritten."""
        mock_device.volume_level = GDVolume.NONE
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.MEDIUM
        await entity.async_media_pause()
        assert entity._last_volume == GDVolume.MEDIUM

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        mock_device.volume_level = GDVolume.LOW
        entity = make_player(mock_device, mock_coordinator)
        await entity.async_media_pause()
        entity.async_write_ha_state.assert_called_once()


# ---------------------------------------------------------------------------
# async_media_play  (turns sound on at last volume)
# ---------------------------------------------------------------------------

class TestMediaPlay:
    @pytest.mark.asyncio
    async def test_restores_last_volume(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.HIGH
        await entity.async_media_play()
        mock_device.set_mode.assert_called_once_with(
            mock_device.effect,
            mock_device.brightness_level,
            GDVolume.HIGH,
            mock_device.humidifier,
        )

    @pytest.mark.asyncio
    async def test_defaults_to_low_when_last_volume_is_none(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.NONE
        await entity.async_media_play()
        mock_device.set_mode.assert_called_once_with(
            mock_device.effect,
            mock_device.brightness_level,
            GDVolume.LOW,
            mock_device.humidifier,
        )

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.LOW
        await entity.async_media_play()
        entity.async_write_ha_state.assert_called_once()


# ---------------------------------------------------------------------------
# async_set_volume_level
# ---------------------------------------------------------------------------

class TestSetVolumeLevel:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("ha_volume,expected_gd", [
        (0.0, GDVolume.NONE),
        (0.1, GDVolume.LOW),
        (1 / 3, GDVolume.LOW),
        (0.5, GDVolume.MEDIUM),
        (2 / 3, GDVolume.MEDIUM),
        (0.8, GDVolume.HIGH),
        (1.0, GDVolume.HIGH),
    ])
    async def test_volume_mapping(self, ha_volume, expected_gd, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        await entity.async_set_volume_level(ha_volume)
        mock_device.set_mode.assert_called_once_with(
            mock_device.effect,
            mock_device.brightness_level,
            expected_gd,
            mock_device.humidifier,
        )

    @pytest.mark.asyncio
    async def test_saves_last_volume_when_non_zero(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.LOW
        await entity.async_set_volume_level(1.0)
        assert entity._last_volume == GDVolume.HIGH

    @pytest.mark.asyncio
    async def test_does_not_save_last_volume_when_zero(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        entity._last_volume = GDVolume.MEDIUM
        await entity.async_set_volume_level(0.0)
        assert entity._last_volume == GDVolume.MEDIUM

    @pytest.mark.asyncio
    async def test_writes_ha_state(self, mock_device, mock_coordinator):
        entity = make_player(mock_device, mock_coordinator)
        await entity.async_set_volume_level(0.5)
        entity.async_write_ha_state.assert_called_once()
