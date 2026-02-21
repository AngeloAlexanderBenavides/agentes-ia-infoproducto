"""
Conversation State Model
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ConversationState(BaseModel):
    """
    Conversation state tracking for each user
    """
    # User Information
    phone_number: str
    user_name: Optional[str] = None
    user_country: Optional[str] = None
    user_level: Optional[str] = None  # beginner, intermediate, advanced

    # Agent Flow
    # greeter, consultant, router, closer, verifier, completed
    current_agent: Optional[str] = "greeter"

    # Stage-specific data
    greeter_step: Optional[str] = None
    consultant_step: Optional[str] = None
    closer_step: Optional[str] = None
    upsell_step: Optional[str] = None

    # Payment Information
    final_price: Optional[float] = None
    waiting_for_payment_proof: bool = False
    payment_proof_received: bool = False
    payment_proof_image: Optional[Dict[str, Any]] = None
    payment_confirmed: bool = False

    # Product Delivery
    product_delivered: bool = False

    # Metadata
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    last_message_at: Optional[datetime] = None

    # Conversation History (optional - for analytics)
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationStateUpdate(BaseModel):
    """
    Schema for updating conversation state
    """
    user_name: Optional[str] = None
    user_country: Optional[str] = None
    user_level: Optional[str] = None
    current_agent: Optional[str] = None
    greeter_step: Optional[str] = None
    consultant_step: Optional[str] = None
    closer_step: Optional[str] = None
    upsell_step: Optional[str] = None
    final_price: Optional[float] = None
    waiting_for_payment_proof: Optional[bool] = None
    payment_proof_received: Optional[bool] = None
    payment_proof_image: Optional[Dict[str, Any]] = None
    payment_confirmed: Optional[bool] = None
    product_delivered: Optional[bool] = None
