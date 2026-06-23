from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from pax_simulator.utils.waits import wait_clickable, wait_for, wait_page_ready, wait_visible

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        self.driver = driver
        self.timeout = timeout

    def open(self, url: str) -> None:
        logger.info("Opening %s", url)
        self.driver.get(url)
        wait_page_ready(self.driver, self.timeout)

    def find(self, css: str) -> WebElement:
        return wait_visible(self.driver, self.timeout, (By.CSS_SELECTOR, css))

    def find_optional(self, css: str) -> WebElement | None:
        try:
            return self.find(css)
        except TimeoutException:
            return None

    def find_all(self, css: str) -> list[WebElement]:
        wait_for(self.driver, self.timeout, EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        return self.driver.find_elements(By.CSS_SELECTOR, css)

    def click(self, css: str) -> None:
        element = wait_clickable(self.driver, self.timeout, (By.CSS_SELECTOR, css))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()

    def type_text(self, css: str, value: str, clear: bool = True) -> None:
        element = self.find(css)
        if clear:
            element.clear()
        element.send_keys(value)

    def wait_until_gone(self, css: str, timeout: int | None = None) -> None:
        wait_for(
            self.driver,
            timeout or self.timeout,
            EC.invisibility_of_element_located((By.CSS_SELECTOR, css)),
        )

    def save_screenshot(self, path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(path))
        return str(path)

    def get_text(self, css: str) -> str:
        return self.find(css).text.strip()

    def js_click(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    def dismiss_overlays(self) -> None:
        # Dismiss cookie banners or other non-essential overlays
        # Avoid clicking close buttons or overlays that belong to the login/register modal
        try:
            # Click cookie buttons
            for btn in self.driver.find_elements(By.CSS_SELECTOR, "[class*='cookie'] button"):
                if btn.is_displayed():
                    try:
                        btn.click()
                    except Exception:
                        pass
            
            # Click close buttons of other popups (not login/register)
            for element in self.driver.find_elements(By.CSS_SELECTOR, "[class*='close'], .van-popup__close-icon"):
                if element.is_displayed():
                    try:
                        # Check if inside login/register modal
                        is_inside_login = self.driver.execute_script(
                            "let el = arguments[0]; while(el) { "
                            "if (el.classList && (el.classList.contains('showLoginPopup') || el.classList.contains('u-van-popup'))) return true; "
                            "el = el.parentElement; "
                            "} return false;",
                            element
                        )
                        if not is_inside_login:
                            self.js_click(element)
                    except Exception:
                        pass
        except Exception as e:
            logger.debug("Error in dismiss_overlays: %s", e)

    def wait_for_modal(self, input_css: str) -> None:
        self.find(input_css)
