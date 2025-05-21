import time
from urllib.parse import urljoin
from typing import List, Union
from bs4 import BeautifulSoup

from scraper.base_extractor import BaseExtractor
from scraper.card_parser import CardParser
from scraper.click_executor import ClickExecutor
from scraper.models import RawProduct, StructuredProduct
from scraper.paginator import Paginator


class ProductListExtractor(BaseExtractor):
    """
    Extractor for product listings from an e-commerce category page.
    Responsible for navigating, paginating, and parsing all product data into structured models.
    """

    def extract(self) -> List[Union[RawProduct, StructuredProduct]]:
        """
        Main entrypoint: navigates to the category page, paginates until done,
        and extracts all products as RawProduct or StructuredProduct objects.

        Returns:
            List[RawProduct | StructuredProduct]: all extracted product data
        """
        self.driver.get(self._category_url())
        self._paginate()
        html = self.driver.page_source
        structured = self.config["global"]["structured_products_data"]
        self.logger.info(f"Extracting {'structured' if structured else 'raw'} products")
        return self._parse_products(html, structured)

    def _category_url(self) -> str:
        """
        Constructs the full category URL using the base URL and category key.

        Returns:
            str: fully qualified URL to the category page
        """
        category_url = self.config["products"]["category_url"]
        return urljoin(self.config["base_url"], f"{category_url.rstrip('/')}/{self.category_key}")

    def _paginate(self):
        """
        Uses a ClickExecutor and Paginator to load all products
        by clicking 'Load More' buttons until all items are visible.
        """
        click_executor = ClickExecutor(
            driver=self.driver,
            logger=self.logger,
            get_selector=self.get_selector,
            button_wait_time=self.config["products"]["load_more_button_wait_time"],
            content_wait_time=self.config["products"]["load_cards_wait_time"]
        )

        paginator = Paginator(executor=click_executor, logger=self.logger)
        paginator.scroll_until_done()

    def _parse_products(self, html: str, structured: bool = True) -> List[Union[StructuredProduct, RawProduct]]:
        """
        Parses product cards from the given HTML and returns a list of structured product models.

        Args:
            html (str): the full HTML source of the loaded category page

        Returns:
            List[RawProduct]: parsed product data
        """
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(self.get_selector("product_card"))
        self.logger.info(f"Found {len(cards)} product cards")
        start = time.time()

        currency_rates = self.products_config.get("currency_rates")
        target_currency = self.products_config.get("target_currency")
        parser = CardParser(
            self.get_selector,
            self.config,
            self.logger,
            currency_rates=currency_rates if currency_rates else None,
            target_currency=target_currency if target_currency else "USD"
        )
        if structured:
            products = [p for card in cards if (p := parser.to_structured(card))]
        else:
            products = [p for card in cards if (p := parser.parse(card))]
        elapsed = time.time() - start
        self.logger.info(
            f"Parsed {len(products)} {'structured' if structured else 'raw'} products in {elapsed:.2f} seconds")
        return products
