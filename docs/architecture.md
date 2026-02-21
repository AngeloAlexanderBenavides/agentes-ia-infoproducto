# System Architecture

## Overview

WhatsApp Agent System is a multi-agent conversational AI system designed to automate infoproduct sales through WhatsApp.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         WhatsApp User                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Messages
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Evolution API                               │
│  (WhatsApp Web Gateway)                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Webhook (messages.upsert)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         Webhook Handler (webhooks.py)                  │   │
│  │  - Receives Evolution API events                       │   │
│  │  - Extracts message data                               │   │
│  │  - Routes to appropriate agent                         │   │
│  └─────────────────────┬──────────────────────────────────┘   │
│                        │                                         │
│                        ▼                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │           Agent Router (process_message)               │   │
│  │  - Loads conversation state from DB                    │   │
│  │  - Determines current agent                            │   │
│  │  - Handles message type (text/image)                   │   │
│  └─────────────────────┬──────────────────────────────────┘   │
│                        │                                         │
│         ┌──────────────┴──────────────┐                        │
│         │                               │                        │
│         ▼                               ▼                        │
│  ┌─────────────┐              ┌─────────────┐                  │
│  │   Greeter   │              │ Consultant  │                  │
│  │    Agent    │─────────────▶│   Agent     │                  │
│  │             │              │             │                  │
│  │ - Welcome   │              │ - Diagnose  │                  │
│  │ - Get name  │              │ - Gift lead │                  │
│  │ - Get       │              │   magnet    │                  │
│  │   country   │              │ - Present   │                  │
│  └─────────────┘              │   product   │                  │
│                                └──────┬──────┘                  │
│                                       │                          │
│                                       ▼                          │
│                              ┌─────────────┐                    │
│                              │   Router    │                    │
│                              │   Agent     │                    │
│                              │             │                    │
│                              │ - Classify  │                    │
│                              │   intent    │                    │
│                              │ - Handle    │                    │
│                              │   objections│                    │
│                              └──────┬──────┘                    │
│                                     │                            │
│                                     ▼                            │
│                            ┌─────────────┐                      │
│                            │   Closer    │                      │
│                            │   Agent     │                      │
│                            │             │                      │
│                            │ - Calculate │                      │
│                            │   price     │                      │
│                            │ - Payment   │                      │
│                            │   details   │                      │
│                            └──────┬──────┘                      │
│                                   │                              │
│                                   ▼                              │
│                          ┌─────────────┐                        │
│                          │  Verifier   │                        │
│                          │   Agent     │                        │
│                          │             │                        │
│                          │ - Receive   │                        │
│                          │   proof     │                        │
│                          │ - Notify    │                        │
│                          │   owner     │                        │
│                          │ - Deliver   │                        │
│                          │   product   │                        │
│                          └──────┬──────┘                        │
│                                 │                                │
└─────────────────────────────────┼────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                            │
                    ▼                            ▼
          ┌──────────────────┐        ┌──────────────────┐
          │   SQLite DB      │        │ Angelo WhatsApp  │
          │                  │        │  (Notifications) │
          │ - Conversation   │        │                  │
          │   states         │        │ - Payment alerts │
          │ - User data      │        │ - Confirmations  │
          │ - Payment info   │        │                  │
          └──────────────────┘        └──────────────────┘
