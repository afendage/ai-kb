from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProfile:
    email: str
    username: str
    password: str
    referral_code: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        
        # Sanitize username: only alphanumeric characters are allowed (no underscores, spaces, etc.)
        sanitized = "".join(ch for ch in self.username if ch.isalnum())[:20]
        if sanitized != self.username:
            import logging
            logging.getLogger(__name__).warning(
                "Username %r contains invalid characters (e.g. underscores). Sanitized to %r",
                self.username, sanitized
            )
            self.username = sanitized


@dataclass
class RegistrationResult:
    success: bool
    user: UserProfile
    message: str = ""
    screenshot_path: str | None = None
