import unittest
from unittest.mock import Mock, patch

import requests

from substack_api.user import (
    HEADERS,
    get_user_commented_posts,
    get_user_id,
    get_user_likes,
    get_user_notes,
    get_user_reads,
    get_user_written_posts,
)


class TestGetUserId(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_id_success(self, mock_get):
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123}
        mock_get.return_value = mock_response

        # Execute
        result = get_user_id("testuser")

        # Assert
        self.assertEqual(result, 123)
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/testuser/public_profile",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_get_user_id_not_found(self, mock_get):
        # Setup
        mock_get.side_effect = requests.exceptions.HTTPError("User not found")

        # Execute & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            get_user_id("nonexistent_user")

    @patch("requests.get")
    def test_get_user_id_connection_error(self, mock_get):
        # Setup
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        # Execute & Assert
        with self.assertRaises(requests.exceptions.ConnectionError):
            get_user_id("testuser")


class TestGetUserReads(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_reads_success(self, mock_get):
        # Setup
        mock_response = {
            "subscriptions": [
                {
                    "publication": {"id": "123", "name": "Tech Newsletter"},
                    "membership_state": "subscribed",
                },
                {
                    "publication": {"id": "456", "name": "Science Weekly"},
                    "membership_state": "paid_subscriber",
                },
            ]
        }
        mock_get.return_value = Mock(json=lambda: mock_response)

        # Execute
        result = get_user_reads("testuser")

        # Assert
        expected = [
            {
                "publication_id": "123",
                "publication_name": "Tech Newsletter",
                "subscription_status": "subscribed",
            },
            {
                "publication_id": "456",
                "publication_name": "Science Weekly",
                "subscription_status": "paid_subscriber",
            },
        ]
        self.assertEqual(result, expected)
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/testuser/public_profile",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_get_user_reads_empty(self, mock_get):
        # Setup
        mock_response = {"subscriptions": []}
        mock_get.return_value = Mock(json=lambda: mock_response)

        # Execute
        result = get_user_reads("testuser")

        # Assert
        self.assertEqual(result, [])

    @patch("requests.get")
    def test_get_user_reads_missing_field(self, mock_get):
        # Setup - response without "subscriptions" field
        mock_response = {"other_data": "something"}
        mock_get.return_value = Mock(json=lambda: mock_response)

        # Execute & Assert
        with self.assertRaises(KeyError):
            get_user_reads("testuser")


class TestGetUserLikes(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_likes_success(self, mock_get):
        # Setup
        mock_likes = {
            "items": [
                {
                    "post_id": 101,
                    "title": "Liked Post 1",
                    "publication": {"name": "Tech Blog"},
                },
                {
                    "post_id": 102,
                    "title": "Liked Post 2",
                    "publication": {"name": "Science Blog"},
                },
            ]
        }
        mock_get.return_value = Mock(json=lambda: mock_likes)

        # Execute
        result = get_user_likes(123)

        # Assert
        self.assertEqual(result, mock_likes["items"])
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/reader/feed/profile/123?types%5B%5D=like",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_get_user_likes_empty(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"items": []})

        # Execute
        result = get_user_likes(123)

        # Assert
        self.assertEqual(result, [])

    @patch("requests.get")
    def test_get_user_likes_with_limit(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"items": ["post1", "post2"]})

        # Execute
        result = get_user_likes(123, limit=10)

        # Assert
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/reader/feed/profile/123?types%5B%5D=like&limit=10",
            headers=HEADERS,
            timeout=30,
        )


class TestGetUserNotes(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_notes_success(self, mock_get):
        # Setup
        mock_notes = {
            "items": [
                {
                    "id": "note1",
                    "text": "This is note 1",
                    "created_at": "2023-01-01T12:00:00Z",
                },
                {
                    "id": "note2",
                    "text": "This is note 2",
                    "created_at": "2023-01-02T12:00:00Z",
                },
            ]
        }
        mock_get.return_value = Mock(json=lambda: mock_notes)

        # Execute
        result = get_user_notes(123)

        # Assert
        self.assertEqual(result, mock_notes["items"])
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/reader/feed/profile/123",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_get_user_notes_empty(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"items": []})

        # Execute
        result = get_user_notes(123)

        # Assert
        self.assertEqual(result, [])

    @patch("requests.get")
    def test_get_user_notes_with_limit(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"items": ["note1", "note2"]})

        # Execute
        result = get_user_notes(123, limit=5, offset=10)

        # Assert
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/reader/feed/profile/123?limit=5&offset=10",
            headers=HEADERS,
            timeout=30,
        )


class TestGetUserWrittenPosts(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_written_posts_success(self, mock_get):
        # Setup
        mock_posts = {
            "posts": [
                {"id": 101, "title": "First Post", "slug": "first-post"},
                {"id": 102, "title": "Second Post", "slug": "second-post"},
            ]
        }
        mock_get.return_value = Mock(json=lambda: mock_posts)

        # Execute
        result = get_user_written_posts(123)

        # Assert
        self.assertEqual(result, mock_posts["posts"])
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/123/written", headers=HEADERS, timeout=30
        )

    @patch("requests.get")
    def test_get_user_written_posts_empty(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"posts": []})

        # Execute
        result = get_user_written_posts(123)

        # Assert
        self.assertEqual(result, [])


class TestGetUserCommentedPosts(unittest.TestCase):
    @patch("requests.get")
    def test_get_user_commented_posts_success(self, mock_get):
        # Setup
        mock_comments = {
            "comments": [
                {
                    "id": "c1",
                    "body": "Great post!",
                    "post": {"id": 101, "title": "First Post"},
                },
                {
                    "id": "c2",
                    "body": "Interesting thoughts",
                    "post": {"id": 102, "title": "Second Post"},
                },
            ]
        }
        mock_get.return_value = Mock(json=lambda: mock_comments)

        # Execute
        result = get_user_commented_posts(123)

        # Assert
        self.assertEqual(result, mock_comments["comments"])
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/123/comments", headers=HEADERS, timeout=30
        )

    @patch("requests.get")
    def test_get_user_commented_posts_empty(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"comments": []})

        # Execute
        result = get_user_commented_posts(123)

        # Assert
        self.assertEqual(result, [])

    @patch("requests.get")
    def test_get_user_commented_posts_with_pagination(self, mock_get):
        # Setup
        mock_get.return_value = Mock(json=lambda: {"comments": ["c1", "c2"]})

        # Execute
        result = get_user_commented_posts(123, page=2, limit=20)

        # Assert
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/user/123/comments?page=2&limit=20",
            headers=HEADERS,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
