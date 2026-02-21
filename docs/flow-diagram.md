# Agent Flow Diagram

## Visual Flow

```mermaid
flowchart TD
    Start([User: "Hola"]) --> Greeter[Greeter Agent]

    Greeter -->|Asks| GetName[Get Name & Country]
    GetName -->|User responds| Consultant[Consultant Agent]

    Consultant -->|Asks| GetLevel[Diagnose Experience Level]
    GetLevel -->|Beginner/Intermediate/Advanced| GiveGift[Deliver Personalized Gift]
    GiveGift --> PresentProduct[Present Product Info]
    PresentProduct --> Router[Router Agent]

    Router -->|Classify Intent| Decision{Intent?}

    Decision -->|Purchase| Closer[Closer Agent]
    Decision -->|More Info| Info[Provide Details]
    Decision -->|Objection| Objection[Handle Objection]

    Info --> Router
    Objection --> Router

    Closer -->|Calculate Price| CheckCountry{Ecuador?}
    CheckCountry -->|Yes| Discount[Apply $1 Discount]
    CheckCountry -->|No| BasePrice[Base Price $10]

    Discount --> PaymentInstructions[Show Bank Details]
    BasePrice --> PaymentInstructions

    PaymentInstructions --> WaitProof[Wait for Payment Proof]
    WaitProof -->|User sends image| Verifier[Verifier Agent]

    Verifier --> SaveProof[Store Payment Proof]
    SaveProof --> NotifyOwner[Notify Angelo via WhatsApp]
    NotifyOwner --> ManualCheck[Angelo Checks Bank]

    ManualCheck -->|Payment Confirmed| ConfirmAPI[Angelo calls /api/confirm-payment]
    ConfirmAPI --> DeliverProduct[Deliver Product to Customer]
    DeliverProduct --> End([Completed])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Greeter fill:#87CEEB
    style Consultant fill:#87CEEB
    style Router fill:#87CEEB
    style Closer fill:#87CEEB
    style Verifier fill:#87CEEB
    style NotifyOwner fill:#FFD700
    style ManualCheck fill:#FFD700
    style DeliverProduct fill:#98FB98
```

## Detailed Agent Interactions

### Phase 1: Greeting & Data Collection

