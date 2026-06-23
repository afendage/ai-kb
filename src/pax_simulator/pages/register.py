from __future__ import annotations

import logging
import time

from selenium.webdriver.common.by import By

from pax_simulator.models import RegistrationResult, UserProfile
from pax_simulator.pages.base import BasePage
from pax_simulator.utils.random_data import UserDataFactory

logger = logging.getLogger(__name__)

NOTICE_POPUP = ".notice-popup"
NOTICE_CLOSE = ".notice-popup .van-popup__close-icon"
AGREE_CHECKBOX = ".showLoginPopup .forget .click-icon"
SUBMIT_BUTTON = ".showLoginPopup button.btn.van-button--primary"


class RegisterPage(BasePage):
    def open_register_modal(self, url: str) -> None:
        self.open(url)
        time.sleep(3)
        self.close_notice_popup()
        self.dismiss_overlays()

        email_input = self.find_optional("#email")
        if email_input is None:
            logger.info("Register modal not visible, opening from header")
            header_register = self.find_optional("button.btn2")
            if header_register:
                self.js_click(header_register)
                time.sleep(2)

        self.wait_for_modal("#email")

    def close_notice_popup(self) -> None:
        """Close the announcement popup that overlays the register form."""
        for _ in range(3):
            popups = [
                p
                for p in self.driver.find_elements(By.CSS_SELECTOR, NOTICE_POPUP)
                if p.is_displayed()
            ]
            if not popups:
                return
            close_icons = self.driver.find_elements(By.CSS_SELECTOR, NOTICE_CLOSE)
            clicked = False
            for icon in close_icons:
                if icon.is_displayed():
                    self.js_click(icon)
                    clicked = True
                    time.sleep(1)
                    break
            if not clicked:
                return
        logger.info("Notice popup dismissed")

    def fill_form(self, user: UserProfile) -> None:
        username = UserDataFactory.sanitize_username(user.username)
        if username != user.username:
            logger.warning("Username sanitized %r -> %r (alphanumeric only)", user.username, username)
            user.username = username

        logger.info("Filling registration form for %s", user.username)
        self.type_text("#email", user.email)
        self.type_text("#username", user.username)
        self.type_text("#password", user.password)
        if user.referral_code:
            self.type_text("#referralCode", user.referral_code)

        self.accept_terms()

    def accept_terms(self) -> None:
        """Tick the 'I have attained 18 years old...' agreement checkbox."""
        checkbox = self.find_optional(AGREE_CHECKBOX)
        if checkbox is None:
            logger.warning("Agreement checkbox not found")
            return
        
        # Check if already checked
        classes = checkbox.get_attribute("class") or ""
        if "checked" in classes.split():
            logger.info("Agreement checkbox is already checked")
            return
            
        logger.info("Ticking agreement checkbox")
        self.js_click(checkbox)
        time.sleep(0.5)
        
        # Verify if checked
        classes = checkbox.get_attribute("class") or ""
        if "checked" not in classes.split():
            logger.warning("Agreement checkbox still not checked, retrying click")
            self.js_click(checkbox)
            time.sleep(0.5)

    def submit(self) -> None:
        buttons = self.driver.find_elements(By.CSS_SELECTOR, SUBMIT_BUTTON)
        for button in buttons:
            if button.is_displayed() and "register" in button.text.lower():
                self.js_click(button)
                return
        self.click(SUBMIT_BUTTON)

    def register(self, url: str, user: UserProfile) -> RegistrationResult:
        self.open_register_modal(url)
        self.fill_form(user)
        self.submit()
        time.sleep(3)
        message = self._detect_result_message()
        success = self._is_success(message)
        screenshot = None
        if not success:
            from pathlib import Path

            screenshot = self.save_screenshot(
                Path("artifacts") / f"register_failed_{user.username}.png"
            )
        return RegistrationResult(
            success=success,
            user=user,
            message=message,
            screenshot_path=screenshot,
        )

    def _detect_result_message(self) -> str:
        selectors = [
            ".van-toast",
            ".van-toast__text",
            "[class*='toast']",
            "[class*='error']",
            "[class*='success']",
        ]
        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = (element.text or "").strip()
                if text:
                    return text
        
        # Check for slider captcha
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "Swipe to complete" in body_text or "滑动完成" in body_text:
                return "Slider captcha detected (requires manual solving or captcha service)"
        except Exception:
            pass

        return ""

    def _is_success(self, message: str) -> bool:
        lowered = message.lower()
        if any(word in lowered for word in ("success", "welcome", "registered")):
            return True
        if any(word in lowered for word in ("fail", "error", "exist", "invalid")):
            return False
        
        # Fallback: Check if we can find the email input.
        # If the browser session is closed/deleted, or we get an invalid session id,
        # it means the browser was closed/killed, NOT that registration failed.
        # In batch mode, we should treat session errors as a browser crash, not a registration failure.
        try:
            email_input = self.find_optional("#email")
            return email_input is None or not email_input.is_displayed()
        except Exception as e:
            # If we get a session error here, propagate it so runner can handle it as a driver crash
            raise e
