from __future__ import annotations

import logging
import random

from selenium.webdriver.common.by import By

from pax_simulator.pages.base import BasePage
from pax_simulator.utils.waits import human_delay

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    def open_home(self, url: str) -> None:
        self.open(url)
        human_delay(1.5, 2.5)
        self.dismiss_overlays()

    def scroll_page(self, steps: int = 3) -> None:
        for _ in range(steps):
            delta = random.randint(300, 900)
            self.driver.execute_script(f"window.scrollBy(0, {delta});")
            human_delay(0.8, 1.8)

    def click_visible_buttons(self, css: str, max_clicks: int = 2) -> int:
        clicked = 0
        buttons = [
            btn
            for btn in self.driver.find_elements(By.CSS_SELECTOR, css)
            if btn.is_displayed() and btn.is_enabled()
        ]
        random.shuffle(buttons)
        for button in buttons[:max_clicks]:
            label = (button.text or "").strip()
            if not label or label.lower() in {"register", "login"}:
                continue
            try:
                self.js_click(button)
                clicked += 1
                logger.info("Clicked button: %s", label)
                human_delay(1.0, 2.0)
            except Exception as exc:
                logger.debug("Skip button %s: %s", label, exc)
        return clicked

    def switch_bet_tab(self) -> None:
        tabs = [
            tab
            for tab in self.driver.find_elements(By.CSS_SELECTOR, "button.u-btn")
            if tab.is_displayed() and tab.text.strip() in {"All Bets", "High Rollers"}
        ]
        if len(tabs) >= 2:
            target = random.choice(tabs)
            self.js_click(target)
            logger.info("Switched bet tab to %s", target.text.strip())

    def open_register_from_header(self) -> None:
        self.click("button.btn2")

    def open_login_from_header(self) -> None:
        self.click("button.btn1")
