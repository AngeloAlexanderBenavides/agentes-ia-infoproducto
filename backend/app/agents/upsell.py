"""
Upsell Agent - Phase 6: Handle post-purchase upsell offer
"""
import logging

from app.config.settings import settings
from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)


class UpsellAgent:
    """
    Upsell Agent:
    - Handles user response to the upsell offer
    - Classifies intent (accept, info, reject)
    - Provides payment details or more info
    - Closes the conversation
    """

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Analyze message and respond to upsell intent
        """
        # Use OpenAI to classify intent intelligently
        openai_service = OpenAiService()
        intent = await openai_service.classifyUpsellIntent(
            message=message,
            user_name=state.user_name
        )

        logger.info(f"Upsell intent classified as: {intent} for user {state.user_name}")

        if intent == "accept":
            # User wants to buy the upsell
            state.current_agent = "completed"
            await update_conversation_state(sender, state)
            return self._get_payment_details(state)

        elif intent == "info":
            # User wants more information about the upsell
            return self._provide_more_info(state)

        elif intent == "reject":
            # User rejected the upsell
            state.current_agent = "completed"
            await update_conversation_state(sender, state)
            return (
                f"¡No hay problema, {state.user_name}! Entiendo perfectamente. 😊\n\n"
                "Disfruta mucho tu E-Book y recuerda que estoy aquí si tienes alguna duda con ese material.\n\n"
                "¡Mucho éxito! 🚀"
            )

        else:  # unclear
            # Unclear intent - prompt user
            return (
                "No estoy seguro de entender. 🤔\n\n"
                f"¿Te gustaría aprovechar la oferta especial del **{settings.UPSELL_PRODUCT_NAME}** por solo ${settings.UPSELL_PRICE}?\n\n"
                "Responde con:\n"
                "1️⃣ Sí, lo quiero\n"
                "2️⃣ Quiero más información\n"
                "3️⃣ No, gracias"
            )

    def _get_payment_details(self, state: ConversationState) -> str:
        """
        Provide payment details for the upsell based on country
        """
        price = settings.UPSELL_ECUADOR_PRICE if state.user_country == "Ecuador" else settings.UPSELL_PRICE
        
        if state.user_country == "Ecuador":
            payment_info = (
                f"🏦 **Transferencia Bancaria (Ecuador)**\n"
                f"Banco: {settings.BANK_NAME}\n"
                f"Tipo: {settings.BANK_ACCOUNT_TYPE}\n"
                f"Cuenta: {settings.BANK_ACCOUNT_NUMBER}\n"
                f"A nombre de: {settings.BANK_ACCOUNT_HOLDER}\n"
            )
        else:
            payment_info = (
                f"💳 **Pago Internacional**\n"
                f"Puedes pagar de forma segura a través de PayPal o Tarjeta:\n"
                f"🔗 {settings.PAYMENT_LINK_INTERNATIONAL}\n"
            )

        return (
            f"¡Excelente decisión, {state.user_name}! 🚀\n\n"
            f"El total con tu descuento especial es de **${price} USD**.\n\n"
            f"{payment_info}\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📸 **IMPORTANTE:** Cuando realices el pago, envíame una foto del comprobante por aquí mismo.\n\n"
            "En cuanto lo reciba, te enviaré el acceso inmediato al curso avanzado. ¡Quedo atento! 😊"
        )

    def _provide_more_info(self, state: ConversationState) -> str:
        """
        Provide more detailed information about the upsell product
        """
        price = settings.UPSELL_ECUADOR_PRICE if state.user_country == "Ecuador" else settings.UPSELL_PRICE
        
        return (
            f"📖 **Detalles del {settings.UPSELL_PRODUCT_NAME}:**\n\n"
            "Este curso está diseñado para que pases de la teoría a la práctica avanzada.\n\n"
            "✅ **Lo que aprenderás:**\n"
            "• Creación de agentes de IA autónomos\n"
            "• Automatización de flujos de trabajo (Make/Zapier)\n"
            "• Integración de APIs con ChatGPT\n"
            "• Casos de uso reales para negocios\n\n"
            f"💰 **Tu Precio Especial:** ${price} USD (Precio normal: $49.99)\n\n"
            "¿Te animas a dar el siguiente paso? 🚀\n"
            "Dime 'Sí' para enviarte los datos de pago, o 'No gracias' si prefieres dejarlo para después."
        )
