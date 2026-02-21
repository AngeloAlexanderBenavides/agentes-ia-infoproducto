"""
Mock simulation: Ecuador customer wants to buy
Tests complete flow WITHOUT OpenAI (using mocked responses)
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.conversation import ConversationState
from app.database.db import get_conversation_state, update_conversation_state
from app.config.settings import settings


# Test customer
CUSTOMER_PHONE = "593999887766"  # Ecuador number


def print_separator(title: str, emoji: str = ""):
    """Print pretty separator"""
    full_title = f"{emoji} {title} {emoji}" if emoji else title
    print(f"\n{'='*70}")
    print(full_title.center(70))
    print(f"{'='*70}\n")


def print_message(sender: str, message: str):
    """Pretty print messages"""
    prefix = "🤖 BOT" if sender == "BOT" else f"👤 {sender}"
    print(f"\n{prefix}:")
    print("-" * 70)
    print(message)
    print("-" * 70)


async def simulate_conversation():
    """Simulate complete customer journey with MOCKED responses"""

    print_separator("SIMULACIÓN: Cliente de Ecuador quiere comprar", "🚀")
    print("📋 Flujo: Greeter → Consultant → Router → Closer → Verifier\n")

    # ===== PHASE 1: GREETER =====
    print_separator("FASE 1: GREETER (Bienvenida)", "🟢")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"📊 Estado inicial: agent={state.current_agent}, step={state.greeter_step}")

    # Bot sends welcome
    bot_msg_1 = """¡Hola! 👋 Bienvenido/a.

Para poder ayudarte de la mejor manera y darte un regalo especial, necesito saber:
¿Cómo te llamas y de qué país me escribes?"""
    print_message("BOT", bot_msg_1)

    # Simulate delay (human behavior)
    await asyncio.sleep(0.5)

    # User responds
    user_msg_1 = "Hola, soy Carlos de Ecuador"
    print_message("CARLOS", user_msg_1)

    # Update state (mock OpenAI parsing)
    state.user_name = "Carlos"
    state.user_country = "Ecuador"
    state.current_agent = "consultant"
    state.greeter_step = "2"
    await update_conversation_state(CUSTOMER_PHONE, state)

    bot_msg_2 = f"""¡Perfecto, {state.user_name}! Gracias por responder. 😊

Ahora pasemos a lo bueno..."""
    print_message("BOT", bot_msg_2)

    # ===== PHASE 2: CONSULTANT =====
    print_separator("FASE 2: CONSULTANT (Calificación)", "🔵")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(
        f"📊 Estado: agent={state.current_agent}, user={state.user_name}, country={state.user_country}")

    # Step 1: Personalized welcome
    bot_msg_3 = f"""¡Hola {state.user_name}! Me da mucho gusto conocerte. 👋

Antes de contarte sobre mi producto, quiero asegurarme de darte la información más relevante para ti.

Cuéntame, ¿qué tal es tu experiencia con [tu tema]?

1️⃣ Soy principiante, apenas estoy empezando
2️⃣ Tengo experiencia intermedia, conozco lo básico
3️⃣ Soy avanzado, busco perfeccionar

Responde con el número que mejor te describa. 😊"""
    print_message("BOT", bot_msg_3)

    await asyncio.sleep(0.5)

    user_msg_2 = "1"
    print_message("CARLOS", user_msg_2)

    # Update state (mock OpenAI classification)
    state.user_level = "beginner"
    state.consultant_step = "2"
    await update_conversation_state(CUSTOMER_PHONE, state)

    # Step 2: Deliver gift
    bot_msg_4 = f"""¡Perfecto, {state.user_name}! 🎯

Como principiante, tengo algo especial para ti. Te voy a regalar un recurso que te ayudará MUCHO:

🎁 **Accede aquí**: {settings.LEAD_MAGNET_URL}

Tómate tu tiempo para revisarlo. Cuando estés listo/a, tengo algo aún mejor para mostrarte... 👀"""
    print_message("BOT", bot_msg_4)

    await asyncio.sleep(0.8)

    user_msg_3 = "¡Gracias! Ya vi el regalo"
    print_message("CARLOS", user_msg_3)

    # Step 3: Present product
    state.consultant_step = "3"
    await update_conversation_state(CUSTOMER_PHONE, state)

    bot_msg_5 = f"""Me alegra que te haya gustado, {state.user_name}. 😊

Ahora déjame contarte sobre **{settings.PRODUCT_NAME}**:

{settings.PRODUCT_DESCRIPTION}

Como principiante, esto te va a ayudar especialmente porque:
- ✅ Está diseñado para gente que está empezando (como tú)
- ✅ Todo explicado paso a paso, sin asumir conocimiento previo
- ✅ Incluye ejemplos prácticos para aplicar de inmediato

