import logging
from typing import cast

from app.agents.closer import CloserAgent
from app.agents.consultant import ConsultantAgent
from app.agents.greeter import GreeterAgent
from app.agents.router import RouterAgent
from app.agents.verifier import VerifierAgent
from app.database.db import get_conversation_state, update_conversation_state
from app.models.conversation import ConversationState
from app.services.evolutionApi import EvolutionApiService
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()
logger = logging.getLogger(__name__)

evolution_service = EvolutionApiService()


@router.post("/evolution")
async def evolution_webhook(request: Request):
    """
    Webhook endpoint to receive messages from Evolution API
    """
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")

        # Extract message data
        event_type = data.get("event")

        if event_type == "messages.upsert":
            message_data = data.get("data", {})
            message_info = message_data.get("message", {})
            key = message_data.get("key", {})

            # Get sender info
            sender = key.get("remoteJid", "")
            message_id = key.get("id", "")

            # Skip messages from the bot itself
            if key.get("fromMe", False):
                return {"status": "ignored", "reason": "own message"}

            # Get message content
            message_type = None
            message_content = None

            if "conversation" in message_info:
                message_type = "text"
                message_content = message_info["conversation"]
            elif "extendedTextMessage" in message_info:
                message_type = "text"
                message_content = message_info["extendedTextMessage"].get("text", "")
            elif "imageMessage" in message_info:
                message_type = "image"
                message_content = message_info["imageMessage"]

            if not message_content:
                return {"status": "ignored", "reason": "no content"}

            if not message_type:
                return {"status": "ignored", "reason": "unknown message type"}

            # Get or create conversation state
            conversation_state = await get_conversation_state(sender)

            # Route to appropriate agent based on state and message type
            response = await process_message(
                sender=sender,
                message_type=message_type,
                message_content=message_content,
                conversation_state=conversation_state
            )

            # Send response with human-like behavior
            if response:
                await evolution_service.sendTextWithHumanBehavior(
                    sender,
                    response,
                    use_typing=True,
                    use_presence=True
                )

            return {"status": "success"}

        return {"status": "ignored", "reason": "unsupported event"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_message(
    sender: str,
    message_type: str,
    message_content: str | dict,
    conversation_state: ConversationState
):
    """
    Process message and route to the appropriate agent
    """
    current_agent = conversation_state.current_agent

    # Handle image messages (payment verification)
    if message_type == "image":
        if conversation_state.waiting_for_payment_proof:
            verifier = VerifierAgent()
            # Type narrowing: message_content is dict for images
            image_data = cast(dict, message_content)
            return await verifier.handlePaymentProof(sender, image_data, conversation_state)
        else:
            return "Por favor, envía solo texto por ahora. Si necesitas enviar comprobantes, espera a que te lo solicite. 😊"

    # Type narrowing: message_content is str for text messages
    text_message = cast(str, message_content)

    if current_agent == "greeter" or current_agent is None:
        greeter = GreeterAgent()
        return await greeter.process(sender, text_message, conversation_state)

    elif current_agent == "consultant":
        consultant = ConsultantAgent()
        return await consultant.process(sender, text_message, conversation_state)

    elif current_agent == "router":
        router_agent = RouterAgent()
        return await router_agent.process(sender, text_message, conversation_state)

    elif current_agent == "closer":
        closer = CloserAgent()
        return await closer.process(sender, text_message, conversation_state)

    elif current_agent == "upsell":
        from app.agents.upsell import UpsellAgent
        upsell = UpsellAgent()
        return await upsell.process(sender, text_message, conversation_state)

    else:
        # Default to greeter if state is unclear
        greeter = GreeterAgent()
        return await greeter.process(sender, text_message, conversation_state)
