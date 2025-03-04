from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .glowdreaming_api.const import GDSound
from .entity import BTEntity
from .coordinator import BTCoordinator
from .const import *

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GlowdreamingMediaPlayer(coordinator)], True)


class GlowdreamingMediaPlayer(BTEntity, MediaPlayerEntity):
    """Representation of a Glowdreaming Media Player."""

    def __init__(self, coordinator: BTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._name = "Sound"

    @property
    def name(self):
        return self._name

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )

    @property
    def device_class(self) -> MediaPlayerDeviceClass | None:
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def source_list(self) -> list[str] | None:
        return [sound.name.capitalize() for sound in GDSound]

    @property
    def volume_level(self) -> float | None:
        return float(self._device.volume / 3)
