# WhatsApp Agent System for Infoproduct Sales

A multi-agent WhatsApp automation system built with FastAPI and Evolution API. This system uses an intelligent agent flow to convert leads into customers through personalized conversations.

## 🎯 Features

### Multi-Agent Flow

1. **Greeter Agent**: Welcomes users and collects name/country
2. **Consultant Agent**: Diagnoses user level and delivers personalized lead magnet
3. **Router Agent**: Classifies purchase intent and handles objections
4. **Closer Agent**: Processes payment (with Ecuador discount)
5. **Verifier Agent**: Handles payment verification and product delivery

### Key Capabilities

- ✅ **AI-Powered Intelligence** (OpenAI GPT-4o-mini for natural conversations)
- ✅ **Anti-Bot Detection** (typing indicators, realistic delays, presence management)
- ✅ Personalized lead magnet delivery based on user level
- ✅ Intelligent intent classification and objection handling
- ✅ Natural language understanding (no rigid keywords)
- ✅ Local payment support for Ecuador (Banco Pichincha)
- ✅ Automatic payment verification workflow
- ✅ Owner notifications for payment confirmations
- ✅ Conversation state management
- ✅ Multi-country pricing support

### 🧠 AI Features

- **Smart Name/Country Parsing**: Understands "Me llamo Carlos de Ecuador"
- **Experience Level Detection**: Classifies beginner/intermediate/advanced from natural responses
- **Intent Classification**: Detects purchase intent, info requests, and objections automatically
- **Dynamic Objection Handling**: AI generates empathetic, personalized responses
- **Cost**: ~$0.0002 per customer (practically free!)

📖 **[See AI Integration Details](docs/ai-integration.md)**

### 🛡️ Anti-Bot Detection

- **Typing Indicators**: Shows "escribiendo..." before responding
- **Realistic Delays**: 0.5-10s based on message length (mimics human typing speed)
- **Presence Management**: Goes online → types → sends → goes offline naturally
- **Random Variability**: All timings randomized to avoid patterns
- **Result**: WhatsApp sees natural human behavior ✅

📖 **[See Anti-Bot Features](docs/ANTI-BOT-DETECTION.md)**

## 🚀 Quick Start

### ☁️ Deploy to Oracle Cloud (Recommended - FREE Forever!)

**100% FREE with Oracle Cloud Free Tier - No time limit!**

Deploy the entire system to Oracle Cloud in 30 minutes:

```powershell
# Follow the interactive guide
.\deploy-oracle.ps1
```

**Cost**: **$0/month FOREVER** with Free Tier 🎉

- 2-4 ARM cores + 12-24 GB RAM
- 200 GB storage
- 10 TB transfer/month
- No credit card charges, ever!

📖 **[Oracle Cloud Deployment Guide](ORACLE-DEPLOYMENT.md)** - Step-by-step with screenshots

---

### ☁️ Alternative: Deploy to Azure

**Have $100 Azure credits?**

```powershell
.\setup-acr.ps1
```

**Cost**: ~$25/month = 4 months with credits

📖 **[Azure Deployment Guide](AZURE-QUICKSTART.md)**

---

### 💻 Local Development

### Prerequisites

- Python 3.9+
- Evolution API instance (running)
- WhatsApp number connected to Evolution API

### Installation

1. **Clone and navigate to the project:**

```powershell
cd "f:\Angelo Archivos\AgentesIAparaInfoproducto\backend"
```

2. **Create virtual environment:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies:**

```powershell
pip install -r requirements.txt
```

4. **Configure environment variables:**

```powershell
Copy-Item .env.example .env
# Edit .env with your actual credentials
notepad .env
```

Required environment variables:

- `EVOLUTION_API_URL`: Your Evolution API URL
- `EVOLUTION_API_KEY`: Your Evolution API key
- `EVOLUTION_INSTANCE_NAME`: Your instance name
- `OPENAI_API_KEY`: Your OpenAI API key (for AI features)
- `OWNER_WHATSAPP`: Your WhatsApp number for notifications
- `BANK_ACCOUNT_NUMBER`: Your bank account for payments
- `PRODUCT_NAME`: Your product name
- `LEAD_MAGNET_URL`: URL to your free gift

5. **Run the application:**

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Configure Evolution API webhook:**
   - Go to your Evolution API dashboard
   - Set webhook URL to: `http://your-server:8000/webhooks/evolution`
   - Enable webhook events: `messages.upsert`

