from typing import List

from scraper.base_extractor import BaseExtractor
from scraper.models import StructuredProduct, RawProduct


class ProductDetailExtractor(BaseExtractor):
    """
    Placeholder class for future product detail scraping from product URLs.
    Currently returns a StructuredProduct from RawProduct without modifications.
    """

    def extract(self, product: RawProduct) -> List[StructuredProduct]:
        self.logger.warning("Detail extraction not yet implemented. Returning raw product as structured.")
