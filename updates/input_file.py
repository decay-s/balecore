from typing import Optional, Dict

class InputFile:
    def __init__(self, file_path: str, file_name: Optional[str] = None, mime_type: Optional[str] = None):
        self.file_path = file_path
        self.file_name = file_name
        self.mime_type = mime_type

    def to_dict(self):
        data = {
            "file_path": self.file_path
        }
        if self.file_name:
            data["file_name"] = self.file_name
        if self.mime_type:
            data["mime_type"] = self.mime_type
        return data