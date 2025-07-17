"""Constants"""
import voluptuous as vol
from enum import Enum

from homeassistant.helpers.config_validation import make_entity_service_schema
import homeassistant.helpers.config_validation as cv

DOMAIN = "glowdreaming"
DEVICE_STARTUP_TIMEOUT_SECONDS = 30

class Schema(Enum):
    """General used service schema definition"""

    SET_MODE = make_entity_service_schema(
        {
            vol.Required("light_effect"): cv.string,
            vol.Required("brightness"): cv.string,
            vol.Required("volume"): cv.string,
            vol.Required("humidifier"): cv.string
        }
    )
    SET_SLEEP_BRIGHTNESS = make_entity_service_schema(
        {
            vol.Required("brightness"): cv.string
        }
    )
    SET_AWAKE_BRIGHTNESS = make_entity_service_schema(
        {
            vol.Required("brightness"): cv.string
        }
    )
    SET_VOLUME = make_entity_service_schema(
        {
            vol.Required("volume"): cv.string
        }
    )
    WRITE_GATT = make_entity_service_schema(
        {
            vol.Required("target_uuid"): cv.string,
            vol.Required("data"): cv.string
        }
    )
    READ_GATT = make_entity_service_schema(
        {
            vol.Required("target_uuid"): cv.string
        }
    )
