from typing import Optional, Dict, Any
from .input_media import InputMedia

class InputMediaDocument(InputMedia):
    def __init__(
        self,
        media: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_content_type_detection: Optional[bool] = None
    ) -> None:
        super().__init__(media_type="document", media=media, caption=caption, parse_mode=parse_mode)
        self.disable_content_type_detection: Optional[bool] = disable_content_type_detection

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        if self.disable_content_type_detection is not None:
            data["disable_content_type_detection"] = self.disable_content_type_detection
        return data