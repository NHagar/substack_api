from unittest.mock import MagicMock, patch

import pytest
import requests

from substack_api.post import Post


@pytest.fixture
def mock_post_data():
    return {
        "id": 123456,
        "title": "Test Post Title",
        "subtitle": "Test Post Subtitle",
        "slug": "test-post-slug",
        "body_html": "<p>This is test content</p>",
        "audience": "everyone",
        "publication_id": 789,
        "published_at": "2023-07-15T12:00:00.000Z",
        "canonical_url": "https://testblog.substack.com/p/test-post-slug",
    }


@pytest.fixture
def sample_post_url():
    return "https://testblog.substack.com/p/test-post-slug"


def test_post_init(sample_post_url):
    post = Post(sample_post_url)

    assert post.url == sample_post_url
    assert post.base_url == "https://testblog.substack.com"
    assert post.slug == "test-post-slug"
    assert post.endpoint == "https://testblog.substack.com/api/v1/posts/test-post-slug"
    assert post._post_data is None


def test_post_string_representation(sample_post_url):
    post = Post(sample_post_url)

    assert str(post) == f"Post: {sample_post_url}"
    assert repr(post) == f"Post(url='{sample_post_url}')"


def test_init_handles_different_url_formats():
    # URL with trailing slash
    post1 = Post("https://blog.substack.com/p/test-slug/")
    assert post1.slug == "test-slug"

    # URL with query parameters
    post2 = Post("https://blog.substack.com/p/test-slug?source=homepage-featured")
    assert post2.slug == "test-slug"

    # URL with fragment
    post3 = Post("https://blog.substack.com/p/test-slug#section-1")
    assert post3.slug == "test-slug"

    # Empty path
    post4 = Post("https://blog.substack.com")
    assert post4.slug == ""


@patch("substack_api.auth.SubstackAuth.get")
def test_fetch_post_data(mock_get, sample_post_url, mock_post_data):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = mock_post_data
    mock_get.return_value = mock_response

    post = Post(sample_post_url)
    data = post._fetch_post_data()

    # Verify the request was made correctly
    mock_get.assert_called_once_with(
        post.endpoint,
        timeout=30,
    )

    # Verify the data is stored and returned
    assert data == mock_post_data
    assert post._post_data == mock_post_data


@patch("substack_api.auth.SubstackAuth.get")
def test_fetch_post_data_uses_cache(mock_get, sample_post_url, mock_post_data):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = mock_post_data
    mock_get.return_value = mock_response

    post = Post(sample_post_url)

    # First call should fetch data
    post._fetch_post_data()
    assert mock_get.call_count == 1

    # Second call should use cached data
    post._fetch_post_data()
    assert mock_get.call_count == 1

    # Force refresh should fetch data again
    post._fetch_post_data(force_refresh=True)
    assert mock_get.call_count == 2


@patch("substack_api.auth.SubstackAuth.get")
def test_fetch_post_data_raises_exception(mock_get, sample_post_url):
    # Configure the mock to raise an exception
    mock_get.side_effect = requests.RequestException("API Error")

    post = Post(sample_post_url)
    with pytest.raises(requests.RequestException, match="API Error"):
        post._fetch_post_data()


@patch("substack_api.post.Post._fetch_post_data")
def test_get_metadata(mock_fetch_data, sample_post_url, mock_post_data):
    mock_fetch_data.return_value = mock_post_data

    post = Post(sample_post_url)
    metadata = post.get_metadata()

    assert metadata == mock_post_data
    mock_fetch_data.assert_called_once_with(force_refresh=False)

    # Test force refresh
    post.get_metadata(force_refresh=True)
    mock_fetch_data.assert_called_with(force_refresh=True)


@patch("substack_api.post.Post._fetch_post_data")
def test_get_content(mock_fetch_data, sample_post_url, mock_post_data):
    mock_fetch_data.return_value = mock_post_data

    post = Post(sample_post_url)
    content = post.get_content()

    assert content == mock_post_data["body_html"]
    mock_fetch_data.assert_called_once_with(force_refresh=False)

    # Test force refresh
    post.get_content(force_refresh=True)
    mock_fetch_data.assert_called_with(force_refresh=True)


@patch("substack_api.post.Post._fetch_post_data")
def test_get_content_handles_missing_content(mock_fetch_data, sample_post_url):
    # Test with missing body_html
    mock_fetch_data.return_value = {"title": "Test Post"}

    post = Post(sample_post_url)
    content = post.get_content()

    assert content is None
