from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, List, Union
from selenium.webdriver.remote.webdriver import WebDriver
from pydantic import BaseModel
import json
import csv
import logging


class BaseExtractor(ABC):
    """Abstract base class for all extractors, providing core utilities for scraping and exporting data."""

    def __init__(self, driver: WebDriver, config: dict[str, Any], category_key: str):
        """
        Initialize the extractor.

        Args:
            driver (WebDriver): Selenium WebDriver instance.
            config (dict): Configuration dictionary.
            category_key (str): Category name used to resolve selectors.
        """
        self.driver = driver
        self.config = config
        self.category_key = category_key
        self.products_config = config.get("products", {})
        self.selectors = self.products_config.get("selectors", {})

        base_logger = logging.getLogger(self.__class__.__name__)
        logging_level = getattr(logging, config['global']['logging_level'], logging.INFO)
        base_logger.setLevel(logging_level)
        self.logger = logging.LoggerAdapter(base_logger, extra={"category": category_key})

    @abstractmethod
    def extract(self) -> Any:
        """Main extraction method to be implemented by subclasses."""
        pass

    def get_selector(self, key: str) -> Optional[str]:
        """Return the configured CSS selector for a given key."""
        return self.selectors.get(key)

    @staticmethod
    def write_to_json(models: List[BaseModel], filepath: Union[str, Path]):
        """Write a list of Pydantic models to a JSON file."""
        if not models:
            return
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(
                [model.model_dump(mode="json") for model in models],
                file,
                indent=2,
                ensure_ascii=False
            )

    @staticmethod
    def write_to_csv(models: List[BaseModel], filepath: Union[str, Path]):
        """Write a list of Pydantic models to a CSV file."""
        if not models:
            return
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=models[0].model_dump(mode="json").keys())
            writer.writeheader()
            for model in models:
                writer.writerow(model.model_dump(mode="json"))
