# Newsletter

The `Newsletter` class provides access to Substack publications.

## Class Definition

```python
Newsletter(url: str)
```

### Parameters

- `url` (str): The URL of the Substack newsletter

## Methods

### `_fetch_paginated_posts(params: Dict[str, str], limit: Optional[int] = None, page_size: int = 15) -> List[Dict[str, Any]]`

Helper method to fetch paginated posts with different query parameters.

#### Parameters

- `params` (Dict[str, str]): Dictionary of query parameters to include in the API request
- `limit` (Optional[int]): Maximum number of posts to return
- `page_size` (int): Number of posts to retrieve per page request

#### Returns

- `List[Dict[str, Any]]`: List of post data dictionaries

### `get_posts(sorting: str = "new", limit: Optional[int] = None) -> List[Post]`

Get posts from the newsletter with specified sorting.

#### Parameters

- `sorting` (str): Sorting order for the posts ("new", "top", "pinned", or "community")
- `limit` (Optional[int]): Maximum number of posts to return

#### Returns

- `List[Post]`: List of Post objects

### `search_posts(query: str, limit: Optional[int] = None) -> List[Post]`

Search posts in the newsletter with the given query.

#### Parameters

- `query` (str): Search query string
- `limit` (Optional[int]): Maximum number of posts to return

#### Returns

- `List[Post]`: List of Post objects matching the search query

### `get_podcasts(limit: Optional[int] = None) -> List[Post]`

Get podcast posts from the newsletter.

#### Parameters

- `limit` (Optional[int]): Maximum number of podcast posts to return

#### Returns

- `List[Post]`: List of Post objects representing podcast posts

### `get_recommendations() -> List[Newsletter]`

Get recommended publications for this newsletter.

#### Returns

- `List[Newsletter]`: List of recommended Newsletter objects

### `get_authors() -> List[User]`

Get authors of the newsletter.

#### Returns

- `List[User]`: List of User objects representing the authors

## Example Usage

```python
from substack_api import Newsletter

# Create a newsletter object
newsletter = Newsletter("https://example.substack.com")

# Get recent posts
recent_posts = newsletter.get_posts(limit=5)
for post in recent_posts:
    metadata = post.get_metadata()
    print(f"Post: {metadata['title']}")

# Search for posts on a specific topic
search_results = newsletter.search_posts("machine learning", limit=3)
for post in search_results:
    metadata = post.get_metadata()
    print(f"Found: {metadata['title']}")

# Get podcast episodes
podcasts = newsletter.get_podcasts(limit=2)
for podcast in podcasts:
    metadata = podcast.get_metadata()
    print(f"Podcast: {metadata['title']}")

# Get newsletter authors
authors = newsletter.get_authors()
for author in authors:
    print(f"Author: {author.name}")

# Get recommended newsletters
recommendations = newsletter.get_recommendations()
for rec in recommendations:
    print(f"Recommended: {rec.url}")
```
