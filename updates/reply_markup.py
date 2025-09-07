class ReplyMarkup:
    def __init__(self, reply_markup_data: dict):
        self.inline_keyboard = reply_markup_data.get("inline_keyboard", [])
        self.keyboard = reply_markup_data.get("keyboard", [])
        self.remove_keyboard = reply_markup_data.get("remove_keyboard", False)
        self.force_reply = reply_markup_data.get("force_reply", False)

    def __str__(self):
        fields = []
        if self.inline_keyboard:
            fields.append(f"inline_keyboard={self.inline_keyboard}")
        if self.keyboard:
            fields.append(f"keyboard={self.keyboard}")
        if self.remove_keyboard:
            fields.append(f"remove_keyboard={self.remove_keyboard}")
        if self.force_reply:
            fields.append(f"force_reply={self.force_reply}")

        return "ReplyMarkup(\n    " + ",\n    ".join(fields) + "\n)"