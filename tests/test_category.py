from unittest.mock import MagicMock, patch

import pytest

from substack_api.category import Category, list_all_categories
from substack_api.newsletter import Newsletter


@pytest.fixture
def mock_categories():
    return [
        {"name": "Technology", "id": 1},
        {"name": "Finance", "id": 2},
        {"name": "Culture", "id": 3},
    ]


@pytest.fixture
def mock_newsletters_data():
    return [
        {
            "id": 101,
            "name": "Tech Insights",
            "paid_subscriber_count": 1500,
            "base_url": "https://techinsights.substack.com",
        },
        {
            "id": 102,
            "name": "Future Tech",
            "paid_subscriber_count": 2500,
            "base_url": "https://futuretech.substack.com",
        },
        {
            "id": 103,
            "name": "AI Weekly",
            "paid_subscriber_count": 3000,
            "base_url": "https://aiweekly.substack.com",
        },
    ]


@patch("substack_api.category.requests.get")
def test_list_all_categories(mock_get, mock_categories):
    # Configure the mock response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_categories
    mock_get.return_value = mock_response

    # Call the function
    categories = list_all_categories()

    # Assert the results
    assert len(categories) == 3
    assert categories[0] == ("Technology", 1)
    assert categories[1] == ("Finance", 2)
    assert categories[2] == ("Culture", 3)

    # Verify the request was made with the correct URL
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "https://substack.com/api/v1/categories" in args[0]
    assert "timeout" in kwargs


@patch("substack_api.category.list_all_categories")
def test_category_init(mock_list_all_categories, mock_categories):
    # Test when both name and id are provided
    category = Category(name="Technology", id=1)
    assert category.name == "Technology"
    assert category.id == 1
    mock_list_all_categories.assert_not_called()

    # Reset the mock
    mock_list_all_categories.reset_mock()
    mock_list_all_categories.return_value = [
        ("Technology", 1),
        ("Finance", 2),
        ("Culture", 3),
    ]

    # Test when only name is provided
    category = Category(name="Finance")
    assert category.name == "Finance"
    assert category.id == 2
    mock_list_all_categories.assert_called_once()

    # Reset the mock
    mock_list_all_categories.reset_mock()

    # Test when only id is provided
    category = Category(id=3)
    assert category.name == "Culture"
    assert category.id == 3
    mock_list_all_categories.assert_called_once()


def test_category_string_representation():
    category = Category(name="Technology", id=1)
    assert str(category) == "Technology (1)"
    assert repr(category) == "Category(name=Technology, id=1)"


@patch("substack_api.category.list_all_categories")
def test_get_id_from_name(mock_list_all_categories):
    categories_data = [
        ("Technology", 1),
        ("Finance", 2),
        ("Culture", 3),
    ]
    mock_list_all_categories.return_value = categories_data

    # When creating a Category with just name, list_all_categories is called already
    category = Category(name="Finance")

    # It should have already retrieved the ID during initialization
    assert category.id == 2
    assert mock_list_all_categories.call_count == 1

    # When calling _get_id_from_name explicitly, it should call list_all_categories again
    category._get_id_from_name()
    assert category.id == 2
    assert mock_list_all_categories.call_count == 2

    # Test with invalid name
    mock_list_all_categories.reset_mock()
    mock_list_all_categories.return_value = categories_data

    # This should raise the error during initialization
    with pytest.raises(ValueError, match="Category name 'Invalid' not found"):
        Category(name="Invalid")

    assert mock_list_all_categories.call_count == 1


@patch("substack_api.category.list_all_categories")
def test_get_name_from_id(mock_list_all_categories):
    categories_data = [
        ("Technology", 1),
        ("Finance", 2),
        ("Culture", 3),
    ]
    mock_list_all_categories.return_value = categories_data

    # When creating a Category with just id, list_all_categories is called already
    category = Category(id=3)

    # It should have already retrieved the name during initialization
    assert category.name == "Culture"
    assert mock_list_all_categories.call_count == 1

    # When calling _get_name_from_id explicitly, it should call list_all_categories again
    category._get_name_from_id()
    assert category.name == "Culture"
    assert mock_list_all_categories.call_count == 2

    # Test with invalid id
    mock_list_all_categories.reset_mock()
    mock_list_all_categories.return_value = categories_data

    # This should raise the error during initialization
    with pytest.raises(ValueError, match="Category ID 999 not found"):
        Category(id=999)

    assert mock_list_all_categories.call_count == 1


@patch("substack_api.category.requests.get")
def test_fetch_newsletters_data(mock_get, mock_newsletters_data):
    # Create mock responses for pagination
    mock_response1 = MagicMock()
    mock_response1.json.return_value = {
        "publications": mock_newsletters_data[:2],
        "more": True,
    }

    mock_response2 = MagicMock()
    mock_response2.json.return_value = {
        "publications": mock_newsletters_data[2:],
        "more": False,
    }

    mock_get.side_effect = [mock_response1, mock_response2]

    # Initialize category
    category = Category(name="Technology", id=1)

    # First call should fetch data
    result = category._fetch_newsletters_data()
    assert len(result) == 3
    assert result == mock_newsletters_data[:2] + mock_newsletters_data[2:]
    assert mock_get.call_count == 2

    # Second call should use cached data
    mock_get.reset_mock()
    result = category._fetch_newsletters_data()
    mock_get.assert_not_called()

    # Force refresh should fetch new data
    mock_get.reset_mock()
    mock_get.side_effect = [mock_response1, mock_response2]
    result = category._fetch_newsletters_data(force_refresh=True)
    assert mock_get.call_count == 2


@patch("substack_api.category.Category._fetch_newsletters_data")
def test_get_newsletter_urls(mock_fetch_data, mock_newsletters_data):
    mock_fetch_data.return_value = mock_newsletters_data

    category = Category(name="Technology", id=1)
    urls = category.get_newsletter_urls()

    assert urls == [
        "https://techinsights.substack.com",
        "https://futuretech.substack.com",
        "https://aiweekly.substack.com",
    ]
    mock_fetch_data.assert_called_once()


@patch("substack_api.category.Category.get_newsletter_urls")
def test_get_newsletters(mock_get_urls):
    # Setup mock URLs to return
    mock_urls = [
        "https://techinsights.substack.com",
        "https://futuretech.substack.com",
        "https://aiweekly.substack.com",
    ]
    mock_get_urls.return_value = mock_urls

    # Call the method
    category = Category(name="Technology", id=1)
    newsletters = category.get_newsletters()

    # Verify the results
    assert len(newsletters) == 3
    assert all(isinstance(newsletter, Newsletter) for newsletter in newsletters)
    assert newsletters[0].url == "https://techinsights.substack.com"
    assert newsletters[1].url == "https://futuretech.substack.com"
    assert newsletters[2].url == "https://aiweekly.substack.com"

    # Verify get_newsletter_urls was called
    mock_get_urls.assert_called_once()


@patch("substack_api.category.Category._fetch_newsletters_data")
def test_get_newsletter_metadata(mock_fetch_data, mock_newsletters_data):
    mock_fetch_data.return_value = mock_newsletters_data

    category = Category(name="Technology", id=1)
    metadata = category.get_newsletter_metadata()

    assert metadata == mock_newsletters_data
    mock_fetch_data.assert_called_once()


@patch("substack_api.category.Category._fetch_newsletters_data")
def test_refresh_data(mock_fetch_data):
    category = Category(name="Technology", id=1)
    category.refresh_data()

    mock_fetch_data.assert_called_with(force_refresh=True)
