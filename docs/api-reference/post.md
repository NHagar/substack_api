# Post

The `Post` class provides access to individual Substack posts.

## Class Definition

```python
Post(url: str)
```

### Parameters

- `url` (str): The URL of the Substack post

## Methods

### `_fetch_post_data(force_refresh: bool = False) -> Dict[str, Any]`

Fetch the raw post data from the API and cache it.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Dict[str, Any]`: Full post metadata

### `get_metadata(force_refresh: bool = False) -> Dict[str, Any]`

Get metadata for the post.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Dict[str, Any]`: Full post metadata

### `get_content(force_refresh: bool = False) -> Optional[str]`

Get the HTML content of the post.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Optional[str]`: HTML content of the post, or None if not available

## Example Usage

```python
from substack_api import Post

# Create a post object
post = Post("https://example.substack.com/p/post-slug")

# Get post metadata
metadata = post.get_metadata()
print(f"Title: {metadata['title']}")
print(f"Published: {metadata['post_date']}")

# Get post content
content = post.get_content()
print(f"Content length: {len(content) if content else 0}")

# Check if the post is paywalled
is_paywalled = metadata.get("audience") == "only_paid"
print(f"Paywalled: {is_paywalled}")
```
