from __future__ import annotations

import time
from typing import Callable, TypeVar

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

T = TypeVar("T")


def wait_for(driver: WebDriver, timeout: int, condition: Callable[[WebDriver], T]) -> T:
    return WebDriverWait(driver, timeout).until(condition)


def _first_visible(css: str):
    """Return the first *visible* element matching the selector.

    Needed because the site renders duplicate ids (e.g. both the E-mail and
    Mobile register forms expose ``#username``), and a plain locator may resolve
    to a hidden copy.
    """

    def _condition(driver: WebDriver):
        try:
            for element in driver.find_elements(By.CSS_SELECTOR, css):
                if element.is_displayed():
                    return element
        except StaleElementReferenceException:
            return False
        return False

    return _condition


def wait_visible(driver: WebDriver, timeout: int, locator):
    by, value = locator
    if by == By.CSS_SELECTOR:
        return wait_for(driver, timeout, _first_visible(value))
    return wait_for(driver, timeout, EC.visibility_of_element_located(locator))


def wait_clickable(driver: WebDriver, timeout: int, locator):
    return wait_for(driver, timeout, EC.element_to_be_clickable(locator))


def wait_page_ready(driver: WebDriver, timeout: int = 30) -> None:
    end = time.time() + timeout
    while time.time() < end:
        state = driver.execute_script("return document.readyState")
        if state == "complete":
            return
        time.sleep(0.2)
    raise TimeoutException("Page did not reach readyState=complete")


def human_delay(min_sec: float, max_sec: float) -> None:
    import random

    time.sleep(random.uniform(min_sec, max_sec))
