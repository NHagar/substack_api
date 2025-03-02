from typing import Any, Dict, List

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class User:
    """
    User class for interacting with Substack user profiles
    """

    def __init__(self, username: str) -> None:
        """
        Initialize a User object.

        Parameters
        ----------
        username : str
            The Substack username
        """
        self.username = username
        self.endpoint = f"https://substack.com/api/v1/user/{username}/public_profile"
        self._user_data = None  # Cache for user data

    def __str__(self) -> str:
        return f"User: {self.username}"

    def __repr__(self) -> str:
        return f"User(username={self.username})"

    def _fetch_user_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch the raw user data from the API and cache it

        Parameters
        ----------
        force_refresh : bool
            Whether to force a refresh of the data, ignoring the cache

        Returns
        -------
        Dict[str, Any]
            Full user profile data
        """
        if self._user_data is not None and not force_refresh:
            return self._user_data

        r = requests.get(self.endpoint, headers=HEADERS, timeout=30)
        r.raise_for_status()

        self._user_data = r.json()
        return self._user_data

    def get_raw_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get the complete raw user data.

        Parameters
        ----------
        force_refresh : bool
            Whether to force a refresh of the data, ignoring the cache

        Returns
        -------
        Dict[str, Any]
            Full user profile data
        """
        return self._fetch_user_data(force_refresh=force_refresh)

    @property
    def id(self) -> int:
        """
        Get the user's unique ID number

        Returns
        -------
        int
            The user's ID
        """
        data = self._fetch_user_data()
        return data["id"]

    @property
    def name(self) -> str:
        """
        Get the user's name

        Returns
        -------
        str
            The user's name
        """
        data = self._fetch_user_data()
        return data["name"]

    @property
    def profile_set_up_at(self) -> str:
        """
        Get the date when the user's profile was set up

        Returns
        -------
        str
            Profile setup timestamp
        """
        data = self._fetch_user_data()
        return data["profile_set_up_at"]

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get newsletters the user has subscribed to

        Returns
        -------
        List[Dict[str, Any]]
            List of publications the user subscribes to with domain info
        """
        data = self._fetch_user_data()
        subscriptions = []

        for sub in data["subscriptions"]:
            pub = sub["publication"]
            domain = pub.get("custom_domain") or f"{pub['subdomain']}.substack.com"
            subscriptions.append(
                {
                    "publication_id": pub["id"],
                    "publication_name": pub["name"],
                    "domain": domain,
                    "membership_state": sub["membership_state"],
                }
            )

        return subscriptions
