class ChatParameter:
    def __init__(self, chat_data: dict):
        self.id = chat_data.get("id")
        self.type = chat_data.get("type")
        self.title = chat_data.get("title")
        self.username = chat_data.get("username")
        self.photo = chat_data.get("photo")
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
            fields.append(f"photo={self.photo}")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.invite_link is not None:
            fields.append(f"invite_link={self.invite_link}")
        if self.permissions is not None:
            fields.append(f"permissions={self.permissions}")
        
        return "ChatParameter(\n    " + ",\n    ".join(fields) + "\n)"