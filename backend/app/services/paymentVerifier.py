"""
Payment Verifier Service - Handle payment verification logic
"""
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class PaymentVerifierService:
    """
    Service to handle payment verification logic
    """

    async def calculateFinalPrice(self, country: str, base_price: float = None) -> float:
        """
        Calculate final price based on country

        Args:
            country: User's country
            base_price: Base price (defaults to settings.BASE_PRICE)

        Returns:
            Final price after discounts
        """
        if base_price is None:
            base_price = settings.BASE_PRICE

        # Ecuador gets special discount
        if country == "Ecuador":
            return base_price - settings.ECUADOR_DISCOUNT

        # Add more country-specific pricing here

        return base_price

    async def getPriceBreakdown(self, country: str) -> dict:
        """
        Get detailed price breakdown for display

        Args:
            country: User's country

        Returns:
            Dictionary with price breakdown
        """
        base_price = settings.BASE_PRICE
        discount = 0

        if country == "Ecuador":
            discount = settings.ECUADOR_DISCOUNT

        final_price = base_price - discount

        return {
            "base_price": base_price,
            "discount": discount,
            "final_price": final_price,
            "currency": "USD",
            "has_discount": discount > 0
        }

    async def getBankDetails(self, country: str) -> dict:
        """
        Get bank details for payment based on country

        Args:
            country: User's country

        Returns:
            Dictionary with bank details
        """
        if country == "Ecuador":
            return {
                "bank_name": settings.BANK_NAME,
                "account_holder": settings.BANK_ACCOUNT_HOLDER,
                "account_number": settings.BANK_ACCOUNT_NUMBER,
                "account_type": settings.BANK_ACCOUNT_TYPE,
                "currency": "USD"
            }

        # Add more country-specific payment methods here

        return {
            "method": "international",
            "options": ["PayPal", "Stripe", "Crypto"]
        }
