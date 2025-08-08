# tests/test_user_redirects.py

from unittest.mock import Mock

import pytest
import requests

from substack_api import User


class TestUserWithRedirects:
    """Test User class with redirect handling."""

    def test_fetch_user_data_no_redirect_found(self, mock_get):
        """Test when no redirect is found (user truly deleted)."""
        # Mock 404 response
        mock_get.return_value.status_code = 404

        user = User("deleteduser", follow_redirects=True)

        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        mock_get.assert_any_call(
            "https://substack.com/api/v1/user/deleteduser/public_profile", timeout=30
        )
        assert user.username == "deleteduser"  # Username unchanged

    def test_fetch_user_data_dont_follow_redirects(self, mock_get):
        """Test when no redirect is found (user truly deleted)."""
        # Mock 404 response
        mock_get.return_value.status_code = 404

        user = User("deleteduser", follow_redirects=False)

        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        mock_get.assert_any_call(
            "https://substack.com/api/v1/user/deleteduser/public_profile", timeout=30
        )
        assert user.username == "deleteduser"  # Username unchanged

    def test_fetch_user_data_redirect(self, mock_get):
        """Test when redirect is found."""
        mock_get.return_value.status_code = 404
        good_response = Mock()
        good_response.status_code = 200
        good_response.url = "https://substack.com/@newhandle"
        mock_get.side_effect = [mock_get.return_value, good_response, good_response]

        user = User("oldhandle", follow_redirects=True)

        user._fetch_user_data()

        assert user.username == "newhandle"  # Username was updated
        assert user.was_redirected
        assert mock_get.call_count == 3

    def test_fetch_user_data_redirect_to_the_same(self, mock_get):
        """Test when redirect is found."""
        mock_get.return_value.status_code = 404
        good_response = Mock()
        good_response.status_code = 200
        good_response.url = "https://substack.com/@oldhandle"
        mock_get.side_effect = [mock_get.return_value, good_response, good_response]

        user = User("oldhandle", follow_redirects=True)

        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

    def test_fetch_user_data_redirect_wrong_reply(self, mock_get):
        """Test when redirect is found."""
        mock_get.return_value.status_code = 404
        wrong_reply = Mock()
        wrong_reply.status_code = 200
        wrong_reply.url = "https://substack.com/error"
        mock_get.side_effect = [mock_get.return_value, wrong_reply]

        user = User("oldhandle", follow_redirects=True)
        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        assert user.username == "oldhandle"  # Username was updated
        assert not user.was_redirected

    def test_fetch_user_data_redirect_still_404(self, mock_get):
        """Test when redirect is found but new handle also returns 404."""
        # Both calls return 404
        mock_get.return_value.status_code = 404
        good_response = Mock()
        good_response.status_code = 200
        good_response.url = "https://substack.com/@newhandle"
        mock_get.side_effect = [
            mock_get.return_value,
            good_response,
            mock_get.return_value,
        ]

        user = User("oldhandle", follow_redirects=True)
        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        assert user.username == "newhandle"  # Username was not updated
        assert user.was_redirected

    def test_fetch_user_data_redirect_all_404(self, mock_get):
        """Test when redirect is found but all calls returns 404."""
        # Both calls return 404
        mock_get.return_value.status_code = 404
        mock_get.side_effect = [mock_get.return_value, requests.RequestException]

        user = User("oldhandle", follow_redirects=True)
        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        assert user.username == "oldhandle"  # Username was not updated
        assert not user.was_redirected
