import unittest
from unittest.mock import Mock, patch

import requests

from substack_api.newsletter import (
    HEADERS,
    category_id_to_name,
    category_name_to_id,
    get_newsletter_post_metadata,
    get_newsletter_recommendations,
    get_newsletters_in_category,
    get_post_contents,
    list_all_categories,
)


class TestCategoryFunctions(unittest.TestCase):
    @patch("requests.get")
    def test_list_all_categories(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Politics"},
            {"id": 2, "name": "Technology"},
        ]
        mock_get.return_value = mock_response

        result = list_all_categories()

        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/categories", headers=HEADERS, timeout=30
        )
        self.assertEqual(result, [("Politics", 1), ("Technology", 2)])

    @patch("substack_api.newsletter.list_all_categories")
    def test_category_id_to_name_success(self, mock_list_all_categories):
        mock_list_all_categories.return_value = [("Politics", 1), ("Technology", 2)]

        result = category_id_to_name(1)
        self.assertEqual(result, "Politics")

    @patch("substack_api.newsletter.list_all_categories")
    def test_category_id_to_name_error(self, mock_list_all_categories):
        mock_list_all_categories.return_value = [("Politics", 1), ("Technology", 2)]

        with self.assertRaises(ValueError):
            category_id_to_name(999)

    @patch("substack_api.newsletter.list_all_categories")
    def test_category_name_to_id_success(self, mock_list_all_categories):
        mock_list_all_categories.return_value = [("Politics", 1), ("Technology", 2)]

        result = category_name_to_id("Technology")
        self.assertEqual(result, 2)

    @patch("substack_api.newsletter.list_all_categories")
    def test_category_name_to_id_error(self, mock_list_all_categories):
        mock_list_all_categories.return_value = [("Politics", 1), ("Technology", 2)]

        with self.assertRaises(ValueError):
            category_name_to_id("NonExistent")


class TestGetNewslettersInCategory(unittest.TestCase):
    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletters_in_category_pagination(self, mock_sleep, mock_get):
        # First page with more=True
        first_response = {
            "publications": [
                {"id": "pub1", "name": "Newsletter 1"},
                {"id": "pub2", "name": "Newsletter 2"},
            ],
            "more": True,
        }
        # Second page with more=False
        second_response = {
            "publications": [{"id": "pub3", "name": "Newsletter 3"}],
            "more": False,
        }

        mock_get.side_effect = [
            Mock(json=lambda: first_response),
            Mock(json=lambda: second_response),
        ]

        result = get_newsletters_in_category(category_id=1)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["id"], "pub1")
        self.assertEqual(result[2]["name"], "Newsletter 3")
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletters_in_category_subdomains_only(self, mock_sleep, mock_get):
        mock_response = {
            "publications": [
                {"id": "pub1", "name": "Newsletter 1"},
                {"id": "pub2", "name": "Newsletter 2"},
            ],
            "more": False,
        }

        mock_get.return_value = Mock(json=lambda: mock_response)

        result = get_newsletters_in_category(category_id=1, subdomains_only=True)

        self.assertEqual(result, ["pub1", "pub2"])
        mock_get.assert_called_once()

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletters_in_category_page_limits(self, mock_sleep, mock_get):
        mock_response = {
            "publications": [{"id": "pub1", "name": "Newsletter 1"}],
            "more": True,  # More pages exist, but we should stop due to end_page
        }

        mock_get.return_value = Mock(json=lambda: mock_response)

        result = get_newsletters_in_category(category_id=1, start_page=1, end_page=2)

        self.assertEqual(len(result), 1)
        self.assertEqual(mock_get.call_count, 1)
        mock_get.assert_called_once_with(
            "https://substack.com/api/v1/category/public/1/all?page=1",
            headers=HEADERS,
            timeout=30,
        )


