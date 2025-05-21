import logging
import os

from scraper.product_list_extractor import ProductListExtractor
from scraper.utils import get_args_with_defaults, create_driver

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():

    args, config = get_args_with_defaults()
    driver = create_driver(config)

    logger.setLevel(config['global']['logging_level'])
    try:
        extractor = ProductListExtractor(driver, config, args.category)
        products = list(extractor.extract())
        os.makedirs(args.output, exist_ok=True)
        raw_path = f"{args.output}/{args.category}_raw.{args.format}"
        structured_path = f"{args.output}/{args.category}_structured.{args.format}"
        out_path = structured_path if config['global']['structured_products_data'] else raw_path
        if args.format == "csv":
            extractor.write_to_csv(products, out_path)
        else:
            extractor.write_to_json(products, out_path)
        logger.info(f"Saved {len(products)} products to {out_path}")
    except Exception as e:
        logger.exception(f"An error occurred during extraction or saving. {e}")
    finally:
        driver.quit()
        logger.info("Browser session closed.")


if __name__ == "__main__":
    main()
