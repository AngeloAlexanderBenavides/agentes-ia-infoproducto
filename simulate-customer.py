"""
Simulation script: Ecuador customer wants to buy
Tests complete flow: Greeter → Consultant → Router → Closer → Verifier
"""
from app.database.db import get_conversation_state
from app.config.settings import settings
from app.agents.verifier import VerifierAgent
from app.agents.router import RouterAgent
from app.agents.greeter import GreeterAgent
from app.agents.consultant import ConsultantAgent
from app.agents.closer import CloserAgent
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


# Test customer
CUSTOMER_PHONE = "593999887766"  # Ecuador number
CUSTOMER_NAME = "Carlos"
CUSTOMER_COUNTRY = "Ecuador"


def print_message(sender: str, message: str):
    """Pretty print messages"""
    print(f"\n{'='*60}")
    print(f"📱 {sender}")
    print(f"{'='*60}")
    print(message)
    print(f"{'='*60}\n")


async def simulate_conversation():
    """Simulate complete customer journey"""

    print("\n🚀 Starting simulation: Ecuador customer wants to buy\n")

    # Get initial state (database auto-initializes)
    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"Initial state: {state.current_agent}")

    # ===== PHASE 1: GREETER =====
    print("\n" + "🟢 PHASE 1: GREETER AGENT ".center(60, "="))

    greeter = GreeterAgent()

    # Step 1: Initial contact (triggers welcome)
    response1 = await greeter.process(CUSTOMER_PHONE, "Hola", state)
    print_message("BOT", response1)

    # Get updated state
    state = await get_conversation_state(CUSTOMER_PHONE)

    # Step 2: User provides name and country
    response2 = await greeter.process(
        CUSTOMER_PHONE,
        f"Hola, soy {CUSTOMER_NAME} de {CUSTOMER_COUNTRY}",
        state
    )
    print_message("BOT", response2)

    # ===== PHASE 2: CONSULTANT =====
    print("\n" + "🔵 PHASE 2: CONSULTANT AGENT ".center(60, "="))

    # Get updated state (should be in consultant now)
    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"Current agent: {state.current_agent}")
    print(f"User info: {state.user_name} from {state.user_country}")

    consultant = ConsultantAgent()

    # User responds about experience level
    response3 = await consultant.process(
        CUSTOMER_PHONE,
        "Soy principiante, apenas estoy empezando en este tema",
        state
    )
    print_message("BOT", response3)

    # Wait for user to check gift
    await asyncio.sleep(1)
    state = await get_conversation_state(CUSTOMER_PHONE)

    response4 = await consultant.process(
        CUSTOMER_PHONE,
        "¡Gracias! Ya vi el regalo",
        state
    )
    print_message("BOT", response4)

    # ===== PHASE 3: ROUTER =====
    print("\n" + "🟡 PHASE 3: ROUTER AGENT ".center(60, "="))

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"Current agent: {state.current_agent}")
    print(f"User level: {state.user_level}")

    router = RouterAgent()

    # User shows interest in buying
    response5 = await router.process(
        CUSTOMER_PHONE,
        "Me interesa mucho, ¿cómo puedo comprarlo?",
        state
    )
    print_message("BOT", response5)

    # ===== PHASE 4: CLOSER =====
    print("\n" + "🟠 PHASE 4: CLOSER AGENT ".center(60, "="))

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"Current agent: {state.current_agent}")

    closer = CloserAgent()

    # User asks about payment
    response6 = await closer.process(
        CUSTOMER_PHONE,
        "Perfecto, voy a hacer la transferencia",
        state
    )
    print_message("BOT", response6)

    # ===== PHASE 5: VERIFIER (Simulated) =====
    print("\n" + "🔴 PHASE 5: VERIFIER AGENT ".center(60, "="))

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"Current agent: {state.current_agent}")
    print(f"Final price: ${state.final_price}")
    print(f"Waiting for payment proof: {state.waiting_for_payment_proof}")

    verifier = VerifierAgent()

    # Simulate image upload
    fake_image_data = {
        "url": "https://example.com/payment-proof.jpg",
        "mimetype": "image/jpeg",
        "caption": "Comprobante de pago"
    }

    response7 = await verifier.handlePaymentProof(
        CUSTOMER_PHONE,
        fake_image_data,
        state
    )
    print_message("BOT", response7)

    # Check final state
    state = await get_conversation_state(CUSTOMER_PHONE)
    print("\n" + "📊 FINAL STATE ".center(60, "="))
    print(f"Customer: {state.user_name} ({state.user_country})")
    print(f"Level: {state.user_level}")
    print(f"Final price: ${state.final_price}")
    print(f"Payment proof received: {state.payment_proof_received}")
    print(f"Payment confirmed: {state.payment_confirmed}")
    print(f"Product delivered: {state.product_delivered}")
    print("="*60)

    print(f"\n✅ Simulation complete!")
    print(f"💰 Ecuador discount applied: $10 - $1 = $9")
    print(f"⏳ Next step: Manual payment confirmation via API endpoint")
    print(f"   POST /api/confirm-payment")
    print(f"   Body: {{\"phone_number\": \"{CUSTOMER_PHONE}\"}}")


if __name__ == "__main__":
    asyncio.run(simulate_conversation())
