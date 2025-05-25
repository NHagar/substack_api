# SubstackAuth

The `SubstackAuth` class handles authentication for accessing paywalled Substack content.

## Class Definition

```python
SubstackAuth(cookies_path: str)
```

### Parameters

- `cookies_path` (str): Path to the JSON file containing session cookies

## Properties

### `authenticated` (bool)
Whether the authentication was successful and cookies were loaded.

### `cookies_path` (str)
Path to the cookies file.

### `session` (requests.Session)
The authenticated requests session object.

## Methods

### `load_cookies() -> bool`

Load cookies from the specified file.

#### Returns

- `bool`: True if cookies were loaded successfully, False otherwise

### `get(url: str, **kwargs) -> requests.Response`

Make an authenticated GET request.

#### Parameters

- `url` (str): The URL to request
- `**kwargs`: Additional arguments passed to requests.get

#### Returns

- `requests.Response`: The response object

### `post(url: str, **kwargs) -> requests.Response`

Make an authenticated POST request.

#### Parameters

- `url` (str): The URL to request
- `**kwargs`: Additional arguments passed to requests.post

#### Returns

- `requests.Response`: The response object

## Example Usage

### Basic Authentication Setup

```python
from substack_api import SubstackAuth

# Initialize with cookies file
auth = SubstackAuth(cookies_path="my_cookies.json")

# Check if authentication succeeded
if auth.authenticated:
    print("Successfully authenticated!")
else:
    print("Authentication failed")
```

### Using with Newsletter and Post Classes

```python
from substack_api import Newsletter, Post, SubstackAuth

# Set up authentication
auth = SubstackAuth(cookies_path="cookies.json")

# Use with Newsletter
newsletter = Newsletter("https://example.substack.com", auth=auth)
posts = newsletter.get_posts(limit=5)

# Use with Post
post = Post("https://example.substack.com/p/paywalled-post", auth=auth)
content = post.get_content()
```

### Manual Authenticated Requests

```python
from substack_api import SubstackAuth

auth = SubstackAuth(cookies_path="cookies.json")

# Make authenticated GET request
response = auth.get("https://example.substack.com/api/v1/posts/123")
data = response.json()

# Make authenticated POST request
response = auth.post(
    "https://example.substack.com/api/v1/some-endpoint",
    json={"key": "value"}
)
```

## Cookie File Format

The cookies file should be in JSON format with the following structure:

```json
[
  {
    "name": "substack.sid",
    "value": "your_session_id",
    "domain": ".substack.com",
    "path": "/",
    "secure": true
  },
  {
    "name": "substack.lli",
    "value": "your_lli_value",
    "domain": ".substack.com",
    "path": "/",
    "secure": true
  },
  ...
]
```

## Error Handling

The `SubstackAuth` class handles several error conditions:

- **File not found**: If the cookies file doesn't exist, `authenticated` will be `False`
- **Invalid JSON**: If the cookies file contains invalid JSON, `load_cookies()` returns `False`
- **Missing cookies**: If required cookies are missing, authentication may fail silently

```python
from substack_api import SubstackAuth

try:
    auth = SubstackAuth(cookies_path="cookies.json")
    if not auth.authenticated:
        print("Authentication failed - check your cookies file")
except Exception as e:
    print(f"Error setting up authentication: {e}")
```

## Security Notes

- Keep your cookies file secure and private
- Don't commit cookies files to version control
- Only use your own session cookies
- Cookies may expire and need to be refreshed periodically
- Respect Substack's Terms of Service when using authentication
