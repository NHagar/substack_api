from unittest.mock import MagicMock, patch

import pytest

from substack_api import Newsletter, User
from substack_api.newsletter import (
    DISCOVERY_HEADERS,
    HEADERS,
    SEARCH_URL,
    _host_from_url,
    _match_publication,
)


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


@pytest.fixture
def mock_search_result():
    return {
        "publications": [
            {
                "id": 123,
                "subdomain": "testblog",
                "custom_domain": None,
                "name": "Test Blog",
            },
            {
                "id": 456,
                "subdomain": "otherblog",
                "custom_domain": "https://custom.example.com",
                "name": "Other Blog",
            },
        ]
    }


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


@patch("substack_api.newsletter.requests.get")
def test_fetch_paginated_posts_empty_first_response(mock_get, newsletter_url):
    # Set up mock to return empty list on first request
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    params = {"sort": "new"}
    results = newsletter._fetch_paginated_posts(params)

    # Should return empty list
    assert results == []
    # Should only make one call before breaking
    assert mock_get.call_count == 1


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


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_success_via_resolve(
    mock_get, mock_resolve, newsletter_url, mock_recommendations
):
    # Mock the publication ID resolution
    mock_resolve.return_value = 123

    # Mock the recommendations API call
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_recommendations
    mock_get.return_value = mock_resp

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Verify _resolve_publication_id was called
    mock_resolve.assert_called_once()

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


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.Newsletter.get_posts")
@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_fallback_to_posts(
    mock_get, mock_get_posts, mock_resolve, newsletter_url, mock_recommendations
):
    # Mock _resolve_publication_id to return None (search fails)
    mock_resolve.return_value = None

    # Mock the post fetch to return a publication ID
    post_mock = MagicMock()
    post_mock.get_metadata.return_value = {"publication_id": 456}
    mock_get_posts.return_value = [post_mock]

    # Mock the recommendations API call
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_recommendations
    mock_get.return_value = mock_resp

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Verify fallback path was used
    mock_resolve.assert_called_once()
    mock_get_posts.assert_called_once_with(limit=1)

    # Verify the API was called with the publication ID from the post
    mock_get.assert_called_once_with(
        f"{newsletter_url}/api/v1/recommendations/from/456",
        headers=HEADERS,
        timeout=30,
    )

    # Verify we got recommendations
    assert len(recommendations) == 3


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.Newsletter.get_posts")
def test_get_recommendations_no_publication_id(
    mock_get_posts, mock_resolve, newsletter_url
):
    # Mock both resolution paths to fail
    mock_resolve.return_value = None
    mock_get_posts.return_value = []

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Should return empty list when publication_id cannot be resolved
    assert recommendations == []


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.Newsletter.get_posts")
def test_get_recommendations_fallback_exception(
    mock_get_posts, mock_resolve, newsletter_url
):
    # Mock _resolve_publication_id to return None
    mock_resolve.return_value = None

    # Mock get_posts to raise an exception
    mock_get_posts.side_effect = Exception("Error fetching posts")

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Should return empty list when exception occurs in fallback
    assert recommendations == []


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_api_error(mock_get, mock_resolve, newsletter_url):
    # Mock successful publication ID resolution
    mock_resolve.return_value = 123

    # Mock error response for recommendations
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_resp

    newsletter = Newsletter(newsletter_url)

    # The implementation raises the error, so we expect an exception
    with pytest.raises(Exception):
        newsletter.get_recommendations()


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_empty_response(mock_get, mock_resolve, newsletter_url):
    # Mock successful publication ID resolution
    mock_resolve.return_value = 123

    # Mock empty recommendations response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    mock_get.return_value = mock_resp

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Should return empty list when no recommendations
    assert recommendations == []


@patch("substack_api.newsletter.Newsletter._resolve_publication_id")
@patch("substack_api.newsletter.requests.get")
def test_get_recommendations_null_response(mock_get, mock_resolve, newsletter_url):
    # Mock successful publication ID resolution
    mock_resolve.return_value = 123

    # Mock None (null) recommendations response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = None
    mock_get.return_value = mock_resp

    newsletter = Newsletter(newsletter_url)
    recommendations = newsletter.get_recommendations()

    # Should return empty list when response is None
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


