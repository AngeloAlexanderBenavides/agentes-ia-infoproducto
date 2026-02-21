from app.database.db import get_all_conversations, get_conversation_state
from app.services.evolutionApi import EvolutionApiService
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
evolution_service = EvolutionApiService()


class ConfirmPaymentRequest(BaseModel):
    phone_number: str
    user_name: str


class SendMessageRequest(BaseModel):
    phone_number: str
    message: str


@router.get("/conversations")
async def list_conversations():
    """
    List all active conversations
    """
    conversations = await get_all_conversations()
    return {"conversations": conversations}


@router.get("/conversation/{phone_number}")
async def get_conversation(phone_number: str):
    """
    Get specific conversation state
    """
    conversation = await get_conversation_state(phone_number)
    return {"conversation": conversation.dict()}


@router.post("/confirm-payment")
async def confirm_payment(request: ConfirmPaymentRequest):
    """
    Manual endpoint for Angelo to confirm payment
    Usage: /api/confirm-payment with phone_number and user_name
    """
    from app.agents.verifier import VerifierAgent

    verifier = VerifierAgent()
    conversation_state = await get_conversation_state(request.phone_number)

    if not conversation_state.waiting_for_payment_proof:
        raise HTTPException(
            status_code=400, detail="User is not waiting for payment confirmation")

    success = await verifier.confirmPaymentAndDeliverProduct(
        request.phone_number,
        request.user_name,
        conversation_state
    )

    if success:
        return {"status": "success", "message": "Payment confirmed and product delivered"}
    else:
        raise HTTPException(status_code=500, detail="Failed to deliver product")


@router.post("/send-message")
async def send_manual_message(request: SendMessageRequest):
    """
    Send a manual message to a user (for testing or manual intervention)
    """
    try:
        await evolution_service.sendTextMessage(request.phone_number, request.message)
        return {"status": "success", "message": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
