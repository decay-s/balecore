class User:
    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.is_bot = user_data.get("is_bot")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.username = user_data.get("username")
        self.language_code = user_data.get("language_code")

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"is_bot={self.is_bot}")
        if self.first_name is not None:
            fields.append(f"first_name={self.first_name}")
        if self.last_name is not None:
            fields.append(f"last_name={self.last_name}")
        if self.username is not None:
            fields.append(f"username={self.username}")
        if self.language_code is not None:
            fields.append(f"language_code={self.language_code}")
        
        return "User(\n    " + ",\n    ".join(fields) + "\n)"