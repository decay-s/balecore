from .photo_size import PhotoSize

class Chat:
    def __init__(self, chat_data: dict):
        self.id = chat_data.get("id")
        self.type = chat_data.get("type")
        self.title = chat_data.get("title")
        self.username = chat_data.get("username")
        
        photo_data = chat_data.get("photo", {})
        self.photo = (
            (
                PhotoSize({
                    "file_id": photo_data.get("small_file_id"),
                    "file_unique_id": photo_data.get("small_file_unique_id")
                }),
                PhotoSize({
                    "file_id": photo_data.get("big_file_id"),
                    "file_unique_id": photo_data.get("big_file_unique_id")
                })
            )
            if photo_data
            else None
        )
        
        self.description = chat_data.get("description")
        self.invite_link = chat_data.get("invite_link")
        self.permissions = chat_data.get("permissions")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"type={self.type}")
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.username is not None:
            fields.append(f"username={self.username}")
        if self.photo is not None:
            photos = ",\n        ".join(str(p) for p in self.photo)
            fields.append(f"photo=(\n        {photos}\n    )")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.invite_link is not None:
            fields.append(f"invite_link={self.invite_link}")
        if self.permissions is not None:
            fields.append(f"permissions={self.permissions}")
        
        return "Chat(\n    " + ",\n    ".join(fields) + "\n)"