```

## Component Responsibilities

### Evolution API

- **Role**: WhatsApp Web gateway
- **Responsibilities**:
  - Maintains WhatsApp Web session
  - Sends/receives messages
  - Delivers webhooks to FastAPI
  - Handles media files

### FastAPI Application

#### Webhook Handler

- **Location**: `app/api/webhooks.py`
- **Responsibilities**:
  - Receives `messages.upsert` events
  - Validates message structure
  - Extracts sender, content, type
  - Loads conversation state
  - Routes to agent processor

#### Agent System

##### 1. Greeter Agent

- **Location**: `app/agents/greeter.py`
- **State**: `current_agent: "greeter"`
- **Flow**:
  1. Send welcome message
  2. Ask for name and country
  3. Parse response
  4. Transition to Consultant
- **Data Collected**:
  - `user_name`
  - `user_country`

##### 2. Consultant Agent

- **Location**: `app/agents/consultant.py`
- **State**: `current_agent: "consultant"`
- **Flow**:
  1. Ask diagnostic question (experience level)
  2. Classify user as beginner/intermediate/advanced
  3. Deliver personalized lead magnet
  4. Present product information
  5. Transition to Router
- **Data Collected**:
  - `user_level`

##### 3. Router Agent

- **Location**: `app/agents/router.py`
- **State**: `current_agent: "router"`
- **Flow**:
  1. Analyze message for intent
  2. Branch on intent:
     - **Purchase intent** → Transfer to Closer
     - **Info request** → Provide details, stay in Router
     - **Objection** → Handle objection, stay in Router
- **Intent Keywords**:
  - Purchase: "comprar", "quiero", "cuánto"
  - Info: "cómo funciona", "detalles"
  - Objection: "caro", "después"

##### 4. Closer Agent

- **Location**: `app/agents/closer.py`
- **State**: `current_agent: "closer"`
- **Flow**:
  1. Calculate final price
     - Ecuador: Apply discount
     - Other countries: Base price
  2. Present payment method
     - Ecuador: Banco Pichincha transfer
     - International: PayPal/Stripe
  3. Request payment proof
  4. Set state: `waiting_for_payment_proof: true`
- **Data Stored**:
  - `final_price`
  - `waiting_for_payment_proof`

##### 5. Verifier Agent

- **Location**: `app/agents/verifier.py`
- **State**: `current_agent: "verifier"`
- **Flow**:
  1. Receive payment proof (image)
  2. Store image metadata
  3. Send notification to Angelo
  4. Wait for manual confirmation
  5. Upon confirmation:
     - Mark payment as confirmed
     - Deliver product (credentials/links)
     - Send confirmation to customer
- **Data Stored**:
  - `payment_proof_received`
  - `payment_proof_image`
  - `payment_confirmed`
  - `product_delivered`

### Services

#### Evolution API Service

- **Location**: `app/services/evolutionApi.py`
- **Methods**:
  - `sendTextMessage()`: Send text to user
  - `sendImageMessage()`: Send image to user
  - `downloadMedia()`: Download media from message
  - `getInstanceStatus()`: Check API status

#### Notification Service

- **Location**: `app/services/notificationService.py`
- **Methods**:
  - `sendToOwner()`: Send message to Angelo's WhatsApp
  - `notifyNewLead()`: Alert about new lead
  - `notifyPaymentPending()`: Alert about pending payment
  - `notifyPaymentConfirmed()`: Confirm successful transaction

#### Payment Verifier Service

- **Location**: `app/services/paymentVerifier.py`
- **Methods**:
  - `calculateFinalPrice()`: Apply country discounts
  - `getPriceBreakdown()`: Return pricing details
  - `getBankDetails()`: Return payment instructions

### Database Layer

#### Conversation State Model

- **Location**: `app/models/conversation.py`
- **Fields**:
  - User info: `user_name`, `user_country`, `user_level`
  - Agent flow: `current_agent`, step indicators
  - Payment: `final_price`, proof status, confirmation
  - Metadata: timestamps, message count

#### Database Operations

- **Location**: `app/database/db.py`
- **Operations**:
  - `get_conversation_state()`: Load or create state
  - `update_conversation_state()`: Save changes
  - `get_all_conversations()`: List all users
  - `delete_conversation_state()`: Cleanup

## Data Flow

### Message Receiving

```
1. User sends "Hola" to WhatsApp
2. Evolution API receives via WhatsApp Web
3. Evolution API POSTs to /webhooks/evolution
4. Webhook handler extracts data:
   - phone: "593999999999@s.whatsapp.net"
   - message: "Hola"
   - type: "text"
5. Load state from DB (new user = greeter agent)
6. Call GreeterAgent.process()
7. Generate response
8. Send via EvolutionApiService.sendTextMessage()
9. Update state in DB
```

### Payment Verification

```
1. User sends image (payment proof)
2. Webhook detects message_type: "image"
3. Check state: waiting_for_payment_proof == true
4. Call VerifierAgent.handlePaymentProof()
5. Store image metadata in DB
6. NotificationService.sendToOwner() with details
7. Response: "Verificando tu pago..."
8. [Manual] Angelo checks bank
9. [Manual] Angelo calls POST /api/confirm-payment
10. VerifierAgent.confirmPaymentAndDeliverProduct()
11. Update state: payment_confirmed = true
12. Send product access to customer
13. Notify Angelo: "Producto entregado"
```

## State Transitions

```
NULL
  ↓ (first message)
greeter (ask name/country)
  ↓ (name provided)
consultant (ask level, give gift)
  ↓ (level provided)
router (classify intent)
  ↓ (purchase detected)
closer (payment instructions)
  ↓ (waiting for proof)
verifier (proof received, pending confirmation)
  ↓ (manual confirmation)
completed (product delivered)
```

## Security Considerations

1. **API Key Protection**: Evolution API key stored in `.env`
2. **Webhook Validation**: Could add signature verification
3. **Database**: SQLite for simplicity; upgrade to PostgreSQL for production
4. **Payment Proof**: Images stored temporarily; consider S3 for persistence
5. **Manual Verification**: Angelo must manually verify payments before delivery

## Scalability

### Current Setup

- Single FastAPI instance
- SQLite database
- Synchronous webhook processing

### Production Upgrades

1. **Database**: Migrate to PostgreSQL/MySQL
2. **Queue**: Add Celery/RabbitMQ for async processing
3. **Storage**: Move images to S3/Minio
4. **Caching**: Add Redis for session state
5. **Load Balancer**: Multiple FastAPI instances
6. **Monitoring**: Add Prometheus/Grafana

## Error Handling

1. **Evolution API Down**: Retry logic with exponential backoff
2. **Database Errors**: Transaction rollback, log errors
3. **Invalid State**: Reset to greeter if state corrupted
4. **Network Issues**: Timeout handling in httpx client
5. **Manual Override**: Admin API to fix stuck states

## Future Enhancements

1. **AI-Powered NLP**: Use OpenAI/LangChain for intent detection
2. **LangGraph Integration**: Visual agent flow management
3. **Multi-Language Support**: i18n for Spanish/English/Portuguese
4. **Analytics Dashboard**: Track conversion funnel
5. **A/B Testing**: Test different messages for optimization
6. **Automated Payment**: Integrate payment gateway APIs
7. **CRM Integration**: Sync with HubSpot/Salesforce