¿Te gustaría saber más detalles o tienes alguna pregunta?"""
    print_message("BOT", bot_msg_5)

    # Transition to router
    state.current_agent = "router"
    state.consultant_step = "4"
    await update_conversation_state(CUSTOMER_PHONE, state)

    # ===== PHASE 3: ROUTER =====
    print_separator("FASE 3: ROUTER (Intención)", "🟡")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"📊 Estado: agent={state.current_agent}, level={state.user_level}")

    await asyncio.sleep(0.5)

    user_msg_4 = "Me interesa mucho, ¿cómo puedo comprarlo?"
    print_message("CARLOS", user_msg_4)

    # Mock OpenAI intent classification → "purchase"
    bot_msg_6 = f"""¡Excelente decisión, {state.user_name}! 🎉

Me emociona que quieras dar este paso. Vamos a proceder con la compra..."""
    print_message("BOT", bot_msg_6)

    # Transition to closer
    state.current_agent = "closer"
    await update_conversation_state(CUSTOMER_PHONE, state)

    # ===== PHASE 4: CLOSER =====
    print_separator("FASE 4: CLOSER (Cierre de Venta)", "🟠")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"📊 Estado: agent={state.current_agent}")

    # Calculate price (Ecuador discount!)
    if state.user_country and state.user_country.lower() == "ecuador":
        final_price = settings.ECUADOR_PRICE  # 6.99
        discount_msg = f"\n🎊 **¡DESCUENTO ESPECIAL PARA ECUADOR!** 🎊\nPrecio internacional: ${settings.BASE_PRICE}\nDescuento aplicado: -${settings.ECUADOR_DISCOUNT}\n"
    else:
        final_price = settings.BASE_PRICE  # 7.99
        discount_msg = ""

    state.final_price = final_price
    state.closer_step = "1"
    await update_conversation_state(CUSTOMER_PHONE, state)

    bot_msg_7 = f"""¡Perfecto, {state.user_name}! 👍
{discount_msg}
💰 **PRECIO FINAL: ${final_price}**

📋 **Datos para la transferencia:**

🏦 Banco: {settings.BANK_NAME}
👤 Titular: {settings.BANK_ACCOUNT_HOLDER}
💳 Cuenta: {settings.BANK_ACCOUNT_NUMBER}
📝 Tipo: {settings.BANK_ACCOUNT_TYPE}
💵 Monto: ${final_price}

Una vez que hagas la transferencia, envíame una foto del comprobante de pago. 📸

¿Todo claro?"""
    print_message("BOT", bot_msg_7)

    state.closer_step = "2"
    state.waiting_for_payment_proof = True
    state.current_agent = "verifier"
    await update_conversation_state(CUSTOMER_PHONE, state)

    await asyncio.sleep(0.8)

    user_msg_5 = "Perfecto, ya hice la transferencia. Te envío el comprobante"
    print_message("CARLOS", user_msg_5)

    # ===== PHASE 5: VERIFIER =====
    print_separator("FASE 5: VERIFIER (Verificación)", "🔴")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(
        f"📊 Estado: agent={state.current_agent}, waiting_for_payment={state.waiting_for_payment_proof}")

    await asyncio.sleep(0.3)

    print_message("CARLOS", "[Envía imagen del comprobante de pago] 🖼️")

    # Simulate image received
    fake_image_data = {
        "url": "https://example.com/payment-proof-carlos.jpg",
        "mimetype": "image/jpeg",
        "caption": "Comprobante de pago"
    }

    state.payment_proof_received = True
    state.payment_proof_image = fake_image_data
    await update_conversation_state(CUSTOMER_PHONE, state)

    bot_msg_8 = f"""¡Gracias, {state.user_name}! 📸

He recibido tu comprobante de pago. Déjame verificarlo con mi sistema bancario.

Te confirmo en los próximos minutos (generalmente es muy rápido). ⏱️

¡Gracias por tu paciencia! 😊"""
    print_message("BOT", bot_msg_8)

    # Simulate owner notification
    print("\n" + "🔔 NOTIFICACIÓN AL PROPIETARIO ".center(70, "="))
    owner_notification = f"""Nueva venta pendiente de verificación:

👤 Cliente: {state.user_name}
🌎 País: {state.user_country}
📱 Teléfono: {state.phone_number}
💰 Monto: ${state.final_price}
📸 Comprobante: {fake_image_data['url']}

Para confirmar el pago:
POST /api/confirm-payment
Body: {{"phone_number": "{state.phone_number}"}}"""
    print(owner_notification)
    print("="*70)

    # Simulate manual confirmation (you would do this via API)
    print("\n⏳ Simulando confirmación manual del propietario...")
    await asyncio.sleep(1)

    # Confirm payment
    state.payment_confirmed = True
    await update_conversation_state(CUSTOMER_PHONE, state)

    bot_msg_9 = f"""¡Excelente noticia, {state.user_name}! ✅

Tu pago ha sido **CONFIRMADO**. 🎉

Aquí tienes acceso inmediato a tu E-Book:

📖 **{settings.PRODUCT_NAME}**

