from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.yaml"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw else default


@dataclass
class SiteConfig:
    base_url: str
    locale: str
    register_path: str
    login_path: str

    @property
    def register_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.register_path}"

    @property
    def home_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.locale}/"


@dataclass
class BrowserConfig:
    name: str
    headless: bool
    window_size: str
    implicit_wait: int
    page_load_timeout: int


@dataclass
class RegistrationConfig:
    email_domain: str
    password_length: int
    referral_code: str


@dataclass
class BehaviorConfig:
    duration_sec: int
    action_delay_min: float
    action_delay_max: float
    scroll_steps: int
    enable_random_clicks: bool


@dataclass
class AppConfig:
    site: SiteConfig
    browser: BrowserConfig
    registration: RegistrationConfig
    behavior: BehaviorConfig
    selectors: dict[str, Any] = field(default_factory=dict)


def load_config(config_path: Path | None = None) -> AppConfig:
    load_dotenv(ROOT_DIR / ".env")
    path = config_path or DEFAULT_CONFIG_PATH
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    site_raw = raw.get("site", {})
    browser_raw = raw.get("browser", {})
    registration_raw = raw.get("registration", {})
    behavior_raw = raw.get("behavior", {})

    return AppConfig(
        site=SiteConfig(
            base_url=os.getenv("BASE_URL", site_raw.get("base_url", "")),
            locale=os.getenv("LOCALE", site_raw.get("locale", "en")),
            register_path=site_raw.get("register_path", "/en/?modal=register&tab=account"),
            login_path=site_raw.get("login_path", "/en/?modal=login"),
        ),
        browser=BrowserConfig(
            name=os.getenv("BROWSER", browser_raw.get("name", "chrome")),
            headless=_env_bool("HEADLESS", browser_raw.get("headless", False)),
            window_size=browser_raw.get("window_size", "1920,1080"),
            implicit_wait=_env_int("IMPLICIT_WAIT", browser_raw.get("implicit_wait", 10)),
            page_load_timeout=_env_int(
                "PAGE_LOAD_TIMEOUT", browser_raw.get("page_load_timeout", 60)
            ),
        ),
        registration=RegistrationConfig(
            email_domain=registration_raw.get("email_domain", "gmail.com"),
            password_length=registration_raw.get("password_length", 12),
            referral_code=os.getenv("REFERRAL_CODE", registration_raw.get("referral_code", "")),
        ),
        behavior=BehaviorConfig(
            duration_sec=_env_int("SIMULATION_DURATION_SEC", behavior_raw.get("duration_sec", 60)),
            action_delay_min=_env_float(
                "ACTION_DELAY_MIN", behavior_raw.get("action_delay_min", 1.0)
            ),
            action_delay_max=_env_float(
                "ACTION_DELAY_MAX", behavior_raw.get("action_delay_max", 3.0)
            ),
            scroll_steps=behavior_raw.get("scroll_steps", 3),
            enable_random_clicks=behavior_raw.get("enable_random_clicks", True),
        ),
        selectors=raw.get("selectors", {}),
    )
