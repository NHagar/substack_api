from time import sleep
from typing import Dict, List, Optional

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class Newsletter:
    """
    Newsletter class for interacting with Substack newsletters
    """

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"Newsletter: {self.url}"

    def __repr__(self):
        return f"Newsletter(url={self.url})"

    def _fetch_paginated_posts(
        self, params: Dict[str, str], limit: Optional[int] = None, page_size: int = 15
    ) -> List[dict]:
        """
        Helper method to fetch paginated posts with different query parameters

        Args:
            params: Dictionary of query parameters to include in the API request
            limit: Maximum number of posts to return

        Returns:
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
            response = requests.get(endpoint, headers=HEADERS)

            if response.status_code != 200:
                break

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

            # Be nice to the API
            sleep(0.5)

        # Instead of creating Post objects directly, return the URLs
        # The caller will create Post objects as needed
        return results

    def get_posts(self, sorting: str = "new", limit: int = None) -> List:
        """
        Get posts from the newsletter with specified sorting

        Returns:
            List of Post objects
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": sorting}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"]) for item in post_data]

    def search_posts(self, query: str, limit: int = None) -> List:
        """
        Search posts in the newsletter with the given query

        Returns:
            List of Post objects
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": "new", "search": query}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"]) for item in post_data]

    def get_podcasts(self, limit: int = None) -> List:
        """
        Get podcast posts from the newsletter

        Returns:
            List of Post objects
        """
        from .post import Post  # Import here to avoid circular import

        params = {"sort": "new", "type": "podcast"}
        post_data = self._fetch_paginated_posts(params, limit)
        return [Post(item["canonical_url"]) for item in post_data]

    def get_recommendations(self):
        """
        Get recommended publications for this newsletter

        Returns:
            List of Newsletter objects
        """
        # First get any post to extract the publication ID
        posts = self.get_posts(limit=1)
        if not posts:
            return []

        publication_id = posts[0].get_metadata()["publication_id"]

        # Now get the recommendations
        endpoint = f"{self.url}/api/v1/recommendations/from/{publication_id}"
        response = requests.get(endpoint, headers=HEADERS)

        if response.status_code != 200:
            return []

        recommendations = response.json()
        if not recommendations:
            return []

        recommended_newsletter_urls = [
            rec["custom_domain"]
            if rec["custom_domain"]
            else f"{rec['subdomain']}.substack.com"
            for rec in recommendations
        ]

        # Avoid circular import
        from .newsletter import Newsletter

        result = [Newsletter(url) for url in recommended_newsletter_urls]

        return result

    def get_authors(self):
        """
        Get authors of the newsletter

        Returns:
            List of User objects
        """
        from .user import User  # Import here to avoid circular import

        r = requests.get(f"{self.url}/api/v1/publication/users/ranked?public=true")
        authors = r.json()
        return [User(author["handle"]) for author in authors]
