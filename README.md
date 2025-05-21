# Crisp Web Data Extraction Assignment

## Prerequisites

- Python 3.9+
- Google Chrome browser
- ChromeDriver compatible with your Chrome version (ensure it's in PATH) also Firefox geckodriver fo testing
- Recommended: Create a virtual environment

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## How to Run

### Run the Scraper (default config)

```bash
python run.py
```

### CLI Options

```bash
python run.py --category laptops --structured --headed
```

- `--category`: category to scrape (e.g., laptops, tablets)
- `--structured`: enable parsing of structured specs (CPU, RAM, etc.)
- `--headed`: run browser in visible (non-headless) mode

## Example Config File (`config.yaml`)

```yaml
base_url: "https://webscraper.io"

global:
  category: "laptops"
  output_dir: "output"
  output_format: "csv"
  logging_level: INFO # DEBUG, ERROR, CRITICAL, NOTSET, INFO
  structured_products_data: true

browser:
  name: "chrome"
  headed: false
  window_size: [1440, 1800] # [800, 600] will show the privacy term and hide the load more button
  implicitly_wait: 0
  disable_extensions: true
  disable_gpu: true
  log_level: 3
  disable_dev_shm_usage: true
  no_sandbox: true
  scroll_into_view_before_click: true
  wait_after_click_ms: 0

products:
  category_url: "/test-sites/e-commerce/more/computers/"
  selectors:
    product_card: ".thumbnail"
    name: ".title"
    price: ".price"
    reviews: "div.ratings p.pull-right"
    rating: "div.ratings p:nth-of-type(2) span.ws-icon-star"
    description: ".description"
    product_link: ".title"
    load_more: "ecomerce-items-scroll-more"
  max_retry_load_more: 5
  max_load_more_idle_clicks: 5
  load_more_button_wait_time: 5
  load_cards_wait_time: 5
  currency_rates: {USD: 1.0}
  target_currency: "RON"
```

## Sample Output (Excerpt from `laptops_raw.json`)

```json
  {
    "name": "Lenovo V510 Blac",
    "price": 2439.0,
    "currency": "RON",
    "rating": 5.0,
    "num_reviews": 12,
    "description": "Lenovo V510 Black, 15.6\" HD, Core i3-6006U, 4GB, 128GB SSD, Windows 10 Home",
    "url": "https://webscraper.io/test-sites/e-commerce/more/product/89",
    "last_scraped": "2025-05-20T20:57:51.352138Z",
    "brand": "Lenovo",
    "screen_inches": 15.6,
    "ram_gb": 4,
    "storage_gb": 132,
    "cpu": "Core i3-6006U",
    "os": "Windows 10 Home"
  },
```

**Note:** The star rating on the product listing page always displayed 5 stars for every item. Accurate star ratings were only available on the product detail pages, which were out of scope for this assignment. As such, the `rating` field may be misleading and was not fully reliable from the listing page alone.

---

## Architectural Overview

### Top-Level Orchestration

- `run.py`: Main entry point. Parses CLI args, loads config, instantiates logger and the `ProductListExtractor`, and triggers the scrape + data dump.

### Modules Overview

#### `scraper/base_extractor.py`
- Abstract class for any extractor (list or detail level).
  Subclass this base class and implement extract() to create a scraper for a specific product category or webpage. Use get_selector() for accessing configured selectors, and use write_to_json() / write_to_csv() for saving the results.
#### `scraper/product_list_extractor.py`
- High-level implementation that coordinates loading, parsing, and converting:
  1. Loads config.
  2. Initializes WebDriver (via `utils`).
  3. Uses `Paginator` to scroll/load all products.
  4. Parses each card using `CardParser`.
  5. Transforms to structured form via `ProductConverter`.

#### `scraper/paginator.py`
- Automates clicking the "Load More" button and waits until no new cards appear.
- Tracks loaded card count and stops after a few failed retries.
- Uses `ClickExecutor` to encapsulate waiting and retry logic.

#### `scraper/card_parser.py`
- Takes raw HTML of each product card and extracts fields using configured CSS selectors.
- Builds a `RawProduct`. Logs parsing errors (e.g., if `price` or `name` is missing).

#### `scraper/description_parser.py`
- Parses `description_raw` into structured specs:
  - CPU (e.g., Intel i7)
  - RAM (e.g., 16GB)
  - Storage (e.g., 512GB SSD)
  - Screen size (e.g., 14")
  - OS (e.g., Windows 10)

#### `scraper/product_converter.py`
- Orchestrates conversion from `RawProduct` → `StructuredProduct`
- Uses `description_parser` under the hood.
- Handles missing/optional fields with validation logic.

#### `scraper/models.py`
- `RawProduct`: Includes name, price, description, rating, etc.
- `StructuredProduct`: Adds parsed CPU, RAM, storage, brand, etc.

#### `scraper/click_executor.py`
- Wraps `element.click()` with logic to wait until page content changes.
- Prevents Selenium from failing on flaky clicks or delays in content rendering.



### Data Flow Summary

```
run.py
 └── ProductListExtractor
      ├── Paginator (loads items via ClickExecutor)
      ├── CardParser (raw product parsing)
      ├── ProductConverter (raw → structured)
      └── Returns ProductDataWrapper
        └── writer logic in run.py saves to output/
```

---

## Assumptions and Next Steps

### Assumptions

- There is always a top-level category URL to start from, defined in config.yaml as category_url.
- All product listings exist under a single consistent HTML structure, such as cards that can be selected with a 
single CSS selector.
- Category pages follow a consistent pattern across multiple categories, allowing for reusability of the same 
extractor logic.
- Dynamic content (e.g. via Load More) can be handled through click-based pagination.
- Only one level of pagination is required the scraper doesn't expect nested or recursive pagination.
- Product detail pages are not currently required, as product_detail_extractor.py is a placeholder.
- Config is static and sufficient for all operations no live detection or fallback mechanisms are implemented.
- Selectors don’t change frequently all logic assumes selectors defined in YAML will remain valid.
- All scraping is assumed to happen with one static Selenium session, session state isn’t reset between steps.
- The browser can access the target page without authentication or cookies.
- Listing page star ratings are static placeholders.

### Next Steps 

- Extract data from product detail pages for real ratings.
- Implement exponential backoff.
- Improve spec parsing with NLP (e.g., RAM: "16GB DDR4" → `ram_gb=16`, `ram_type=DDR4`).
- Add visual monitoring or alerts.
- Containerize with Docker for CI/CD integration. 
- Introduce Playwright for parallelized and faster scraping across multiple product categories. Playwright supports 
  async scraping with multiple browser contexts, which can significantly improve performance over Selenium. Each category (e.g., laptops, tablets, phones) can be scraped concurrently using an asyncio event loop, reducing total scrape time. This also opens the door to more robust testing across browsers (Chromium, Firefox, WebKit).
- Avoid Saving Unchanged Data Using Hash and Last Scraped Date
To prevent redundant saves and improve efficiency, we add logic to detect changes in scraped data using:
Data Hashing: Compute a hash (e.g. SHA256) of the product list to detect content changes. Last Scraped Timestamp: Track the timestamp of the last successful scrape to compare against existing data.
---

## Tests and How to Run Them

### Run All Tests

```bash
pytest
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Integration Test Summary

File: `tests/test_integration_extract_laptops.py`
- Loads all products.
- Asserts number of records (117).
- Verifies data types, parsed values.

### Notes
- Use `test_config.yaml` to point to test category.
- Switch `headed: true` in config for debugging.

---

For further help, consult inline code comments and logging output.
