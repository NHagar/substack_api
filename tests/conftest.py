import unittest
from typing import Any, Generator
from unittest.mock import Mock, patch, MagicMock, AsyncMock

import pytest
import requests


@pytest.fixture
def mock_categories_response():
    return [
        {"id": 1, "name": "Politics"},
        {"id": 2, "name": "Technology"},
        {"id": 3, "name": "Science"},
    ]


@pytest.fixture
def mock_newsletters_response():
    return {
        "publications": [
            {"id": "newsletter1", "name": "The Daily Update", "subscribers": 1000},
            {"id": "newsletter2", "name": "Tech Weekly", "subscribers": 500},
        ],
        "more": False,
    }


@pytest.fixture
def mock_posts_response():
    return [
        {
            "id": 101,
            "slug": "first-post",
            "title": "First Post",
            "subtitle": "An introduction",
            "publish_date": "2023-01-01T12:00:00Z",
        },
        {
            "id": 102,
            "slug": "second-post",
            "title": "Second Post",
            "subtitle": "A follow-up",
            "publish_date": "2023-01-15T14:30:00Z",
        },
    ]


@pytest.fixture
def mock_post_content():
    return {
        "id": 101,
        "slug": "first-post",
        "title": "First Post",
        "subtitle": "An introduction",
        "body_html": "<p>This is the content of the first post.</p>",
        "publish_date": "2023-01-01T12:00:00Z",
        "audience": "everyone",
        "comments_count": 5,
    }


@pytest.fixture
def mock_get() -> Generator[MagicMock | AsyncMock, None, None]:
    with patch("substack_api.auth.SubstackAuth.get") as p:
        p.return_value.json.return_value = []
        p.return_value.status_code = 200
        p.return_value.reason = "OK"
        p.return_value.raise_for_status.side_effect = lambda: requests.Response.raise_for_status(p.return_value)
        yield p