```
┌─────────────────────────────────────────────────────────────┐
│                      GREETER AGENT                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User: "Hola"                                               │
│    ↓                                                         │
│  Bot: "¡Hola! Para darte el regalo perfecto,               │
│        ¿cómo te llamas y de qué país escribes?"            │
│    ↓                                                         │
│  User: "Carlos, Ecuador"                                    │
│    ↓                                                         │
│  [SAVE] user_name = "Carlos"                                │
│         user_country = "Ecuador"                            │
│    ↓                                                         │
│  [TRANSITION] → Consultant Agent                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Diagnostic & Lead Magnet

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSULTANT AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Bot: "¡Buenísimo, Carlos! 🇪🇨                              │
│        Para no darte material que ya conozcas...            │
│        ¿Ya has trabajado con [Tema] antes o empiezas        │
│        de cero?"                                            │
│    ↓                                                         │
│  User: "Estoy de cero"                                      │
│    ↓                                                         │
│  [CLASSIFY] user_level = "beginner"                         │
│    ↓                                                         │
│  Bot: "¡Perfecto! Te va a ENCANTAR esta Guía de            │
│        Inicio Rápido: [LINK]                                │
│                                                              │
│        Ahora, sobre el producto principal:                  │
│        [PRODUCT DESCRIPTION]                                │
│                                                              │
│        ¿Te gustaría saber más o proceder con la compra?"   │
│    ↓                                                         │
│  [SAVE] user_level = "beginner"                             │
│  [TRANSITION] → Router Agent                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Intent Classification

```
┌─────────────────────────────────────────────────────────────┐
│                      ROUTER AGENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User: "Quiero comprarlo"                                   │
│    ↓                                                         │
│  [ANALYZE] Keywords: "quiero", "comprar"                    │
│    ↓                                                         │
│  [CLASSIFY] Intent: PURCHASE                                │
│    ↓                                                         │
│  [TRANSITION] → Closer Agent                                │
│                                                              │
│  ───────────── OR ─────────────                            │
│                                                              │
│  User: "¿Cómo funciona?"                                    │
│    ↓                                                         │
│  [CLASSIFY] Intent: INFO_REQUEST                            │
│    ↓                                                         │
│  Bot: [Detailed product information]                        │
│    ↓                                                         │
│  [STAY] Router Agent (wait for purchase intent)             │
│                                                              │
│  ───────────── OR ─────────────                            │
│                                                              │
│  User: "Está caro"                                          │
│    ↓                                                         │
│  [CLASSIFY] Intent: OBJECTION_PRICE                         │
│    ↓                                                         │
│  Bot: [Handle price objection]                              │
│    ↓                                                         │
│  [STAY] Router Agent (re-engage)                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 4: Payment Processing

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOSER AGENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [CHECK] user_country == "Ecuador"?                         │
│    ↓ YES                                                     │
│  [CALCULATE] final_price = $10 - $1 = $9                    │
│    ↓                                                         │
│  Bot: "¡Excelente decisión, Carlos! 🎉                      │
│        Por ser de Ecuador, tienes descuento:                │
│        Precio final: $9                                     │
│                                                              │
│        🏦 Banco: Pichincha                                  │
│        👤 Titular: Angelo [...]                             │
│        🔢 Cuenta Ahorros: 1234567890                        │
│        💵 Monto: $9                                         │
│                                                              │
│        ⚠️ IMPORTANTE:                                        │
│        Envíame la foto del comprobante por aquí."           │
│    ↓                                                         │
│  [SAVE] final_price = 9.0                                   │
│         waiting_for_payment_proof = True                    │
│    ↓                                                         │
│  [WAIT] For image message                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 5: Verification & Delivery

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFIER AGENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User: [Sends image - payment proof]                        │
│    ↓                                                         │
│  [DETECT] message_type = "image"                            │
│  [CHECK] waiting_for_payment_proof == True                  │
│    ↓ YES                                                     │
│  [SAVE] payment_proof_received = True                       │
│         payment_proof_image = [image_data]                  │
│    ↓                                                         │
│  Bot → Customer:                                            │
│    "¡Gracias, Carlos! 📸                                    │
│     He recibido tu comprobante.                             │
│     Verificando con mi sistema bancario...                  │
│     Te confirmo en minutos. ⏱️"                             │
│    ↓                                                         │
│  Bot → Angelo (Notification):                               │
│    "🔔 NUEVO PAGO PENDIENTE                                 │
│     👤 Cliente: Carlos                                      │
│     🌍 País: Ecuador                                        │
│     💰 Monto: $9                                            │
│     📸 Comprobante recibido                                 │
│                                                              │
│     Para confirmar:                                         │
│     POST /api/confirm-payment                               │
│     {"phone_number": "593...", "user_name": "Carlos"}"     │
│    ↓                                                         │
│  [WAIT] Manual confirmation from Angelo                     │
│    ↓                                                         │
│  Angelo: Checks Pichincha app                               │
│  Angelo: Payment found ✓                                    │
│  Angelo: Calls API /api/confirm-payment                     │
│    ↓                                                         │
│  [UPDATE] payment_confirmed = True                          │
│           product_delivered = True                          │
│           current_agent = "completed"                       │
│    ↓                                                         │
│  Bot → Customer:                                            │
│    "🎉 ¡CONFIRMADO, Carlos!                                 │
│     ✅ Tu pago ha sido verificado.                          │
│                                                              │
│     🎁 Acceso a [PRODUCT]:                                  │
│     🔗 Link: [PRODUCT_URL]                                  │
│     🔑 Usuario: carlos@example.com                          │
│     🔐 Contraseña: [PASSWORD]                               │
│                                                              │
│     ¡Disfruta tu compra! 🚀"                                │
│    ↓                                                         │
│  Bot → Angelo:                                              │
│    "✅ Producto entregado a Carlos"                         │
│    ↓                                                         │
│  [END] Flow completed                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## State Machine

```
State: NULL
├─ Event: first_message
└─ Action: Initialize conversation
   └─ Next: GREETER

State: GREETER
├─ Event: message_received
├─ Check: has_user_name?
│  ├─ NO: Ask for name & country
│  └─ YES: Transition to CONSULTANT
└─ Next: CONSULTANT

State: CONSULTANT
├─ Event: message_received
├─ Check: has_user_level?
│  ├─ NO: Ask diagnostic question
│  └─ YES: Deliver gift + present product
└─ Next: ROUTER

State: ROUTER
├─ Event: message_received
├─ Analyze: intent_classification
│  ├─ PURCHASE: Transition to CLOSER
│  ├─ INFO: Provide details, stay
│  └─ OBJECTION: Handle, stay
└─ Next: CLOSER (if purchase) OR stay

State: CLOSER
├─ Event: message_received
├─ Action: Calculate price, show payment
├─ Set: waiting_for_payment_proof = True
└─ Next: VERIFIER (when image received)

State: VERIFIER
├─ Event: image_received
├─ Action: Save proof, notify owner
├─ Wait: manual_confirmation
├─ Event: confirmation_api_call
├─ Action: Deliver product
└─ Next: COMPLETED

State: COMPLETED
└─ End of flow
```

## Example Full Conversation

