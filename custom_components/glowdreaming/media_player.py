"""Support for Glowdreaming media player (sound/volume)."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .glowdreaming_api.const import GDSound
from .entity import BTEntity
from .coordinator import BTCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
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

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

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
