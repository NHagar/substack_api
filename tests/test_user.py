import unittest
from unittest.mock import patch
from substack_api.user import (
    get_user_id,
    get_user_reads,
    get_user_likes,
    get_user_notes,
)


class TestUser(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_id(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 123}
        result = get_user_id("testuser")
        self.assertEqual(result, 123)

    @patch("requests.get")
    def test_get_user_reads(self, mock_get):
        mock_get.return_value.json.return_value = {
            "subscriptions": [
                {
                    "publication": {"id": "123", "name": "Test Publication"},
                    "membership_state": "subscribed",
                }
            ]
        }
        expected_result = [
            {
                "publication_id": "123",
                "publication_name": "Test Publication",
                "subscription_status": "subscribed",
            }
        ]
        result = get_user_reads("testuser")
        self.assertEqual(result, expected_result)

    @patch("requests.get")
    def test_get_user_likes(self, mock_get):
        mock_get.return_value.json.return_value = {"items": ["post1", "post2"]}
        result = get_user_likes(123)
        self.assertEqual(result, ["post1", "post2"])

    @patch("requests.get")
    def test_get_user_notes(self, mock_get):
        mock_get.return_value.json.return_value = {"items": ["note1", "note2"]}
        result = get_user_notes(123)
        self.assertEqual(result, ["note1", "note2"])


if __name__ == "__main__":
    unittest.main()
