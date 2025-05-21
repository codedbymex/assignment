from scraper.description_parser import DescriptionParser
from scraper.models import StructuredProduct
from datetime import datetime,timezone

class ProductConverter:
    def __init__(self, currency_rates: dict = None, target_currency: str = "USD"):
        self.rates = currency_rates
        self.target_currency = target_currency.upper()

    def to_structured(self, raw):
        rate = self.rates.get(self.target_currency, 1.0)
        converted_price = round(raw.price_usd * rate, 2)
        parsed = DescriptionParser.parse(raw.description_raw or "", raw.name)
        return StructuredProduct(
            name=raw.name,
            price=converted_price,
            currency=self.target_currency,
            rating=raw.rating,
            num_reviews=raw.num_reviews,
            description=raw.description_raw or "",
            url=raw.url,
            last_scraped=datetime.now(timezone.utc),
            **parsed
        )
