import unittest
from unittest.mock import Mock, patch

from substack_api.user import HEADERS, User


class TestUser(unittest.TestCase):
    def test_user_init(self):
        user = User("testuser")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(
            user.endpoint, "https://substack.com/api/v1/user/testuser/public_profile"
        )
        self.assertIsNone(user._user_data)

    def test_user_string_representation(self):
        user = User("testuser")
        self.assertEqual(str(user), "User: testuser")
        self.assertEqual(repr(user), "User(username=testuser)")

    @patch("requests.get")
    def test_fetch_user_data(self, mock_get):
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_get.return_value = mock_response

        # Execute
        user = User("testuser")
        data = user._fetch_user_data()

        # Assert
        self.assertEqual(data, {"id": 123, "name": "Test User"})
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/testuser/public_profile",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_fetch_user_data_uses_cache(self, mock_get):
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_get.return_value = mock_response

        # Execute
        user = User("testuser")
        user._fetch_user_data()  # First call
        user._fetch_user_data()  # Should use cache

        # Assert - only called once despite two fetch attempts
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_fetch_user_data_force_refresh(self, mock_get):
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_get.return_value = mock_response

        # Execute
        user = User("testuser")
        user._fetch_user_data()  # First call
        user._fetch_user_data(force_refresh=True)  # Force refresh

        # Assert - called twice due to force refresh
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.get")
    def test_get_raw_data(self, mock_get):
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_get.return_value = mock_response

        # Execute
        user = User("testuser")
        data = user.get_raw_data()

        # Assert
        self.assertEqual(data, {"id": 123, "name": "Test User"})
        mock_get.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_id_property(self, mock_fetch):
        # Setup
        mock_fetch.return_value = {"id": 456, "name": "Test User"}

        # Execute
        user = User("testuser")
        user_id = user.id

        # Assert
        self.assertEqual(user_id, 456)
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_name_property(self, mock_fetch):
        # Setup
        mock_fetch.return_value = {"id": 123, "name": "John Doe"}

        # Execute
        user = User("testuser")
        name = user.name

        # Assert
        self.assertEqual(name, "John Doe")
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_profile_setup_date(self, mock_fetch):
        # Setup
        mock_fetch.return_value = {
            "id": 123,
            "name": "Test User",
            "profile_set_up_at": "2023-01-01T12:00:00Z",
        }

        # Execute
        user = User("testuser")
        setup_date = user.profile_set_up_at

        # Assert
        self.assertEqual(setup_date, "2023-01-01T12:00:00Z")
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_get_subscriptions(self, mock_fetch):
        # Setup
        mock_fetch.return_value = {
            "subscriptions": [
                {
                    "publication": {
                        "id": "123",
                        "name": "Tech Newsletter",
                        "subdomain": "tech",
                    },
                    "membership_state": "subscribed",
                },
                {
                    "publication": {
                        "id": "456",
                        "name": "Science Weekly",
                        "custom_domain": "science-weekly.com",
                    },
                    "membership_state": "paid_subscriber",
                },
            ]
        }

        # Execute
        user = User("testuser")
        subscriptions = user.get_subscriptions()

        # Assert
        expected = [
            {
                "publication_id": "123",
                "publication_name": "Tech Newsletter",
                "domain": "tech.substack.com",
                "membership_state": "subscribed",
            },
            {
                "publication_id": "456",
                "publication_name": "Science Weekly",
                "domain": "science-weekly.com",
                "membership_state": "paid_subscriber",
            },
        ]
        self.assertEqual(subscriptions, expected)
        mock_fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
