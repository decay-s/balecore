import aiohttp
import asyncio
from typing import Callable, Optional, Dict, Any, List, Union, overload, Tuple, TypeVar, Sequence
from re import Pattern as re_Pattern
from collections import namedtuple, defaultdict
from ..filters.filters import Filters
from ..filters.base_filter import Filter
from ..updates.update_wrapper import UpdateWrapper
from ..updates.message import Message
import inspect
from ..updates import (
    UpdateWrapper,
    PhotoSize,
    InputMediaPhoto,
    InputMediaVideo
)
import json
from .transaction import Transaction
from .bot_info import BotInfo
from ..types.type import FILE_TYPES
import logging
import os
from io import BytesIO
import re
import base64

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

F = TypeVar('F', bound=Callable)
T = TypeVar('T', bound=Union[Callable[..., Any], 'Bot'])
MessageFilter = Union[
    Callable[[Dict[str, Any]], bool],
    Filter,
    Sequence[Callable[[Dict[str, Any]], bool]],
    re_Pattern[str]
]

ChatMemberInfo = namedtuple(
    'ChatMemberInfo',
    [
        'id', 'is_bot',
        'first_name',
        'last_name',
        'username',
        'status',
        'can_edit_messages',
        'can_delete_messages',
        'can_restrict_members',
        'can_change_info',
        'can_invite_users',
    ]
)

AdminInfo = namedtuple(
    'AdminInfo', [
        'id',
        'is_bot',
        'first_name',
        'last_name',
        'username',
        'status',
        'custom_title',
        'until_date',
        'can_be_edited',
        'can_post_messages',
        'can_edit_messages',
        'can_delete_messages',
        'can_restrict_members',
        'can_promote_members',
        'can_change_info',
        'can_invite_users',
        'can_pin_messages',
        'is_member',
        'can_send_messages',
        'can_send_media_messages',
        'can_send_polls',
        'can_send_other_messages'
    ]
)

