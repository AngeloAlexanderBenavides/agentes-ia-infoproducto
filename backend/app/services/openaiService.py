"""
AI Service - powered by Anthropic Claude
"""
import json
import logging
from typing import Literal

import anthropic
from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpenAiService:
    """
    Service to interact with Anthropic Claude for intelligent message processing.
    Class name kept as OpenAiService for backward compatibility.
    """

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-haiku-20241022"  # Fast and cost-effective

    async def classifyUserLevel(self, message: str, user_name: str) -> Literal["beginner", "intermediate", "advanced"]:
        try:
            prompt = f"""Analiza la siguiente respuesta de {user_name} sobre su nivel de experiencia y clasifícalo.

Respuesta del usuario: "{message}"

Clasifica su nivel como:
- "beginner" si es novato, principiante, empieza de cero, nunca ha hecho esto
- "intermediate" si tiene algo de experiencia, conoce lo básico, ha probado antes
- "advanced" si es experto, avanzado, tiene mucha experiencia, domina el tema

Responde SOLO con una palabra: beginner, intermediate o advanced"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                system="Eres un clasificador experto que determina el nivel de experiencia de usuarios. Responde solo con: beginner, intermediate o advanced",
                messages=[{"role": "user", "content": prompt}]
            )

            classification = response.content[0].text.strip().lower()

            if classification not in ["beginner", "intermediate", "advanced"]:
                logger.warning(
                    f"Unexpected classification: {classification}, defaulting to beginner")
                return "beginner"

            logger.info(f"User level classified as: {classification}")
            return classification

        except Exception as e:
            logger.error(f"Error classifying user level: {str(e)}")
            return "beginner"

    async def classifyIntent(
        self,
        message: str,
        user_name: str,
        context: str = ""
    ) -> Literal["purchase", "info", "objection", "unclear"]:
        try:
            prompt = f"""Analiza la intención del siguiente mensaje de {user_name}.

Mensaje: "{message}"
{f'Contexto: {context}' if context else ''}

Clasifica la intención como:
- "purchase" si quiere comprar, proceder, le interesa, dice cuánto cuesta, pregunta cómo pagar
- "info" si quiere más información, detalles, características, cómo funciona
- "objection" si tiene dudas, dice que está caro, no tiene dinero, lo dejará para después
- "unclear" si no está claro o es otro tema

Responde SOLO con una palabra: purchase, info, objection o unclear"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                system="Eres un clasificador experto de intenciones de compra. Responde solo con: purchase, info, objection o unclear",
                messages=[{"role": "user", "content": prompt}]
            )

            intent = response.content[0].text.strip().lower()

            if intent not in ["purchase", "info", "objection", "unclear"]:
                logger.warning(f"Unexpected intent: {intent}, defaulting to unclear")
                return "unclear"

            logger.info(f"Intent classified as: {intent}")
            return intent

        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return "unclear"

    async def parseNameAndCountry(self, message: str) -> tuple[str | None, str | None]:
        try:
            prompt = f"""Extrae el nombre y el país del siguiente mensaje:

Mensaje: "{message}"

Responde en formato JSON exactamente así:
{{"name": "Nombre", "country": "País"}}

Si no encuentras el nombre o país, usa null.
El país debe estar en español y capitalizado (Ecuador, Colombia, Perú, etc.)
Responde SOLO con el JSON, sin texto adicional."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=50,
                system="Eres un extractor experto de información. Responde SOLO con JSON válido, sin texto adicional.",
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text.strip()
            # Extract JSON even if there's surrounding text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                text = text[start:end]
            result = json.loads(text)

            name = result.get("name")
            country = result.get("country")

            logger.info(f"Parsed name: {name}, country: {country}")
            return name, country

        except Exception as e:
            logger.error(f"Error parsing name and country: {str(e)}")
            return None, None

    async def handleObjection(
        self,
        message: str,
        user_name: str,
        objection_type: str = "general"
    ) -> str:
        try:
            prompt = f"""Eres un vendedor experto y empático. {user_name} tiene una objeción sobre un producto.

Objeción de {user_name}: "{message}"

Genera una respuesta que:
1. Sea empática y comprensiva
2. Maneje la objeción de forma natural
3. Reoriente hacia el valor del producto
4. Use emojis de forma moderada
5. Sea conversacional y amigable
6. Máximo 3-4 líneas
7. NO seas insistente ni presiones

Genera SOLO la respuesta, sin introducción."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                system="Eres un vendedor consultivo experto que maneja objeciones con empatía y profesionalismo.",
                messages=[{"role": "user", "content": prompt}]
            )

            objection_response = response.content[0].text.strip()
            logger.info(f"Generated objection response for {user_name}")
            return objection_response

        except Exception as e:
            logger.error(f"Error handling objection: {str(e)}")
            return (
                f"Entiendo tus dudas, {user_name}. 🤔\n\n"
                "Cuéntame específicamente qué te preocupa y con gusto te lo aclaro.\n\n"
                "Estoy aquí para ayudarte a tomar la mejor decisión. 😊"
            )

    async def classifyUpsellIntent(
        self,
        message: str,
        user_name: str
    ) -> Literal["accept", "info", "reject", "unclear"]:
        """
        Classify user's response to the upsell offer

        Args:
            message: User's message
            user_name: User's name

        Returns:
            Intent: "accept", "info", "reject", or "unclear"
        """
        try:
            prompt = f"""Analiza la respuesta de {user_name} a una oferta de un curso avanzado (upsell).

Mensaje: "{message}"

Clasifica la intención como:
- "accept" si dice que sí, lo quiere, le interesa, pregunta cómo pagar, acepta la oferta
- "info" si quiere más información, de qué trata, qué incluye, cuánto dura
- "reject" si dice que no, no gracias, por ahora no, en otro momento, está muy caro
- "unclear" si no está claro o habla de otra cosa

Responde SOLO con una palabra: accept, info, reject o unclear"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                system="Eres un clasificador experto de intenciones de compra para upsells. Responde solo con: accept, info, reject o unclear",
                messages=[{"role": "user", "content": prompt}]
            )

            intent = response.content[0].text.strip().lower()

            if intent not in ["accept", "info", "reject", "unclear"]:
                logger.warning(
                    f"Unexpected upsell intent: {intent}, defaulting to unclear")
                return "unclear"

            logger.info(f"Upsell intent classified as: {intent}")
            return intent

        except Exception as e:
            logger.error(f"Error classifying upsell intent: {str(e)}")
            return "unclear"
