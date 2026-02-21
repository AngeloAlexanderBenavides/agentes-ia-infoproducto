from app.api.routes import router as api_router
from app.api.webhooks import router as webhook_router
from app.config.settings import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WhatsApp Agent System",
    description="Multi-agent system for infoproduct sales via WhatsApp",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    return {
        "message": "WhatsApp Agent System is running",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
