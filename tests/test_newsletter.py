from unittest.mock import MagicMock, patch

import pytest

from substack_api import Newsletter, User
from substack_api.newsletter import HEADERS


@pytest.fixture
def newsletter_url():
    return "https://testblog.substack.com"


@pytest.fixture
def mock_post_items():
    return [
        {
            "id": 101,
            "title": "First Test Post",
            "canonical_url": "https://testblog.substack.com/p/first-test-post",
        },
        {
            "id": 102,
            "title": "Second Test Post",
            "canonical_url": "https://testblog.substack.com/p/second-test-post",
        },
        {
            "id": 103,
            "title": "Third Test Post",
            "canonical_url": "https://testblog.substack.com/p/third-test-post",
        },
    ]


@pytest.fixture
def mock_recommendations():
    return [
        {"recommendedPublication": {"subdomain": "newsletter1", "custom_domain": None}},
        {"recommendedPublication": {"subdomain": "newsletter2", "custom_domain": None}},
        {
            "recommendedPublication": {
                "subdomain": "newsletter3",
                "custom_domain": "https://custom.domain.com",
            }
        },
    ]


@pytest.fixture
def mock_authors():
    return [
        {"handle": "author1", "name": "Author One"},
        {"handle": "author2", "name": "Author Two"},
    ]


def test_newsletter_init(newsletter_url):
    newsletter = Newsletter(newsletter_url)
    assert newsletter.url == newsletter_url


def test_newsletter_string_representation(newsletter_url):
    newsletter = Newsletter(newsletter_url)
    assert str(newsletter) == f"Newsletter: {newsletter_url}"
    assert repr(newsletter) == f"Newsletter(url={newsletter_url})"


@patch("substack_api.newsletter.requests.get")
def test_fetch_paginated_posts_single_page(mock_get, newsletter_url, mock_post_items):
    # Set up mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_post_items
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    params = {"sort": "new"}
    results = newsletter._fetch_paginated_posts(params, limit=None)

    # Check we made the right API call
    mock_get.assert_called_once_with(
        f"{newsletter_url}/api/v1/archive?sort=new&offset=0&limit=15",
        headers=HEADERS,
        timeout=30,
    )

    # Check we got the expected results
    assert len(results) == 3
    assert isinstance(results[0], dict)
    assert results[0]["canonical_url"] == mock_post_items[0]["canonical_url"]


@patch("substack_api.newsletter.requests.get")
def test_fetch_paginated_posts_multiple_pages(
    mock_get, newsletter_url, mock_post_items
):
    # Set up mock to return 3 items for first page, 1 item for second page
    mock_response_1 = MagicMock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = mock_post_items

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = [
        {
            "id": 104,
            "title": "Fourth Test Post",
            "canonical_url": "https://testblog.substack.com/p/fourth-test-post",
        }
    ]

    mock_response_3 = MagicMock()
    mock_response_3.status_code = 200
    mock_response_3.json.return_value = []

    mock_get.side_effect = [mock_response_1, mock_response_2, mock_response_3]

    newsletter = Newsletter(newsletter_url)
    params = {"sort": "new"}
    results = newsletter._fetch_paginated_posts(params, page_size=3)

    # Check we made the expected number of API calls
    assert mock_get.call_count == 2

    # Check we got the expected results (3 from first page + 1 from second)
    assert len(results) == 4


@patch("substack_api.newsletter.requests.get")
def test_fetch_paginated_posts_with_limit(mock_get, newsletter_url, mock_post_items):
    # Set up mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_post_items
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    params = {"sort": "new"}
    results = newsletter._fetch_paginated_posts(params, limit=2)

    # Check we only got the requested limit
    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert results[0]["canonical_url"] == mock_post_items[0]["canonical_url"]


@patch("substack_api.newsletter.requests.get")
def test_fetch_paginated_posts_error_response(mock_get, newsletter_url):
    # Set up mock to return an error
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    params = {"sort": "new"}
    results = newsletter._fetch_paginated_posts(params)

    # Should return empty list on error
    assert results == []


