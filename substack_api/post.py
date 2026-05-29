from typing import Any, Dict, Optional
from urllib.parse import urlparse

import time
import random
import requests

from substack_api.auth import SubstackAuth

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class Post:
    """
    A class to represent a Substack post.
    """

    def __init__(self, url: str, auth: Optional[SubstackAuth] = None) -> None:
        """
        Initialize a Post object.

        Parameters
        ----------
        url : str
            The URL of the Substack post
        auth : Optional[SubstackAuth]
            Authentication handler for accessing paywalled content
        """
        self.url = url
        self.auth = auth
        parsed_url = urlparse(url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_parts = parsed_url.path.strip("/").split("/")
        # The slug is typically the last part of the path in Substack URLs
        self.slug = path_parts[-1] if path_parts else None

        self.endpoint = f"{self.base_url}/api/v1/posts/{self.slug}"
        self._post_data = None  # Cache for post data

    def __str__(self) -> str:
        return f"Post: {self.url}"

    def __repr__(self) -> str:
        return f"Post(url={self.url})"

    def _fetch_post_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch the raw post data from the API and cache it

        Parameters
        ----------
        force_refresh : bool
            Whether to force a refresh of the data, ignoring the cache

        Returns
        -------
        Dict[str, Any]
            Full post metadata
        """
        if self._post_data is not None and not force_refresh:
            return self._post_data

        def _parse_retry_after_seconds(response: Optional[requests.Response]) -> Optional[float]:
            if response is None:
                return None
            ra = response.headers.get("Retry-After")
            if not ra:
                return None
            try:
                return float(ra)
            except ValueError:
                return None

        max_retries = 8
        base_delay = 1.0
        max_delay = 120.0
        jitter = 0.3

        last_http_error: Optional[requests.HTTPError] = None

        for attempt in range(max_retries + 1):
            # Use authenticated session if available
            if self.auth and self.auth.authenticated:
                r = self.auth.get(self.endpoint, timeout=30)
            else:
                r = requests.get(self.endpoint, headers=HEADERS, timeout=30)

            try:
                r.raise_for_status()
                self._post_data = r.json()
                return self._post_data
            except requests.HTTPError as e:
                last_http_error = e
                status = getattr(r, "status_code", None)

                retryable = status in (429, 500, 502, 503, 504)
                if (not retryable) or attempt >= max_retries:
                    raise

                retry_after = _parse_retry_after_seconds(r)
                if retry_after is not None:
                    delay = retry_after
                else:
                    delay = min(max_delay, base_delay * (2 ** attempt))

                # Jitter, um gleichzeitige Retries zu entzerren
                delay = delay * (1.0 + random.uniform(-jitter, jitter))
                delay = max(0.0, delay)
                time.sleep(delay)

        # Sollte praktisch nie erreicht werden, aber als Fallback:
        if last_http_error is not None:
            raise last_http_error
        raise RuntimeError("Failed to fetch post data: unknown error")

    def get_metadata(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get metadata for the post.

        Parameters
        ----------
        force_refresh : bool
            Whether to force a refresh of the data, ignoring the cache

        Returns
        -------
        Dict[str, Any]
            Full post metadata
        """
        return self._fetch_post_data(force_refresh=force_refresh)

    def get_content(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get the HTML content of the post.

        Parameters
        ----------
        force_refresh : bool
            Whether to force a refresh of the data, ignoring the cache

        Returns
        -------
        Optional[str]
            HTML content of the post, or None if not available
        """
        data = self._fetch_post_data(force_refresh=force_refresh)
        content = data.get("body_html")

        # Check if content is paywalled and we don't have auth
        if not content and data.get("audience") == "only_paid" and not self.auth:
            print(
                "Warning: This post is paywalled. Provide authentication to access full content."
            )

        return content

    def is_paywalled(self) -> bool:
        """
        Check if the post is paywalled.

        Returns
        -------
        bool
            True if post is paywalled
        """
        data = self._fetch_post_data()
        return data.get("audience") == "only_paid"
