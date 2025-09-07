class Voice:
    def __init__(self, voice_data: dict):
        self.file_id = voice_data.get("file_id")
        self.file_unique_id = voice_data.get("file_unique_id")
        self.duration = voice_data.get("duration")
        self.mime_type = voice_data.get("mime_type")
        self.file_size = voice_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Voice(\n    " + ",\n    ".join(fields) + "\n)"