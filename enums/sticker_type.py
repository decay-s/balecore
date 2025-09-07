from enum import Enum

class StickerType(str, Enum):
    REGULAR = "regular"
    MASK = "mask"
    CUSTOM_EMOJI = "custom_emoji"
    ANIMATED = "animated"
    VIDEO = "video"