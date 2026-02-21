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
            f"¡Buenísimo, {state.user_name}! {flag}\n\n"
            f"Mira, para no darte material que ya conozcas y darte el regalo perfecto para ti...\n\n"
            f"¿Ya has trabajado con {settings.PRODUCT_NAME} antes o estás empezando desde cero?\n\n"
            "Responde con:\n"
            "1️⃣ Soy novato/a, empiezo de cero\n"
            "2️⃣ Ya tengo algo de experiencia\n"
            "3️⃣ Soy avanzado/a"
        )

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Process user response about their experience level (using AI)
        """
        if state.consultant_step == "asked_level":
            # Use OpenAI to classify user level intelligently
            openai_service = OpenAiService()
            level = await openai_service.classifyUserLevel(message, state.user_name)

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
        return "Por favor, responde 1, 2 o 3 según tu nivel de experiencia. 😊"

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
