import unittest
from unittest.mock import patch, Mock, MagicMock
from bs4 import BeautifulSoup
from substack_api.newsletter import (
    get_newsletter_post_metadata,
    get_newsletter_recommendations,
    get_post_contents,
    HEADERS,
)


class TestGetNewsletterPostMetadata(unittest.TestCase):
    @patch("requests.get")
    def test_get_newsletter_post_metadata_slugs_only(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = [
            {"id": 1, "slug": "post-1"},
            {"id": 2, "slug": "post-2"},
        ]

        result = get_newsletter_post_metadata("test_subdomain.substack.com", slugs_only=True)
        self.assertEqual(result, ["post-1", "post-2"])

    @patch("requests.get")
    def test_get_newsletter_post_metadata_all_metadata(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = [
            {"id": 1, "slug": "post-1", "title": "Post 1"},
            {"id": 2, "slug": "post-2", "title": "Post 2"},
        ]

        result = get_newsletter_post_metadata("test_subdomain.substack.com", slugs_only=False)
        self.assertEqual(
            result,
            [
                {"id": 1, "slug": "post-1", "title": "Post 1"},
                {"id": 2, "slug": "post-2", "title": "Post 2"},
            ],
        )

    @patch("requests.get")
    def test_get_newsletter_post_metadata_pagination(self, mock_get):
        mock_get.side_effect = [
            Mock(
                ok=True,
                json=Mock(
                    return_value=[
                        {"id": 1, "slug": "post-1"},
                        {"id": 2, "slug": "post-2"},
                    ]
                ),
            ),
            Mock(
                ok=True,
                json=Mock(
                    return_value=[
                        {"id": 3, "slug": "post-3"},
                        {"id": 4, "slug": "post-4"},
                    ]
                ),
            ),
        ]

        result = get_newsletter_post_metadata(
            "test_subdomain.substack.com", slugs_only=True, start_offset=0, end_offset=20
        )
        self.assertEqual(result, ["post-1", "post-2", "post-3", "post-4"])

    @patch("requests.get")
    def test_get_newsletter_post_metadata_no_posts(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = []

        result = get_newsletter_post_metadata("test_subdomain.substack.com")
        self.assertEqual(result, [])


class TestGetNewsletterRecommendations(unittest.TestCase):
    @patch("requests.get")
    @patch.object(BeautifulSoup, "find_all")
    @patch.object(BeautifulSoup, "__init__", return_value=None)
    def test_get_newsletter_recommendations(
        self, mock_bs_init, mock_find_all, mock_get
    ):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.text = "mocked_html"

        mock_div = MagicMock()
        mock_div.find.return_value = {"href": "https://mocked_url.com?param=value"}

        mock_find_all.side_effect = [
            [mock_div, mock_div],  # div_elements
            [Mock(text="title1"), Mock(text="title2")],  # titles
        ]

        result = get_newsletter_recommendations("test_subdomain")

        self.assertEqual(
            result,
            [
                {"title": "title1", "url": "https://mocked_url.com"},
                {"title": "title2", "url": "https://mocked_url.com"},
            ],
        )

        mock_get.assert_called_once_with(
            "https://test_subdomain.substack.com/recommendations",
            headers=HEADERS,
            timeout=30,
        )
        mock_bs_init.assert_called_once_with("mocked_html", "html.parser")
        self.assertEqual(mock_find_all.call_count, 2)


class TestGetPostContents(unittest.TestCase):
    @patch("requests.get")
    def test_get_post_contents_html_only(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "body_html": "<html><body>Test post</body></html>"
        }

        result = get_post_contents("test_subdomain.substack.com", "test_slug", html_only=True)
        self.assertEqual(result, "<html><body>Test post</body></html>")

    @patch("requests.get")
    def test_get_post_contents_all_metadata(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "body_html": "<html><body>Test post</body></html>",
            "title": "Test post",
            "author": "Test author",
            "date": "2022-01-01",
        }

        result = get_post_contents("test_subdomain.substack.com", "test_slug", html_only=False)
        self.assertEqual(
            result,
            {
                "body_html": "<html><body>Test post</body></html>",
                "title": "Test post",
                "author": "Test author",
                "date": "2022-01-01",
            },
        )


if __name__ == "__main__":
    unittest.main()
