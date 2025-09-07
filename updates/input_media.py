from typing import Optional, Dict, Any, Union

class InputMedia:
    def __init__(
        self,
        media_type: str,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> None:
        self.type = media_type
        self.media = media
        self.caption = caption
        self.parse_mode = parse_mode

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "type": self.type,
            "media": self.media,
        }
        if self.caption is not None:
            data["caption"] = self.caption
        if self.parse_mode is not None:
            data["parse_mode"] = self.parse_mode
        return data


class InputMediaPhoto(InputMedia):
    def __init__(self, media: str, caption: Optional[str] = None, parse_mode: Optional[str] = None):
        super().__init__("photo", media, caption, parse_mode)


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
        super().__init__("video", media, caption, parse_mode)
        self.width = width
        self.height = height
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self.width is not None:
            data["width"] = self.width
        if self.height is not None:
            data["height"] = self.height
        if self.duration is not None:
            data["duration"] = self.duration
        return data