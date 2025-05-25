# Substack API

An unofficial Python library for interacting with Substack.

## Overview

The Substack API library provides a simple interface to interact with Substack newsletters, users, posts, and categories. This unofficial API wrapper allows you to:

- Browse newsletter content
- Retrieve user profiles and subscriptions
- Access post content and metadata
- Discover newsletters by category
- Access paywalled content **that you have access to** with user-provided authentication

## Quick Start

```python
from substack_api import Newsletter, User, Post, Category, SubstackAuth

# Get information about a newsletter
newsletter = Newsletter("https://example.substack.com")
posts = newsletter.get_posts(limit=5)

# Get information about a user
user = User("username")
subscriptions = user.get_subscriptions()

# Get information about a post
post = Post("https://example.substack.com/p/post-slug")
content = post.get_content()

# Browse newsletters by category
tech_category = Category(name="Technology")
tech_newsletters = tech_category.get_newsletters()

# Access paywalled content with authentication
auth = SubstackAuth(cookies_path="cookies.json")
authenticated_post = Post("https://example.substack.com/p/paywalled-post", auth=auth)
paywalled_content = authenticated_post.get_content()
```

## Features

- Simple, intuitive API
- Comprehensive access to Substack data
- Pagination support for large collections
- Automatic caching to minimize API calls
- Authentication support for accessing paywalled content

## Important Note

This is an **unofficial** API wrapper. It is not affiliated with or endorsed by Substack. Be mindful of Substack's terms of service when using this library.
