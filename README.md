# Substack API

An unofficial Python client library for interacting with Substack newsletters and content.

## Overview

This library provides Python interfaces for interacting with Substack's unofficial API, allowing you to:

- Retrieve newsletter posts, podcasts, and recommendations
- Get user profile information and subscriptions
- Fetch post content and metadata
- Search for posts within newsletters
- Access paywalled content **that you have written or paid for** with user-provided authentication

## Installation

```bash
# Using pip
pip install substack-api

# Using poetry
poetry add substack-api
```

## Usage Examples

### Working with Newsletters

```python
from substack_api import Newsletter

# Initialize a newsletter by its URL
newsletter = Newsletter("https://example.substack.com")

# Get recent posts (returns Post objects)
recent_posts = newsletter.get_posts(limit=5)

# Get posts sorted by popularity
top_posts = newsletter.get_posts(sorting="top", limit=10)

# Search for posts
search_results = newsletter.search_posts("machine learning", limit=3)

# Get podcast episodes
podcasts = newsletter.get_podcasts(limit=5)

# Get recommended newsletters
recommendations = newsletter.get_recommendations()

# Get newsletter authors
authors = newsletter.get_authors()
```

### Working with Posts

```python
from substack_api import Post

# Initialize a post by its URL
post = Post("https://example.substack.com/p/post-slug")

# Get post metadata
metadata = post.get_metadata()

# Get the post's HTML content
content = post.get_content()
```

### Accessing Paywalled Content with Authentication

To access paywalled content, you need to provide your own session cookies from a logged-in Substack session:

```python
from substack_api import Newsletter, Post, SubstackAuth

# Set up authentication with your cookies
auth = SubstackAuth(cookies_path="path/to/your/cookies.json")

# Use authentication with newsletters
newsletter = Newsletter("https://example.substack.com", auth=auth)
posts = newsletter.get_posts(limit=5)  # Can now access paywalled posts

# Use authentication with individual posts
post = Post("https://example.substack.com/p/paywalled-post", auth=auth)
content = post.get_content()  # Can now access paywalled content

# Check if a post is paywalled
if post.is_paywalled():
    print("This post requires a subscription")
```

#### Getting Your Cookies

To access paywalled content, you need to export your browser cookies from a logged-in Substack session. The cookies should be in JSON format with the following structure:

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

**Important**: Only use your own cookies from your own authenticated session. **This feature is intended for users to access their own subscribed or authored content programmatically.**

### Working with Users

```python
from substack_api import User

# Initialize a user by their username
user = User("username")

# Get user profile information
profile_data = user.get_raw_data()

# Get user ID and name
user_id = user.id
name = user.name

# Get user's subscriptions
subscriptions = user.get_subscriptions()
```

## Limitations

- This is an unofficial library and not endorsed by Substack
- APIs may change without notice, potentially breaking functionality
- Rate limiting may be enforced by Substack
- **Authentication requires users to provide their own session cookies**
- **Users are responsible for complying with Substack's terms of service when using authentication features**

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This package is not affiliated with, endorsed by, or connected to Substack in any way. It is an independent project created to make Substack content more accessible through Python.
