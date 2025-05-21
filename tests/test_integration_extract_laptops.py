import pytest
from scraper.product_list_extractor import ProductListExtractor
from scraper.models import StructuredProduct
from datetime import datetime


@pytest.mark.integration
def test_laptop_extraction_with_real_driver(driver, config):
    extractor = ProductListExtractor(driver, config, "laptops")
    products = extractor.extract()

    assert isinstance(products, list), "Products should be a list"
    assert len(products) == 117, f"Expected 117 products, got {len(products)}"

    for idx, product in enumerate(products):
        assert isinstance(product, StructuredProduct), f"Product {idx} is not a StructuredProduct"
        assert isinstance(product.name, str) and product.name.strip(), f"Missing or empty name on product {idx}"
        assert isinstance(product.price, float) and product.price > 0, f"Invalid price on product {idx}"
        assert product.currency == "USD", f"Unexpected currency on product {idx}"
        assert isinstance(product.rating, float), f"Rating not float on product {idx}"
        assert isinstance(product.num_reviews, int), f"num_reviews not int on product {idx}"
        assert product.url.startswith("https://"), f"Invalid URL on product {idx}"
        assert isinstance(product.last_scraped, datetime), f"last_scraped not datetime on product {idx}"

        # Optional fields
        if product.brand is not None:
            assert isinstance(product.brand, str) and product.brand.strip(), f"Invalid brand on product {idx}"
        if product.screen_inches is not None:
            assert isinstance(product.screen_inches, float) and 10.0 <= product.screen_inches <= 20.0, f"Unrealistic screen_inches on product {idx}"
        if product.ram_gb is not None:
            assert isinstance(product.ram_gb, int) and product.ram_gb > 0, f"Invalid ram_gb on product {idx}"
        if product.storage_gb is not None:
            assert isinstance(product.storage_gb, int) and product.storage_gb > 0, f"Invalid storage_gb on product {idx}"
        if product.cpu is not None:
            assert isinstance(product.cpu, str) and product.cpu.strip(), f"Invalid CPU on product {idx}"
        if product.os is not None:
            assert isinstance(product.os, str) and product.os.strip(), f"Invalid OS on product {idx}"
