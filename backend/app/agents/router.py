"""
Router Agent - Phase 3: Classify purchase intent and route accordingly
"""
import logging

from app.config.settings import settings
from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)


class RouterAgent:
    """
    Router Agent:
    - Classifies user intent (purchase vs. more info vs. objection)
    - Routes to Closer for purchases
    - Handles information requests
    - Handles objections
    """

    def _classifyIntentLocally(self, message: str) -> str | None:
        """
        Fast keyword-based intent classification — no API call needed.
        Returns None if ambiguous so the caller can use AI as fallback.
        """
        m = message.strip().lower()
        PURCHASE = ["1", "comprar", "pagar", "precio", "cómo pago", "como pago", "quiero",
                    "proceder", "sí quiero", "si quiero", "me interesa", "cuánto", "cuanto"]
        INFO = ["2", "más info", "mas info", "información", "informacion", "cómo funciona",
                "como funciona", "detalles", "qué incluye", "que incluye", "saber más", "saber mas"]
        OBJECTION = ["3", "caro", "no tengo", "sin dinero", "después",
                     "luego", "espera", "duda", "dudas", "no sé", "no se", "pensarlo"]
        for kw in PURCHASE:
            if kw in m:
                return "purchase"
        for kw in INFO:
            if kw in m:
                return "info"
        for kw in OBJECTION:
            if kw in m:
                return "objection"
        return None

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Analyze message and route appropriately.
        Uses fast local matching; only calls AI when ambiguous.
        """
        openai_service = OpenAiService()

        # 1) Try keyword match first (free, instant)
        intent = self._classifyIntentLocally(message)
        if intent is None:
            # 2) Fallback to AI only when we truly can't tell
            intent = await openai_service.classifyIntent(
                message=message,
                user_name=state.user_name,
                context=f"Usuario de nivel {state.user_level}"
            )
            logger.info(f"[router] AI classifyIntent → {intent} for {state.user_name}")
        else:
            logger.info(
                f"[router] local classifyIntent → {intent} for {state.user_name}")

        # Route based on classified intent
        if intent == "purchase":
            # User wants to buy - route to Closer
            state.current_agent = "closer"
            await update_conversation_state(sender, state)

            from app.agents.closer import CloserAgent
            closer = CloserAgent()
            return await closer.start(sender, state)

        elif intent == "info":
            # User wants more information
            return await self._provide_more_info(sender, state)

        elif intent == "objection":
            # Handle objections with deterministic templates (no AI generation)
            return await self._handle_objection(sender, state, message)

        else:  # unclear
            # Unclear intent - prompt user
            return (
                "Entiendo. ¿Qué te gustaría hacer?\n\n"
                "1️⃣ Proceder con la compra\n"
                "2️⃣ Saber más detalles del producto\n"
                "3️⃣ Tengo algunas dudas\n\n"
                "Responde con el número o escríbeme lo que necesites. 😊"
            )

    async def _provide_more_info(self, sender: str, state: ConversationState) -> str:
        """
        Provide more detailed information about the product
        """
        from app.config.settings import settings

        return (
            f"📖 **Detalles completos de {settings.PRODUCT_NAME}:**\n\n"
            f"{settings.PRODUCT_DESCRIPTION}\n\n"
            "✅ **Lo que obtienes:**\n"
            "• Acceso inmediato al contenido completo\n"
            "• Actualizaciones gratis de por vida\n"
            "• Soporte directo conmigo\n"
            "• Garantía de satisfacción\n\n"
            f"💰 **Precio:** ${settings.BASE_PRICE}\n"
            f"{'🇪🇨 **Precio Ecuador:** $' + str(settings.BASE_PRICE - settings.ECUADOR_DISCOUNT) + ' (¡Descuento especial!)' if state.user_country == 'Ecuador' else ''}\n\n"
            "¿Listo/a para empezar? 🚀"
        )

    async def _handle_objection(self, sender: str, state: ConversationState, message: str) -> str:
        """
        Handle common objections
        """
        if "caro" in message or "precio" in message:
            return (
                f"Entiendo tu preocupación, {state.user_name}. 💭\n\n"
                f"Piénsalo así: ${settings.BASE_PRICE} es menos de lo que gastas en un almuerzo, "
                "pero esto es una inversión que te va a durar para siempre.\n\n"
                "Además, piensa en el tiempo y dinero que vas a AHORRAR al tener todo esto resuelto. 🎯\n\n"
                f"{'Y como eres de Ecuador, te lo dejo en $' + str(settings.BASE_PRICE - settings.ECUADOR_DISCOUNT) + '. 🇪🇨' if state.user_country == 'Ecuador' else ''}\n\n"
                "¿Qué te parece?"
            )

        elif "después" in message or "luego" in message or "tarde" in message:
            return (
                f"Te entiendo, {state.user_name}. La vida está ocupada. 😅\n\n"
                "Pero déjame decirte algo: los mejores momentos para actuar son cuando tienes la motivación AHORA.\n\n"
                "El acceso es inmediato, así que en 5 minutos ya podrías estar dentro. ⚡\n\n"
                "¿Qué te detiene realmente? Cuéntame y vemos cómo resolverlo. 💪"
            )

        else:
            return (
                f"Entiendo tus dudas, {state.user_name}. 🤔\n\n"
                "Cuéntame específicamente qué te preocupa y con gusto te lo aclaro.\n\n"
                "Estoy aquí para ayudarte a tomar la mejor decisión. 😊"
            )
