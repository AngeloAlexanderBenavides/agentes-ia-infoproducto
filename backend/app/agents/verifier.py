"""
Verifier Agent - Phase 5: Handle payment verification and product delivery
"""
import logging

from app.config.settings import settings
from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.notificationService import NotificationService

logger = logging.getLogger(__name__)


class VerifierAgent:
    """
    Verifier Agent:
    - Receives payment proof (image)
    - Notifies Angelo via WhatsApp
    - Waits for manual confirmation
    - Delivers product upon confirmation
    """

    def __init__(self):
        self.notification_service = NotificationService()

    async def handlePaymentProof(
        self,
        sender: str,
        image_data: dict,
        state: ConversationState
    ) -> str:
        """
        Handle when user sends payment proof image
        """
        if not state.waiting_for_payment_proof:
            return (
                "Gracias por la imagen, pero no estoy esperando un comprobante de pago en este momento. 🤔\n\n"
                "¿En qué puedo ayudarte?"
            )

        # Save image info
        state.payment_proof_received = True
        state.payment_proof_image = image_data
        await update_conversation_state(sender, state)

        # Notify Angelo
        await self._notify_owner(sender, state)

        # Respond to user
        return (
            f"¡Gracias, {state.user_name}! 📸\n\n"
            "He recibido tu comprobante de pago. Déjame verificarlo con mi sistema bancario.\n\n"
            "Te confirmo en los próximos minutos (generalmente es muy rápido). ⏱️\n\n"
            "¡Gracias por tu paciencia! 😊"
        )

    async def _notify_owner(self, sender: str, state: ConversationState):
        """
        Send notification to Angelo's WhatsApp
        """
        notification_message = (
            "🔔 **¡NUEVO PAGO PENDIENTE!**\n\n"
            f"👤 **Cliente:** {state.user_name}\n"
            f"🌍 **País:** {state.user_country}\n"
            f"📱 **Teléfono:** {sender}\n"
            f"💰 **Monto:** ${state.final_price}\n"
            f"🏦 **Banco:** {settings.BANK_NAME}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📸 El cliente envió comprobante de pago.\n\n"
            "**Acción requerida:**\n"
            "1. Revisa tu app del banco\n"
            "2. Si el pago llegó, confirma con:\n"
            f"   `/confirmar {sender.replace('@s.whatsapp.net', '')}`\n\n"
            "O usa el endpoint:\n"
            "POST /api/confirm-payment\n"
            f'{{"phone_number": "{sender}", "user_name": "{state.user_name}"}}'
        )

        await self.notification_service.sendToOwner(notification_message)

        # Log for debugging
        logger.info(f"Payment proof received from {state.user_name} ({sender})")

    async def confirmPaymentAndDeliverProduct(
        self,
        sender: str,
        user_name: str,
        state: ConversationState
    ) -> bool:
        """
        Called after Angelo confirms payment (via API or command)
        Delivers the product to the customer
        """
        try:
            # Mark as paid
            state.payment_confirmed = True
            state.waiting_for_payment_proof = False
            state.product_delivered = True
            state.current_agent = "upsell"

            await update_conversation_state(sender, state)

            # Send product delivery message with human behavior
            delivery_message = await self._get_delivery_message(user_name)

            from app.services.evolutionApi import EvolutionApiService
            evolution_service = EvolutionApiService()
            await evolution_service.sendTextWithHumanBehavior(
                sender,
                delivery_message,
                use_typing=True,
                use_presence=True
            )

            # Notify Angelo of successful delivery
            await self.notification_service.sendToOwner(
                f"✅ Producto entregado exitosamente a {user_name} ({sender})"
            )

            logger.info(f"Product delivered to {user_name} ({sender})")
            return True

        except Exception as e:
            logger.error(f"Error delivering product: {str(e)}")
            return False

    async def _get_delivery_message(self, user_name: str) -> str:
        """
        Create product delivery message with upsell
        """
        return (
            f"🎉 **¡CONFIRMADO, {user_name}!**\n\n"
            "✅ Tu pago ha sido verificado exitosamente.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎁 **Acceso a tu E-Book:**\n\n"
            f"📖 **{settings.PRODUCT_NAME}**\n\n"
            f"🔗 **Link de descarga:** {settings.PRODUCT_DELIVERY_URL}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📚 **Instrucciones:**\n"
            "1. Haz clic en el link de arriba\n"
            "2. Descarga el E-Book en formato PDF\n"
            "3. ¡Comienza a dominar la Ingeniería de Prompts!\n\n"
            "🎯 **Bonus incluidos:**\n"
            f"• {settings.LEAD_MAGNET_NAME} (ya los tienes)\n"
            "• Soporte directo vía WhatsApp\n"
            "• Actualizaciones del contenido gratis\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 **Tip:** Guarda este link para siempre. Podrás acceder cuando quieras.\n\n"
            "¡Disfruta tu aprendizaje y mucho éxito aplicando estas técnicas! 🚀\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔥 **¡ESPERA! TENGO UNA OFERTA EXCLUSIVA PARA TI** 🔥\n\n"
            f"Ya que confiaste en mí y adquiriste el E-Book, quiero ofrecerte algo especial para llevar tus conocimientos al siguiente nivel.\n\n"
            f"🚀 **{settings.UPSELL_PRODUCT_NAME}**\n\n"
            "En este curso aprenderás a crear tus propios agentes de IA y automatizar procesos como un profesional.\n\n"
            f"💰 **Precio Especial:** Solo ${settings.UPSELL_PRICE} USD (o ${settings.UPSELL_ECUADOR_PRICE} si estás en Ecuador).\n\n"
            "👉 **¿Te interesa?** Solo dime 'Sí, quiero el curso' y te enviaré los detalles para acceder de inmediato.\n\n"
            "Si necesitas ayuda o tienes dudas con tu E-Book, sigo estando aquí. 😊"
        )
