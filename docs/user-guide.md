# User Guide

## Basic Concepts

The Substack API library is organized around four main classes:

- `User` - Represents a Substack user profile
- `Newsletter` - Represents a Substack publication
- `Post` - Represents an individual post on Substack
- `Category` - Represents a Substack category of newsletters

Each class provides methods to access different aspects of the Substack ecosystem.

## Working with Newsletters

The `Newsletter` class is the main entry point for interacting with Substack publications:

```python
from substack_api import Newsletter

# Create a newsletter object
newsletter = Newsletter("https://example.substack.com")

# Get recent posts
recent_posts = newsletter.get_posts(limit=10)

# Search for posts on a specific topic
search_results = newsletter.search_posts("artificial intelligence")

# Get podcast episodes
podcasts = newsletter.get_podcasts()

# Get newsletter authors
authors = newsletter.get_authors()

# Get recommended newsletters
recommendations = newsletter.get_recommendations()
```

## Working with Users

The `User` class allows you to access information about Substack users:

```python
from substack_api import User

# Create a user object
user = User("username")

# Get basic user information
user_id = user.id
name = user.name

# Get the user's subscriptions
subscriptions = user.get_subscriptions()

# Get raw user data
user_data = user.get_raw_data()
```

## Working with Posts

The `Post` class allows you to access information about individual Substack posts:

```python
from substack_api import Post

# Create a post object
post = Post("https://example.substack.com/p/post-slug")

# Get post content
content = post.get_content()

# Get post metadata
metadata = post.get_metadata()
```

## Working with Categories

The `Category` class allows you to discover newsletters by category:

```python
from substack_api import Category

# List all available categories
from substack_api.category import list_all_categories
categories = list_all_categories()

# Create a category object
category = Category(name="Technology")
# Or by ID
category = Category(id=12)

# Get newsletters in this category
newsletters = category.get_newsletters()

# Get full metadata for newsletters in this category
newsletter_metadata = category.get_newsletter_metadata()
```

## Caching Behavior

By default, the library caches API responses to minimize the number of requests. You can force a refresh of the data by passing `force_refresh=True` to relevant methods:

```python
# Force refresh of post data
post.get_metadata(force_refresh=True)

# Force refresh of user data
user.get_raw_data(force_refresh=True)
```
