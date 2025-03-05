"""constants"""
from enum import StrEnum, IntEnum

CHAR_CHARACTERISTIC = "c28909e04d8632a9914333c7c5e6ec29"

# class GDModeCommand(StrEnum):
#     """Glowdreaming Mode Command"""
#     OFF = "000000000000ffff0000"
#     NOISE_QUIET = "000000010000ffff0000"
#     NOISE_MEDIUM = "000000020000ffff0000"
#     NOISE_LOUD = "000000030000ffff0000"

class GDSound(IntEnum):
    WHITE_NOISE = 0

class GDEffect(StrEnum):
    NONE = "None"
    AWAKE = "Awake"
    SLEEP = "Sleep"
