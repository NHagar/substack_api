"""
Substack Chat module for accessing publication subscriber chats.

This module provides classes for interacting with Substack's community chat features,
including reading threads and messages from publication chats.
"""

import requests
from typing import Any, Dict, List, Optional, Union

from substack_api.auth import SubstackAuth

BASE_URL = "https://substack.com/api/v1"
SEARCH_URL = "https://substack.com/api/v1/publication/search"
_DISCOVERY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://substack.com",
    "Referer": "https://substack.com/discover",
}


def _resolve_subdomain_to_id(subdomain: str) -> Optional[int]:
    """Resolve a publication subdomain to its numeric ID.

    Tries the Substack search API first; if that yields no match, falls back to
    fetching a single post from the publication's own API and reading the
    publication_id field from the response.
    """
    params = {
        "query": f"{subdomain}.substack.com",
        "page": 0,
        "limit": 25,
        "skipExplanation": "true",
        "sort": "relevance",
    }
    r = requests.get(SEARCH_URL, headers=_DISCOVERY_HEADERS, params=params, timeout=30)
    r.raise_for_status()
    for item in r.json().get("publications", []):
        if item.get("subdomain", "").lower() == subdomain.lower():
            return item.get("id")

    # Fall back to the publication's own posts endpoint
    r = requests.get(
        f"https://{subdomain}.substack.com/api/v1/posts",
        headers=_DISCOVERY_HEADERS,
        params={"limit": 1},
        timeout=30,
    )
    if r.status_code == 200:
        posts = r.json()
        if posts and isinstance(posts, list):
            return posts[0].get("publication_id")
    return None


# Exceptions
class ChatError(Exception):
    """Base exception for chat-related errors."""

    pass


class ChatAuthenticationRequired(ChatError):
    """Raised when authentication is required to access a chat."""

    pass


class ChatAccessDenied(ChatError):
    """Raised when the user does not have permission to access a chat."""

    pass


class ChatPaymentRequired(ChatAccessDenied):
    """Raised when chat access requires a paid subscription or a higher subscription tier."""

    pass


class ChatNotFound(ChatError):
    """Raised when the specified chat/publication is not found."""

    pass


class ThreadNotFound(ChatError):
    """Raised when the specified thread is not found."""

    pass


class ChatMessage:
    """
    Represents a message/reply in a chat thread.

    This is a lightweight wrapper around the message data dictionary
    returned from the Substack API.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize a ChatMessage.

        Parameters
        ----------
        data : Dict[str, Any]
            The raw message data from the API, containing 'comment' and 'user' keys.
        """
        self._data = data

    def __str__(self) -> str:
        return f"ChatMessage(id={self.id})"

    def __repr__(self) -> str:
        return f"ChatMessage(id={self.id}, author={self.author.get('name', 'Unknown')})"

    @property
    def id(self) -> str:
        """The unique identifier (UUID) for this message."""
        return self._data["comment"]["id"]

    @property
    def body(self) -> str:
        """The text content of the message."""
        return self._data["comment"]["body"]

    @property
    def author(self) -> Dict[str, Any]:
        """
        The author information dictionary.

        Contains keys like 'id', 'name', 'handle', 'photo_url'.
        """
        return self._data.get("user", {})

    @property
    def created_at(self) -> str:
        """The ISO timestamp when the message was created."""
        return self._data["comment"]["created_at"]

    @property
    def media_attachments(self) -> List[Dict[str, Any]]:
        """List of media attachments (images, etc.) in the message."""
        return self._data["comment"].get("mediaAttachments", [])

    @property
    def reaction_count(self) -> int:
        """The number of reactions on this message."""
        return self._data["comment"].get("reaction_count", 0)

    @property
    def raw_data(self) -> Dict[str, Any]:
        """The complete raw data dictionary from the API."""
        return self._data


