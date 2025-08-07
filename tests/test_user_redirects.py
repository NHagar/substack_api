# tests/test_user_redirects.py

import unittest
from unittest.mock import ANY, Mock, patch

import pytest
import requests

from substack_api.user import User

#
# class TestHandleRedirects(unittest.TestCase):
#     """Test cases for handle redirect functionality."""
#
#     def test_resolve_handle_redirect_success(self, mock_get):
#         """Test successful handle redirect resolution."""
#         # Mock a successful redirect
#         mock_response = Mock()
#         mock_response.status_code = 200
#         mock_response.url = "https://substack.com/@newhandle"
#         mock_get.return_value = mock_response
#
#         result = resolve_handle_redirect("oldhandle")
#
#         assert result == "newhandle"
#         mock_get.assert_called_once_with(
#             "https://substack.com/@oldhandle",
#             headers=ANY,
#             timeout=30,
#             allow_redirects=True,
#         )
#
#     def test_resolve_handle_redirect_no_redirect(self, mock_get):
#         """Test when no redirect occurs (same handle)."""
#         # Mock no redirect
#         mock_response = Mock()
#         mock_response.status_code = 200
#         mock_response.url = "https://substack.com/@samehandle"
#         mock_get.return_value = mock_response
#
#         result = resolve_handle_redirect("samehandle")
#
#         assert result is None
#
#     def test_resolve_handle_redirect_error(self, mock_get):
#         """Test error handling in redirect resolution."""
#         # Mock network error
#         mock_get.side_effect = requests.RequestException("Network error")
#
#         result = resolve_handle_redirect("errorhandle")
#
#         assert result is None
#
#     def test_resolve_handle_redirect_404(self, mock_get):
#         """Test when profile page itself returns 404."""
#         mock_response = Mock()
#         mock_response.status_code = 404
#         mock_get.return_value = mock_response
#
#         result = resolve_handle_redirect("deletedhandle")
#
#         assert result is None


class TestUserWithRedirects:
    """Test User class with redirect handling."""
    #
    # def test_user_init_with_redirects(self):
    #     """Test User initialization with redirect support."""
    #     user = User("testuser", follow_redirects=True)
    #
    #     assert user.username == "testuser"
    #     assert user.original_username == "testuser"
    #     assert user.follow_redirects is True
    #     assert user._redirect_attempted is False
    #
    # def test_user_init_without_redirects(self):
    #     """Test User initialization without redirect support."""
    #     user = User("testuser", follow_redirects=False)
    #
    #     assert user.follow_redirects is False
    #
    # def test_fetch_user_data_no_redirect_needed(self, mock_get):
    #     """Test normal case where no redirect is needed."""
    #     # Mock successful API response
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"id": 123, "name": "Test User"}
    #     mock_get.return_value = mock_response
    #
    #     user = User("testuser")
    #     data = user._fetch_user_data()
    #
    #     assert data == {"id": 123, "name": "Test User"}
    #     assert user.username == "testuser"  # Username unchanged
    #     assert not user.was_redirected
    #     mock_get.assert_called_once()
    #
    # def test_fetch_user_data_with_redirect(self, mock_get):
    #     """Test handling of renamed user with redirect."""
    #     # First call returns 404
    #     mock_404 = Mock()
    #     mock_404.status_code = 404
    #     mock_404.raise_for_status.side_effect = requests.HTTPError(response=mock_404)
    #
    #     # Second call (after redirect) succeeds
    #     mock_success = Mock()
    #     mock_success.status_code = 200
    #     mock_success.json.return_value = {
    #         "id": 123,
    #         "name": "Test User",
    #         "handle": "newhandle",
    #     }
    #
    #     mock_get.side_effect = [mock_404, mock_success]
    #
    #     # Mock redirect resolution
    #     mock_resolve.return_value = "newhandle"
    #
    #     user = User("oldhandle", follow_redirects=True)
    #     data = user._fetch_user_data()
    #
    #     assert data == {"id": 123, "name": "Test User", "handle": "newhandle"}
    #     assert user.username == "newhandle"  # Username updated
    #     assert user.original_username == "oldhandle"
    #     assert user.was_redirected
    #     assert user._redirect_attempted is True
    #
    #     # Verify API calls
    #     assert mock_get.call_count == 2
    #     mock_resolve.assert_called_once_with("oldhandle")
    #
    # def test_fetch_user_data_redirect_disabled(self, mock_get):
    #     """Test that redirects are not followed when disabled."""
    #     # Mock 404 response
    #     mock_404 = Mock()
    #     mock_404.status_code = 404
    #     mock_404.raise_for_status.side_effect = requests.HTTPError(response=mock_404)
    #     mock_get.return_value = mock_404
    #
    #     user = User("oldhandle", follow_redirects=False)
    #
    #     with pytest.raises(requests.HTTPError):
    #         user._fetch_user_data()
    #
    #     # Should not attempt redirect
    #     mock_resolve.assert_not_called()
    #     assert user.username == "oldhandle"  # Username unchanged

    def test_fetch_user_data_no_redirect_found(self, mock_get):
        """Test when no redirect is found (user truly deleted)."""
        # Mock 404 response
        mock_get.return_value.status_code = 404

        user = User("deleteduser", follow_redirects=True)

        with pytest.raises(requests.HTTPError):
            user._fetch_user_data()

        mock_get.assert_any_call('https://substack.com/api/v1/user/deleteduser/public_profile', timeout=30)
        assert user.username == "deleteduser"  # Username unchanged

    def test_fetch_user_data_redirect_still_404(self, mock_get):
        """Test when redirect is found but new handle also returns 404."""
        # Both calls return 404
        mock_get.return_value.status_code = 404
        response = Mock()
        response.status_code = 200
        response.url = "https://substack.com/@newhandle"
        mock_get.side_effect = [mock_get.return_value, response, response]

        user = User("oldhandle", follow_redirects=True)

        user._fetch_user_data()

        assert user.username == "newhandle"  # Username was updated
        assert user.was_redirected
        assert mock_get.call_count == 3

