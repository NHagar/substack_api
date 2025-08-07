import json
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest
import requests

from substack_api import Newsletter, Post, SubstackAuth


@pytest.fixture
def temp_cookies_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary file for cookies storage."""
    temp_path = tmp_path / "cookies.json"
    temp_path.write_bytes(b"[]")
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def mock_cookies():
    """Mock cookies data."""
    return {
        "substack.sid": {
            "value": "test_session_id",
            "domain": ".substack.com",
            "path": "/",
            "secure": True,
            "expires": None,
        },
        "substack.lli": {
            "value": "test_lli_value",
            "domain": ".substack.com",
            "path": "/",
            "secure": True,
            "expires": None,
        },
    }


@pytest.fixture
def mock_selenium_cookies():
    """Mock cookies returned by Selenium."""
    return [
        {
            "name": "substack.sid",
            "value": "test_session_id",
            "domain": ".substack.com",
            "path": "/",
            "secure": True,
        },
        {
            "name": "substack.lli",
            "value": "test_lli_value",
            "domain": ".substack.com",
            "path": "/",
            "secure": True,
        },
    ]


class TestSubstackAuth:
    """Test cases for SubstackAuth class."""

    def test_init_without_credentials(self, temp_cookies_file):
        """Test initialization without credentials."""
        auth = SubstackAuth(cookies_path=temp_cookies_file)

        assert auth.cookies_path == temp_cookies_file
        assert auth.authenticated
        assert isinstance(auth, requests.Session)

    def test_init_with_existing_cookies(self, temp_cookies_file, mock_cookies):
        """Test initialization with existing cookies file."""
        # Write cookies to file
        with open(temp_cookies_file, "w") as f:
            json.dump(mock_cookies, f)

        with patch.object(SubstackAuth, "load_cookies") as mock_load:
            _ = SubstackAuth(cookies_path=temp_cookies_file)
            mock_load.assert_called_once()

    def test_load_cookies_file_not_found(self, temp_cookies_file):
        """Test loading cookies when file doesn't exist."""
        auth = SubstackAuth(cookies_path=temp_cookies_file / ".nonexistent")
        result = auth.load_cookies()

        assert result is False
        assert not auth.authenticated

    def test_get_request(self, temp_cookies_file, mock_cookies):
        """Test authenticated GET request."""
        # Write cookies to file
        with open(temp_cookies_file, "w") as f:
            json.dump(mock_cookies, f)
        auth = SubstackAuth(cookies_path=temp_cookies_file)
        auth.authenticated = True

        mock_response = Mock()

        with patch.object(auth, "get", return_value=mock_response) as mock_get:
            result = auth.get("https://example.com/api", timeout=30)

            assert result == mock_response
            mock_get.assert_called_once_with("https://example.com/api", timeout=30)

    def test_post_request(self, temp_cookies_file, mock_cookies):
        """Test authenticated POST request."""
        # Write cookies to file
        with open(temp_cookies_file, "w") as f:
            json.dump(mock_cookies, f)
        auth = SubstackAuth(cookies_path=temp_cookies_file)
        auth.authenticated = True

        mock_response = Mock()
        data = {"key": "value"}

        with patch.object(auth, "post", return_value=mock_response) as mock_post:
            result = auth.post("https://example.com/api", json=data)

            assert result == mock_response
            mock_post.assert_called_once_with("https://example.com/api", json=data)

    def test_session_headers(self, temp_cookies_file, mock_cookies):
        """Test that session has proper default headers."""
        # Write cookies to file
        with open(temp_cookies_file, "w") as f:
            json.dump(mock_cookies, f)
        auth = SubstackAuth(cookies_path=temp_cookies_file)

        assert "User-Agent" in auth.headers
        assert auth.headers["Accept"] == "application/json"
        assert auth.headers["Content-Type"] == "application/json"


# Integration tests with Post and Newsletter classes
class TestAuthIntegration:
    """Test authentication integration with Post and Newsletter classes."""

    @patch("substack_api.auth.SubstackAuth.get")
    def test_post_without_auth(self, mock_get):
        """Test Post class without authentication uses regular requests."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 123,
            "body_html": None,
            "audience": "only_paid",
        }
        mock_get.return_value = mock_response

        post = Post("https://test.substack.com/p/test-post")
        content = post.get_content()

        # Should use regular requests.get
        mock_get.assert_called_once()
        assert content is None

    def test_post_with_auth(self, temp_cookies_file, mock_cookies):
        """Test Post class with authentication uses auth session."""
        # Write cookies to file
        with open(temp_cookies_file, "w") as f:
            json.dump(mock_cookies, f)
        auth = SubstackAuth(cookies_path=temp_cookies_file)

        auth.authenticated = True

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 123,
            "body_html": "<p>Paywalled content</p>",
            "audience": "only_paid",
        }

        with patch.object(auth, "get", return_value=mock_response) as mock_auth_get:
            post = Post("https://test.substack.com/p/test-post", auth=auth)
            content = post.get_content()

            # Should use auth.get instead of requests.get
            mock_auth_get.assert_called_once()
            assert content == "<p>Paywalled content</p>"

    def test_post_is_paywalled(self):
        """Test is_paywalled method."""

        post = Post("https://test.substack.com/p/test-post")

        # Mock paywalled post
        with patch.object(
            post, "_fetch_post_data", return_value={"audience": "only_paid"}
        ):
            assert post.is_paywalled() is True

        # Mock public post
        with patch.object(
            post, "_fetch_post_data", return_value={"audience": "everyone"}
        ):
            assert post.is_paywalled() is False

    @patch("substack_api.auth.SubstackAuth.get")
    def test_newsletter_with_auth_passes_to_posts(
        self, mock_get, temp_cookies_file, mock_cookies
    ):
        """Test Newsletter passes auth to Post objects."""
        newsletter = Newsletter("https://test.substack.com")

        mock_get.return_value.json.return_value = [
            {"canonical_url": "https://test.substack.com/p/post1"},
            {"canonical_url": "https://test.substack.com/p/post2"},
        ]

        posts = newsletter.get_posts(limit=2)

        # Verify auth was passed to Post objects
        assert len(posts) == 2
        assert all(isinstance(p, Post) for p in posts)
        assert all(p.auth == newsletter.auth for p in posts)