@patch("substack_api.newsletter.Newsletter._fetch_paginated_posts")
def test_get_posts(mock_fetch, newsletter_url):
    newsletter = Newsletter(newsletter_url)

    # Test with default parameters
    newsletter.get_posts()
    mock_fetch.assert_called_once_with({"sort": "new"}, None)

    # Test with custom parameters
    mock_fetch.reset_mock()
    newsletter.get_posts(sorting="top", limit=10)
    mock_fetch.assert_called_once_with({"sort": "top"}, 10)


@patch("substack_api.newsletter.Newsletter._fetch_paginated_posts")
def test_search_posts(mock_fetch, newsletter_url):
    newsletter = Newsletter(newsletter_url)

    # Test search
    newsletter.search_posts("test query")
    mock_fetch.assert_called_once_with({"sort": "new", "search": "test query"}, None)

    # Test with limit
    mock_fetch.reset_mock()
    newsletter.search_posts("test query", limit=5)
    mock_fetch.assert_called_once_with({"sort": "new", "search": "test query"}, 5)


@patch("substack_api.newsletter.Newsletter._fetch_paginated_posts")
def test_get_podcasts(mock_fetch, newsletter_url):
    newsletter = Newsletter(newsletter_url)

    # Test podcast retrieval
    newsletter.get_podcasts()
    mock_fetch.assert_called_once_with({"sort": "new", "type": "podcast"}, None)

    # Test with limit
    mock_fetch.reset_mock()
    newsletter.get_podcasts(limit=3)
    mock_fetch.assert_called_once_with({"sort": "new", "type": "podcast"}, 3)


@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_success(mock_get, newsletter_url, mock_recommendations):
    # Mock the post fetch to return a publication ID
    post_mock = MagicMock()
    post_mock.get_metadata.return_value = {"publication_id": 123}

    # First patch _fetch_paginated_posts to return our mocked post
    with patch.object(Newsletter, "get_posts", return_value=[post_mock]):
        # Then patch the recommendations API call
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_recommendations
        mock_get.return_value = mock_resp

        newsletter = Newsletter(newsletter_url)
        recommendations = newsletter.get_recommendations()

        # Verify the API was called correctly
        mock_get.assert_called_once_with(
            f"{newsletter_url}/api/v1/recommendations/from/123",
            headers=HEADERS,
            timeout=30,
        )

        # Verify we got the expected recommendations
        assert len(recommendations) == 3
        assert all(isinstance(rec, Newsletter) for rec in recommendations)
        # Check URL formation with and without custom domains
        assert recommendations[0].url == "newsletter1.substack.com"
        assert recommendations[2].url == "https://custom.domain.com"


@patch("substack_api.newsletter.Newsletter.get_posts")
def test_get_recommendations_no_posts(mock_get_posts, newsletter_url):
    # Mock empty post list
    mock_get_posts.return_value = []

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Should return empty list when no posts
    assert recommendations == []


@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_error(mock_get, newsletter_url):
    # Mock the post fetch
    post_mock = MagicMock()
    post_mock.get_metadata.return_value = {"publication_id": 123}

    with patch.object(Newsletter, "get_posts", return_value=[post_mock]):
        # Mock error response for recommendations
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        newsletter = Newsletter(newsletter_url)
        recommendations = newsletter.get_recommendations()

        # Should return empty list on error
        assert recommendations == []


@patch("substack_api.newsletter.requests.get")
def test_get_authors(mock_get, newsletter_url, mock_authors):
    # Set up mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_authors
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    authors = newsletter.get_authors()

    # Check API call
    expected_url = f"{newsletter_url}/api/v1/publication/users/ranked?public=true"
    mock_get.assert_called_once_with(expected_url, headers=HEADERS, timeout=30)

    # Check results
    assert len(authors) == 2
    assert all(isinstance(author, User) for author in authors)
    assert authors[0].username == "author1"
    assert authors[1].username == "author2"


@patch("substack_api.newsletter.requests.get")
def test_get_authors_empty_response(mock_get, newsletter_url):
    # Set up mock with empty response
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    authors = newsletter.get_authors()

    # Should return empty list
    assert authors == []
