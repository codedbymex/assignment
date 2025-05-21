import time
from typing import Optional, Callable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scraper.enums import ClickStatus


class ClickExecutor:
    def __init__(
        self,
        driver,
        logger,
        get_selector: Callable[[str], Optional[str]],
        button_wait_time: int = 10,
        content_wait_time: int = 10
    ):
        """Initialize ClickExecutor with WebDriver, logger, selector resolver, and timeouts."""
        self.driver = driver
        self.logger = logger
        self.get_selector = get_selector
        self.button_wait_time = button_wait_time
        self.content_wait_time = content_wait_time

    def try_click_and_wait(
        self,
        button_name: str,
        wait_condition: Callable[[], bool]
    ) -> ClickStatus:
        """Click a button and wait for the given condition to become True. Returns ClickStatus."""
        try:
            button = self._find_button(button_name)
            if not button or not self._is_button_visible(button):
                self.logger.debug(
                    f"Button '{button_name}' is not visible.",
                    extra={"event": "button_hidden", "button": button_name}
                )
                return ClickStatus.BUTTON_HIDDEN

            self._click(button)
            start = time.time()

            WebDriverWait(self.driver, self.content_wait_time).until(lambda d: wait_condition())
            duration = round(time.time() - start, 2)

            self.logger.debug(
                f"Click on '{button_name}' succeeded and condition met.",
                extra={
                    "event": "click_success",
                    "button": button_name,
                    "status": ClickStatus.SUCCESS.value,
                    "duration": duration
                }
            )
            return ClickStatus.SUCCESS

        except TimeoutException:
            self.logger.info(
                f"Click on '{button_name}' timed out waiting for condition.",
                extra={"event": "no_state_change", "button": button_name, "status": ClickStatus.NO_NEW_ITEMS.value}
            )
            return ClickStatus.NO_NEW_ITEMS

        except (NoSuchElementException, Exception) as e:
            self.logger.error(
                f"Click on '{button_name}' failed due to exception.",
                extra={
                    "event": "click_failed",
                    "button": button_name,
                    "status": ClickStatus.FAILURE.value,
                    "error": str(e)
                }
            )
            return ClickStatus.FAILURE

    def get_count(self, selector_name: str) -> Optional[int]:
        """Return number of elements matching the given selector name, or None on failure."""
        selector = self.get_selector(selector_name)
        if not selector:
            self.logger.error(f"Missing selector for '{selector_name}'", extra={"event": "missing_selector"})
            return None

        try:
            return len(self.driver.find_elements(By.CSS_SELECTOR, selector))
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(
                f"Failed to count elements for '{selector_name}': {e}",
                extra={"event": "count_failed", "selector": selector_name, "error": str(e)}
            )
            return None

    def is_button_present_and_visible(self, name: str) -> bool:
        """Check if the button is present in the DOM and is visible."""
        selector = self.get_selector(name)
        if not selector:
            return False
        try:
            button = self.driver.find_element(By.CLASS_NAME, selector)
            return button.is_displayed()
        except NoSuchElementException:
            return False

    def _find_button(self, name: str):
        """Wait for a button to appear by name and return the WebElement, or None on timeout."""
        selector = self.get_selector(name)
        if not selector:
            self.logger.error(f"No selector found for '{name}'.", extra={"event": "missing_selector", "button": name})
            return None

        try:
            return WebDriverWait(self.driver, self.button_wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, selector))
            )
        except TimeoutException:
            self.logger.warning(
                f"Button '{name}' not found in time.",
                extra={"event": "button_timeout", "button": name}
            )
            return None

    def _is_button_visible(self, button) -> bool:
        """Return True if the button is displayed (visible to user)."""
        return button.is_displayed()

    def _click(self, button):
        """Click the given WebElement."""
        button.click()
