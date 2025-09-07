from .message import Message
from .callback_query import CallbackQuery

class UpdateWrapper:
    def __init__(self, update: dict):
        self.update = update
        self.update_id = update.get("update_id")
        self.message = (
            Message(update.get("message", {}))
            if update.get("message")
            else None
        )
        callback_query_data = update.get("callback_query", {})
        self.callback_query = (
            CallbackQuery(callback_query_data)
            if callback_query_data
            else None
        )

    def __str__(self):
        fields = []
        fields.append(f"update_id={self.update_id}")
        if self.message is not None:
            fields.append(f"message={self.message}")
        if self.callback_query is not None:
            fields.append(f"callback_query={self.callback_query}")
        
        return "UpdateWrapper(\n    " + ",\n    ".join(fields) + "\n)"