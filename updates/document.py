class Document:
    def __init__(self, document_data: dict):
        self.file_id = document_data.get("file_id")
        self.file_unique_id = document_data.get("file_unique_id")
        self.file_name = document_data.get("file_name")
        self.mime_type = document_data.get("mime_type")
        self.file_size = document_data.get("file_size")

    def __str__(self):
        fields = []
        fields.append(f"file_id={self.file_id}")
        fields.append(f"file_unique_id={self.file_unique_id}")
        if self.file_name is not None:
            fields.append(f"file_name={self.file_name}")
        if self.mime_type is not None:
            fields.append(f"mime_type={self.mime_type}")
        if self.file_size is not None:
            fields.append(f"file_size={self.file_size}")
        
        return "Document(\n    " + ",\n    ".join(fields) + "\n)"