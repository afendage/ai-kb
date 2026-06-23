from __future__ import annotations

import random
import string

from faker import Faker

from pax_simulator.config import RegistrationConfig
from pax_simulator.models import UserProfile


class UserDataFactory:
    def __init__(self, config: RegistrationConfig, locale: str = "en_US") -> None:
        self._config = config
        self._faker = Faker(locale)

    def create(self) -> UserProfile:
        # Site rule: username is 4-20 alphanumeric chars (no underscore/symbols)
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f"sim{suffix}"
        email = f"{username}@{self._config.email_domain}"
        password = self._generate_password(self._config.password_length)

        return UserProfile(
            email=email,
            username=username,
            password=password,
            referral_code=self._config.referral_code,
        )

    @staticmethod
    def sanitize_username(username: str) -> str:
        """Strip characters the site rejects (only alphanumeric allowed)."""
        cleaned = "".join(ch for ch in username if ch.isalnum())
        return cleaned[:20]

    @staticmethod
    def _generate_password(length: int) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        while True:
            password = "".join(random.choices(alphabet, k=length))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
            ):
                return password
