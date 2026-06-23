"""Inspect registration page elements."""

from __future__ import annotations

import json
import time

from selenium.webdriver.common.by import By

from pax_simulator.config import AppConfig, load_config
from pax_simulator.driver import DriverFactory


def inspect_register_page(url: str | None = None, wait_sec: int = 8, config: AppConfig | None = None) -> None:
    config = config or load_config()
    target_url = url or config.site.register_url
    driver = DriverFactory.create(config.browser)
    try:
        driver.get(target_url)
        time.sleep(wait_sec)
        inputs = driver.find_elements(By.CSS_SELECTOR, "input, button, textarea, select")
        data = []
        for el in inputs:
            if not el.is_displayed():
                continue
            data.append(
                {
                    "tag": el.tag_name,
                    "type": el.get_attribute("type"),
                    "name": el.get_attribute("name"),
                    "id": el.get_attribute("id"),
                    "class": (el.get_attribute("class") or "")[:120],
                    "placeholder": el.get_attribute("placeholder"),
                    "text": (el.text or "")[:80],
                }
            )
        print(json.dumps(data, indent=2, ensure_ascii=False))
    finally:
        driver.quit()
