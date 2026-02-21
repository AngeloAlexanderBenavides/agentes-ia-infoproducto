"""
Database operations for conversation state management
Uses SQLite for simplicity (can be upgraded to PostgreSQL later)
"""
import logging
from datetime import datetime

from app.config.settings import settings
from app.models.conversation import ConversationState
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model


class ConversationStateDB(Base):
    """
    Database model for conversation state
    """
    __tablename__ = "conversation_states"

    phone_number = Column(String, primary_key=True, index=True)
    user_name = Column(String, nullable=True)
    user_country = Column(String, nullable=True)
    user_level = Column(String, nullable=True)
    current_agent = Column(String, default="greeter")
    greeter_step = Column(String, nullable=True)
    consultant_step = Column(String, nullable=True)
    closer_step = Column(String, nullable=True)
    upsell_step = Column(String, nullable=True)
    final_price = Column(Float, nullable=True)
    waiting_for_payment_proof = Column(Boolean, default=False)
    payment_proof_received = Column(Boolean, default=False)
    payment_proof_image = Column(JSON, nullable=True)
    payment_confirmed = Column(Boolean, default=False)
    product_delivered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_message_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)


# Create tables
Base.metadata.create_all(bind=engine)

# Database operations


async def get_conversation_state(phone_number: str) -> ConversationState:
    """
    Get or create conversation state for a phone number
    """
    db = SessionLocal()
    try:
        db_state = db.query(ConversationStateDB).filter(
            ConversationStateDB.phone_number == phone_number
        ).first()

        if not db_state:
            # Create new conversation state
            db_state = ConversationStateDB(
                phone_number=phone_number,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_state)
            db.commit()
            db.refresh(db_state)
            logger.info(f"Created new conversation state for {phone_number}")

        # Convert to Pydantic model
        return ConversationState(
            phone_number=db_state.phone_number,
            user_name=db_state.user_name,
            user_country=db_state.user_country,
            user_level=db_state.user_level,
            current_agent=db_state.current_agent,
            greeter_step=db_state.greeter_step,
            consultant_step=db_state.consultant_step,
            closer_step=db_state.closer_step,
            upsell_step=db_state.upsell_step,
            final_price=db_state.final_price,
            waiting_for_payment_proof=db_state.waiting_for_payment_proof,
            payment_proof_received=db_state.payment_proof_received,
            payment_proof_image=db_state.payment_proof_image,
            payment_confirmed=db_state.payment_confirmed,
            product_delivered=db_state.product_delivered,
            created_at=db_state.created_at,
            updated_at=db_state.updated_at,
            last_message_at=db_state.last_message_at,
            message_count=db_state.message_count
        )
    finally:
        db.close()


async def update_conversation_state(phone_number: str, state: ConversationState):
    """
    Update conversation state in database
    """
    db = SessionLocal()
    try:
        db_state = db.query(ConversationStateDB).filter(
            ConversationStateDB.phone_number == phone_number
        ).first()

        if not db_state:
            db_state = ConversationStateDB(phone_number=phone_number)
            db.add(db_state)

        # Update fields
        db_state.user_name = state.user_name
        db_state.user_country = state.user_country
        db_state.user_level = state.user_level
        db_state.current_agent = state.current_agent
        db_state.greeter_step = state.greeter_step
        db_state.consultant_step = state.consultant_step
        db_state.closer_step = state.closer_step
        db_state.upsell_step = state.upsell_step
        db_state.final_price = state.final_price
        db_state.waiting_for_payment_proof = state.waiting_for_payment_proof
        db_state.payment_proof_received = state.payment_proof_received
        db_state.payment_proof_image = state.payment_proof_image
        db_state.payment_confirmed = state.payment_confirmed
        db_state.product_delivered = state.product_delivered
        db_state.updated_at = datetime.now()
        db_state.last_message_at = datetime.now()
        db_state.message_count += 1

        db.commit()
        logger.info(f"Updated conversation state for {phone_number}")
    finally:
        db.close()


async def get_all_conversations() -> list:
    """
    Get all active conversations
    """
    db = SessionLocal()
    try:
        conversations = db.query(ConversationStateDB).all()
        return [
            {
                "phone_number": conv.phone_number,
                "user_name": conv.user_name,
                "user_country": conv.user_country,
                "current_agent": conv.current_agent,
                "payment_confirmed": conv.payment_confirmed,
                "product_delivered": conv.product_delivered,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    finally:
        db.close()


async def delete_conversation_state(phone_number: str):
    """
    Delete conversation state (for testing or cleanup)
    """
    db = SessionLocal()
    try:
        db.query(ConversationStateDB).filter(
            ConversationStateDB.phone_number == phone_number
        ).delete()
        db.commit()
        logger.info(f"Deleted conversation state for {phone_number}")
    finally:
        db.close()