# Tests for helper functions
def test_host_from_url():
    # Test with full URL
    assert _host_from_url("https://testblog.substack.com") == "testblog.substack.com"

    # Test without protocol
    assert _host_from_url("testblog.substack.com") == "testblog.substack.com"

    # Test with custom domain
    assert _host_from_url("https://custom.example.com") == "custom.example.com"

    # Test with port
    assert _host_from_url("https://testblog.substack.com:8080") == "testblog.substack.com:8080"

    # Test case insensitivity
    assert _host_from_url("https://TestBlog.Substack.COM") == "testblog.substack.com"


def test_match_publication():
    search_results = {
        "publications": [
            {
                "id": 123,
                "subdomain": "testblog",
                "custom_domain": None,
            },
            {
                "id": 456,
                "subdomain": "otherblog",
                "custom_domain": "https://custom.example.com",
            },
            {
                "id": 789,
                "subdomain": "thirdblog",
                "custom_domain": "custom2.example.com",
            },
        ]
    }

    # Test exact subdomain match
    match = _match_publication(search_results, "testblog.substack.com")
    assert match is not None
    assert match["id"] == 123

    # Test custom domain match (with https)
    match = _match_publication(search_results, "custom.example.com")
    assert match is not None
    assert match["id"] == 456

    # Test custom domain match (without protocol)
    match = _match_publication(search_results, "custom2.example.com")
    assert match is not None
    assert match["id"] == 789

    # Test no match
    match = _match_publication(search_results, "nonexistent.substack.com")
    assert match is None

    # Test case insensitive subdomain match (via fallback regex path)
    # The regex path converts to lowercase, so it should match
    search_results_mixed_case = {
        "publications": [
            {
                "id": 999,
                "subdomain": "TestBlog",
                "custom_domain": None,
            }
        ]
    }
    match = _match_publication(search_results_mixed_case, "testblog.substack.com")
    assert match is not None
    assert match["id"] == 999

    # Test fallback path when first pass doesn't match but regex does
    # This tests the scenario where the exact match fails but regex succeeds
    search_results_fallback = {
        "publications": [
            {
                "id": 888,
                "subdomain": "TESTBLOG",  # Won't match on first pass due to case
                "custom_domain": None,
            }
        ]
    }
    match = _match_publication(search_results_fallback, "testblog.substack.com")
    assert match is not None
    assert match["id"] == 888

    # Test empty publications list
    match = _match_publication({"publications": []}, "testblog.substack.com")
    assert match is None


@patch("substack_api.newsletter.requests.get")
def test_resolve_publication_id_success(mock_get, newsletter_url, mock_search_result):
    # Set up mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_search_result
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    publication_id = newsletter._resolve_publication_id()

    # Check API call
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[0][0] == SEARCH_URL
    assert call_args[1]["headers"] == DISCOVERY_HEADERS
    assert call_args[1]["timeout"] == 30

    # Check params
    params = call_args[1]["params"]
    assert params["query"] == "testblog.substack.com"
    assert params["page"] == 0
    assert params["limit"] == 25
    assert params["skipExplanation"] == "true"
    assert params["sort"] == "relevance"

    # Check result
    assert publication_id == 123


@patch("substack_api.newsletter.requests.get")
def test_resolve_publication_id_no_match(mock_get, newsletter_url):
    # Set up mock with empty results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"publications": []}
    mock_get.return_value = mock_response

    newsletter = Newsletter(newsletter_url)
    publication_id = newsletter._resolve_publication_id()

    # Should return None when no match
    assert publication_id is None


@patch("substack_api.newsletter.requests.get")
def test_resolve_publication_id_with_custom_domain(mock_get):
    # Set up mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "publications": [
            {
                "id": 999,
                "subdomain": "blog",
                "custom_domain": "https://custom.example.com",
            }
        ]
    }
    mock_get.return_value = mock_response

    newsletter = Newsletter("https://custom.example.com")
    publication_id = newsletter._resolve_publication_id()

    # Check that query is based on the custom domain
    call_args = mock_get.call_args
    params = call_args[1]["params"]
    assert params["query"] == "custom.example.com"

    # Check result
    assert publication_id == 999
