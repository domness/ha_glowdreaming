"""Support for Glowdreaming media player (sound/volume)."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .glowdreaming_api.const import GDSound, GDVolume
from .entity import BTEntity
from .coordinator import BTCoordinator
from .const import DOMAIN

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Glowdreaming media player based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GlowdreamingMediaPlayer(coordinator)], True)


class GlowdreamingMediaPlayer(BTEntity, MediaPlayerEntity):
    """Representation of a Glowdreaming Media Player (sound output)."""

    _attr_name = "Sound"
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.PLAY
    )

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)
        self._paused = False
        self._last_volume = GDVolume.LOW

    @property
    def source_list(self) -> list[str] | None:
        """Return list of available sound sources."""
        return [sound.name.capitalize() for sound in GDSound]

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the playback state."""
        if self._device.volume is None:
            return None
        if self._device.volume > 0:
            return MediaPlayerState.PLAYING
        if self._paused:
            return MediaPlayerState.PAUSED
        return MediaPlayerState.OFF

    @property
    def source(self) -> str | None:
        """Return the current sound source."""
        sound = getattr(self._device, '_sound', None)
        if sound is None:
            return None
        return sound.name.capitalize()

    @property
    def volume_level(self) -> float | None:
        """Return volume level as a float 0.0–1.0."""
        if self._device.volume is None:
            return None
        return float(self._device.volume / 3)

    async def async_media_pause(self) -> None:
        """Pause playback by muting the volume, preserving state for resume."""
        if self._device.volume_level != GDVolume.NONE:
            self._last_volume = self._device.volume_level
        self._paused = True
        await self._device.set_mode(
            self._device.effect,
            self._device.brightness_level,
            GDVolume.NONE,
            self._device.humidifier,
        )
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Resume playback at the last known volume level."""
        self._paused = False
        volume = self._last_volume if self._last_volume != GDVolume.NONE else GDVolume.LOW
        await self._device.set_mode(
            self._device.effect,
            self._device.brightness_level,
            volume,
            self._device.humidifier,
        )
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the volume level (0.0–1.0) mapped to device Low/Medium/High."""
        self._paused = False
        if volume <= 0:
            gd_volume = GDVolume.NONE
        elif volume <= 1 / 3:
            gd_volume = GDVolume.LOW
        elif volume <= 2 / 3:
            gd_volume = GDVolume.MEDIUM
        else:
            gd_volume = GDVolume.HIGH
        if gd_volume != GDVolume.NONE:
            self._last_volume = gd_volume
        await self._device.set_mode(
            self._device.effect,
            self._device.brightness_level,
            gd_volume,
            self._device.humidifier,
        )
        self.async_write_ha_state()
