"""
Greeter Agent - Phase 1: Initial greeting, extract name/country, hook with prize.

FLOW:
  1. First message arrives → AI tries to extract name+country
  2. If found → skip straight to Consultant
  3. If NOT found → hook: "Tengo un regalo para ti, solo necesito nombre y país"
  4. User replies → extract again → move to Consultant
  5. Final retry → take best guess and move on

ALL responses are pre-written templates.
AI is ONLY used for extraction (parseNameAndCountry) — never for generating text.
"""
import logging
import re

from app.database.db import update_conversation_state
from app.models.conversation import ConversationState
from app.services.openaiService import OpenAiService

logger = logging.getLogger(__name__)

# ── Greeting words that are NOT valid names ───────────────────────────────────
_GREETING_WORDS = {
    "hola", "hello", "hi", "buenas", "buenos", "buen", "buenas tardes",
    "buenas noches", "buenos días", "good morning", "hey", "ola", "que tal",
    "qué tal", "como estas", "cómo estás", "saludos", "buen día",
}


def _clean_name(name: str | None) -> str | None:
    """Strip trailing/leading punctuation, normalize whitespace, title-case."""
    if not name:
        return None
    name = re.sub(r"[,.\-!?;:]+$", "", name)   # trailing punctuation
    name = re.sub(r"^[,.\-!?;:]+", "", name)   # leading punctuation
    name = name.strip()
    return name.title() if name else None


def _is_valid_name(name: str | None) -> bool:
    """Return True if the parsed name looks like a real name (not a greeting)."""
    if not name:
        return False
    n = name.strip().lower()
    if n in _GREETING_WORDS:
        return False
    if len(n) < 2:
        return False
    return True


class GreeterAgent:
    """
    Greeter Agent:
    - Tries to extract name+country from the FIRST message
    - If found → greet and move to consultant immediately
    - If not found → hook with prize, ask for name+country
    - Parse response → move to consultant

    All responses are deterministic templates.
    AI is ONLY used for extraction (parseNameAndCountry).
    """

    async def process(self, sender: str, message: str, state: ConversationState) -> str:
        """Route by greeter_step. No 'cambiar nombre' intercept during collection."""

        # ── 1. First interaction: try to extract from the initial message ────
        if not state.greeter_step or state.greeter_step == "init":
            name, country = await self._extract(message)

            if name:
                # Got it on the first message — skip to consultant
                return await self._complete(sender, state, name, country)

            # Can't extract → hook with prize
            state.greeter_step = "asked_name"
            await update_conversation_state(sender, state)
            return (
                "¡Hola! 👋 Qué bueno que escribes.\n\n"
                "Tengo un *regalo especial* listo para ti 🎁\n"
                "Para enviártelo solo necesito dos cosas:\n\n"
                "📝 Tu *nombre*\n"
                "🌍 Tu *país*\n\n"
                "Por ejemplo: *Luis, Ecuador*"
            )

        # ── 2. User replied after the hook ───────────────────────────────────
        elif state.greeter_step == "asked_name":
            name, country = await self._extract(message)

            if not name:
                state.greeter_step = "retry_name"
                await update_conversation_state(sender, state)
                return (
                    "No logré captar tu nombre 😅\n\n"
                    "Escríbelo así: *Nombre, País*\n"
                    "Ejemplo: *Carlos, Colombia*"
                )

            return await self._complete(sender, state, name, country)

        # ── 3. Final retry — accept whatever we can get ──────────────────────
        elif state.greeter_step == "retry_name":
            name, country = await self._extract(message)

            if not name:
                # Best guess: first word ≥2 chars
                words = [w for w in message.split() if len(w) >= 2]
                name = _clean_name(words[0]) if words else "Amigo"

            return await self._complete(sender, state, name or "Amigo", country)

        # ── Fallback ─────────────────────────────────────────────────────────
        return (
            "Escríbeme tu nombre y país para enviarte tu regalo 🎁\n"
            "Ejemplo: *María, Perú*"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _extract(self, message: str) -> tuple[str | None, str | None]:
        """Use AI to extract name+country, then clean & validate."""
        openai_service = OpenAiService()
        name, country = await openai_service.parseNameAndCountry(message)

        name = _clean_name(name)
        if not _is_valid_name(name):
            name = None

        if country and country.lower() in ("unknown", "null", "none", ""):
            country = None

        return name, country

    async def _complete(
        self, sender: str, state: ConversationState,
        name: str, country: str | None
    ) -> str:
        """Save name+country, transition to consultant."""
        state.user_name = name
        state.user_country = country or "Unknown"
        state.greeter_step = "completed"
        state.current_agent = "consultant"
        await update_conversation_state(sender, state)

        from app.agents.consultant import ConsultantAgent
        consultant = ConsultantAgent()
        return await consultant.start(sender, state)
