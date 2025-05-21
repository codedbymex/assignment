from logging import Logger

from scraper.click_executor import ClickExecutor
from scraper.enums import ClickStatus


class Paginator:
    def __init__(
        self,
        logger: Logger,
        executor: ClickExecutor,
        max_idle_clicks: int = 3,
        item_selector: str = "product_card"
    ):
        self.executor = executor
        self.logger = logger
        self.max_idle_clicks = max_idle_clicks
        self.item_selector = item_selector

    def scroll_until_done(self) -> None:
        clicks: int = 0
        idle_clicks: int = 0

        while idle_clicks < self.max_idle_clicks:
            prev_count = self.executor.get_count(self.item_selector)
            if prev_count is None:
                self.logger.error("Cannot determine number of items.")
                break

            status = self.executor.try_click_and_wait(
                "load_more",
                lambda: (count := self.executor.get_count(self.item_selector)) is not None and count > prev_count
            )

            if status == ClickStatus.SUCCESS:
                clicks += 1
                idle_clicks = 0
                self.logger.debug(f"Click #{clicks} succeeded, more items loaded.")

            elif status in (ClickStatus.NO_NEW_ITEMS, ClickStatus.BUTTON_HIDDEN):
                button_visible = self.executor.is_button_present_and_visible("load_more")
                if not button_visible:
                    self.logger.info("No new items and 'load_more' button is gone. Ending pagination.")
                    break
                idle_clicks += 1
                self.logger.debug(
                    f"No new items (idle #{idle_clicks}/{self.max_idle_clicks}), but button still visible."
                )

            else:
                self.logger.error("Click failed. Ending pagination.")
                break

        self.logger.info(f"Pagination done. {clicks} clicks, {idle_clicks} idle attempts.")
