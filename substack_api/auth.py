import json
from pathlib import Path

import requests
from logprise import logger

from .constants import DEFAULT_HEADERS


class SubstackAuth(requests.Session):
    """Handles authentication for Substack API requests."""

    def __init__(
        self,
        cookies_path: str | Path | None = None,
    ):
        """
        Initialize authentication handler.

        Parameters
        ----------
        cookies_path : str, optional
            Path to retrieve session cookies from
        """
        super().__init__()

        self.cookies_path = Path(cookies_path) if cookies_path else None
        self.verify = False

        # Set default headers
        self.headers.update(DEFAULT_HEADERS)
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = "application/json"

        # Try to load existing cookies
        self.authenticated = self.load_cookies()

    def load_cookies(self) -> bool:
        """
        Load cookies from file.

        Returns
        -------
        bool
            True if cookies loaded successfully
        """
        try:
            if not self.cookies_path or not self.cookies_path.exists():
                return False

            with self.cookies_path.open("r", encoding="utf8") as f:
                cookies = json.load(f)

            for cookie in cookies:
                self.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                    secure=cookie.get("secure", False),
                )

            return True

        except Exception as e:
            self.cookies.clear()
            logger.error(f"Failed to load cookies: {e}")
            return False