```
[14:01] Carlos: Hola
[14:01] Bot: ¡Hola! Bienvenido/a.
              Para poder ayudarte de la mejor manera y darte un regalo especial,
              necesito saber:
              ¿Cómo te llamas y de qué país me escribes?

[14:02] Carlos: Carlos, de Ecuador
[14:02] Bot: ¡Buenísimo, Carlos! 🇪🇨
              Mira, para no darte material que ya conozcas y darte el regalo
              perfecto para ti...
              ¿Ya has trabajado con [Tema] antes o estás empezando desde cero?

              Responde con:
              1️⃣ Soy novato/a, empiezo de cero
              2️⃣ Ya tengo algo de experiencia
              3️⃣ Soy avanzado/a

[14:03] Carlos: 1
[14:03] Bot: ¡Perfecto, Carlos! Veo que eres novato/a.

              📚 Te va a ENCANTAR este recurso que tengo para ti:
              Es una Guía de Inicio Rápido perfecta para alguien que empieza.

              🎁 Aquí está tu regalo: bit.ly/gift123

              ━━━━━━━━━━━━━━━━━━━━

              Ahora, sobre el producto principal:

              📦 **[PRODUCT NAME]**
              [PRODUCT DESCRIPTION]

              ¿Te gustaría saber más sobre cómo funciona o ya quieres proceder
              con la compra?

[14:05] Carlos: Quiero comprarlo
[14:05] Bot: ¡Excelente decisión, Carlos! 🎉

              🎉 ¡Buenas noticias! Por ser de Ecuador, tienes un descuento
              especial de $1.

              💰 **Tu precio final: $9**

              ━━━━━━━━━━━━━━━━━━━━

              **Opción de pago (Ecuador):**

              🏦 **Banco:** Banco Pichincha
              👤 **Titular:** Angelo Rodriguez
              🔢 **Cuenta Ahorros:** 1234567890
              💵 **Monto:** $9

              ━━━━━━━━━━━━━━━━━━━━

              ⚠️ **IMPORTANTE:**
              Una vez que hagas la transferencia, envíame una foto del
              comprobante por aquí mismo para verificar tu pago y activar
              tu acceso inmediatamente. 📸

              ¿Alguna duda antes de proceder?

[14:08] Carlos: Listo, ya hice la transferencia
[14:08] Bot: ¡Perfecto, Carlos! 👍

              Haz la transferencia cuando estés listo/a y envíame la foto
              del comprobante.

              Estaré atento para verificar y darte acceso inmediato. ⚡

[14:09] Carlos: [Sends image]
[14:09] Bot: ¡Gracias, Carlos! 📸

              He recibido tu comprobante de pago. Déjame verificarlo con
              mi sistema bancario.

              Te confirmo en los próximos minutos (generalmente es muy rápido). ⏱️

              ¡Gracias por tu paciencia! 😊

[14:09] Bot → Angelo: 🔔 **¡NUEVO PAGO PENDIENTE!**

                       👤 **Cliente:** Carlos
                       🌍 **País:** Ecuador
                       📱 **Teléfono:** 593999999999@s.whatsapp.net
                       💰 **Monto:** $9
                       🏦 **Banco:** Banco Pichincha

                       ━━━━━━━━━━━━━━━━━━━━

                       📸 El cliente envió comprobante de pago.

                       **Acción requerida:**
                       1. Revisa tu app del banco
                       2. Si el pago llegó, confirma con:
                          `/confirmar 593999999999`

[14:11] Angelo checks bank → Payment confirmed ✓
[14:11] Angelo calls API: POST /api/confirm-payment

[14:11] Bot → Carlos: 🎉 **¡CONFIRMADO, Carlos!**

                      ✅ Tu pago ha sido verificado exitosamente.

                      ━━━━━━━━━━━━━━━━━━━━

                      🎁 **Acceso a [PRODUCT NAME]:**

                      🔗 **Link de acceso:** [PRODUCT_URL]
                      🔑 **Usuario:** carlos@example.com
                      🔐 **Contraseña:** Pass123!

                      ━━━━━━━━━━━━━━━━━━━━

                      📚 **Instrucciones:**
                      1. Accede al link de arriba
                      2. Comienza de inmediato
                      3. Si tienes dudas, escríbeme aquí mismo

                      🎯 **Bonus adicionales:**
                      • Soporte directo conmigo
                      • Actualizaciones gratis de por vida
                      • Acceso a la comunidad privada

                      ━━━━━━━━━━━━━━━━━━━━

                      ¡Disfruta tu compra y mucho éxito! 🚀

                      Si necesitas ayuda, estoy aquí. 😊

[14:11] Bot → Angelo: ✅ Producto entregado exitosamente a Carlos
                       (593999999999@s.whatsapp.net)

[END OF FLOW]
```
