class PhotoSize:
    def __init__(self, photo_data: dict):
        self.file_id = photo_data.get("file_id")
        self.file_unique_id = photo_data.get("file_unique_id")
        self.width = photo_data.get("width")
        self.height = photo_data.get("height")
        self.file_size = photo_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "PhotoSize(\n    " + ",\n    ".join(fields) + "\n)"