from __future__ import annotations

import logging
import random
import time

from selenium.webdriver.remote.webdriver import WebDriver

from pax_simulator.config import AppConfig
from pax_simulator.pages.home import HomePage
from pax_simulator.utils.waits import human_delay

logger = logging.getLogger(__name__)


class UserBehaviorSimulator:
    """Simulate typical browsing behavior on the uwin site."""

    def __init__(self, driver: WebDriver, config: AppConfig) -> None:
        self.driver = driver
        self.config = config
        self.home = HomePage(driver)

    def run(self) -> None:
        behavior = self.config.behavior
        end_time = time.time() + behavior.duration_sec
        self.home.open_home(self.config.site.home_url)

        actions = [
            self._scroll,
            self._switch_bet_tab,
            self._click_safe_buttons,
            self._pause,
        ]

        while time.time() < end_time:
            action = random.choice(actions)
            action()
            human_delay(behavior.action_delay_min, behavior.action_delay_max)

        logger.info("Behavior simulation finished")

    def _scroll(self) -> None:
        self.home.scroll_page(self.config.behavior.scroll_steps)

    def _switch_bet_tab(self) -> None:
        self.home.switch_bet_tab()

    def _click_safe_buttons(self) -> None:
        if not self.config.behavior.enable_random_clicks:
            return
        self.home.click_visible_buttons("button.u-btn", max_clicks=1)
        self.home.click_visible_buttons("button.btn", max_clicks=1)

    def _pause(self) -> None:
        human_delay(2.0, 4.0)
