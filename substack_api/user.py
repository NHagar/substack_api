from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class User:
    """
    User class for interacting with Substack user profiles
    """

    def __init__(self, username: str):
        self.username = username

    def __str__(self):
        return f"User: {self.username}"

    def __repr__(self):
        return f"User(username={self.username})"


def get_user_id(username: str) -> int:
    """
    Get the user ID of a Substack user.

    Parameters
    ----------
    username : str
        The username of the Substack user.

    Returns
    -------
    int
        The user's unique ID number

    Raises
    ------
    requests.exceptions.HTTPError
        If the user doesn't exist or the request fails
    """
    endpoint = f"https://substack.com/api/v1/user/{username}/public_profile"
    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()  # Raise an exception for bad responses
    user_id = r.json()["id"]
    return user_id


def get_user_reads(username: str) -> List[Dict[str, str]]:
    """
    Get newsletters from the "Reads" section of a user's profile.

    Parameters
    ----------
    username : str
        The username of the Substack user.

    Returns
    -------
    List[Dict[str, str]]
        List of dictionaries containing publication information and subscription status
    """
    endpoint = f"https://substack.com/api/v1/user/{username}/public_profile"
    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()
    user_data = r.json()
    reads = [
        {
            "publication_id": i["publication"]["id"],
            "publication_name": i["publication"]["name"],
            "subscription_status": i["membership_state"],
        }
        for i in user_data["subscriptions"]
    ]
    return reads


def get_user_likes(user_id: int, limit: Optional[int] = None) -> List[Dict]:
    """
    Get liked posts from a user's profile.

    Parameters
    ----------
    user_id : int
        The user ID of the Substack user.
    limit : Optional[int]
        Optional limit for number of results to return

    Returns
    -------
    List[Dict]
        List of posts that the user has liked
    """
    params = {"types[]": "like"}
    if limit:
        params["limit"] = limit

    query_string = urlencode(params)
    endpoint = (
        f"https://substack.com/api/v1/reader/feed/profile/{user_id}?{query_string}"
    )
    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()
    likes = r.json()["items"]
    return likes


def get_user_notes(
    user_id: int, limit: Optional[int] = None, offset: Optional[int] = None
) -> List[Dict]:
    """
    Get notes and comments posted by a user.

    Parameters
    ----------
    user_id : int
        The user ID of the Substack user.
    limit : Optional[int]
        Optional limit for number of results to return
    offset : Optional[int]
        Optional offset for pagination

    Returns
    -------
    List[Dict]
        List of notes and comments by the user
    """
    params = {}
    if limit:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    query_string = urlencode(params)
    endpoint = f"https://substack.com/api/v1/reader/feed/profile/{user_id}"
    if query_string:
        endpoint += f"?{query_string}"

    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()
    notes = r.json()["items"]
    return notes


def get_user_written_posts(user_id: int) -> List[Dict[str, Any]]:
    """
    Get posts written by a user.

    Parameters
    ----------
    user_id : int
        The user ID of the Substack user.

    Returns
    -------
    List[Dict[str, Any]]
        List of posts written by the user
    """
    endpoint = f"https://substack.com/api/v1/user/{user_id}/written"
    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()
    posts = r.json()["posts"]
    return posts


def get_user_commented_posts(
    user_id: int, page: Optional[int] = None, limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get posts that a user has commented on.

    Parameters
    ----------
    user_id : int
        The user ID of the Substack user.
    page : Optional[int]
        Optional page number for pagination
    limit : Optional[int]
        Optional limit for number of results per page

    Returns
    -------
    List[Dict[str, Any]]
        List of comments made by the user
    """
    params = {}
    if page:
        params["page"] = page
    if limit:
        params["limit"] = limit

    query_string = urlencode(params)
    endpoint = f"https://substack.com/api/v1/user/{user_id}/comments"
    if query_string:
        endpoint += f"?{query_string}"

    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    r.raise_for_status()
    comments = r.json()["comments"]
    return comments
