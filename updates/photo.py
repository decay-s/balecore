from .photo_size import PhotoSize
from typing import Optional, Tuple

class Photo:
    def __init__(self, photo_data: dict):
        self.file_id = photo_data.get("file_id")
        self.file_unique_id = photo_data.get("file_unique_id")
        self.width = photo_data.get("width")
        self.height = photo_data.get("height")
        self.file_size = photo_data.get("file_size")
        self.photo_sizes: Optional[Tuple[PhotoSize, ...]] = tuple(PhotoSize(p) for p in photo_data.get("photo_sizes", [])) if photo_data.get("photo_sizes") else None

    def __str__(self):
        fields = []
        if self.file_id:
            fields.append(f"file_id='{self.file_id}'")
        if self.file_unique_id:
            fields.append(f"file_unique_id='{self.file_unique_id}'")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Photo(" + ", ".join(fields) + ")"