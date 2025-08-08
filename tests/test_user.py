from unittest.mock import Mock, patch

from substack_api import User


class TestUser:
    def test_user_init(self):
        user = User("testuser")
        assert user.username == "testuser"
        assert (
            user.endpoint == "https://substack.com/api/v1/user/testuser/public_profile"
        )
        assert user._user_data is None

    def test_user_string_representation(self):
        user = User("testuser")
        assert str(user) == "User: testuser"
        assert repr(user) == "User(username='testuser')"

    def test_fetch_user_data(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 123, "name": "Test User"}

        user = User("testuser")
        data = user._fetch_user_data()

        assert data == {"id": 123, "name": "Test User"}
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/testuser/public_profile",
            timeout=30,
        )

    def test_fetch_user_data_uses_cache(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_get.return_value = mock_response

        user = User("testuser")
        user._fetch_user_data()  # First call
        user._fetch_user_data()  # Should use cache

        # Assert - only called once despite two fetch attempts
        mock_get.assert_called_once()

    def test_fetch_user_data_force_refresh(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 123, "name": "Test User"}

        user = User("testuser")
        user._fetch_user_data()  # First call
        user._fetch_user_data(force_refresh=True)  # Force refresh

        # Assert - called twice due to force refresh
        assert mock_get.call_count == 2

    def test_get_raw_data(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 123, "name": "Test User"}

        user = User("testuser")
        data = user.get_raw_data()

        assert data == {"id": 123, "name": "Test User"}
        mock_get.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_id_property(self, mock_fetch):
        mock_fetch.return_value = {"id": 456, "name": "Test User"}

        user = User("testuser")
        user_id = user.id

        assert user_id == 456
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_name_property(self, mock_fetch):
        mock_fetch.return_value = {"id": 123, "name": "John Doe"}

        user = User("testuser")
        name = user.name

        assert name == "John Doe"
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_user_profile_setup_date(self, mock_fetch):
        mock_fetch.return_value = {
            "id": 123,
            "name": "Test User",
            "profile_set_up_at": "2023-01-01T12:00:00Z",
        }

        user = User("testuser")
        setup_date = user.profile_set_up_at

        assert setup_date == "2023-01-01T12:00:00Z"
        mock_fetch.assert_called_once()

    @patch("substack_api.user.User._fetch_user_data")
    def test_get_subscriptions(self, mock_fetch):
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

        user = User("testuser")
        subscriptions = user.get_subscriptions()

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
        assert subscriptions == expected
        mock_fetch.assert_called_once()
