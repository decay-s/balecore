from typing import Optional, Dict, Any
from .input_media import InputMedia

class InputMediaAnimation(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        super().__init__("animation", media, caption, parse_mode)
        self.duration = duration
        self.width = width
        self.height = height

    def to_dict(self):
        data = super().to_dict()
        if self.duration:
            data["duration"] = self.duration
        if self.width:
            data["width"] = self.width
        if self.height:
            data["height"] = self.height
        return data