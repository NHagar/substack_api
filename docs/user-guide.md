# User Guide

## Basic Concepts

The Substack API library is organized around these main classes:

- `User` - Represents a Substack user profile
- `Newsletter` - Represents a Substack publication
- `Post` - Represents an individual post on Substack
- `Category` - Represents a Substack category of newsletters
- `Chat` - Represents a publication's subscriber chat
- `SubstackAuth` - Handles authentication for accessing paywalled content

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

### Accessing Paywalled Newsletter Content

To access paywalled posts from a newsletter, provide authentication:

```python
from substack_api import Newsletter, SubstackAuth

# Set up authentication
auth = SubstackAuth(cookies_path="cookies.json")

# Create authenticated newsletter
newsletter = Newsletter("https://example.substack.com", auth=auth)

# All retrieved posts will use authentication
posts = newsletter.get_posts(limit=10)

# Access content from paywalled posts
for post in posts:
    if post.is_paywalled():
        content = post.get_content()  # Now accessible with auth
        print(f"Paywalled content: {content[:100]}...")
```

## Working with Users

The `User` class allows you to access information about Substack users:

```python
from substack_api import User

# Create a user object
user = User("username")

# Create a user object without redirect handling (if a handle has been renamed)
user = User("username", follow_redirects=False)

# Get basic user information
user_id = user.id
name = user.name

# Get the user's subscriptions
subscriptions = user.get_subscriptions()

# Get raw user data
user_data = user.get_raw_data()

# Check if the user was redirected (handle was renamed)
if user.was_redirected:
    print(f"Original handle '{user.original_username}' was redirected to '{user.username}'")
```

### Handle Redirects

Substack users sometimes change handles. The `User` class automatically handles these redirects by default:

```python
# This will work even if "old_username" has been renamed to "new_username"
user = User("old_username")  # follow_redirects=True by default

# Check if a redirect happened
if user.was_redirected:
    print(f"User was redirected from {user.original_username} to {user.username}")
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

# Check if post is paywalled
if post.is_paywalled():
    print("This post requires a subscription")
```

### Accessing Paywalled Content

To access paywalled content, you need to provide authentication:

```python
from substack_api import Post, SubstackAuth

# Set up authentication
auth = SubstackAuth(cookies_path="cookies.json")

# Create authenticated post
post = Post("https://example.substack.com/p/paywalled-post", auth=auth)

# Now you can access paywalled content
content = post.get_content()
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

## Working with Chats

The `Chat` class allows you to access publication subscriber chats. This feature requires authentication.

```python
from substack_api import Chat, SubstackAuth

# Set up authentication (required for chat access)
auth = SubstackAuth(cookies_path="cookies.json")

# Access a publication's chat using its publication ID
chat = Chat(4906951, auth=auth)

# Get recent threads
threads = chat.get_threads(limit=5)

for thread in threads:
    print(f"Thread: {thread.body[:80]}...")
    print(f"  By: {thread.author['name']} on {thread.created_at}")
    print(f"  {thread.comment_count} messages")
```

### Reading Messages in Threads

```python
from substack_api import Chat, SubstackAuth

auth = SubstackAuth(cookies_path="cookies.json")
chat = Chat(4906951, auth=auth)

# Get threads and read messages
threads = chat.get_threads(limit=1)
if threads:
    thread = threads[0]
    messages = thread.get_messages()

    for msg in messages:
        print(f"[{msg.created_at}] {msg.author['name']}: {msg.body[:60]}...")
```

### Error Handling for Chats

```python
from substack_api import Chat, SubstackAuth
from substack_api.chat import ChatAuthenticationRequired, ChatAccessDenied, ChatNotFound

auth = SubstackAuth(cookies_path="cookies.json")
chat = Chat(4906951, auth=auth)

try:
    threads = chat.get_threads()
except ChatAuthenticationRequired:
    print("Authentication required - check your cookies")
except ChatAccessDenied:
    print("You don't have access to this chat")
except ChatNotFound:
    print("Publication not found")
```

## Authentication

The library supports authentication to access paywalled content. See the [Authentication Guide](authentication.md) for detailed information on setting up and using authentication.

```python
from substack_api import SubstackAuth

# Set up authentication
auth = SubstackAuth(cookies_path="cookies.json")

# Use with any class that supports authentication
newsletter = Newsletter("https://example.substack.com", auth=auth)
post = Post("https://example.substack.com/p/paywalled-post", auth=auth)
```

## Caching Behavior

By default, the library caches API responses to minimize the number of requests. You can force a refresh of the data by passing `force_refresh=True` to relevant methods:

```python
# Force refresh of post data
post.get_metadata(force_refresh=True)

# Force refresh of user data
user.get_raw_data(force_refresh=True)
```
