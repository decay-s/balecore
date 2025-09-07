from .input_media import InputMedia
from typing import Optional

class InputMediaPhoto(InputMedia):
    def __init__(self, media: str, caption: Optional[str] = None, parse_mode: Optional[str] = None):
        super().__init__("photo", media, caption, parse_mode)