from dataclasses import dataclass

@dataclass
class BotInfo:
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str
    language_code: str
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool