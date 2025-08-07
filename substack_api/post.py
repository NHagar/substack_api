from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from logprise import logger

from .auth import SubstackAuth


@dataclass
class Post:
    """
    A class to represent a Substack post.
    """

    url: str
    auth: SubstackAuth = field(default_factory=SubstackAuth, repr=False)

    def __post_init__(self):
        parsed_url = urlparse(self.url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_parts = parsed_url.path.strip("/").split("/")
        # The slug is typically the last part of the path in Substack URLs
        self.slug = path_parts[-1] if path_parts else None

        self.endpoint = f"{self.base_url}/api/v1/posts/{self.slug}"
        self._post_data = None  # Cache for post data

    def __str__(self) -> str:
        return f"Post: {self.url}"

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

        # Use authenticated session if available
        r = self.auth.get(self.endpoint, timeout=30)
        r.raise_for_status()

        self._post_data = r.json()
        return self._post_data

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
            logger.warning(
                "This post is paywalled. Provide authentication to access full content."
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
