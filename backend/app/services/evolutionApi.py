"""
WAHA (WhatsApp HTTP API) Service - Handle all interactions with WAHA
Dropin replacement for Evolution API service.
"""
import asyncio
import logging
import random

import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)


def _toWahaId(phone: str) -> str:
    """Convert phone to WAHA chatId format: 593999@c.us
    @lid IDs are passed through unchanged — WAHA NOWEB handles them natively.
    """
    if phone.endswith("@lid") or phone.endswith("@g.us"):
        return phone
    phone = phone.replace("@s.whatsapp.net", "").replace("@c.us", "")
    return f"{phone}@c.us"


class EvolutionApiService:
    """
    WAHA-backed service (drop-in replacement for Evolution API).
    All method signatures remain identical so no other code changes.
    """

    def __init__(self):
        self.base_url = settings.WAHA_API_URL
        self.api_key = settings.WAHA_API_KEY
        self.session = settings.WAHA_SESSION

        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def sendTextMessage(self, phone_number: str, message: str) -> dict:
        """Send text message via WAHA."""
        try:
            chat_id = _toWahaId(phone_number)
            url = f"{self.base_url}/api/sendText"
            payload = {"session": self.session, "chatId": chat_id, "text": message}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Message sent to {chat_id}")
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def sendImageMessage(
        self,
        phone_number: str,
        image_url: str,
        caption: str = ""
    ) -> dict:
        """Send image message via WAHA."""
        try:
            chat_id = _toWahaId(phone_number)
            url = f"{self.base_url}/api/sendImage"
            payload = {
                "session": self.session,
                "chatId": chat_id,
                "file": {"url": image_url},
                "caption": caption
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Image sent to {chat_id}")
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error sending image: {str(e)}")
            raise

    async def downloadMedia(self, message_key: dict) -> bytes:
        """Download media - not used in WAHA flow, returns empty bytes."""
        return b""

    async def getInstanceStatus(self) -> dict:
        """Get WAHA session status."""
        try:
            url = f"{self.base_url}/api/sessions/{self.session}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting session status: {str(e)}")
            raise

    async def sendSeen(self, phone_number: str) -> dict:
        """Mark messages as read (double blue tick) via WAHA."""
        try:
            chat_id = _toWahaId(phone_number)
            url = f"{self.base_url}/api/sendSeen"
            payload = {"session": self.session, "chatId": chat_id}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                logger.debug(f"sendSeen for {chat_id}")
                return response.json() if response.content else {}
        except httpx.HTTPError as e:
            logger.error(f"Error sending seen: {str(e)}")
            return {}

    async def resolveLidToPhone(self, lid: str) -> str | None:
        """
        Resolve a WAHA @lid hidden ID to a real @c.us phone number.
        Uses GET /api/{session}/lids/{lid} → LidToPhoneNumber schema.
        Returns the resolved 'xxx@c.us' string, or None on failure.
        """
        try:
            url = f"{self.base_url}/api/{self.session}/lids/{lid}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    # LidToPhoneNumber: {lid: "...", phoneNumber: "593xxx@c.us"}
                    phone = data.get("phoneNumber") or data.get("phone")
                    if phone:
                        return _toWahaId(phone)
        except Exception as e:
            logger.warning(f"Could not resolve @lid {lid}: {e}")
        return None

    async def setPresence(self, phone_number: str, presence: str = "available") -> dict:
        """Presence not supported directly in WAHA NOWEB — no-op."""
        return {}

    async def sendPresenceUpdate(self, phone_number: str, state: str = "composing") -> dict:
        """Send typing indicator via WAHA."""
        try:
            chat_id = _toWahaId(phone_number)
            endpoint = "startTyping" if state == "composing" else "stopTyping"
            url = f"{self.base_url}/api/{endpoint}"
            payload = {"session": self.session, "chatId": chat_id}

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                logger.debug(f"Typing {endpoint} for {chat_id}")
                return response.json() if response.content else {}

        except httpx.HTTPError as e:
            logger.error(f"Error sending typing indicator: {str(e)}")
            return {}

    async def simulateHumanDelay(self, message: str) -> None:
        """Simulate human typing delay based on message length."""
        base_delay = random.uniform(1.0, 2.5)
        char_delay = len(message) * random.uniform(0.04, 0.07)
        total_delay = min(base_delay + char_delay, 22.0)
        logger.debug(f"Simulating typing delay: {total_delay:.2f}s")
        await asyncio.sleep(total_delay)

    async def sendTextWithHumanBehavior(
        self,
        phone_number: str,
        message: str,
        use_typing: bool = True,
        use_presence: bool = True
    ) -> dict:
        """Send text with human-like reading + typing delay."""
        try:
            # Simulate reading the incoming message before reacting
            reading_delay = random.uniform(1.5, 4.0)
            await asyncio.sleep(reading_delay)

            if use_typing:
                await self.sendPresenceUpdate(phone_number, "composing")

            await self.simulateHumanDelay(message)

            if use_typing:
                await self.sendPresenceUpdate(phone_number, "paused")
                await asyncio.sleep(random.uniform(0.3, 0.8))

            response = await self.sendTextMessage(phone_number, message)
            logger.info(f"Message sent with human behavior to {phone_number}")
            return response

        except Exception as e:
            logger.error(f"Error sending message with human behavior: {str(e)}")
            return await self.sendTextMessage(phone_number, message)
