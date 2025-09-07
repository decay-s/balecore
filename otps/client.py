import aiohttp
import asyncio
import time
import re
import logging
from typing import Optional, Union, Dict, Any, Coroutine
from .exceptions import (
    TokenError,
    InvalidClientError,
    BadRequestError,
    ServerError,
    OTPError,
    InvalidPhoneNumberError,
    UserNotFoundError,
    InsufficientBalanceError,
    RateLimitExceededError,
    UnexpectedResponseError,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class OTP:
    def __init__(self, username: str, password: str, url: str = "https://safir.bale.ai") -> None:
        self.client_id = username
        self.client_secret = password
        self.base_url = url.rstrip("/")
        self.token: Optional[str] = None
        self.expires_at: float = 0.0

    def _normalize_phone(self, phone: str) -> str:
        p = re.sub(r"[^\d]", "", phone.strip())
        if p.startswith("0") and len(p) == 11:
            p = "98" + p[1:]
        elif len(p) == 10:
            p = "98" + p
        return p

    async def _post(
        self, 
        endpoint: str, 
        **kwargs
    ) -> Any:
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as s:
            async with s.post(url, **kwargs) as r:
                try:
                    data = await r.json()
                except aiohttp.ContentTypeError:
                    text = await r.text()
                    raise UnexpectedResponseError(text)

                if 200 <= r.status < 300:
                    return data

                if endpoint.endswith("/auth/token"):
                    if r.status == 401: raise InvalidClientError(data)
                    if r.status == 400: raise BadRequestError(data)
                    if r.status >= 500: raise ServerError(data)

                code = data.get("code")
                msg  = data.get("message", "")

                if r.status == 400:
                    if code == 8:  raise InvalidPhoneNumberError(msg)
                    if code == 18: raise RateLimitExceededError(msg)
                    if code == 20: raise InsufficientBalanceError(msg)
                    raise OTPError(msg)
                
                if r.status == 402: raise InsufficientBalanceError(msg)
                if r.status == 404: raise UserNotFoundError(msg)
                if r.status >= 500: raise ServerError(msg)

                raise UnexpectedResponseError(f"{r.status}: {data}")

    async def _fetch_token(self) -> None:
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "read",
        }
        data = await self._post("/api/v2/auth/token", data=body)
        self.token = data["access_token"]
        expires_in = float(data.get("expires_in", 3600))
        self.expires_at = time.time() + expires_in - 30

    async def _ensure_token(self) -> None:
        if not self.token or time.time() >= self.expires_at:
            await self._fetch_token()

    async def _send_otp(self, phone_number: str, code: int) -> Dict[str, Any]:
        await self._ensure_token()
        hdr     = {"Authorization": f"Bearer {self.token}"}
        payload = {"phone": self._normalize_phone(phone_number), "otp": code}
        return await self._post("/api/v2/send_otp", json=payload, headers=hdr)

    def send_otp(self, phone_number: str, code: Union[int, str]) -> Union[Coroutine, Any]:
        if isinstance(code, str):
            otp = int(code)
        try:
            loop = asyncio.get_running_loop()
            return asyncio.ensure_future(self._send_otp(phone_number, otp))
        except RuntimeError:
            return asyncio.run(self._send_otp(phone_number, otp))

    def send_otp2(self, phone_number: str, code: Union[int, str]) -> None:
        async def _task():
            try:
                resp = await self._send_otp(phone_number, int(code))
                logger.info("OTP sent successfully to %s: %s", phone_number, resp)
            except Exception as e:
                logger.error("Failed to send OTP to %s: %s", phone_number, e)

        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(_task())
        except RuntimeError:
            asyncio.run(_task())