"""
Greeter Agent - Phase 1: Initial greeting and collect name/country
"""
import logging

from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)


class GreeterAgent:
    """
    Greeter Agent handles the initial interaction:
    - Greets the user
    - Asks for name and country
    - Transitions to Consultant agent
    """

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Process user message in greeter stage
        """
        # First interaction - send greeting
        if not state.user_name:
            # User just said hello or something
            state.greeter_step = "asked_name"
            await update_conversation_state(sender, state)

            return (
                "¡Hola! 👋 Bienvenido/a.\n\n"
                "Para poder ayudarte de la mejor manera y darte un regalo especial, "
                "necesito saber:\n\n"
                "¿Cómo te llamas y de qué país me escribes?"
            )

        # User responded with name and country
        if state.greeter_step == "asked_name":
            # Use OpenAI to parse name and country intelligently
            openai_service = OpenAiService()
            name, country = await openai_service.parseNameAndCountry(message)

            # Validate parsing
            if not name or not country:
                # Try to extract at least something
                if not name:
                    name = message.split()[0].strip().title(
                    ) if message.split() else "Amigo/a"
                if not country:
                    country = "Unknown"

            # Save to state
            state.user_name = name
            state.user_country = country
            state.current_agent = "consultant"
            state.greeter_step = "completed"

            await update_conversation_state(sender, state)

            # Transition to Consultant
            from app.agents.consultant import ConsultantAgent
            consultant = ConsultantAgent()
            return await consultant.start(sender, state)

        # Fallback
        return "Perdona, no entendí bien. Por favor dime tu nombre y país. Ejemplo: 'Carlos, Ecuador'"
