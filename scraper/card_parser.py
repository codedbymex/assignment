from urllib.parse import urljoin
from datetime import datetime
from typing import Optional

from scraper.models import RawProduct, StructuredProduct
from scraper.product_converter import ProductConverter
from scraper.utils import clean_review_count


class CardParser:
    """
    Parses individual product cards from the HTML into structured RawProduct objects.
    """

    def __init__(self, get_selector, config, logger, currency_rates=None, target_currency="USD"):
        """
        Initialize the CardParser.

        Args:
            get_selector: Callable that returns a CSS selector by key.
            config: Configuration dictionary.
            logger: Logger instance for structured logging.
        """
        self.get_selector = get_selector
        self.config = config
        self.logger = logger
        self.converter = ProductConverter(currency_rates or {"USD": 1.0}, target_currency)

    def parse(self, card) -> Optional[RawProduct]:
        """
        Parse a single product card into a RawProduct object.

        Args:
            card: BeautifulSoup Tag object representing a product card.

        Returns:
            RawProduct if parsing succeeds, otherwise None.
        """
        try:
            name = self._text(card, "name")
            price = self._text(card, "price")
            rating = float(len(card.select(self.get_selector("rating"))))
            reviews = self._text(card, "reviews")
            description = self._text(card, "description") or ""
            href = self._attr(card, "product_link", "href")

            # Check for critical missing fields
            if not name:
                self._log_failure("Missing product name", card, name, price, href)
                return None
            if not price:
                self._log_failure("Missing product price", card, name, price, href)
                return None
            if not href:
                self._log_failure("Missing product URL", card, name, price, href)
                return None

            return RawProduct(
                name=name,
                price_usd=price,
                rating=rating,
                num_reviews=clean_review_count(reviews),
                description_raw=description,
                url=urljoin(self.config["base_url"], href),
                last_scraped=datetime.utcnow()
            )
        except Exception as e:
            self._log_failure("Exception during parsing", card,  error=str(e))
            return None

    def to_structured(self, card) -> Optional[StructuredProduct]:
        raw = self.parse(card)
        return self.converter.to_structured(raw) if raw else None

    def _text(self, card, key) -> Optional[str]:
        selector = self.get_selector(key)
        tag = card.select_one(selector)
        if not tag:
            self.logger.warning(
                f"Selector '{key}' not found in card.",
                extra={"selector": selector, "key": key}
            )
            return None
        return tag.get_text(strip=True)

    def _attr(self, card, key, attr) -> Optional[str]:
        selector = self.get_selector(key)
        tag = card.select_one(selector)
        if not tag:
            self.logger.warning(
                f"Selector '{key}' not found in card for attribute '{attr}'.",
                extra={"selector": selector, "key": key, "attr": attr}
            )
            return None
        return tag.get(attr)

    def _log_failure(self, reason, card, name=None, price=None, href=None, error=None):
        self.logger.warning(
            f"Failed to parse product card: {reason}",
            extra={
                "name": name,
                "price": price,
                "href": href,
                "reason": reason,
                "error": error,
            }
        )

    def to_structured(self, card) -> Optional[StructuredProduct]:
        raw = self.parse(card)
        return self.converter.to_structured(raw) if raw else None
