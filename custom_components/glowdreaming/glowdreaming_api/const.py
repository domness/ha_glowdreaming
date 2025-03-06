"""constants"""
from enum import StrEnum, IntEnum

CHAR_CHARACTERISTIC = "c28909e04d8632a9914333c7c5e6ec29"

class GDSound(IntEnum):
    WHITE_NOISE = 0

class GDEffect(StrEnum):
    NONE = "None"
    AWAKE = "Awake"
    SLEEP = "Sleep"

class GDBrightness(StrEnum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class GDVolume(StrEnum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
