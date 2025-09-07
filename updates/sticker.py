class Sticker:
    def __init__(self, sticker_data: dict):
        self.file_id = sticker_data.get("file_id")
        self.file_unique_id = sticker_data.get("file_unique_id")
        self.width = sticker_data.get("width")
        self.height = sticker_data.get("height")
        self.is_animated = sticker_data.get("is_animated")
        self.is_video = sticker_data.get("is_video")
        self.emoji = sticker_data.get("emoji")
        self.set_name = sticker_data.get("set_name")
        self.mask_position = sticker_data.get("mask_position")
        self.file_size = sticker_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.is_animated is not None:
            fields.append(f"is_animated={self.is_animated}")
        if self.is_video is not None:
            fields.append(f"is_video={self.is_video}")
        if self.emoji is not None:
            fields.append(f"emoji={self.emoji}")
        if self.set_name is not None:
            fields.append(f"set_name={self.set_name}")
        if self.mask_position is not None:
            fields.append(f"mask_position={self.mask_position}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Sticker(\n    " + ",\n    ".join(fields) + "\n)"