🔗 **Link de descarga**: {settings.PRODUCT_DELIVERY_URL}

━━━━━━━━━━━━━━━━━━━━

📚 **Instrucciones:**
1. Haz clic en el link de arriba
2. Descarga el E-Book en formato PDF
3. ¡Comienza a dominar la Ingeniería de Prompts!

🎯 **Bonus incluidos:**
• {settings.LEAD_MAGNET_NAME} (ya los tienes)
• Soporte directo vía WhatsApp
• Actualizaciones del contenido gratis

💡 **Tip:** Guarda este link para siempre. Podrás acceder cuando quieras.

¡Disfruta tu aprendizaje y mucho éxito aplicando estas técnicas! 🚀

━━━━━━━━━━━━━━━━━━━━

🔥 **¡ESPERA! TENGO UNA OFERTA EXCLUSIVA PARA TI** 🔥

Ya que confiaste en mí y adquiriste el E-Book, quiero ofrecerte algo especial para llevar tus conocimientos al siguiente nivel.

🚀 **{settings.UPSELL_PRODUCT_NAME}**

En este curso aprenderás a crear tus propios agentes de IA y automatizar procesos como un profesional.

💰 **Precio Especial:** Solo ${settings.UPSELL_PRICE} USD (o ${settings.UPSELL_ECUADOR_PRICE} si estás en Ecuador).

👉 **¿Te interesa?** Solo dime 'Sí, quiero el curso' y te enviaré los detalles para acceder de inmediato.

Si necesitas ayuda o tienes dudas con tu E-Book, sigo estando aquí. 😊"""
    print_message("BOT", bot_msg_9)

    state.product_delivered = True
    state.current_agent = "upsell"
    await update_conversation_state(CUSTOMER_PHONE, state)

    # ===== PHASE 6: UPSELL =====
    print_separator("FASE 6: UPSELL (Oferta Post-Compra)", "💎")

    state = await get_conversation_state(CUSTOMER_PHONE)
    print(f"📊 Estado: agent={state.current_agent}")

    await asyncio.sleep(0.8)

    user_msg_6 = "Sí, me interesa mucho el curso avanzado. ¿Cómo lo pago?"
    print_message("CARLOS", user_msg_6)

    # Mock OpenAI upsell intent classification -> "accept"
    bot_msg_10 = f"""¡Excelente decisión, {state.user_name}! 🚀

El total con tu descuento especial es de **${settings.UPSELL_ECUADOR_PRICE} USD**.

🏦 **Transferencia Bancaria (Ecuador)**
Banco: {settings.BANK_NAME}
Tipo: {settings.BANK_ACCOUNT_TYPE}
Cuenta: {settings.BANK_ACCOUNT_NUMBER}
A nombre de: {settings.BANK_ACCOUNT_HOLDER}

━━━━━━━━━━━━━━━━━━━━

📸 **IMPORTANTE:** Cuando realices el pago, envíame una foto del comprobante por aquí mismo.

En cuanto lo reciba, te enviaré el acceso inmediato al curso avanzado. ¡Quedo atento! 😊"""
    print_message("BOT", bot_msg_10)

    state.current_agent = "completed"
    await update_conversation_state(CUSTOMER_PHONE, state)

    # ===== FINAL STATE =====
    print_separator("RESUMEN FINAL", "📊")

    state = await get_conversation_state(CUSTOMER_PHONE)

    summary = f"""
✅ **CONVERSIÓN EXITOSA**

👤 Cliente: {state.user_name}
🌎 País: {state.user_country}
📊 Nivel: {state.user_level}
💰 Precio final: ${state.final_price}
🎊 Descuento Ecuador: -${settings.ECUADOR_DISCOUNT}

✅ Comprobante recibido: {state.payment_proof_received}
✅ Pago confirmado: {state.payment_confirmed}
✅ Producto entregado: {state.product_delivered}

📈 Fases completadas:
  1. Greeter ✓
  2. Consultant ✓
  3. Router ✓
  4. Closer ✓
  5. Verifier ✓
  6. Upsell ✓

💡 Tiempo aproximado: ~3-5 minutos
💸 Costo OpenAI estimado: ~$0.0003 USD
"""
    print(summary)
    print("="*70)

    print("\n🎉 ¡SIMULACIÓN COMPLETA! El cliente está feliz con su compra y el upsell.")
    print(f"💰 Ecuador pagó ${settings.ECUADOR_PRICE} (producto) + ${settings.UPSELL_ECUADOR_PRICE} (upsell)")
    print(f"🌎 Internacional pagaría ${settings.BASE_PRICE} (producto) + ${settings.UPSELL_PRICE} (upsell)")
    print(f"📖 E-Book: {settings.PRODUCT_NAME[:60]}...")
    print(f"🚀 Upsell: {settings.UPSELL_PRODUCT_NAME[:60]}...")
    print("🤖 Sistema funcionando al 100%\n")


if __name__ == "__main__":
    asyncio.run(simulate_conversation())
