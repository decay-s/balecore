from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    VOICE = "voice"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    ANIMATION = "animation"
    POLL = "poll"
    DICE = "dice"
    VENUE = "venue"
    INVOICE = "invoice"
    SUCCESSFUL_PAYMENT = "successful_payment"