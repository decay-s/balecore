class File:
    def __init__(self, file_data: dict):
        self.file_id = file_data.get("file_id")
        self.file_unique_id = file_data.get("file_unique_id")
        self.file_size = file_data.get("file_size")
        self.file_path = file_data.get("file_path")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        if self.file_path is not None:
            fields.append(f"file_path={self.file_path}")
        
        return "File(\n    " + ",\n    ".join(fields) + "\n)"