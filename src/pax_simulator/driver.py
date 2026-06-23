from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from pax_simulator.config import BrowserConfig


class DriverFactory:
    @staticmethod
    def create(config: BrowserConfig) -> WebDriver:
        browser = config.name.lower()
        if browser == "edge":
            return DriverFactory._create_edge(config)
        return DriverFactory._create_chrome(config)

    @staticmethod
    def _create_chrome(config: BrowserConfig) -> WebDriver:
        options = ChromeOptions()
        DriverFactory._apply_common_options(options, config)
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        DriverFactory._configure(driver, config)
        return driver

    @staticmethod
    def _create_edge(config: BrowserConfig) -> WebDriver:
        options = EdgeOptions()
        DriverFactory._apply_common_options(options, config)
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        DriverFactory._configure(driver, config)
        return driver

    @staticmethod
    def _apply_common_options(options, config: BrowserConfig) -> None:
        if config.headless:
            options.add_argument("--headless=new")
        width, height = config.window_size.split(",")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-US")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    @staticmethod
    def _configure(driver: WebDriver, config: BrowserConfig) -> None:
        driver.implicitly_wait(config.implicit_wait)
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            },
        )
