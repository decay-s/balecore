from typing import Optional, Dict, Any
from .input_media import InputMedia

class InputMediaAudio(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None
    ) -> None:
        super().__init__("audio", media, caption, parse_mode)
        self.duration = duration
        self.performer = performer
        self.title = title

    def to_dict(self):
        data = super().to_dict()
        if self.duration:
            data["duration"] = self.duration
        if self.performer:
            data["performer"] = self.performer
        if self.title:
            data["title"] = self.title
        return data