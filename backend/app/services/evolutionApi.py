"""
Evolution API Service - Handle all interactions with Evolution API
"""
import asyncio
import logging
import random

import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EvolutionApiService:
    """
    Service to interact with Evolution API for sending WhatsApp messages
    """

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME

        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def sendTextMessage(self, phone_number: str, message: str) -> dict:
        """
        Send text message via Evolution API

        Args:
            phone_number: WhatsApp number (format: 593999999999@s.whatsapp.net or 593999999999)
            message: Text message to send

        Returns:
            Response from Evolution API
        """
        try:
            # Ensure phone number has correct format
            if "@s.whatsapp.net" not in phone_number:
                phone_number = f"{phone_number}@s.whatsapp.net"

            url = f"{self.base_url}/message/sendText/{self.instance_name}"

            payload = {
                "number": phone_number,
                "text": message
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                logger.info(f"Message sent to {phone_number}")
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
        """
        Send image message via Evolution API

        Args:
            phone_number: WhatsApp number
            image_url: URL of the image
            caption: Optional caption for the image

        Returns:
            Response from Evolution API
        """
        try:
            if "@s.whatsapp.net" not in phone_number:
                phone_number = f"{phone_number}@s.whatsapp.net"

            url = f"{self.base_url}/message/sendMedia/{self.instance_name}"

            payload = {
                "number": phone_number,
                "media": image_url,
                "caption": caption,
                "mediatype": "image"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                logger.info(f"Image sent to {phone_number}")
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error sending image: {str(e)}")
            raise

    async def downloadMedia(self, message_key: dict) -> bytes:
        """
        Download media file from Evolution API

        Args:
            message_key: Message key containing media info

        Returns:
            Media file bytes
        """
        try:
            url = f"{self.base_url}/chat/getBase64FromMediaMessage/{self.instance_name}"

            payload = {
                "message": message_key
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                return response.content

        except httpx.HTTPError as e:
            logger.error(f"Error downloading media: {str(e)}")
            raise

    async def getInstanceStatus(self) -> dict:
        """
        Get Evolution API instance status

        Returns:
            Instance status information
        """
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error getting instance status: {str(e)}")
            raise

    async def setPresence(self, phone_number: str, presence: str = "available") -> dict:
        """
        Set presence status (online/offline)

        Args:
            phone_number: WhatsApp number
            presence: "available" (online) or "unavailable" (offline)

        Returns:
            Response from Evolution API
        """
        try:
            if "@s.whatsapp.net" not in phone_number:
                phone_number = f"{phone_number}@s.whatsapp.net"

            url = f"{self.base_url}/chat/presence/{self.instance_name}"

            payload = {
                "number": phone_number,
                "presence": presence  # "available" or "unavailable"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                logger.debug(f"Presence set to {presence} for {phone_number}")
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error setting presence: {str(e)}")
            # Don't raise - presence is not critical
            return {}

    async def sendPresenceUpdate(self, phone_number: str, state: str = "composing") -> dict:
        """
        Send presence update (typing indicator)

        Args:
            phone_number: WhatsApp number
            state: "composing" (typing) or "paused" (stopped typing)

        Returns:
            Response from Evolution API
        """
        try:
            if "@s.whatsapp.net" not in phone_number:
                phone_number = f"{phone_number}@s.whatsapp.net"

            url = f"{self.base_url}/chat/presenceUpdate/{self.instance_name}"

            payload = {
                "number": phone_number,
                "state": state,  # "composing" or "paused"
                "delay": 2000  # milliseconds
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                logger.debug(f"Presence update: {state} for {phone_number}")
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error sending presence update: {str(e)}")
            # Don't raise - typing indicator is not critical
            return {}

    async def simulateHumanDelay(self, message: str) -> None:
        """
        Simulate human typing delay based on message length

        Args:
            message: The message being typed (used to calculate delay)
        """
        # Base delay: 0.5-1.5 seconds
        base_delay = random.uniform(0.5, 1.5)

        # Additional delay based on message length
        # Humans type ~40-60 characters per minute = ~0.7-1 char/second
        # We'll be faster but still realistic
        char_delay = len(message) * random.uniform(0.05, 0.08)

        # Total delay (max 10 seconds to not keep user waiting too long)
        total_delay = min(base_delay + char_delay, 10.0)

        logger.debug(
            f"Simulating human typing delay: {total_delay:.2f}s for {len(message)} chars")
        await asyncio.sleep(total_delay)

    async def sendTextWithHumanBehavior(
        self,
        phone_number: str,
        message: str,
        use_typing: bool = True,
        use_presence: bool = True
    ) -> dict:
        """
        Send text message with human-like behavior to avoid bot detection

        This method:
        1. Sets presence to "available" (online)
        2. Shows "typing..." indicator
        3. Waits a realistic time based on message length
        4. Sends the message
        5. Sets presence back to "unavailable" (offline) after a delay

        Args:
            phone_number: WhatsApp number
            message: Text message to send
            use_typing: Whether to show typing indicator (default: True)
            use_presence: Whether to manage online/offline status (default: True)

        Returns:
            Response from Evolution API
        """
        try:
            # Step 1: Go online
            if use_presence:
                await self.setPresence(phone_number, "available")
                await asyncio.sleep(random.uniform(0.3, 0.8))

            # Step 2: Start typing
            if use_typing:
                await self.sendPresenceUpdate(phone_number, "composing")

            # Step 3: Simulate human typing delay
            await self.simulateHumanDelay(message)

            # Step 4: Stop typing indicator
            if use_typing:
                await self.sendPresenceUpdate(phone_number, "paused")
                await asyncio.sleep(random.uniform(0.2, 0.5))

            # Step 5: Send message
            response = await self.sendTextMessage(phone_number, message)

            # Step 6: Stay online a bit, then go offline (optional)
            if use_presence:
                await asyncio.sleep(random.uniform(1.0, 3.0))
                await self.setPresence(phone_number, "unavailable")

            logger.info(f"Message sent with human behavior to {phone_number}")
            return response

        except Exception as e:
            logger.error(f"Error sending message with human behavior: {str(e)}")
            # Fallback to regular message if humanization fails
            return await self.sendTextMessage(phone_number, message)