class TestGetNewsletterPostMetadata(unittest.TestCase):
    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletter_post_metadata_slugs_only(self, mock_sleep, mock_get):
        mock_get.return_value = Mock(
            json=lambda: [
                {"id": 1, "slug": "post-1"},
                {"id": 2, "slug": "post-2"},
            ]
        )

        result = get_newsletter_post_metadata("test_subdomain", slugs_only=True)
        self.assertEqual(result, ["post-1", "post-2"])
        mock_get.assert_called_once_with(
            "https://test_subdomain.substack.com/api/v1/archive?sort=new&search=&offset=0&limit=10",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletter_post_metadata_all_metadata(self, mock_sleep, mock_get):
        test_posts = [
            {"id": 1, "slug": "post-1", "title": "Post 1"},
            {"id": 2, "slug": "post-2", "title": "Post 2"},
        ]
        mock_get.return_value = Mock(json=lambda: test_posts)

        result = get_newsletter_post_metadata("test_subdomain", slugs_only=False)
        self.assertEqual(result, test_posts)

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletter_post_metadata_pagination(self, mock_sleep, mock_get):
        first_page = [
            {"id": 1, "slug": "post-1"},
            {"id": 2, "slug": "post-2"},
        ]

        second_page = [
            {"id": 3, "slug": "post-3"},
            {"id": 4, "slug": "post-4"},
        ]

        empty_page = []

        mock_get.side_effect = [
            Mock(json=lambda: first_page),
            Mock(json=lambda: second_page),
            Mock(json=lambda: empty_page),
        ]

        result = get_newsletter_post_metadata(
            "test_subdomain", slugs_only=True, start_offset=0, end_offset=30
        )
        self.assertEqual(result, ["post-1", "post-2", "post-3", "post-4"])
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletter_post_metadata_same_last_id(self, mock_sleep, mock_get):
        # Test case where last_id is the same (should break loop)
        repeating_post = [{"id": 1, "slug": "post-1"}]
        mock_get.return_value = Mock(json=lambda: repeating_post)

        result = get_newsletter_post_metadata("test_subdomain")
        self.assertEqual(result, [{"id": 1, "slug": "post-1"}])
        self.assertEqual(
            mock_get.call_count, 2
        )  # Initial call + one more that returns same ID

    @patch("requests.get")
    @patch("time.sleep")
    def test_get_newsletter_post_metadata_no_posts(self, mock_sleep, mock_get):
        mock_get.return_value = Mock(json=lambda: [])

        result = get_newsletter_post_metadata("test_subdomain")
        self.assertEqual(result, [])
        self.assertEqual(mock_get.call_count, 1)


class TestGetPostContents(unittest.TestCase):
    @patch("requests.get")
    def test_get_post_contents_html_only(self, mock_get):
        mock_get.return_value = Mock(
            json=lambda: {
                "body_html": "<html><body>Test post</body></html>",
                "title": "Test Title",
            }
        )

        result = get_post_contents("test_subdomain", "test_slug", html_only=True)
        self.assertEqual(result, "<html><body>Test post</body></html>")
        mock_get.assert_called_once_with(
            "https://test_subdomain.substack.com/api/v1/posts/test_slug",
            headers=HEADERS,
            timeout=30,
        )

    @patch("requests.get")
    def test_get_post_contents_all_metadata(self, mock_get):
        post_data = {
            "body_html": "<html><body>Test post</body></html>",
            "title": "Test post",
            "author": "Test author",
            "date": "2022-01-01",
        }
        mock_get.return_value = Mock(json=lambda: post_data)

        result = get_post_contents("test_subdomain", "test_slug", html_only=False)
        self.assertEqual(result, post_data)

    @patch("requests.get")
    def test_get_post_contents_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        with self.assertRaises(requests.exceptions.RequestException):
            get_post_contents("test_subdomain", "test_slug")


class TestGetNewsletterRecommendations(unittest.TestCase):
    def setUp(self):
        self.html_content = """
        <div class="publication-content">
            <a href="https://url1.com?param=value">Link 1</a>
        </div>
        <div class="publication-content">
            <a href="https://url2.com?param=value">Link 2</a>
        </div>
        <div class="publication-title">Title 1</div>
        <div class="publication-title">Title 2</div>
        """

    @patch("requests.get")
    def test_get_newsletter_recommendations(self, mock_get):
        mock_get.return_value = Mock(text=self.html_content)

        result = get_newsletter_recommendations("test_subdomain")

        mock_get.assert_called_once_with(
            "https://test_subdomain.substack.com/recommendations",
            headers=HEADERS,
            timeout=30,
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Title 1")
        self.assertEqual(result[0]["url"], "https://url1.com")
        self.assertEqual(result[1]["title"], "Title 2")
        self.assertEqual(result[1]["url"], "https://url2.com")

    @patch("requests.get")
    def test_get_newsletter_recommendations_empty(self, mock_get):
        mock_get.return_value = Mock(text="<html></html>")

        result = get_newsletter_recommendations("test_subdomain")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
