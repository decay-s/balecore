class Contact:
    def __init__(self, contact_data: dict):
        self.phone_number = contact_data.get("phone_number")
        self.first_name = contact_data.get("first_name")
        self.last_name = contact_data.get("last_name")
        self.user_id = contact_data.get("user_id")
        self.vcard = contact_data.get("vcard")

    def __str__(self):
        fields = []
        fields.append(f"phone_number={self.phone_number}")
        fields.append(f"first_name={self.first_name}")
        if self.last_name is not None:
            fields.append(f"last_name={self.last_name}")
        if self.user_id is not None:
            fields.append(f"user_id={self.user_id}")
        if self.vcard is not None:
            fields.append(f"vcard={self.vcard}")
        
        return "Contact(\n    " + ",\n    ".join(fields) + "\n)"