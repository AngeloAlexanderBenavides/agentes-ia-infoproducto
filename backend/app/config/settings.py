from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WhatsApp Agent System"
    DEBUG: bool = True

    # WAHA (WhatsApp HTTP API)
    WAHA_API_URL: str = "http://localhost:3000"
    WAHA_API_KEY: str = "test-key"
    WAHA_SESSION: str = "default"

    # Evolution API (kept for backward compat)
    EVOLUTION_API_URL: str = "http://localhost:3000"
    EVOLUTION_API_KEY: str = "test-key"
    EVOLUTION_INSTANCE_NAME: str = "default"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # OpenAI (legacy, kept for backward compat)
    OPENAI_API_KEY: str = ""

    # Database (stored in /app/data so it persists across Docker rebuilds)
    DATABASE_URL: str = "sqlite:///./data/whatsapp_agents.db"

    # WhatsApp Configuration
    OWNER_WHATSAPP: str = "593999496469"  # Angelo's WhatsApp number for notifications

    # Payment Configuration
    ECUADOR_DISCOUNT: float = 1.0
    BASE_PRICE: float = 7.99
    ECUADOR_PRICE: float = 6.99

    # Bank Details (Ecuador)
    BANK_NAME: str = "Banco Pichincha"
    BANK_ACCOUNT_NUMBER: str = "2208483287"
    BANK_ACCOUNT_HOLDER: str = "Angelo Benavides"
    BANK_ACCOUNT_TYPE: str = "Ahorros Transaccional"

    # Product Configuration
    PRODUCT_NAME: str = "LA BIBLIA DEL PROMPTING: GUÍA DEFINITIVA DE 0 A EXPERTO EN INGENIERÍA DE PROMPTS"
    PRODUCT_DESCRIPTION: str = "¿Alguna vez has sentido la frustración de recibir respuestas genéricas, incompletas o erróneas de la Inteligencia Artificial?"
    LEAD_MAGNET_URL: str = "https://drive.google.com/drive/folders/1Pg86uw1FTmTXM199xcRfmrcQwGdgJehv?usp=drive_link"
    LEAD_MAGNET_NAME: str = "Cursos Gratis: Usar ChatGPT para trabajar + Automatización con IA"
    PRODUCT_DELIVERY_URL: str = "https://drive.google.com/drive/folders/1pDcLPDmAlafsaP9svwg553F4gIdlv5Uc?usp=drive_link"

    # Upsell Configuration
    UPSELL_PRODUCT_NAME: str = "CURSO AVANZADO DE IA Y AUTOMATIZACIÓN"
    UPSELL_PRICE: float = 14.99
    UPSELL_ECUADOR_PRICE: float = 12.99
    UPSELL_DELIVERY_URL: str = "https://drive.google.com/drive/folders/11ikoGWmF9JpTL-FpMkO0FL6Ir2KSIK_c?usp=drive_link"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