class ChatThread:
    """
    Represents a thread within a publication chat.

    A thread is a top-level post in the chat that can contain multiple
    message replies.
    """

    def __init__(
        self,
        publication_id: Union[str, int],
        thread_id: str,
        auth: SubstackAuth,
        _data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a ChatThread.

        Parameters
        ----------
        publication_id : Union[str, int]
            The publication ID this thread belongs to.
        thread_id : str
            The unique identifier (UUID) for this thread.
        auth : SubstackAuth
            Authentication handler for API requests.
        _data : Optional[Dict[str, Any]]
            Pre-fetched thread data (for internal use).
        """
        self.publication_id = (
            int(publication_id) if isinstance(publication_id, str) else publication_id
        )
        self.thread_id = thread_id
        self.auth = auth
        self._thread_data = _data
        self._messages_data: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return f"ChatThread(id={self.thread_id})"

    def __repr__(self) -> str:
        return f"ChatThread(publication_id={self.publication_id}, thread_id={self.thread_id})"

    def _fetch_thread_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch thread data including messages from the API.

        Parameters
        ----------
        force_refresh : bool
            If True, fetch fresh data even if cached data exists.

        Returns
        -------
        Dict[str, Any]
            The full thread data including replies.

        Raises
        ------
        ChatAuthenticationRequired
            If authentication is required.
        ThreadNotFound
            If the thread is not found.
        ChatAccessDenied
            If access to the thread is denied.
        """
        if self._messages_data is not None and not force_refresh:
            return self._messages_data

        if not self.auth or not self.auth.authenticated:
            raise ChatAuthenticationRequired(
                "Authentication is required to access chat threads."
            )

        url = f"{BASE_URL}/community/posts/{self.thread_id}/comments"
        params = {"order": "asc", "initial": "true"}

        response = self.auth.get(url, params=params, timeout=30)

        if response.status_code == 401:
            raise ChatAuthenticationRequired(
                "Authentication is required to access this thread."
            )
        elif response.status_code == 402:
            raise ChatPaymentRequired(
                "Access to this thread requires a paid subscription or a higher subscription tier."
            )
        elif response.status_code == 403:
            raise ChatAccessDenied(
                "You do not have permission to access this thread."
            )
        elif response.status_code == 404:
            raise ThreadNotFound(f"Thread with ID '{self.thread_id}' was not found.")

        response.raise_for_status()
        data = response.json()

        if "post" in data and self._thread_data is None:
            self._thread_data = data["post"]

        # Paginate backwards (older messages not included in the initial window)
        all_replies = list(data.get("replies", []))
        while data.get("moreBefore") and all_replies:
            r = self.auth.get(
                url,
                params={"order": "asc", "before_id": all_replies[0]["comment"]["id"]},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            all_replies = data.get("replies", []) + all_replies

        # Paginate forwards (in case the initial window is not at the latest end)
        data = response.json()
        while data.get("moreAfter") and all_replies:
            r = self.auth.get(
                url,
                params={"order": "asc", "after_id": all_replies[-1]["comment"]["id"]},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            all_replies = all_replies + data.get("replies", [])

        self._messages_data = response.json()
        self._messages_data["replies"] = all_replies

        return self._messages_data

    @property
    def id(self) -> str:
        """The unique identifier (UUID) for this thread."""
        return self.thread_id

    @property
    def body(self) -> str:
        """The text content of the thread's original post."""
        if self._thread_data:
            return self._thread_data.get("communityPost", {}).get("body", "")
        # Fetch if needed
        self._fetch_thread_data()
        if self._thread_data:
            return self._thread_data.get("communityPost", {}).get("body", "")
        return ""

    @property
    def author(self) -> Dict[str, Any]:
        """
        The author information dictionary.

        Contains keys like 'id', 'name', 'handle', 'photo_url'.
        """
        if self._thread_data:
            return self._thread_data.get("user", {})
        return {}

    @property
    def created_at(self) -> str:
        """The ISO timestamp when the thread was created."""
        if self._thread_data:
            return self._thread_data.get("communityPost", {}).get("created_at", "")
        return ""

    @property
    def comment_count(self) -> int:
        """The number of replies/comments in this thread."""
        if self._thread_data:
            return self._thread_data.get("communityPost", {}).get("comment_count", 0)
        return 0

    @property
    def raw_data(self) -> Optional[Dict[str, Any]]:
        """The raw thread data dictionary from the API."""
        return self._thread_data

    def get_messages(
        self, limit: Optional[int] = None, force_refresh: bool = False
    ) -> List[ChatMessage]:
        """
        Get all messages/replies in this thread.

        Parameters
        ----------
        limit : Optional[int]
            Client-side truncation of the first page of results returned by the
            API. The full page is always fetched; this just slices the list.
            If None, returns all messages from the page.
        force_refresh : bool
            If True, fetch fresh data from the API.

        Returns
        -------
        List[ChatMessage]
            List of ChatMessage objects.

        Raises
        ------
        ChatAuthenticationRequired
            If authentication is required.
        ThreadNotFound
            If the thread is not found.
        """
        data = self._fetch_thread_data(force_refresh=force_refresh)
        messages = [ChatMessage(reply) for reply in data.get("replies", [])]

        if limit is not None:
            return messages[:limit]
        return messages


class Chat:
    """
    Represents a publication's community chat.

    Use this class to access threads and messages in a Substack publication's
    subscriber chat.
    """

    def __init__(
        self,
        publication_id: Union[str, int],
        auth: SubstackAuth,
    ) -> None:
        """
        Initialize a Chat.

        Parameters
        ----------
        publication_id : Union[str, int]
            The numeric publication ID, or a subdomain string (e.g. ``"platformer"``
            for ``platformer.substack.com``). If a non-numeric string is given it is
            resolved to a numeric ID via the Substack search API.
        auth : SubstackAuth
            Authentication handler for API requests.

        Raises
        ------
        ValueError
            If a subdomain string is given but cannot be resolved to a publication ID.
        """
        if isinstance(publication_id, str):
            try:
                self._publication_id = int(publication_id)
            except ValueError:
                resolved = _resolve_subdomain_to_id(publication_id)
                if resolved is None:
                    raise ValueError(
                        f"Could not resolve subdomain '{publication_id}' to a publication ID."
                    )
                self._publication_id = resolved
        else:
            self._publication_id = publication_id
        self.auth = auth
        self._threads_data: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return f"Chat(publication_id={self._publication_id})"

    def __repr__(self) -> str:
        return f"Chat(publication_id={self._publication_id})"

    @property
    def publication_id(self) -> int:
        """The publication ID for this chat."""
        return self._publication_id

    def _fetch_threads_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch threads data from the API.

        Parameters
        ----------
        force_refresh : bool
            If True, fetch fresh data even if cached data exists.

        Returns
        -------
        Dict[str, Any]
            The threads data from the API.

        Raises
        ------
        ChatAuthenticationRequired
            If authentication is required.
        ChatNotFound
            If the publication is not found.
        ChatAccessDenied
            If access to the chat is denied.
        """
        if self._threads_data is not None and not force_refresh:
            return self._threads_data

        if not self.auth or not self.auth.authenticated:
            raise ChatAuthenticationRequired(
                "Authentication is required to access publication chats."
            )

        url = f"{BASE_URL}/community/publications/{self._publication_id}/posts"

        response = self.auth.get(url, timeout=30)

        if response.status_code == 401:
            raise ChatAuthenticationRequired(
                "Authentication is required to access this chat."
            )
        elif response.status_code == 402:
            raise ChatPaymentRequired(
                "Access to this chat requires a paid subscription or a higher subscription tier."
            )
        elif response.status_code == 403:
            raise ChatAccessDenied(
                "You do not have permission to access this publication's chat."
            )
        elif response.status_code == 404:
            raise ChatNotFound(
                f"Publication with ID '{self._publication_id}' was not found."
            )

        response.raise_for_status()
        self._threads_data = response.json()
        return self._threads_data

    def get_threads(
        self, limit: Optional[int] = None, force_refresh: bool = False
    ) -> List[ChatThread]:
        """
        Get threads from the publication chat.

        Parameters
        ----------
        limit : Optional[int]
            Client-side truncation of the first page of results returned by the
            API. The full page is always fetched; this just slices the list.
            If None, returns all threads from the page.
        force_refresh : bool
            If True, fetch fresh data from the API.

        Returns
        -------
        List[ChatThread]
            List of ChatThread objects.

        Raises
        ------
        ChatAuthenticationRequired
            If authentication is required.
        ChatNotFound
            If the publication is not found.
        """
        data = self._fetch_threads_data(force_refresh=force_refresh)
        threads = [
            ChatThread(
                publication_id=self._publication_id,
                thread_id=t["communityPost"]["id"],
                auth=self.auth,
                _data=t,
            )
            for t in data.get("threads", [])
        ]

        if limit is not None:
            return threads[:limit]
        return threads

    def get_thread(self, thread_id: str) -> ChatThread:
        """
        Get a specific thread by its ID.

        Parameters
        ----------
        thread_id : str
            The UUID of the thread to retrieve.

        Returns
        -------
        ChatThread
            The ChatThread object for the specified thread.

        Notes
        -----
        This creates a ChatThread object without pre-fetched data.
        The thread data will be fetched when properties are accessed.
        """
        return ChatThread(
            publication_id=self._publication_id,
            thread_id=thread_id,
            auth=self.auth,
        )
