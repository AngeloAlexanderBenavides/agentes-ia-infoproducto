"""
Consultant Agent - Phase 2: The Hook - Diagnose need and deliver personalized gift
"""
import logging

from app.config.settings import settings
from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)


class ConsultantAgent:
    """
    Consultant Agent (The Hook):
    - Asks diagnostic question about experience level
    - Delivers personalized gift (lead magnet)
    - Presents product information
    - Transitions to Router agent
    """

    async def start(self, sender: str, state: ConversationState) -> str:
        """
        Start consultant interaction after greeter
        """
        state.consultant_step = "asked_level"
        await update_conversation_state(sender, state)

        flag = self._get_country_flag(state.user_country)

        return (
            f"¡Qué bueno conocerte, {state.user_name}! {flag}\n\n"
            "Antes de enviarte cualquier cosa, quiero asegurarme de darte justo lo que necesitas... "
            "no tiene sentido mandarte cosas que ya sabes o que se te van a hacer muy básicas.\n\n"
            "Cuéntame: ¿tienes experiencia trabajando con inteligencia artificial o "
            "esto es algo nuevo que estás explorando por primera vez?"
        )

    def _classifyLevelLocally(self, message: str) -> str | None:
        """
        Fast keyword-based level classification — no API call needed.
        Returns None if ambiguous, so the caller can fall back to AI.
        """
        m = message.strip().lower()
        BEGINNER = ["1", "novato", "princip", "cero", "empiezo",
                    "empezando", "comenzando", "nunca", "nuevo"]
        INTERMEDIATE = ["2", "algo", "básico",
                        "experiencia", "probado", "un poco", "conoce"]
        ADVANCED = ["3", "avanzado", "experto", "domino", "mucha", "avanzad"]
        for kw in BEGINNER:
            if kw in m:
                return "beginner"
        for kw in ADVANCED:
            if kw in m:
                return "advanced"
        for kw in INTERMEDIATE:
            if kw in m:
                return "intermediate"
        return None

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Process user response about their experience level.
        Uses fast local matching; only calls AI when the message is ambiguous.
        """
        if state.consultant_step == "asked_level":
            # 1) Try keyword match first (free, instant)
            level = self._classifyLevelLocally(message)
            if level is None:
                # 2) Fallback to AI only when we truly can't tell
                openai_service = OpenAiService()
                level = await openai_service.classifyUserLevel(message, state.user_name)
                logger.info(f"[consultant] AI classifyUserLevel → {level}")
            else:
                logger.info(f"[consultant] local classifyUserLevel → {level}")

            # Get level text for display
            level_text_map = {
                "beginner": "novato/a",
                "intermediate": "con experiencia",
                "advanced": "avanzado/a"
            }
            level_text = level_text_map.get(level, "empezando")

            state.user_level = level
            state.consultant_step = "completed"
            state.current_agent = "router"

            await update_conversation_state(sender, state)

            # Personalized response based on level
            response = self._get_personalized_gift_message(
                state.user_name, level, level_text)

            return response

        # Fallback
        return "Cuéntame con tus palabras, no te preocupes por la forma. 😊 ¿Eres nuevo en esto o ya tienes alguna experiencia?"

    def _get_personalized_gift_message(self, name: str, level: str, level_text: str) -> str:
        """
        Create personalized message based on user level
        """
        base_message = f"¡Perfecto, {name}! Veo que eres {level_text}.\n\n"

        if level == "beginner":
            gift_message = (
                "📚 Como principiante, tengo algo PERFECTO para ti:\n"
                f"**{settings.LEAD_MAGNET_NAME}**\n\n"
                "Estos cursos te darán las bases que necesitas.\n\n"
            )
        elif level == "intermediate":
            gift_message = (
                "🚀 Tengo justo lo que necesitas para dar el siguiente paso:\n"
                f"**{settings.LEAD_MAGNET_NAME}**\n\n"
                "Te ayudarán a consolidar y expandir lo que ya sabes.\n\n"
            )
        else:  # advanced
            gift_message = (
                "💎 Para alguien de tu nivel, esto te servirá de repaso:\n"
                f"**{settings.LEAD_MAGNET_NAME}**\n\n"
                "Incluso los expertos encuentran tips valiosos aquí.\n\n"
            )

        product_info = (
            f"🎁 **Accede aquí:** {settings.LEAD_MAGNET_URL}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Ahora, sobre el producto PREMIUM:\n\n"
            f"📖 **{settings.PRODUCT_NAME}**\n"
            f"{settings.PRODUCT_DESCRIPTION}\n\n"
            "¿Te gustaría saber más sobre cómo funciona o ya quieres proceder con la compra?"
        )

        return base_message + gift_message + product_info

    def _get_country_flag(self, country: str) -> str:
        """Get emoji flag for country"""
        flags = {
            "Ecuador": "🇪🇨",
            "Colombia": "🇨🇴",
            "Perú": "🇵🇪",
            "México": "🇲🇽",
            "Argentina": "🇦🇷",
            "Chile": "🇨🇱",
            "España": "🇪🇸",
        }
        return flags.get(country, "🌍")
