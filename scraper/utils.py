import argparse
import logging
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)


def load_config(path: str) -> dict:
    """Load YAML config from the given path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config file '{path}': {e}")
        raise


def create_driver(config: dict) -> webdriver.Chrome:
    """Create and return a Selenium Chrome WebDriver using config options."""
    args = config.get("args", {})
    options = Options()

    if args.get("headless", True):
        options.add_argument("--headless=new")

    window_size = config.get("browser", {}).get("window_size", [1280, 720])
    if not isinstance(window_size, (list, tuple)) or len(window_size) != 2:
        logger.warning("Invalid or missing 'window_size'. Falling back to 1280x720.")
        window_size = [1280, 720]
    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

    implicitly_wait = config.get("browser", {}).get("implicitly_wait", 5)
    if not isinstance(implicitly_wait, (int, float)):
        logger.warning("Invalid 'implicitly_wait'. Falling back to 5s.")
        implicitly_wait = 5

    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(implicitly_wait)
        return driver
    except Exception as e:
        logger.error(f"Failed to create WebDriver: {e}")
        raise



def get_args_with_defaults():
    """Parse CLI args and override config with CLI values if provided."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML file")

    # First parse just to get config path
    temp_args, _ = parser.parse_known_args()
    try:
        config = load_config(temp_args.config)
    except Exception:
        raise SystemExit(1)

    global_cfg = config.get("global", {})
    browser_cfg = config.get("browser", {})

    # CLI args — no defaults here yet
    parser.add_argument("--category")
    parser.add_argument("--output")
    parser.add_argument("--format", choices=["json", "csv"])
    parser.add_argument("--headed", action="store_true", help="Run in headed (non-headless) mode")

    args = parser.parse_args()

    # Final merged config: CLI > config > fallback
    merged = {
        "category": args.category or global_cfg.get("category", "laptops"),
        "output": args.output or global_cfg.get("output_dir", "output"),
        "format": args.format or global_cfg.get("output_format", "json"),
        "headless": not args.headed if "headed" in args else not browser_cfg.get("headed", False),
    }

    config["args"] = merged
    return argparse.Namespace(**merged), config


def clean_review_count(text: str) -> str:
    """Extract only digits from a review count string."""
    return ''.join(filter(str.isdigit, text or "0")) or "0"
