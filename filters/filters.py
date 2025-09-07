from typing import List, Optional, Dict, Any, Callable
from .base_filter import Filter
from functools import wraps

class Filters:
    def __init__(self, bot: Any):
        self.bot = bot

    def state(self, state: str) -> Filter:
        return Filter(
            lambda update: (
                ("message" in update 
                 and "from" in update["message"] 
                 and self.bot.get_user_state(update["message"]["from"]["id"]) == state)
                or
                ("callback_query" in update 
                 and "from" in update["callback_query"]
                 and self.bot.get_user_state(update["callback_query"]["from"]["id"]) == state)
            )
        )

    @property
    def any_message(self) -> Filter:
        return Filter(lambda update: "message" in update)

    @property
    def private(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "private"
            )
        )

    @property
    def group(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "group"
            )
        )

    @property
    def channel(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "chat" in update["message"]
                and update["message"]["chat"]["type"] == "channel"
            )
        )

    @property
    def text(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "text" in update["message"]
                and isinstance(update["message"]["text"], str)
            )
        )

    @property
    def video(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "video" in update["message"]
            )
        )

    @property
    def location(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "location" in update["message"]
            )
        )

    @property
    def photo(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "photo" in update["message"]
            )
        )

    @property
    def reply(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "reply_to_message" in update["message"]
            )
        )

    @property
    def supergroup_chat_created(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "supergroup_chat_created" in update["message"]
            )
        )

    @property
    def pinned_message(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "pinned_message" in update["message"]
            )
        )

    @property
    def new_chat_title(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_title" in update["message"]
            )
        )

    @property
    def new_chat_photo(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_photo" in update["message"]
            )
        )

    @property
    def new_chat_members(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "new_chat_members" in update["message"]
            )
        )

    @property
    def media(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and (
                    "photo" in update["message"]
                    or "video" in update["message"]
                    or "document" in update["message"]
                    or "audio" in update["message"]
                    or "voice" in update["message"]
                )
            )
        )

    @property
    def left_chat_member(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "left_chat_member" in update["message"]
            )
        )

    @property
    def group_chat_created(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "group_chat_created" in update["message"]
            )
        )

    @property
    def forward(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "forward_from" in update["message"]
            )
        )

    @property
    def document(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "document" in update["message"]
            )
        )

    @property
    def contact(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "contact" in update["message"]
            )
        )

    @property
    def channel_chat_created(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "channel_chat_created" in update["message"]
            )
        )

    @property
    def caption(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "caption" in update["message"]
            )
        )

    @property
    def all(self) -> Filter:
        return Filter(lambda update: True)

    @property
    def audio(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "audio" in update["message"]
            )
        )

    @property
    def sticker(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "sticker" in update["message"]
            )
        )

    @property
    def voice(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update 
                and "voice" in update["message"]
            )
        )

    def command(self, command: str, username: str = None, exact_match: bool = False) -> Filter:
            def async_filter_func(update: Dict) -> bool:
                if not ("message" in update and "text" in update["message"]):
                    return False
                
                text = update["message"]["text"].strip()
                
                patterns = [
                    f"/{command}",
                    f"/{command}@{username}" if username else None,
                    f"/{command} ",
                    f"/{command}@{username} " if username else None
                ]
                
                valid_patterns = [p for p in patterns if p is not None]
                
                if exact_match:
                    return text == f"/{command}" or (username and text == f"/{command}@{username}")
                else:
                    return any(
                        text.startswith(pattern) or 
                        text == f"/{command}" or 
                        (username and text == f"/{command}@{username}")
                        for pattern in valid_patterns
                    )

            return Filter(async_filter_func)

    def pattern(self, pattern: str) -> Filter:
        if pattern.startswith('/'):
            return self.command(pattern[1:])
        
        if '|' in pattern:
            patterns = [p.strip() for p in pattern.split('|')]
            return Filter(
                lambda update: (
                    "message" in update
                    and "text" in update["message"]
                    and any(
                        update["message"]["text"].startswith(p)
                        for p in patterns
                    )
                )
            )
        
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and update["message"]["text"].startswith(pattern)
            )
        )

    def multi_command(self, commands: List[str]) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and any(
                    update["message"]["text"].startswith(f"/{cmd} ")
                    or update["message"]["text"].startswith(f"/{cmd}@")
                    or update["message"]["text"] == f"/{cmd}"
                    for cmd in commands
                )
            )
        )

    def callback_query(self, data: Optional[str] = None) -> Filter:
        return Filter(
            lambda update: (
                "callback_query" in update
                and (data is None or update["callback_query"].get("data") == data)
            )
        )

    def callback_query_data_startswith(self, prefix: str) -> Filter:
        return Filter(
            lambda update: (
                "callback_query" in update
                and update["callback_query"].get("data", "").startswith(prefix)
            )
        )

    @property
    def callback_query_all(self) -> Filter:
        return Filter(lambda update: "callback_query" in update)

    @property
    def pre_checkout_query(self) -> Filter:
        return Filter(lambda update: "pre_checkout_query" in update)

    @property
    def successful_payment(self) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "successful_payment" in update["message"]
            )
        )

    def contains_keywords(self, keywords: List[str]) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and any(
                    keyword.lower() in update["message"]["text"].lower()
                    for keyword in keywords
                )
            )
        )

    def long_message(self, min_length: int) -> Filter:
        return Filter(
            lambda update: (
                "message" in update
                and "text" in update["message"]
                and len(update["message"]["text"]) >= min_length
            )
        )
    
    def custom(self, filter_func: Callable[[Dict], bool]) -> Filter:
        @wraps(filter_func)
        def wrapper(update: Dict) -> bool:
            try:
                return bool(filter_func(update))
            except Exception:
                return False
        return Filter(wrapper)