from .user import User

class ChatMember:
    def __init__(self, chat_member_data: dict):
        self.user = User(chat_member_data.get("user", {}))
        self.status = chat_member_data.get("status")
        self.custom_title = chat_member_data.get("custom_title")
        self.until_date = chat_member_data.get("until_date")
        self.can_be_edited = chat_member_data.get("can_be_edited")
        self.can_post_messages = chat_member_data.get("can_post_messages")
        self.can_edit_messages = chat_member_data.get("can_edit_messages")
        self.can_delete_messages = chat_member_data.get("can_delete_messages")
        self.can_restrict_members = chat_member_data.get("can_restrict_members")
        self.can_promote_members = chat_member_data.get("can_promote_members")
        self.can_change_info = chat_member_data.get("can_change_info")
        self.can_invite_users = chat_member_data.get("can_invite_users")
        self.can_pin_messages = chat_member_data.get("can_pin_messages")
        self.is_member = chat_member_data.get("is_member")
        self.can_send_messages = chat_member_data.get("can_send_messages")
        self.can_send_media_messages = chat_member_data.get("can_send_media_messages")
        self.can_send_polls = chat_member_data.get("can_send_polls")
        self.can_send_other_messages = chat_member_data.get("can_send_other_messages")
        self.can_add_web_page_previews = chat_member_data.get("can_add_web_page_previews")

    def __str__(self):
        fields = []
        fields.append(f"user={self.user}")
        if self.status is not None:
            fields.append(f"status={self.status}")
        if self.custom_title is not None:
            fields.append(f"custom_title={self.custom_title}")
        if self.until_date is not None:
            fields.append(f"until_date={self.until_date}")
        if self.can_be_edited is not None:
            fields.append(f"can_be_edited={self.can_be_edited}")
        if self.can_post_messages is not None:
            fields.append(f"can_post_messages={self.can_post_messages}")
        if self.can_edit_messages is not None:
            fields.append(f"can_edit_messages={self.can_edit_messages}")
        if self.can_delete_messages is not None:
            fields.append(f"can_delete_messages={self.can_delete_messages}")
        if self.can_restrict_members is not None:
            fields.append(f"can_restrict_members={self.can_restrict_members}")
        if self.can_promote_members is not None:
            fields.append(f"can_promote_members={self.can_promote_members}")
        if self.can_change_info is not None:
            fields.append(f"can_change_info={self.can_change_info}")
        if self.can_invite_users is not None:
            fields.append(f"can_invite_users={self.can_invite_users}")
        if self.can_pin_messages is not None:
            fields.append(f"can_pin_messages={self.can_pin_messages}")
        if self.is_member is not None:
            fields.append(f"is_member={self.is_member}")
        if self.can_send_messages is not None:
            fields.append(f"can_send_messages={self.can_send_messages}")
        if self.can_send_media_messages is not None:
            fields.append(f"can_send_media_messages={self.can_send_media_messages}")
        if self.can_send_polls is not None:
            fields.append(f"can_send_polls={self.can_send_polls}")
        if self.can_send_other_messages is not None:
            fields.append(f"can_send_other_messages={self.can_send_other_messages}")
        if self.can_add_web_page_previews is not None:
            fields.append(f"can_add_web_page_previews={self.can_add_web_page_previews}")
        
        return "ChatMember(\n    " + ",\n    ".join(fields) + "\n)"