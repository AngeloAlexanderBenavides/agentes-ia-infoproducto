"""
Notification Service - Send notifications to Angelo
"""
import logging

from app.config.settings import settings
from app.services.evolutionApi import EvolutionApiService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service to send notifications to the owner (Angelo)
    """

    def __init__(self):
        self.evolution_service = EvolutionApiService()
        self.owner_phone = settings.OWNER_WHATSAPP

    async def sendToOwner(self, message: str) -> bool:
        """
        Send notification message to Angelo's WhatsApp

        Args:
            message: Notification message

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Ensure owner phone has correct format
            owner_phone = self.owner_phone
            if "@s.whatsapp.net" not in owner_phone:
                owner_phone = f"{owner_phone}@s.whatsapp.net"

            await self.evolution_service.sendTextMessage(owner_phone, message)
            logger.info(f"Notification sent to owner: {message[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification to owner: {str(e)}")
            return False

    async def notifyNewLead(self, user_name: str, user_country: str, phone: str):
        """
        Notify about new lead
        """
        message = (
            f"👤 **Nuevo Lead**\n\n"
            f"Nombre: {user_name}\n"
            f"País: {user_country}\n"
            f"Teléfono: {phone}"
        )
        await self.sendToOwner(message)

    async def notifyPaymentPending(
        self,
        user_name: str,
        user_country: str,
        phone: str,
        amount: float
    ):
        """
        Notify about pending payment verification
        """
        message = (
            f"💰 **Pago Pendiente de Verificación**\n\n"
            f"Cliente: {user_name}\n"
            f"País: {user_country}\n"
            f"Teléfono: {phone}\n"
            f"Monto: ${amount}\n\n"
            "Revisa tu banco y confirma el pago."
        )
        await self.sendToOwner(message)

    async def notifyPaymentConfirmed(self, user_name: str, amount: float):
        """
        Notify about confirmed payment
        """
        message = (
            f"✅ **Pago Confirmado**\n\n"
            f"Cliente: {user_name}\n"
            f"Monto: ${amount}\n\n"
            "Producto entregado exitosamente."
        )
        await self.sendToOwner(message)
