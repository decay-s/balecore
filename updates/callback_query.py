from .user import User
from .message import Message
from .reply_markup import ReplyMarkup

class CallbackQuery:
    def __init__(self, callback_query_data: dict):
        self.id = callback_query_data.get("id")
        self.from_user = User(callback_query_data.get("from", {}))
        message_data = callback_query_data.get("message", {})
        self.message = Message(message_data) if message_data else None
        self.inline_message_id = callback_query_data.get("inline_message_id")
        self.chat_instance = callback_query_data.get("chat_instance")
        self.data = callback_query_data.get("data")
        self.game_short_name = callback_query_data.get("game_short_name")
        
        reply_markup_data = callback_query_data.get("reply_markup", {})
        self.reply_markup = ReplyMarkup(reply_markup_data) if reply_markup_data else None

    def __str__(self):
        fields = []
        fields.append(f"id={self.id}")
        fields.append(f"from_user={self.from_user}")
        if self.message is not None:
            fields.append(f"message={self.message}")
        if self.inline_message_id is not None:
            fields.append(f"inline_message_id={self.inline_message_id}")
        if self.chat_instance is not None:
            fields.append(f"chat_instance={self.chat_instance}")
        if self.data is not None:
            fields.append(f"data={self.data}")
        if self.game_short_name is not None:
            fields.append(f"game_short_name={self.game_short_name}")
        if self.reply_markup is not None:
            fields.append(f"reply_markup={self.reply_markup}")

        return "CallbackQuery(\n    " + ",\n    ".join(fields) + "\n)"