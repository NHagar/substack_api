import re
import urllib.parse
from time import sleep
from typing import Any, Dict, List, Optional

import requests

from substack_api.auth import SubstackAuth

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


SEARCH_URL = "https://substack.com/api/v1/publication/search"

DISCOVERY_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "Accept": "application/json",
    "Origin": "https://substack.com",
    "Referer": "https://substack.com/discover",
}


def _host_from_url(url: str) -> str:
    host = urllib.parse.urlparse(
        url if "://" in url else f"https://{url}"
    ).netloc.lower()
    return host


def _match_publication(search_results: dict, host: str) -> Optional[dict]:
    # Try exact custom domain, then subdomain match
    for item in search_results.get("publications", []):
        if (
            item.get("custom_domain") and _host_from_url(item["custom_domain"]) == host
        ) or (
            item.get("subdomain")
            and f"{item['subdomain'].lower()}.substack.com" == host
        ):
            return item
    # Fallback: loose match on subdomain token
    m = re.match(r"^([a-z0-9-]+)\.substack\.com$", host)
    if m:
        sub = m.group(1)
        for item in search_results.get("publications", []):
            if item.get("subdomain", "").lower() == sub:
                return item
    return None


class Newsletter:
    """
    Newsletter class for interacting with Substack newsletters
    """

    def __init__(self, url: str, auth: Optional[SubstackAuth] = None) -> None:
        """
        Initialize a Newsletter object.

        Parameters
        ----------
        url : str
            The URL of the Substack newsletter
        auth : Optional[SubstackAuth]
            Authentication handler for accessing paywalled content
        """
        self.url = url
        self.auth = auth

    def __str__(self) -> str:
        return f"Newsletter: {self.url}"

    def __repr__(self) -> str:
        return f"Newsletter(url={self.url})"

    def _make_request(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a GET request to the specified endpoint with authentication if needed.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request
        **kwargs : Any
            Additional parameters for the request

        Returns
        -------
        requests.Response
            The response object from the request
        """
        if self.auth and self.auth.authenticated:
            resp = self.auth.get(endpoint, **kwargs)
        else:
            resp = requests.get(endpoint, headers=HEADERS, **kwargs)

        sleep(2)  # Be polite to the server
        return resp

    def _fetch_paginated_posts(
        self, params: Dict[str, str], limit: Optional[int] = None, page_size: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Helper method to fetch paginated posts with different query parameters

        Parameters
        ----------
        params : Dict[str, str]
            Dictionary of query parameters to include in the API request
        limit : Optional[int]
            Maximum number of posts to return
        page_size : int
            Number of posts to retrieve per page request

        Returns
        -------
        List[Dict[str, Any]]
            List of post data dictionaries
        """
        results = []
        offset = 0
        batch_size = page_size  # The API default limit per request
        more_items = True

        while more_items:
            # Update params with current offset and batch size
            current_params = params.copy()
            current_params.update({"offset": str(offset), "limit": str(batch_size)})

            # Format query parameters
            query_string = "&".join([f"{k}={v}" for k, v in current_params.items()])
            endpoint = f"{self.url}/api/v1/archive?{query_string}"

            # Make the request
            response = self._make_request(endpoint, timeout=30)
            response.raise_for_status()

            items = response.json()
            if not items:
                break

            results.extend(items)

            # Update offset for next batch
            offset += batch_size

            # Check if we've reached the requested limit
            if limit and len(results) >= limit:
                results = results[:limit]
                more_items = False

            # Check if we got fewer items than requested (last page)
            if len(items) < batch_size:
                more_items = False

        # Instead of creating Post objects directly, return the URLs
        # The caller will create Post objects as needed
        return results

    def get_posts(self, sorting: str = "new", limit: Optional[int] = None) -> List:
        """
        Get posts from the newsletter with specified sorting

        Parameters
        ----------
        sorting : str
            Sorting order for the posts ("new", "top", "pinned", or "community")
        limit : Optional[int]
            Maximum number of posts to return

        Returns
        -------
        List[Post]
            List of Post objects
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": sorting}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"], auth=self.auth) for item in post_data]

    def search_posts(self, query: str, limit: Optional[int] = None) -> List:
        """
        Search posts in the newsletter with the given query

        Parameters
        ----------
        query : str
            Search query string
        limit : Optional[int]
            Maximum number of posts to return

        Returns
        -------
        List[Post]
            List of Post objects matching the search query
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": "new", "search": query}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"], auth=self.auth) for item in post_data]

    def get_podcasts(self, limit: Optional[int] = None) -> List:
        """
        Get podcast posts from the newsletter

        Parameters
        ----------
        limit : Optional[int]
            Maximum number of podcast posts to return

        Returns
        -------
        List[Post]
            List of Post objects representing podcast posts
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": "new", "type": "podcast"}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"], auth=self.auth) for item in post_data]

    def _resolve_publication_id(self) -> Optional[int]:
        """Resolve publication_id via Substack discovery search—no posts needed."""
        host = _host_from_url(self.url)
        q = host.split(":")[0]  # strip port if present
        params = {
            "query": q,
            "page": 0,
            "limit": 25,
            "skipExplanation": "true",
            "sort": "relevance",
        }
        r = requests.get(
            SEARCH_URL, headers=DISCOVERY_HEADERS, params=params, timeout=30
        )
        r.raise_for_status()
        match = _match_publication(r.json(), host)
        return match.get("id") if match else None

    def get_recommendations(self) -> List["Newsletter"]:
        """
        Get recommended publications without relying on the latest post.
        """
        publication_id = self._resolve_publication_id()
        if not publication_id:
            # graceful fallback to your existing (post-derived) path
            try:
                posts = self.get_posts(limit=1)
                publication_id = (
                    posts[0].get_metadata()["publication_id"] if posts else None
                )
            except Exception:
                publication_id = None
        if not publication_id:
            return []

        endpoint = f"{self.url}/api/v1/recommendations/from/{publication_id}"
        response = self._make_request(endpoint, timeout=30)
        response.raise_for_status()
        recommendations = response.json() or []

        urls = []
        for rec in recommendations:
            pub = rec.get("recommendedPublication", {})
            if pub.get("custom_domain"):
                urls.append(pub["custom_domain"])
            elif pub.get("subdomain"):
                urls.append(f"{pub['subdomain']}.substack.com")

        from .newsletter import Newsletter  # avoid circular import

        return [Newsletter(u, auth=self.auth) for u in urls]

    def get_authors(self) -> List:
        """
        Get authors of the newsletter

        Returns
        -------
        List[User]
            List of User objects representing the authors
        """
        from .user import User  # Import here to avoid circular import

        endpoint = f"{self.url}/api/v1/publication/users/ranked?public=true"
        r = self._make_request(endpoint, timeout=30)
        r.raise_for_status()
        authors = r.json()
        return [User(author["handle"]) for author in authors]
