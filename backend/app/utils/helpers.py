"""
Helper utilities
"""
import re
from typing import Optional, Tuple


def parseNameAndCountry(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse name and country from user message

    Args:
        message: User's message containing name and country

    Returns:
        Tuple of (name, country)
    """
    # Try comma-separated format first
    if "," in message:
        parts = message.split(",")
        if len(parts) >= 2:
            name = parts[0].strip().title()
            country = parts[1].strip().title()
            return name, country

    # Try to detect country keywords
    message_lower = message.lower()
    country_keywords = {
        "ecuador": "Ecuador",
        "colombia": "Colombia",
        "perú": "Perú",
        "peru": "Perú",
        "méxico": "México",
        "mexico": "México",
        "argentina": "Argentina",
        "chile": "Chile",
        "españa": "España",
        "venezuela": "Venezuela",
        "bolivia": "Bolivia",
        "paraguay": "Paraguay",
        "uruguay": "Uruguay",
    }

    country = None
    for keyword, country_name in country_keywords.items():
        if keyword in message_lower:
            country = country_name
            # Remove country from message to get name
            message = re.sub(keyword, "", message, flags=re.IGNORECASE)
            break

    # Extract name (remaining text)
    name = message.strip().title()

    # Clean up name
    name = re.sub(r'[,.]', '', name).strip()

    if name and country:
        return name, country

    return None, None


def formatPhoneNumber(phone: str) -> str:
    """
    Format phone number for WhatsApp

    Args:
        phone: Phone number in various formats

    Returns:
        Formatted phone number with @s.whatsapp.net
    """
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Remove leading + or 00
    phone = re.sub(r'^(\+|00)', '', phone)

    # Add WhatsApp suffix if not present
    if "@s.whatsapp.net" not in phone:
        phone = f"{phone}@s.whatsapp.net"

    return phone


def cleanPhoneNumber(phone: str) -> str:
    """
    Clean phone number (remove @s.whatsapp.net)

    Args:
        phone: Phone number with @s.whatsapp.net

    Returns:
        Clean phone number
    """
    return phone.replace("@s.whatsapp.net", "")


def detectPurchaseIntent(message: str) -> bool:
    """
    Detect if message indicates purchase intent

    Args:
        message: User's message

    Returns:
        True if purchase intent detected
    """
    message_lower = message.lower()
    purchase_keywords = [
        "comprar", "compra", "quiero", "si", "sí", "proceder",
        "adelante", "cómo pago", "como pago", "precio", "cuánto", "cuanto",
        "me interesa", "lo quiero", "dale", "ok", "listo"
    ]

    return any(keyword in message_lower for keyword in purchase_keywords)


def detectInfoRequest(message: str) -> bool:
    """
    Detect if message is requesting more information

    Args:
        message: User's message

    Returns:
        True if information request detected
    """
    message_lower = message.lower()
    info_keywords = [
        "cómo funciona", "como funciona", "más info", "mas info",
        "detalles", "explicar", "que incluye", "qué incluye",
        "features", "características", "que es", "qué es",
        "más detalles", "mas detalles"
    ]

    return any(keyword in message_lower for keyword in info_keywords)


def getCountryFlag(country: str) -> str:
    """
    Get emoji flag for country

    Args:
        country: Country name

    Returns:
        Emoji flag
    """
    flags = {
        "Ecuador": "🇪🇨",
        "Colombia": "🇨🇴",
        "Perú": "🇵🇪",
        "México": "🇲🇽",
        "Argentina": "🇦🇷",
        "Chile": "🇨🇱",
        "España": "🇪🇸",
        "Venezuela": "🇻🇪",
        "Bolivia": "🇧🇴",
        "Paraguay": "🇵🇾",
        "Uruguay": "🇺🇾",
    }
    return flags.get(country, "🌍")