class Bot:
    def __init__(
        self,
        token: str,
        url: Optional[str] = None,
        concurrency_limit: Optional[int] = 120,
        proxy: Optional[str] = None
    ) -> None:
        self.token = token
        self.base_url = url if url is not None else "https://tapi.bale.ai"
        self.handlers: List[Dict] = []
        self.callback_handlers: List[Dict] = []
        self.running = asyncio.Event()
        self.user_states: Dict[str, Dict[int, str]] = {}
        self.user_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.filters = Filters(self)
        self.initialize_handlers: List[Callable] = []
        self.concurrency_limit = concurrency_limit
        self.active_tasks = set()
        self.proxy = proxy
        self.semaphore = asyncio.Semaphore(concurrency_limit if concurrency_limit else 120)

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[Union[str, BytesIO]] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: Optional[bool] = None,
        secret_token: Optional[str] = None
    ) -> Dict[str, Any]:
        webhook_url = f"{self.base_url}/bot{self.token}/setWebhook"
        params = {"url": url}

        if ip_address:
            params["ip_address"] = ip_address
        if max_connections:
            params["max_connections"] = max_connections
        if allowed_updates:
            params["allowed_updates"] = allowed_updates
        if drop_pending_updates is not None:
            params["drop_pending_updates"] = drop_pending_updates
        if secret_token:
            params["secret_token"] = secret_token

        form = None
        if certificate:
            form = aiohttp.FormData()
            form.add_field("url", url)

            if isinstance(certificate, str):
                if os.path.isfile(certificate):
                    form.add_field(
                        name="certificate",
                        value=open(certificate, "rb"),
                        filename=os.path.basename(certificate),
                        content_type="application/octet-stream"
                    )
                else:
                    raise ValueError("Certificate file not found")
            elif isinstance(certificate, BytesIO):
                form.add_field(
                    name="certificate",
                    value=certificate,
                    filename="certificate.pem",
                    content_type="application/octet-stream"
                )
            else:
                raise ValueError("Invalid certificate type")

        try:
            async with aiohttp.ClientSession() as session:
                if form:
                    async with session.post(
                        webhook_url,
                        data=form,
                        proxy=self.proxy
                    ) as response:
                        return await response.json()
                else:
                    async with session.post(
                        webhook_url,
                        json=params,
                        proxy=self.proxy
                    ) as response:
                        return await response.json()
        except Exception as e:
            logger.error(f"Error setting webhook: {str(e)}")
            return {"ok": False, "description": str(e)}

    async def get_webhook_info(self) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/getWebhookInfo"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=self.proxy) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error getting webhook info: {str(e)}")
            return {"ok": False, "description": str(e)}

    async def delete_webhook(
        self,
        drop_pending_updates: Optional[bool] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/deleteWebhook"
        params = {}

        if drop_pending_updates is not None:
            params["drop_pending_updates"] = drop_pending_updates

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error deleting webhook: {str(e)}")
            return {"ok": False, "description": str(e)}

    async def get_chat(
        self,
        chat_id: Union[int, str]
    ) -> Union[str, Tuple]:
        url = f"{self.base_url}/bot{self.token}/getChat"
        params = {"chat_id": chat_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response_data = await response.json()

                    if not response_data.get("ok"):
                        logger.error("API Error in get_chat: %s", response_data.get("description"))
                        return tuple()

                    result = response_data["result"]
                    photo_data = result.get("photo", {})

                    photo = (
                        (
                            PhotoSize({
                                "file_id": photo_data.get("small_file_id"),
                                "file_unique_id": photo_data.get("small_file_unique_id")
                            }),
                            PhotoSize({
                                "file_id": photo_data.get("big_file_id"),
                                "file_unique_id": photo_data.get("big_file_unique_id")
                            })
                        )
                        if photo_data
                        else None
                    )

                    fields: List[Optional[str]] = [
                        f"id={result.get('id')}",
                        f"type={result.get('type')}",
                        f"title={result.get('title')}" if result.get('title') is not None else None,
                        f"username={result.get('username')}" if result.get('username') is not None else None,
                        f"first_name={result.get('first_name')}" if result.get('first_name') is not None else None,
                        f"last_name={result.get('last_name')}" if result.get('last_name') is not None else None,
                        f"photo={photo}" if photo is not None else None,
                        f"description={result.get('description')}" if result.get('description') is not None else None,
                        f"invite_link={result.get('invite_link')}" if result.get('invite_link') is not None else None,
                        f"permissions={result.get('permissions')}" if result.get('permissions') is not None else None
                    ]

                    filtered_fields = [field for field in fields if field is not None]
                    field_string = ",\n    ".join(filtered_fields)

                    output = f"Chat(\n    {field_string}\n)"
                    return output

        except Exception as e:
            logger.error(f"Error in get_chat: {str(e)}")
            return tuple()

    def set_user_state(self, user_id: int, state: str) -> None:
        if self.token not in self.user_states:
            self.user_states[self.token] = {}
        self.user_states[self.token][user_id] = state

    def get_user_state(self, user_id: int) -> Optional[str]:
        return self.user_states.get(self.token, {}).get(user_id)

    def clear_user_state(self, user_id: int) -> None:
        if self.token in self.user_states and user_id in self.user_states[self.token]:
            del self.user_states[self.token][user_id]

    @property
    def Message(self):
        return self._message_decorator

    def _message_decorator(
        self,
        __filter: Optional[MessageFilter] = None,
        __func: Optional[F] = None,
        *,
        commands: Optional[Union[str, List[str]]] = None,
        pattern: Optional[Union[str, re_Pattern[str]]] = None,
        content_types: Optional[List[str]] = None,
        state: Optional[str] = None,
        custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Union[Callable[[F], F], F]:
        if any([commands, pattern, content_types, state, custom_filter]):
            if __filter is not None:
                raise ValueError("Cannot use both positional filter and keyword arguments")

            filters = []

            if commands:
                if isinstance(commands, str):
                    commands = [commands]
                filters.append(self.filters.multi_command(commands))

            if pattern:
                if isinstance(pattern, str):
                    filters.append(self.filters.pattern(pattern))
                elif isinstance(pattern, re_Pattern):
                    filters.append(Filter(
                        lambda update: (
                            "message" in update
                            and "text" in update["message"]
                            and bool(pattern.match(update["message"]["text"]))
                        )
                    ))

            if content_types:
                type_filters = {
                    "text": self.filters.text,
                    "photo": self.filters.photo,
                    "video": self.filters.video,
                    "document": self.filters.document,
                    "audio": self.filters.audio,
                    "voice": self.filters.voice,
                    "sticker": self.filters.sticker,
                    "location": self.filters.location,
                    "contact": self.filters.contact
                }

                for content_type in content_types:
                    if content_type in type_filters:
                        filters.append(type_filters[content_type])

            if state:
                filters.append(self.filters.state(state))

            if custom_filter:
                filters.append(self.filters.custom(custom_filter))

            chosen_filter = (
                Filter(lambda update: all(f(update) for f in filters))
                if filters else
                self.filters.any_message
            )
        else:
            chosen_filter = (
                self.filters.any_message
                if __filter is None else
                __filter
            )

        if __func is not None:
            self.handlers.append({"filter": chosen_filter, "func": __func})
            return __func

        def decorator(func: F) -> F:
            self.handlers.append({"filter": chosen_filter, "func": func})
            return func

        return decorator

    @overload
    def Message(self) -> Callable[[F], F]: ...

    @overload
    def Message(self, __func: F) -> F: ...

    @overload
    def Message(
        self,
        *,
        commands: Optional[Union[str, List[str]]] = None,
        pattern: Optional[Union[str, re_Pattern[str]]] = None,
        content_types: Optional[List[str]] = None,
        state: Optional[str] = None,
        custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Callable[[F], F]: ...

    @overload
    def Message(
        self,
        __filter: MessageFilter
    ) -> Callable[[F], F]: ...

    def Message(
        self,
        __filter: Optional[MessageFilter] = None,
        __func: Optional[F] = None,
        *,
        commands: Optional[Union[str, List[str]]] = None,
        pattern: Optional[Union[str, re_Pattern[str]]] = None,
        content_types: Optional[List[str]] = None,
        state: Optional[str] = None,
        custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Union[Callable[[F], F], F]:
        if any([commands, pattern, content_types, state, custom_filter]):
            if __filter is not None:
                raise ValueError("Cannot use both positional filter and keyword arguments")

            filters = []

            if commands:
                if isinstance(commands, str):
                    commands = [commands]
                filters.append(self.filters.multi_command(commands))

            if pattern:
                if isinstance(pattern, str):
                    filters.append(self.filters.pattern(pattern))
                elif isinstance(pattern, re_Pattern):
                    filters.append(Filter(
                        lambda update: (
                            "message" in update
                            and "text" in update["message"]
                            and bool(pattern.match(update["message"]["text"]))
                        )
                    ))

            if content_types:
                type_filters = {
                    "text": self.filters.text,
                    "photo": self.filters.photo,
                    "video": self.filters.video,
                    "document": self.filters.document,
                    "audio": self.filters.audio,
                    "voice": self.filters.voice,
                    "sticker": self.filters.sticker,
                    "location": self.filters.location,
                    "contact": self.filters.contact
                }

                for content_type in content_types:
                    if content_type in type_filters:
                        filters.append(type_filters[content_type])

            if state:
                filters.append(self.filters.state(state))

            if custom_filter:
                filters.append(self.filters.custom(custom_filter))

            chosen_filter = (
                Filter(lambda update: all(f(update) for f in filters))
                if filters else
                self.filters.any_message
            )
        else:
            chosen_filter = (
                self.filters.any_message
                if __filter is None else
                __filter
            )

        if __func is not None:
            self.handlers.append({"filter": chosen_filter, "func": __func})
            return __func

        def decorator(func: F) -> F:
            self.handlers.append({"filter": chosen_filter, "func": func})
            return func

        return decorator

    async def get_me(
        self
    ):
        url = f"{self.base_url}/bot{self.token}/getMe"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get("ok"):
                        result = data["result"]
                        return BotInfo(
                            id=result.get("id"),
                            is_bot=result.get("is_bot", False),
                            first_name=result.get("first_name", ""),
                            last_name=result.get("last_name", ""),
                            username=result.get("username", ""),
                            language_code=result.get("language_code", "en"),
                            can_join_groups=result.get("can_join_groups", False),
                            can_read_all_group_messages=result.get("can_read_all_group_messages", False),
                            supports_inline_queries=result.get("supports_inline_queries", False)
                        )
                    return BotInfo(0, False, "", "", "", "en", False, False, False)
        except Exception as e:
            logger.error(f"Error in getMe: {e}")
            return BotInfo(0, False, "", "", "", "en", False, False, False)

    async def get_updates(
        self,
        offset=None,
        limit=120,
        timeout=30
    ):
        url = f"{self.base_url}/bot{self.token}/getUpdates"
        params = {"timeout": timeout, "limit": limit}
        if offset is not None:
            params["offset"] = offset

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, proxy=self.proxy) as response:
                    if response.status != 200:
                        logger.error(f"HTTP Error: {response.status}")
                        return None

                    response_data = await response.json()

                    if response_data is None:
                        logger.error("Empty response from server")
                        return None

                    if not isinstance(response_data, dict) or "ok" not in response_data:
                        logger.error("Invalid response format")
                        return None

                    if not response_data.get("ok"):
                        logger.error(f"API Error: {response_data.get('description', 'Unknown error')}")
                        return None

                    return response_data.get("result", [])
        except Exception as e:
            logger.error(f"An error occurred in get_updates: {e}")
            return None

    @staticmethod
    async def retry_on_errors(
        func: Callable,
        max_retries: Optional[int] = None,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        allowed_errors: tuple = (400, 401, 403, 404, 420, 429, 500, 502, 503, 504)
    ) -> Any:
        retries = 0
        delay = initial_delay

        retryable_errors = (400, 404, 420, 429, 500, 502, 503, 504)
        non_retryable_errors = (401, 403)

        while True:
            try:
                return await func()
            except Exception as e:
                error_code = getattr(e, 'code', None)

                if error_code in non_retryable_errors:
                    logger.error(f"Non-retryable error {error_code} occurred: {str(e)}")
                    raise

                if error_code not in allowed_errors:
                    logger.error(f"Unhandled error {error_code} occurred: {str(e)}")
                    raise

                retries += 1

                if error_code == 404 and max_retries is None:
                    pass
                elif max_retries is not None and retries >= max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for error {error_code}")
                    raise

                delay = min(initial_delay * (backoff_factor ** (retries - 1)), max_delay)

                if error_code in (420, 429):
                    flood_wait = getattr(e, 'retry_after', delay)
                    delay = max(delay, flood_wait)

                logger.warning(
                    f"Retryable error {error_code} occurred. "
                    f"Retry {retries}/{max_retries if max_retries else '∞'}. "
                    f"Waiting {delay:.2f} seconds..."
                )
                await asyncio.sleep(delay)

    async def _process_update(self, update_wrapper):
        async with self.semaphore:
            try:
                if hasattr(update_wrapper, 'callback_query') and update_wrapper.callback_query:
                    callback_data = update_wrapper.callback_query.data
                    update_wrapper.callback_query.message.bot = self

                    for handler in self.callback_handlers:
                        if handler["filter"](update_wrapper.update):
                            try:
                                async def callback_handler():
                                    try:
                                        handler_func = handler["func"]
                                        sig = inspect.signature(handler_func)
                                        params = {}

                                        if 'bot' in sig.parameters:
                                            params['bot'] = self
                                        if 'update' in sig.parameters:
                                            params['update'] = update_wrapper.update
                                        if 'callback_query' in sig.parameters:
                                            params['callback_query'] = update_wrapper.callback_query

                                        result = await handler_func(**params)
                                        if result and not result.get("ok"):
                                            logger.error(f"Handler failed: {result.get('description')}")
                                        return result or {"ok": True}
                                    except Exception as e:
                                        logger.error(f"Error in callback handler function: {str(e)}")
                                        return {"ok": False, "description": str(e)}

                                await self.retry_on_errors(
                                    callback_handler,
                                    max_retries=5,
                                    allowed_errors=(420, 404)
                                )
                            except Exception as e:
                                logger.error(f"Error in callback handler: {str(e)}")
                            return

                if hasattr(update_wrapper, 'message') and update_wrapper.message:
                    update_wrapper.message.bot = self

                    for handler in self.handlers:
                        if handler["filter"](update_wrapper.update):
                            try:
                                async def message_handler():
                                    try:
                                        handler_func = handler["func"]
                                        sig = inspect.signature(handler_func)
                                        params = {}

                                        if 'bot' in sig.parameters:
                                            params['bot'] = self
                                        if 'update' in sig.parameters:
                                            params['update'] = update_wrapper.update
                                        if 'message' in sig.parameters:
                                            params['message'] = update_wrapper.message

                                        if len(sig.parameters) == 1 and 'message' in sig.parameters:
                                            result = await handler_func(update_wrapper.message)
                                        else:
                                            result = await handler_func(**params)

                                        if result and not result.get("ok"):
                                            logger.error(f"Handler failed: {result.get('description')}")
                                        return result or {"ok": True}
                                    except Exception as e:
                                        logger.error(f"Error in message handler function: {str(e)}")
                                        return {"ok": False, "description": str(e)}

                                await self.retry_on_errors(
                                    message_handler,
                                    max_retries=5,
                                    allowed_errors=(420, 404)
                                )
                            except Exception as e:
                                logger.error(f"Error in message handler: {str(e)}")
                            return
            except Exception as e:
                logger.error(f"Error in _process_update: {str(e)}")

    async def process_updates(self):
        offset = None
        while self.running.is_set():
            try:
                async def get_updates_wrapper():
                    updates = await self.get_updates(offset=offset)
                    if updates is None:
                        raise Exception("No updates received or invalid response")
                    return updates or []

                updates = await self.retry_on_errors(
                            get_updates_wrapper,
                            max_retries=5,
                            allowed_errors=(420, 404, 500)
                        )


                tasks = []
                for update in updates:
                    offset = update["update_id"] + 1
                    update_wrapper = UpdateWrapper(update)
                    task = asyncio.create_task(self._process_update(update_wrapper))
                    tasks.append(task)

                await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                error_code = getattr(e, 'code', None)
                if error_code not in (420, 404):
                    logger.error(f"Non-retryable error occurred in process_updates: {e}")

    def Initialize(self) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self.initialize_handlers.append(func)
            return func

        return decorator

    async def run_initialize_handlers(self):
        for handler in self.initialize_handlers:
            await handler(self)

    @property
    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_polling)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.stop

    @property
    async def start_polling(self):
        self.running.set()
        try:
            bot_info = await self.get_me()
            if bot_info:
                logger.info(f"Bot is running! Username: @{bot_info.username}")
            else:
                logger.error(
                    "Failed to start the bot. Please check your token and API URL."
                )
                return
        except Exception as e:
            logger.error(f"An error occurred while starting the bot: {e}")
            return

        await self.run_initialize_handlers()
        await self.process_updates()

    @property
    def stop(self):
        self.running.clear()
        logger.info("Bot has been stopped.")

    async def delete_message_auto(self, message: dict):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.delete_message(chat_id=chat_id, message_id=message_id)

    async def edit_message_text_auto(self, message: dict, text: str, reply_markup=None):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)

    async def edit_message_caption_auto(
        self,
        chat_id: Union[str, int],
        message_id: int,
        caption: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageCaption"
        params = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def schedule_message(
        self,
        chat_id: Union[str, int],
        text: str,
        delay_seconds: int,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None
    ):
        await asyncio.sleep(delay_seconds)
        return await self.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None,
    ) -> Message:
        url = f"{self.base_url}/bot{self.token}/sendMessage"
        params: Dict[str, Any] = {"chat_id": chat_id, "text": text}

        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id

        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_text = await response.text()
                    try:
                        response_data = await response.json()
                    except Exception:
                        logger.error(f"Failed to decode JSON. Raw response: {response_text}")
                        response_data = {"ok": False, "description": response_text}

                    if not response_data.get("ok", False):
                        logger.error(f"API Error: {response_data.get('description')}")
                        raise ValueError(f"API Error: {response_data.get('description')}")

                    message_data = response_data.get("result", {})
                    message = Message(message_data)
                    message.bot = self
                    return message

        except Exception as e:
            logger.error(f"Network error in send_message: {e}")
            raise

    async def answer_callback_query(
        self,
        callback_query_id: Union[int, str],
        text: Optional[str] = None,
        show_alert: Optional[bool] = False,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not isinstance(callback_query_id, str) or not callback_query_id.strip():
            raise ValueError("callback_query_id must be a non-empty string")

        api_url: str = f"{self.base_url}/bot{self.token}/answerCallbackQuery"
        params: Dict[str, Any] = {"callback_query_id": callback_query_id}

        if text is not None:
            params["text"] = text
        if show_alert:
            params["show_alert"] = True
        if url is not None:
            params["url"] = url
        if cache_time is not None:
            params["cache_time"] = cache_time

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    json=params,
                    proxy=self.proxy,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_text: str = await response.text()
                    try:
                        response_data: Dict[str, Any] = await response.json()
                    except Exception:
                        logger.error(f"Failed to decode JSON. Raw response: {response_text}")
                        response_data = {"ok": False, "description": response_text}

                    if not response_data.get("ok", False):
                        logger.error(f"API Error: {response_data.get('description')}")

                    return response_data
        except Exception as e:
            logger.error(f"Network error in answer_callback_query: {e}")
            return {"ok": False, "error": str(e)}

    async def pin_chat_message(
        self,
        chat_id: Union[int, str],
        message_id: int
    ):
        url = f"{self.base_url}/bot{self.token}/pinChatMessage"
        params = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def unpin_chat_message(
        self,
        chat_id: Union[int, str],
        message_id: Optional[int] = None
    ):
        url = f"{self.base_url}/bot{self.token}/unpinChatMessage"
        params = {"chat_id": chat_id}
        if message_id is not None:
            params["message_id"] = message_id
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def unpin_all_chat_messages(
        self,
        chat_id: int
    ):
        url = f"{self.base_url}/bot{self.token}/unpinAllChatMessages"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data.get("ok", False)

    async def pin_message_auto(
        self,
        message: dict,
    ):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.pin_chat_message(
            chat_id=chat_id,
            message_id=message_id
        )

    async def unpin_message_auto(
        self,
        message: dict
    ):
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        return await self.unpin_chat_message(
            chat_id=chat_id,
            message_id=message_id
        )

    async def send_animation(
        self,
        chat_id: Union[int, str],
        animation: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendAnimation"

        if animation.startswith(("http://", "https://")) or animation.isdigit():
            payload: Dict[str, Any] = {"chat_id": chat_id, "animation": animation}
            if caption: payload["caption"] = caption
            if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup: payload["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as sess:
                async with sess.post(url, json=payload, proxy=self.proxy) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        if not os.path.isfile(animation):
            raise ValueError(f"File not found: {animation}")

        ext = os.path.splitext(animation)[1].lower()
        allowed = {".gif", ".mp4", ".mov", ".mkv", ".avi", ".webm"}
        if ext not in allowed:
            raise ValueError(f"Unsupported extension {ext}. Use gif|mp4|mov|mkv|avi|webm")

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        if caption: form.add_field("caption", caption)
        if reply_to_message_id: form.add_field("reply_to_message_id", str(reply_to_message_id))
        if reply_markup: form.add_field("reply_markup", reply_markup.to_dict())

        f = open(animation, "rb")
        form.add_field(
            name="animation",
            value=f,
            filename=os.path.basename(animation),
            content_type="application/octet-stream"
        )

        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                result = await resp.json()

        f.close()
        return result

    async def send_audio(
        self,
        chat_id: Union[int, str],
        audio: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendAudio"

        if audio.startswith(("http://", "https://")) or audio.isdigit():
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "audio": audio
            }
            if caption:
                payload["caption"] = caption
            if reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup:
                payload["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, proxy=self.proxy) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        if not os.path.isfile(audio):
            raise ValueError(f"File not found: {audio}")

        ext = os.path.splitext(audio)[1].lower()
        allowed = {".mp3", ".m4a", ".ogg", ".wav", ".flac", ".aac"}
        if ext not in allowed:
            raise ValueError(f"Unsupported audio extension {ext}. Use one of {allowed}")

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        if caption:
            form.add_field("caption", caption)
        if reply_to_message_id:
            form.add_field("reply_to_message_id", str(reply_to_message_id))
        if reply_markup:
            form.add_field("reply_markup", reply_markup.to_dict())

        f = open(audio, "rb")
        form.add_field(
            name="audio",
            value=f,
            filename=os.path.basename(audio),
            content_type="application/octet-stream"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                result = await resp.json()

        f.close()
        return result

    async def send_contact(
        self,
        chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendContact"
        params = {"chat_id": chat_id, "phone_number": phone_number, "first_name": first_name}
        if last_name:
            params["last_name"] = last_name
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_document(
        self,
        chat_id: Union[int, str],
        document: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendDocument"

        if document.startswith(("http://", "https://")) or document.isdigit():
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "document": document
            }
            if caption:
                payload["caption"] = caption
            if reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup:
                payload["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, proxy=self.proxy) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        if not os.path.isfile(document):
            raise ValueError(f"File not found: {document}")

        ext = os.path.splitext(document)[1].lower()
        allowed = FILE_TYPES
        if ext not in allowed:
            raise ValueError(f"Unsupported document extension {ext}. Use one of {allowed}")

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        if caption:
            form.add_field("caption", caption)
        if reply_to_message_id:
            form.add_field("reply_to_message_id", str(reply_to_message_id))
        if reply_markup:
            form.add_field("reply_markup", reply_markup.to_dict())

        f = open(document, "rb")
        form.add_field(
            name="document",
            value=f,
            filename=os.path.basename(document),
            content_type="application/octet-stream"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                result = await resp.json()

        f.close()
        return result

    async def send_location(
        self,
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendLocation"
        params = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_media_group(
        self,
        chat_id: Union[int, str],
        media: List[Union[InputMediaPhoto, InputMediaVideo]],
        reply_to_message_id: Optional[int] = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendMediaGroup"
        params = {
            "chat_id": chat_id,
            "media": [m.to_dict() for m in media]
        }
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                return await response.json()

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendPhoto"

        if photo.startswith(("http://", "https://")) or photo.isdigit():
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "photo": photo,
            }
            if caption: payload["caption"] = caption
            if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup: payload["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, proxy=self.proxy) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))

        if caption:
            form.add_field("caption", caption)
        if reply_to_message_id:
            form.add_field("reply_to_message_id", str(reply_to_message_id))
        if reply_markup:
            form.add_field("reply_markup", reply_markup.to_dict_json())

        if photo.startswith("data:"):
            m = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", photo)
            if not m:
                raise ValueError("Invalid data URI format")
            ext = m.group("ext")
            b64data = m.group("data")
            raw = base64.b64decode(b64data)
            file_field = BytesIO(raw)
            filename = f"photo.{ext}"

        else:
            if not os.path.isfile(photo):
                raise ValueError(f"File not found: {photo}")
            file_field = open(photo, "rb")
            filename = os.path.basename(photo)

        form.add_field(
            name="photo",
            value=file_field,
            filename=filename,
            content_type="application/octet-stream",
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                result = await resp.json()

        if not isinstance(file_field, BytesIO):
            file_field.close()

        return result

    async def send_video(
        self,
        chat_id: Union[int, str],
        video: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None
        ):

        url = f"{self.base_url}/bot{self.token}/sendVideo"

        if video.startswith(("http://", "https://")) or video.isdigit():
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "video": video,
            }
            if caption: payload["caption"] = caption
            if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup: payload["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, proxy=self.proxy) as resp:
                    resp.raise_for_status()
                    return await resp.json()

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))

        if caption:
            form.add_field("caption", caption)
        if reply_to_message_id:
            form.add_field("reply_to_message_id", str(reply_to_message_id))
        if reply_markup:
            form.add_field("reply_markup", reply_markup.to_dict_json())

        if video.startswith("data:"):
            m = re.match(r"data:video/(?P<ext>\w+);base64,(?P<data>.+)", video)
            if not m:
                raise ValueError("Invalid data URI format")
            ext = m.group("ext")
            b64data = m.group("data")
            raw = base64.b64decode(b64data)
            file_field = BytesIO(raw)
            filename = f"video.{ext}"

        else:
            if not os.path.isfile(video):
                raise ValueError(f"File not found: {video}")
            file_field = open(video, "rb")
            filename = os.path.basename(video)

        form.add_field(
            name="video",
            value=file_field,
            filename=filename,
            content_type="application/octet-stream",
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                result = await resp.json()

        if not isinstance(file_field, BytesIO):
            file_field.close()

    async def send_voice(
        self,
        chat_id: Union[int, str],
        voice: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/sendVoice"
        params = {"chat_id": chat_id, "voice": voice}
        if caption:
            params["caption"] = caption
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def send_sticker(
        self,
        chat_id: Union[int, str],
        sticker: Union[str, BytesIO],
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
        emoji: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendSticker"

        if (isinstance(sticker, str) and
            (sticker.startswith(("http://", "https://")) or
            sticker.isdigit() or
            (os.path.isfile(sticker) and sticker.lower().endswith('.webp')))):

            payload = {
                "chat_id": chat_id,
                "sticker": sticker
            }
            if reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
            if reply_markup:
                payload["reply_markup"] = reply_markup.to_dict()
            if emoji:
                payload["emoji"] = emoji

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        try:
            from PIL import Image, ImageSequence
        except ImportError:
            raise ImportError("Pillow package is required for image conversion. Install with: pip install pillow")

        file_obj = None
        should_close = False

        try:
            if isinstance(sticker, str) and sticker.startswith("data:"):
                m = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", sticker)
                if not m:
                    raise ValueError("Invalid data URI format")

                ext = m.group("ext").lower()
                b64data = m.group("data")
                raw = base64.b64decode(b64data)
                file_obj = BytesIO(raw)
                should_close = True

            elif isinstance(sticker, str) and os.path.isfile(sticker):
                with open(sticker, "rb") as f:
                    file_obj = BytesIO(f.read())
                should_close = True

            elif isinstance(sticker, BytesIO):
                file_obj = sticker
                file_obj.seek(0)

            else:
                raise ValueError("Invalid sticker input format")

            file_obj.seek(0)
            if file_obj.read(4) == b"RIFF" and file_obj.read(4) == b"WEBP":
                file_obj.seek(0)
            else:
                file_obj.seek(0)
                img = Image.open(file_obj)

                output = BytesIO()

                if getattr(img, "is_animated", False):
                    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                    frames[0].save(
                        output,
                        format="WEBP",
                        save_all=True,
                        append_images=frames[1:],
                        duration=img.info.get('duration', 100),
                        loop=0,
                        quality=80
                    )
                else:
                    img.save(output, format="WEBP", quality=90)

                file_obj = output

            form = aiohttp.FormData()
            form.add_field("chat_id", str(chat_id))
            if reply_to_message_id:
                form.add_field("reply_to_message_id", str(reply_to_message_id))
            if reply_markup:
                form.add_field("reply_markup", reply_markup.to_dict())
            if emoji:
                form.add_field("emoji", emoji)

            form.add_field(
                name="sticker",
                value=file_obj,
                filename="sticker.webp",
                content_type="image/webp"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        finally:
            if should_close and file_obj and hasattr(file_obj, 'close'):
                file_obj.close()

    async def send_chat_action(
        self,
        chat_id: Union[int, str],
        action: str
    ):
        valid_actions = {
            'typing',
            'upload_photo',
            'record_video',
            'upload_video',
            'record_voice',
            'upload_voice',
            'upload_document',
            'choose_sticker',
            'find_location',
            'record_video_note',
            'upload_video_note'
        }

        if action not in valid_actions:
            raise ValueError(f"Action '{action}' does not exist. Valid actions are: {', '.join(valid_actions)}")

        url = f"{self.base_url}/bot{self.token}/sendChatAction"
        params = {"chat_id": chat_id, "action": action}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def edit_message_text(
        self,
        chat_id: Union[int, str],
        message_id: Union[int, str],
        text: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageText"
        params = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def delete_message(
        self,
        chat_id: Union[int, str],
        message_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/deleteMessage"
        params = {"chat_id": chat_id, "message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: Union[int, str],
    ):
        url = f"{self.base_url}/bot{self.token}/forwardMessage"
        params = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def get_chat_administrators(
            self,
            chat_id: Union[int, str]
        ) -> tuple[AdminInfo, ...]:
            url = f"{self.base_url}/bot{self.token}/getChatAdministrators"
            params = {"chat_id": chat_id}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response_data = await response.json()
                    if response_data.get("ok"):
                        admins = []
                        for admin in response_data["result"]:
                            user = admin.get("user", {})
                            admins.append(AdminInfo(
                                id=user.get("id"),
                                is_bot=user.get("is_bot"),
                                first_name=user.get("first_name"),
                                last_name=user.get("last_name"),
                                username=user.get("username"),
                                status=admin.get("status"),
                                custom_title=admin.get("custom_title"),
                                until_date=admin.get("until_date"),
                                can_be_edited=admin.get("can_be_edited"),
                                can_post_messages=admin.get("can_post_messages"),
                                can_edit_messages=admin.get("can_edit_messages"),
                                can_delete_messages=admin.get("can_delete_messages"),
                                can_restrict_members=admin.get("can_restrict_members"),
                                can_promote_members=admin.get("can_promote_members"),
                                can_change_info=admin.get("can_change_info"),
                                can_invite_users=admin.get("can_invite_users"),
                                can_pin_messages=admin.get("can_pin_messages"),
                                is_member=admin.get("is_member"),
                                can_send_messages=admin.get("can_send_messages"),
                                can_send_media_messages=admin.get("can_send_media_messages"),
                                can_send_polls=admin.get("can_send_polls"),
                                can_send_other_messages=admin.get("can_send_other_messages"),
                            ))
                        return tuple(admins)
                    return tuple()

    async def get_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str]
    ) -> Optional[ChatMemberInfo]:

        url = f"{self.base_url}/bot{self.token}/getChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response_data = await response.json()

                    if not response_data.get("ok"):
                        logger.error(f"Failed to get chat member: {response_data.get('description')}")
                        return None

                    result = response_data["result"]
                    user = result.get("user", {})

                    status = result.get("status", "")

                    return ChatMemberInfo(
                        id=user.get("id"),
                        is_bot=user.get("is_bot", False),
                        first_name=user.get("first_name", ""),
                        last_name=user.get("last_name", ""),
                        username=user.get("username", ""),
                        status=status,
                        can_edit_messages=result.get("can_edit_messages", False),
                        can_delete_messages=result.get("can_delete_messages", False),
                        can_restrict_members=result.get("can_restrict_members", False),
                        can_change_info=result.get("can_change_info", False),
                        can_invite_users=result.get("can_invite_users", False),
                    )

        except Exception as e:
            logger.error(f"Error in get_chat_member: {str(e)}")
            return None

    async def get_chat_members_count(
        self,
        chat_id: Union[int, str]
    ) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getChatMembersCount"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    return (response_data["result"],)
                return tuple()

    async def get_file(
        self,
        file_id: str
    ) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getFile"
        params = {"file_id": file_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    result = response_data["result"]
                    return (
                        result.get("file_id"),
                        result.get("file_unique_id"),
                        result.get("file_size"),
                        result.get("file_path")
                    )
                return tuple()

    async def get_sticker_set(
        self,
        name: str
    ) -> tuple:
        url = f"{self.base_url}/bot{self.token}/getStickerSet"
        params = {"name": name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if response_data.get("ok"):
                    result = response_data["result"]
                    stickers = []
                    for sticker in result.get("stickers", []):
                        stickers.append((
                            sticker.get("file_id"),
                            sticker.get("file_unique_id"),
                            sticker.get("width"),
                            sticker.get("height"),
                            sticker.get("is_animated"),
                            sticker.get("is_video"),
                            sticker.get("emoji"),
                            sticker.get("set_name"),
                            sticker.get("mask_position"),
                            sticker.get("file_size"),
                            sticker.get("thumbnail")
                        ))
                    return (
                        result.get("name"),
                        result.get("title"),
                        result.get("is_animated"),
                        result.get("is_video"),
                        result.get("contains_masks"),
                        tuple(stickers)
                    )
                return tuple()

    async def invite_user(
        self,
        chat_id: Union[int, str], user_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/inviteUser"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def leave_chat(
        self,
        chat_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/leaveChat"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def promote_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        can_manage_chat: Optional[bool] = None,
        can_manage_video_chats: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/promoteChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}

        if can_change_info is not None:
            params["can_change_info"] = can_change_info
        if can_post_messages is not None:
            params["can_post_messages"] = can_post_messages
        if can_edit_messages is not None:
            params["can_edit_messages"] = can_edit_messages
        if can_delete_messages is not None:
            params["can_delete_messages"] = can_delete_messages
        if can_invite_users is not None:
            params["can_invite_users"] = can_invite_users
        if can_restrict_members is not None:
            params["can_restrict_members"] = can_restrict_members
        if can_pin_messages is not None:
            params["can_pin_messages"] = can_pin_messages
        if can_promote_members is not None:
            params["can_promote_members"] = can_promote_members
        if can_manage_chat is not None:
            params["can_manage_chat"] = can_manage_chat
        if can_manage_video_chats is not None:
            params["can_manage_video_chats"] = can_manage_video_chats
        if can_manage_topics is not None:
            params["can_manage_topics"] = can_manage_topics

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                if not response_data.get("ok"):
                    logger.error(f"Failed to promote chat member: {response_data.get('description')}")
                return response_data

    async def restrict_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        can_send_message: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/restrictChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}

        if can_send_message is not None:
            params["can_send_message"] = can_send_message
        if can_invite_users is not None:
            params["can_invite_users"] = can_invite_users
        if can_pin_messages is not None:
            params["can_pin_messages"] = can_pin_messages

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                try:
                    response_data = await response.json()
                    if not response_data.get("ok"):
                        logger.error(f"Failed to restrict chat member: {response_data.get('description')}")
                    return response_data
                except ValueError:
                    text_response = await response.text()
                    if text_response.strip().lower() == "true":
                        return {"ok": True, "result": True}
                    else:
                        logger.error(f"Unexpected response format: {text_response}")
                        return {"ok": False, "description": text_response}

    async def set_chat_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, BytesIO],
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/setChatPhoto"

        if isinstance(photo, str) and (photo.startswith(("http://", "https://")) or photo.isdigit()):
            params = {
                "chat_id": chat_id,
                "photo": photo
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))

        file_obj = None
        should_close = False

        try:
            if isinstance(photo, str) and photo.startswith("data:"):
                m = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", photo)
                if not m:
                    raise ValueError("Invalid data URI format")

                ext = m.group("ext")
                b64data = m.group("data")
                raw = base64.b64decode(b64data)
                file_obj = BytesIO(raw)
                filename = f"photo.{ext}"
                should_close = True

            elif isinstance(photo, str) and os.path.isfile(photo):
                file_obj = open(photo, "rb")
                filename = os.path.basename(photo)
                should_close = True

            elif isinstance(photo, BytesIO):
                file_obj = photo
                file_obj.seek(0)
                filename = "photo.jpg"

            else:
                raise ValueError("Invalid photo input format")

            form.add_field(
                name="photo",
                value=file_obj,
                filename=filename,
                content_type="image/jpeg"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        finally:
            if should_close and file_obj and hasattr(file_obj, 'close'):
                file_obj.close()

    async def ban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/banChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def unban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/unbanChatMember"
        params = {"chat_id": chat_id, "user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()
                return response_data

    async def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: Union[int, str],
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url: str = f"{self.base_url}/bot{self.token}/copyMessage"
        params: Dict[str, Any] = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }

        if caption is not None:
            params["caption"] = caption
        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup is not None:
            params["reply_markup"] = reply_markup.to_dict()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data: Dict[str, Any] = await response.json()
                return response_data

    async def add_sticker_to_set(
        self,
        user_id: Union[int, str],
        name: str,
        sticker: Union[str, BytesIO],
        emojis: str,
        mask_position: Optional[dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/addStickerToSet"

        if isinstance(sticker, str) and (sticker.startswith(("http://", "https://")) or sticker.isdigit()):
            params = {
                "user_id": user_id,
                "name": name,
                "png_sticker": sticker,
                "emojis": emojis
            }
            if mask_position:
                params["mask_position"] = mask_position

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        form = aiohttp.FormData()
        form.add_field("user_id", str(user_id))
        form.add_field("name", name)
        form.add_field("emojis", emojis)
        if mask_position:
            form.add_field("mask_position", json.dumps(mask_position))

        file_obj = None
        should_close = False

        try:
            if isinstance(sticker, str) and sticker.startswith("data:"):
                m = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", sticker)
                if not m:
                    raise ValueError("Invalid data URI format")

                ext = m.group("ext")
                b64data = m.group("data")
                raw = base64.b64decode(b64data)
                file_obj = BytesIO(raw)
                filename = f"sticker.{ext}"
                should_close = True

            elif isinstance(sticker, str) and os.path.isfile(sticker):
                file_obj = open(sticker, "rb")
                filename = os.path.basename(sticker)
                should_close = True

            elif isinstance(sticker, BytesIO):
                file_obj = sticker
                file_obj.seek(0)
                filename = "sticker.png"

            else:
                raise ValueError("Invalid sticker input format")

            form.add_field(
                name="png_sticker",
                value=file_obj,
                filename=filename,
                content_type="image/png"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        finally:
            if should_close and file_obj and hasattr(file_obj, 'close'):
                file_obj.close()

    async def create_new_sticker_set(
        self,
        user_id: Union[int, str],
        name: str,
        title: str,
        sticker: Union[str, BytesIO],
        emojis: str,
        sticker_format: str = "static",
        contains_masks: Optional[bool] = None,
        mask_position: Optional[dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/createNewStickerSet"

        sticker_field = {
            "static": "png_sticker",
            "animated": "tgs_sticker",
            "video": "webm_sticker"
        }.get(sticker_format, "png_sticker")

        if isinstance(sticker, str) and (sticker.startswith(("http://", "https://")) or sticker.isdigit()):
            params = {
                "user_id": user_id,
                "name": name,
                "title": title,
                sticker_field: sticker,
                "emojis": emojis,
                "sticker_format": sticker_format
            }
            if contains_masks is not None:
                params["contains_masks"] = contains_masks
            if mask_position:
                params["mask_position"] = mask_position

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        form = aiohttp.FormData()
        form.add_field("user_id", str(user_id))
        form.add_field("name", name)
        form.add_field("title", title)
        form.add_field("emojis", emojis)
        form.add_field("sticker_format", sticker_format)

        if contains_masks is not None:
            form.add_field("contains_masks", str(contains_masks).lower())
        if mask_position:
            form.add_field("mask_position", json.dumps(mask_position))

        file_obj = None
        should_close = False

        try:
            if isinstance(sticker, str) and sticker.startswith("data:"):
                m = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", sticker)
                if not m:
                    raise ValueError("Invalid data URI format")

                ext = m.group("ext")
                b64data = m.group("data")
                raw = base64.b64decode(b64data)
                file_obj = BytesIO(raw)
                filename = f"sticker.{ext}"
                should_close = True

            elif isinstance(sticker, str) and os.path.isfile(sticker):
                file_obj = open(sticker, "rb")
                filename = os.path.basename(sticker)
                should_close = True

            elif isinstance(sticker, BytesIO):
                file_obj = sticker
                file_obj.seek(0)
                filename = {
                    "static": "sticker.png",
                    "animated": "sticker.tgs",
                    "video": "sticker.webm"
                }.get(sticker_format, "sticker.png")

            else:
                raise ValueError("Invalid sticker input format")

            content_type = {
                "static": "image/png",
                "animated": "application/x-tgsticker",
                "video": "video/webm"
            }.get(sticker_format, "image/png")

            form.add_field(
                name=sticker_field,
                value=file_obj,
                filename=filename,
                content_type=content_type
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        finally:
            if should_close and file_obj and hasattr(file_obj, 'close'):
                file_obj.close()

    async def upload_sticker_file(
        self,
        user_id: Union[int, str],
        sticker: Union[str, BytesIO],
        sticker_format: str = "static"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/uploadStickerFile"

        sticker_field = {
            "static": "png_sticker",
            "animated": "tgs_sticker",
            "video": "webm_sticker"
        }.get(sticker_format, "png_sticker")

        if (isinstance(sticker, str) and sticker.startswith(("http://", "https://")) and sticker_format == "static"):
            params = {
                "user_id": user_id,
                sticker_field: sticker
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        form = aiohttp.FormData()
        form.add_field("user_id", str(user_id))

        file_obj = None
        should_close = False

        try:
            if isinstance(sticker, str) and sticker.startswith("data:"):
                m = re.match(r"data:(image|video)/(?P<ext>\w+);base64,(?P<data>.+)", sticker)
                if not m:
                    raise ValueError("Invalid data URI format")

                ext = m.group("ext")
                b64data = m.group("data")
                raw = base64.b64decode(b64data)
                file_obj = BytesIO(raw)
                filename = f"sticker.{ext}"
                should_close = True

            elif isinstance(sticker, str) and os.path.isfile(sticker):
                file_obj = open(sticker, "rb")
                filename = os.path.basename(sticker)
                should_close = True

            elif isinstance(sticker, BytesIO):
                file_obj = sticker
                file_obj.seek(0)
                filename = {
                    "static": "sticker.png",
                    "animated": "sticker.tgs",
                    "video": "sticker.webm"
                }.get(sticker_format, "sticker.png")

            else:
                raise ValueError("Invalid sticker input format")

            content_type = {
                "static": "image/png",
                "animated": "application/x-tgsticker",
                "video": "video/webm"
            }.get(sticker_format, "image/png")

            form.add_field(
                name=sticker_field,
                value=file_obj,
                filename=filename,
                content_type=content_type
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()

        finally:
            if should_close and file_obj and hasattr(file_obj, 'close'):
                file_obj.close()

    async def create_chat_invite_link(
        self,
        chat_id: Union[int, str],
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
    ):
        url = f"{self.base_url}/bot{self.token}/createChatInviteLink"
        params = {"chat_id": chat_id}
        if expire_date:
            params["expire_date"] = expire_date
        if member_limit:
            params["member_limit"] = member_limit
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def delete_chat_photo(
        self,
        chat_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/deleteChatPhoto"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def delete_sticker_from_set(
        self,
        sticker: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/deleteStickerFromSet"
        params = {"sticker": sticker}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def edit_message_caption(
        self,
        chat_id: Union[int, str],
        message_id: Union[int, str],
        caption: str,
        reply_markup=None,
    ):
        url = f"{self.base_url}/bot{self.token}/editMessageCaption"
        params = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if reply_markup:
            params["reply_markup"] = reply_markup.to_dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def export_chat_invite_link(
        self,
        chat_id: Union[int, str]
    ):
        url = f"{self.base_url}/bot{self.token}/exportChatInviteLink"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def revoke_chat_invite_link(
        self,
        chat_id: Union[int, str],
        invite_link: str
    ):
        url = f"{self.base_url}/bot{self.token}/revokeChatInviteLink"
        params = {"chat_id": chat_id, "invite_link": invite_link}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def set_chat_description(
        self,
        chat_id: Union[int, str],
        description: str
    ):
        url = f"{self.base_url}/bot{self.token}/setChatDescription"
        params = {"chat_id": chat_id, "description": description}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    async def set_chat_title(
        self,
        chat_id: Union[int, str],
        title: str
    ):
        url = f"{self.base_url}/bot{self.token}/setChatTitle"
        params = {"chat_id": chat_id, "title": title}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, proxy=self.proxy) as response:
                response_data = await response.json()

    def CallbackQuery(
        self,
        __filter: Optional[Union[Callable[[Any], bool],
                        Sequence[Callable[[Any], bool]],
                        re_Pattern[str]]] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        chosen_filter: Union[Callable[[Any], bool],
                        Sequence[Callable[[Any], bool]],
                        re_Pattern[str]] = (
            self.filters.callback_query_all if __filter is None else __filter
        )

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            if isinstance(chosen_filter, (list, tuple)):
                def sequence_filter(update: Any) -> bool:
                    if not isinstance(chosen_filter, (list, tuple)):
                        return False
                    return all(f(update) for f in chosen_filter)
                actual_filter = sequence_filter

            elif hasattr(chosen_filter, 'pattern') and callable(getattr(chosen_filter, 'match', None)):
                def regex_filter(update: Any) -> bool:
                    if not (hasattr(update, 'callback_query')) or not hasattr(update.callback_query, 'data'):
                        return False
                    if hasattr(chosen_filter, 'match'):
                        return bool(chosen_filter.match(update.callback_query.data))
                actual_filter = regex_filter

            elif callable(chosen_filter):
                actual_filter = chosen_filter

            else:
                raise TypeError(
                    f"Filter must be callable, sequence of callables, or regex Pattern. "
                    f"Got {type(chosen_filter).__name__}"
                )

            self.callback_handlers.append({
                "filter": actual_filter,
                "func": fn,
                "original_filter": chosen_filter
            })
            return fn

        return decorator

    @property
    def CallbackQuery(self):
        return self._callback_query_decorator

    def _callback_query_decorator(
        self,
        __filter: Optional[Union[Callable[[Any], bool],
                        Sequence[Callable[[Any], bool]],
                        re_Pattern[str]]] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        chosen_filter: Union[Callable[[Any], bool],
                        Sequence[Callable[[Any], bool]],
                        re_Pattern[str]] = (
            self.filters.callback_query_all if __filter is None else __filter
        )

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            if isinstance(chosen_filter, (list, tuple)):
                def sequence_filter(update: Any) -> bool:
                    if not isinstance(chosen_filter, (list, tuple)):
                        return False
                    return all(f(update) for f in chosen_filter)
                actual_filter = sequence_filter

            elif hasattr(chosen_filter, 'pattern') and callable(getattr(chosen_filter, 'match', None)):
                def regex_filter(update: Any) -> bool:
                    if not (hasattr(update, 'callback_query')) or not hasattr(update.callback_query, 'data'):
                        return False
                    if hasattr(chosen_filter, 'match'):
                        return bool(chosen_filter.match(update.callback_query.data))
                actual_filter = regex_filter

            elif callable(chosen_filter):
                actual_filter = chosen_filter

            else:
                raise TypeError(
                    f"Filter must be callable, sequence of callables, or regex Pattern. "
                    f"Got {type(chosen_filter).__name__}"
                )

            self.callback_handlers.append({
                "filter": actual_filter,
                "func": fn,
                "original_filter": chosen_filter
            })
            return fn

        return decorator

    @staticmethod
    def LabeledPrice(
        label: str,
        amount: Union[int, str]
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                prices = [{"label": label, "amount": amount}]
                return func(*args, prices=prices, **kwargs)
            return wrapper
        return decorator

    def PreCheckoutQuery(
        self
        ) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.callback_handlers.append({
                "filter": self.filters.pre_checkout_query,
                "func": func
            })
            return func
        return decorator

    async def send_invoice(
            self,
            chat_id: Union[int, str],
            title: str,
            description: str,
            payload: str,
            provider_token: str,
            prices: List[Dict[str, Union[int, float]]],
            photo_url: Optional[Union[str, BytesIO]] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[Any] = None,
            **kwargs
        ) -> Dict[str, Any]:
            url = f"{self.base_url}/bot{self.token}/sendInvoice"
            params = {
                "chat_id": str(chat_id),
                "title": title,
                "description": description,
                "payload": payload,
                "provider_token": provider_token,
                "currency": "IRR",
                "prices": prices,
                **kwargs
            }

            if photo_url is not None:
                if isinstance(photo_url, str):
                    if photo_url.startswith(("http://", "https://")) or photo_url.isdigit():
                        params["photo_url"] = photo_url
                    elif os.path.isfile(photo_url):
                        try:
                            with open(photo_url, "rb") as f:
                                photo_data = BytesIO(f.read())
                            upload_result = await self._upload_photo(chat_id, photo_data)
                            if upload_result.get("ok"):
                                file_id = upload_result["result"]["photo"][-1]["file_id"]
                                params["photo_url"] = file_id
                        except Exception as e:
                            logger.error(f"Error uploading photo: {e}")
                elif isinstance(photo_url, BytesIO):
                    try:
                        upload_result = await self._upload_photo(chat_id, photo_url)
                        if upload_result.get("ok"):
                            file_id = upload_result["result"]["photo"][-1]["file_id"]
                            params["photo_url"] = file_id
                    except Exception as e:
                        logger.error(f"Error uploading photo from BytesIO: {e}")

            optional_params = {
                "reply_to_message_id": reply_to_message_id,
            }

            for key, value in optional_params.items():
                if value is not None:
                    params[key] = value

            if reply_markup is not None:
                params["reply_markup"] = reply_markup.to_dict()

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        url,
                        json=params,
                        proxy=self.proxy,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
                except Exception as e:
                    logger.error(f"Error sending invoice: {e}")
                    return {"ok": False, "description": str(e)}

    async def _upload_photo(
        self,
        chat_id: Union[int, str],
        photo_data: BytesIO,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/sendPhoto"
        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        if caption:
            form.add_field("caption", caption)

        photo_data.seek(0)
        form.add_field(
            name="photo",
            value=photo_data,
            filename="invoice_photo.jpg",
            content_type="image/jpeg"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, proxy=self.proxy) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/bot{self.token}/answerPreCheckoutQuery"
        params = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
            **kwargs
        }

        if not ok and not error_message:
            logger.warning("Error message is required when ok=False")
            error_message = "Payment failed"

        if error_message:
            params["error_message"] = error_message

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if not result.get('ok'):
                        logger.error(f"Failed to answer pre-checkout query: {result.get('description')}")

                    return result

            except aiohttp.ClientError as e:
                logger.error(f"Network error while answering pre-checkout query: {str(e)}")
                return {"ok": False, "description": f"Network error: {str(e)}"}

            except Exception as e:
                logger.error(f"Unexpected error while answering pre-checkout query: {str(e)}")
                return {"ok": False, "description": f"Unexpected error: {str(e)}"}

    async def inquire_transaction(
        self,
        transaction_id: str,
        timeout: int = 30
    ) -> Optional[Transaction]:
        url = f"{self.base_url}/bot{self.token}/inquireTransaction"
        params = {"transaction_id": transaction_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=params,
                    proxy=self.proxy,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:

                    if response.status != 200:
                        logger.error(f"HTTP Error in inquire_transaction: {response.status}")
                        return None

                    response_data = await response.json()

                    if not response_data.get("ok"):
                        logger.error(f"API Error in inquire_transaction: {response_data.get('description')}")
                        return None

                    result = response_data.get("result", {})

                    return Transaction(
                        id=result.get("id"),
                        status=result.get("status", "pending"),
                        userID=result.get("userID", 0),
                        amount=result.get("amount", 0),
                        createdAt=result.get("createdAt", 0)
                    )

        except asyncio.TimeoutError:
            logger.error("Timeout occurred while inquiring transaction")
            return None

        except Exception as e:
            logger.error(f"Error in inquire_transaction: {str(e)}")
            return None