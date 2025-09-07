from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime
from .user import User
from .chat import Chat
from .photo import Photo
from .video import Video
from .document import Document
from .audio import Audio
from .voice import Voice
from .sticker import Sticker
from .contact import Contact
from .location import Location
from .input_media_photo import InputMediaPhoto
from .input_media_video import InputMediaVideo

class Message:
    def __init__(self, message_data: Dict[str, Any]):
        self.message_id: Optional[int] = message_data.get("message_id")
        self.from_user: Optional[User] = User(message_data.get("from", {})) if message_data.get("from") else None
        self.date: Optional[datetime] = message_data.get("date")
        self.chat: Chat = Chat(message_data.get("chat", {}))
        self.text: Optional[str] = message_data.get("text")
        self.caption: Optional[str] = message_data.get("caption")
        self.data: Dict[str, Any] = message_data
        self.bot: Optional[Any] = None
        self.photo: Optional[Tuple[Photo, ...]] = tuple(Photo(p) for p in message_data.get("photo", [])) if message_data.get("photo") else None
        self.video: Optional[Video] = Video(message_data.get("video", {})) if message_data.get("video") else None
        self.document: Optional[Document] = Document(message_data.get("document", {})) if message_data.get("document") else None
        self.audio: Optional[Audio] = Audio(message_data.get("audio", {})) if message_data.get("audio") else None
        self.voice: Optional[Voice] = Voice(message_data.get("voice", {})) if message_data.get("voice") else None
        self.sticker: Optional[Sticker] = Sticker(message_data.get("sticker", {})) if message_data.get("sticker") else None
        self.contact: Optional[Contact] = Contact(message_data.get("contact", {})) if message_data.get("contact") else None
        self.location: Optional[Location] = Location(message_data.get("location", {})) if message_data.get("location") else None
        self.reply_to_message: Optional[Message] = Message(message_data.get("reply_to_message", {})) if message_data.get("reply_to_message") else None

    async def reply(self, text: str, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        result = await self.bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )
        return result

    async def reply_text(self, text: str, reply_markup=None, **kwargs) -> 'Message':
        return await self.reply(text, reply_markup, **kwargs)

    async def edit_text(self, text: str, reply_markup=None, **kwargs) -> bool:
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )

    async def edit_caption(self, caption: str, reply_markup=None, **kwargs) -> bool:
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.edit_message_caption(
            chat_id=self.chat.id,
            message_id=self.message_id,
            caption=caption,
            reply_markup=reply_markup,
            **kwargs
        )

    async def delete(self, **kwargs) -> bool:
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.delete_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def pin(self, disable_notification: bool = False, **kwargs) -> bool:
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            **kwargs
        )

    async def copy(self, chat_id: int, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def forward(self, chat_id: int, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.message_id,
            **kwargs
        )

    async def reply_photo(self, photo: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_photo(
            chat_id=self.chat.id,
            photo=photo,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_video(self, video: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_video(
            chat_id=self.chat.id,
            video=video,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_document(self, document: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_document(
            chat_id=self.chat.id,
            document=document,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_audio(self, audio: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_audio(
            chat_id=self.chat.id,
            audio=audio,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_voice(self, voice: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_voice(
            chat_id=self.chat.id,
            voice=voice,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_sticker(self, sticker: str, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_sticker(
            chat_id=self.chat.id,
            sticker=sticker,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_animation(self, animation: str, caption: Optional[str] = None, reply_markup=None, **kwargs) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_animation(
            chat_id=self.chat.id,
            animation=animation,
            caption=caption,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_contact(
        self,
        phone_number: str,
        first_name: Optional[str],
        last_name: Optional[str] = None,
        reply_markup=None,
        **kwargs
    ) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_contact(
            chat_id=self.chat.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_location(
        self,
        latitude: float,
        longitude: float,
        reply_markup=None,
        **kwargs
    ) -> 'Message':
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_location(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    async def reply_media_group(
        self,
        media: List[Union[InputMediaPhoto, InputMediaVideo]],
        reply_markup=None,
        **kwargs
    ) -> List['Message']:
        if not self.bot:
            raise ValueError("Bot instance not set on this Message object")
        return await self.bot.send_media_group(
            chat_id=self.chat.id,
            media=media,
            reply_to_message_id=self.message_id,
            reply_markup=reply_markup,
            **kwargs
        )

    def __str__(self) -> str:
        base_attrs = [
            f"chat={self.chat}",
            f"message_id={self.message_id}",
            f"date={self.date}",
            f"from_user={self.from_user}"
        ]
        
        media_attrs = []
        
        if self.caption is not None:
            media_attrs.append(f"caption='{self.caption}'")
        
        if self.sticker is not None:
            media_attrs.append(f"sticker={self.sticker}")
        elif self.photo is not None:
            photos_str = ",\n        ".join(str(photo) for photo in self.photo)
            media_attrs.append(f"photo=[\n        {photos_str}\n    ]")
        elif self.video is not None:
            media_attrs.append(f"video={self.video}")
        elif self.document is not None:
            media_attrs.append(f"document={self.document}")
        elif self.audio is not None:
            media_attrs.append(f"audio={self.audio}")
        elif self.voice is not None:
            media_attrs.append(f"voice={self.voice}")
        elif self.contact is not None:
            media_attrs.append(f"contact={self.contact}")
        elif self.location is not None:
            media_attrs.append(f"location={self.location}")
        
        if not media_attrs and self.text is not None:
            media_attrs.append(f"text='{self.text}'")
        
        if self.reply_to_message is not None:
            media_attrs.append(f"reply_to_message={self.reply_to_message}")
        
        all_attrs = base_attrs + media_attrs
        return f"Message({', '.join(all_attrs)})"