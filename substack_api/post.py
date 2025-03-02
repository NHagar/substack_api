from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class Post:
    """
    A class to represent a Substack post.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize a Post object.

        Parameters
        ----------
        url : str
            The URL of the Substack post
        """
        self.url = url
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

        r = requests.get(self.endpoint, headers=HEADERS, timeout=30)
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
        return data.get("body_html")
