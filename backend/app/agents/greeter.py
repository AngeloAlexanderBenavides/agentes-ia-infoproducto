"""
Greeter Agent - Phase 1: Initial greeting and collect name/country
"""
import logging

from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)

# Words that are greetings, not names — reject these if Claude returns them as a name
_GREETING_WORDS = {
    "hola", "hello", "hi", "buenas", "buenos", "buen", "buenas tardes",
    "buenas noches", "buenos días", "good morning", "hey", "ola", "que tal",
    "qué tal", "como estas", "cómo estás", "saludos", "buen día",
}


def _is_valid_name(name: str | None) -> bool:
    """Return True if the parsed name looks like a real name (not a greeting)."""
    if not name:
        return False
    n = name.strip().lower()
    if n in _GREETING_WORDS:
        return False
    # Single word less than 2 chars is probably not a name
    if len(n) < 2:
        return False
    return True


class GreeterAgent:
    """
    Greeter Agent handles the initial interaction:
    - Greets the user
    - Asks for name and country
    - Transitions to Consultant agent
    """

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """
        Process user message in greeter stage.
        Also handles "cambiar nombre / me llamo X" commands at any stage.
        """
        m = message.strip().lower()

        # ── Update command: user wants to change their name/country ──────────
        if any(kw in m for kw in ["cambiar nombre", "cambiar datos", "me llamo", "mi nombre es", "actualizar"]):
            state.greeter_step = "asked_name"
            state.user_name = None
            state.user_country = None
            await update_conversation_state(sender, state)
            return (
                "Sin problema, cuéntame de nuevo. 😊\n\n"
                "¿Cómo te llamas y de qué país me escribes?"
            )

        # ── First interaction ─────────────────────────────────────────────────
        if not state.greeter_step or state.greeter_step == "init":
            state.greeter_step = "asked_name"
            await update_conversation_state(sender, state)

            return (
                "¡Hola! 👋 Qué bueno que estás aquí.\n\n"
                "Antes de empezar, ¿me dices tu nombre y desde qué país me escribes?"
            )

        # ── User responded with name and country ──────────────────────────────
        elif state.greeter_step == "asked_name":
            openai_service = OpenAiService()
            name, country = await openai_service.parseNameAndCountry(message)

            # Validate: reject greeting words as names
            if not _is_valid_name(name):
                name = None

            if not name:
                # Can't extract a name — ask once more with a friendly nudge
                state.greeter_step = "retry_name"
                await update_conversation_state(sender, state)
                return (
                    "Disculpa, no capté bien tu nombre. 😅\n\n"
                    "¿Me puedes decir cómo te llamas y de qué país eres? "
                    "Por ejemplo: *\"Carlos, Ecuador\"*"
                )

            if not country or country == "Unknown":
                country = "Unknown"

            state.user_name = name
            state.user_country = country
            state.current_agent = "consultant"
            state.greeter_step = "completed"
            await update_conversation_state(sender, state)

            from app.agents.consultant import ConsultantAgent
            consultant = ConsultantAgent()
            return await consultant.start(sender, state)

        # ── Retry after failed name extraction ───────────────────────────────
        elif state.greeter_step == "retry_name":
            openai_service = OpenAiService()
            name, country = await openai_service.parseNameAndCountry(message)

            if not _is_valid_name(name):
                # Take first capitalized word as best guess
                words = [w for w in message.split() if len(w) >= 2]
                name = words[0].strip().title() if words else "Amigo/a"

            if not country or country == "Unknown":
                country = "Unknown"

            state.user_name = name
            state.user_country = country
            state.current_agent = "consultant"
            state.greeter_step = "completed"
            await update_conversation_state(sender, state)

            from app.agents.consultant import ConsultantAgent
            consultant = ConsultantAgent()
            return await consultant.start(sender, state)

        # ── Fallback ──────────────────────────────────────────────────────────
        return "Cuéntame tu nombre y país para poder ayudarte mejor. 😊"
