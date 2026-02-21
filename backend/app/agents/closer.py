"""
Closer Agent - Phase 4: Handle payment process (especially Ecuador local transfers)
"""
import logging

from app.config.settings import settings
from app.database.db import update_conversation_state
from app.models.conversation import ConversationState

logger = logging.getLogger(__name__)


class CloserAgent:
    """
    Closer Agent:
    - Calculates final price (with Ecuador discount if applicable)
    - Provides payment instructions
    - Requests payment proof for local transfers
    - Routes to Verifier for payment confirmation
    """

    async def start(self, sender: str, state: ConversationState) -> str:
        """
        Start closing process
        """
        state.closer_step = "presenting_payment"
        await update_conversation_state(sender, state)

        # Calculate price
        final_price = settings.BASE_PRICE
        discount_message = ""

        if state.user_country == "Ecuador":
            final_price = settings.BASE_PRICE - settings.ECUADOR_DISCOUNT
            discount_message = f"🎉 ¡Buenas noticias! Por ser de Ecuador, tienes un descuento especial de ${settings.ECUADOR_DISCOUNT}.\n\n"

        state.final_price = final_price
        await update_conversation_state(sender, state)

        # Payment instructions
        if state.user_country == "Ecuador":
            # Local transfer option for Ecuador
            payment_message = (
                f"¡Excelente decisión, {state.user_name}! 🎉\n\n"
                f"{discount_message}"
                f"💰 **Tu precio final: ${final_price}**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "**Opción de pago (Ecuador):**\n\n"
                f"🏦 **Banco:** {settings.BANK_NAME}\n"
                f"👤 **Titular:** {settings.BANK_ACCOUNT_HOLDER}\n"
                f"🔢 **Cuenta {settings.BANK_ACCOUNT_TYPE}:** {settings.BANK_ACCOUNT_NUMBER}\n"
                f"💵 **Monto:** ${final_price}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ **IMPORTANTE:**\n"
                "Una vez que hagas la transferencia, envíame una foto del comprobante "
                "por aquí mismo para verificar tu pago y activar tu acceso inmediatamente. 📸\n\n"
                "¿Alguna duda antes de proceder?"
            )
        else:
            # International payment (you can add PayPal, Stripe, etc.)
            payment_message = (
                f"¡Excelente decisión, {state.user_name}! 🎉\n\n"
                f"💰 **Tu precio: ${final_price}**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Para pagos internacionales, acepto:\n\n"
                "💳 PayPal: [tu_email_paypal]\n"
                "💳 Stripe: [tu_link_stripe]\n\n"
                "Una vez realizado el pago, envíame el comprobante por aquí. 📸"
            )

        return payment_message

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Handle questions or confirmations during closing
        """
        message_lower = message.lower()

        # User has questions
        if "?" in message or "duda" in message_lower or "pregunta" in message_lower:
            return (
                "Claro, con gusto te respondo. 😊\n\n"
                "¿Qué necesitas saber específicamente?"
            )

        # User confirms they're going to pay
        if any(word in message_lower for word in ["ok", "listo", "ya", "ahora", "voy", "entendido"]):
            state.waiting_for_payment_proof = True
            state.closer_step = "waiting_proof"
            await update_conversation_state(sender, state)

            return (
                f"¡Perfecto, {state.user_name}! 👍\n\n"
                "Haz la transferencia cuando estés listo/a y envíame la foto del comprobante.\n\n"
                "Estaré atento para verificar y darte acceso inmediato. ⚡"
            )

        # User might want to reconsider
        if any(word in message_lower for word in ["no", "espera", "después", "luego"]):
            return (
                "Sin problema. Tómate tu tiempo. 😊\n\n"
                "Cuando estés listo/a, solo escríbeme y retomamos desde aquí.\n\n"
                "¿Hay algo específico que te esté frenando? Cuéntame y vemos cómo resolverlo."
            )

        # Default response
        return (
            "Si tienes alguna pregunta sobre el pago, escríbela.\n"
            "Si ya estás listo/a, haz la transferencia y envíame el comprobante. 📸"
        )