## 📁 Project Structure

```
backend/
├── app/
│   ├── agents/              # Agent logic (Greeter, Consultant, Router, Closer, Verifier)
│   │   ├── greeter.py
│   │   ├── consultant.py
│   │   ├── router.py
│   │   ├── closer.py
│   │   └── verifier.py
│   ├── api/                 # API routes and webhooks
│   │   ├── webhooks.py      # Evolution API webhook handler
│   │   └── routes.py        # Admin API routes
│   ├── config/              # Configuration
│   │   └── settings.py
│   ├── database/            # Database operations
│   │   └── db.py
│   ├── models/              # Data models
│   │   ├── user.py
│   │   └── conversation.py
│   ├── services/            # External services
│   │   ├── evolutionApi.py
│   │   ├── notificationService.py
│   │   └── paymentVerifier.py
│   ├── utils/               # Utilities
│   │   └── helpers.py
│   └── main.py              # FastAPI app
├── requirements.txt
└── .env.example
```

## 🔄 Agent Flow

```
User sends message
    ↓
Greeter Agent
- Asks name and country
- Collects basic info
    ↓
Consultant Agent
- Asks about experience level
- Delivers personalized lead magnet
- Presents product
    ↓
Router Agent
- Detects purchase intent
- Handles objections
- Provides more info if needed
    ↓
Closer Agent
- Calculates price (Ecuador discount)
- Provides payment instructions
- Requests payment proof
    ↓
Verifier Agent
- Receives payment proof
- Notifies owner (Angelo)
- Waits for confirmation
- Delivers product
```

## 🌐 API Endpoints

### Webhooks

- `POST /webhooks/evolution` - Receive messages from Evolution API

### Admin API

- `GET /api/conversations` - List all conversations
- `GET /api/conversation/{phone}` - Get specific conversation
- `POST /api/confirm-payment` - Manually confirm payment
- `POST /api/send-message` - Send manual message

### Health Check

- `GET /` - API status
- `GET /health` - Health check

## 💰 Payment Verification Flow

### For Ecuador Users

1. User expresses interest in buying
2. Closer Agent provides Banco Pichincha details
3. User makes transfer and sends screenshot
4. Verifier Agent receives screenshot
5. System notifies Angelo via WhatsApp
6. Angelo checks bank account
7. Angelo confirms via API or command:
   ```powershell
   curl -X POST http://localhost:8000/api/confirm-payment `
     -H "Content-Type: application/json" `
     -d '{"phone_number":"593999999999@s.whatsapp.net","user_name":"Carlos"}'
   ```
8. System delivers product to customer

## 🧪 Testing

### Test the webhook locally:

```powershell
curl -X POST http://localhost:8000/webhooks/evolution `
  -H "Content-Type: application/json" `
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "593999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "test123"
      },
      "message": {
        "conversation": "Hola"
      }
    }
  }'
```

### List active conversations:

```powershell
curl http://localhost:8000/api/conversations
```

## 🔧 Configuration

### Add More Country Discounts

Edit `app/services/paymentVerifier.py`:

```python
async def calculateFinalPrice(self, country: str, base_price: float = None) -> float:
    if country == "Ecuador":
        return base_price - settings.ECUADOR_DISCOUNT
    elif country == "Colombia":
        return base_price - 0.5  # Example
    # Add more countries...
```

### Customize Agent Messages

Each agent file (`app/agents/*.py`) contains the conversation logic. Edit the response strings to match your brand voice.

## 📊 Database

SQLite database stores conversation states:

- User information
- Current agent
- Payment status
- Product delivery status

View database:

```powershell
sqlite3 whatsapp_agents.db
.tables
SELECT * FROM conversation_states;
```

## 🚨 Troubleshooting

### Webhook not receiving messages

1. Check Evolution API is running and connected
2. Verify webhook URL is correct in Evolution dashboard
3. Check firewall/network allows incoming connections
4. Test with ngrok if behind NAT: `ngrok http 8000`

### Agent not responding correctly

1. Check logs: Look at console output
2. Verify conversation state: `GET /api/conversation/{phone}`
3. Check Evolution API credentials in `.env`

## 📝 License

MIT

## 👤 Author

Angelo - WhatsApp Agent System

---

**Need help?** Check the [Evolution API documentation](https://github.com/EvolutionAPI/evolution-api)