#     def test_prevent_infinite_redirect_loop(self, mock_get):
#         """Test that redirect is only attempted once."""
#         # All calls return 404
#         mock_404 = Mock()
#         mock_404.status_code = 404
#         mock_404.raise_for_status.side_effect = requests.HTTPError(response=mock_404)
#         mock_get.return_value = mock_404
#
#         user = User("testuser", follow_redirects=True)
#
#         # First attempt
#         with pytest.raises(requests.HTTPError):
#             user._fetch_user_data()
#
#         # Second attempt should not try redirect again
#         with pytest.raises(requests.HTTPError):
#             user._fetch_user_data()
#
#         # Should only have made 3 API calls total (2 original + 1 after redirect)
#         # not 4+ calls
#         assert mock_get.call_count <= 3
#
#     def test_update_handle(self):
#         """Test the _update_handle method."""
#         user = User("oldhandle")
#
#         user._update_handle("newhandle")
#
#         assert user.username == "newhandle"
#         assert (
#             user.endpoint == "https://substack.com/api/v1/user/newhandle/public_profile"
#         )
#         assert user.original_username == "oldhandle"  # Original preserved
#
#     def test_was_redirected_property(self):
#         """Test the was_redirected property."""
#         user = User("testuser")
#         assert not user.was_redirected
#
#         user._update_handle("newhandle")
#         assert user.was_redirected
#
#
# class TestUserRedirectExamples(unittest.TestCase):
#     """Test the specific redirect examples provided."""
#
#     def test_real_world_redirects(self, mock_get):
#         """Test with the real examples provided."""
#         test_cases = [
#             ("150wordreviews", "johndevore"),
#             ("15thcfeminist", "15thcenturyfeminist"),
#             ("300tangpoems", "hyunwookimwriter"),
#             ("5thingsyoushouldbuy", "beckymalinsky"),
#         ]
#
#         for old_handle, new_handle in test_cases:
#             with self.subTest(old=old_handle, new=new_handle):
#                 # Reset mocks
#                 mock_get.reset_mock()
#                 mock_resolve.reset_mock()
#
#                 # Setup mocks
#                 mock_404 = Mock()
#                 mock_404.status_code = 404
#                 mock_404.raise_for_status.side_effect = requests.HTTPError(
#                     response=mock_404
#                 )
#
#                 mock_success = Mock()
#                 mock_success.status_code = 200
#                 mock_success.json.return_value = {
#                     "id": 123,
#                     "handle": new_handle,
#                     "name": "Test User",
#                 }
#
#                 mock_get.side_effect = [mock_404, mock_success]
#                 mock_resolve.return_value = new_handle
#
#                 # Test
#                 user = User(old_handle)
#                 data = user.get_raw_data()
#
#                 # Verify
#                 assert user.original_username == old_handle
#                 assert user.username == new_handle
#                 assert user.was_redirected
#                 assert data["handle"] == new_handle
