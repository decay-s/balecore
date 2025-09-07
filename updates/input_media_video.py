from typing import Optional, Dict, Any
from .input_media import InputMedia

class InputMediaVideo(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None
    ) -> None:
        super().__init__(media_type="video", media=media, caption=caption, parse_mode=parse_mode)
        self.width: Optional[int] = width
        self.height: Optional[int] = height
        self.duration: Optional[int] = duration

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        if self.width is not None:
            data["width"] = self.width
        if self.height is not None:
            data["height"] = self.height
        if self.duration is not None:
            data["duration"] = self.duration
        return data