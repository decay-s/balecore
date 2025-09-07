class Audio:
    def __init__(self, audio_data: dict):
        self.file_id = audio_data.get("file_id")
        self.file_unique_id = audio_data.get("file_unique_id")
        self.duration = audio_data.get("duration")
        self.performer = audio_data.get("performer")
        self.title = audio_data.get("title")
        self.file_name = audio_data.get("file_name")
        self.mime_type = audio_data.get("mime_type")
        self.file_size = audio_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.duration is not None:
            fields.append(f"duration={self.duration}")
        if self.performer is not None:
            fields.append(f"performer={self.performer}")
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.file_name is not None:
            fields.append(f"file_name={self.file_name}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Audio(\n    " + ",\n    ".join(fields) + "\n)"