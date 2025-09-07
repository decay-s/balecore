class Video:
    def __init__(self, video_data: dict):
        self.file_id = video_data.get("file_id")
        self.file_unique_id = video_data.get("file_unique_id")
        self.width = video_data.get("width")
        self.height = video_data.get("height")
        self.duration = video_data.get("duration")
        self.file_size = video_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.width is not None:
            fields.append(f"width={self.width}")
        if self.height is not None:
            fields.append(f"height={self.height}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Video(\n    " + ",\n    ".join(fields) + "\n)"