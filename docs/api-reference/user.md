# User

The `User` class provides access to Substack user profiles. It also handles renamed Substack handles by following redirects.

## Class Definition

```python
User(username: str, follow_redirects: bool = True)
```

### Parameters

- `username` (str): The Substack username
- `follow_redirects` (bool): Whether to follow redirects when a handle has been renamed (default: True)

## Methods

### `_fetch_user_data(force_refresh: bool = False) -> Dict[str, Any]`

Fetch the raw user data from the API and cache it. Handles renamed accounts by following redirects when `follow_redirects` is True.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Dict[str, Any]`: Full user profile data

#### Raises

- `requests.HTTPError`: If the user cannot be found even after redirect attempts

### `get_raw_data(force_refresh: bool = False) -> Dict[str, Any]`

Get the complete raw user data.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Dict[str, Any]`: Full user profile data

### `get_subscriptions() -> List[Dict[str, Any]]`

Get newsletters the user has subscribed to.

#### Returns

- `List[Dict[str, Any]]`: List of publications the user subscribes to with domain info

### `_update_handle(new_handle: str) -> None`

Update the user's handle and endpoint.

#### Parameters

- `new_handle` (str): The new handle after redirect

## Properties

### `id` -> int

Get the user's unique ID number.

### `name` -> str

Get the user's name.

### `profile_set_up_at` -> str

Get the date when the user's profile was set up.

### `was_redirected` -> bool

Check if this user's handle was redirected from the original.

#### Returns

- `bool`: True if the handle was changed via redirect

## Helper Functions

### `resolve_handle_redirect(old_handle: str, timeout: int = 30) -> Optional[str]`

Resolve a potentially renamed Substack handle by following redirects.

#### Parameters

- `old_handle` (str): The original handle that may have been renamed
- `timeout` (int): Request timeout in seconds

#### Returns

- `Optional[str]`: The new handle if renamed, None if no redirect or on error

## Example Usage

```python
from substack_api import User

# Create a user object (automatically handles redirects)
user = User("username")

# Create a user object without redirect handling
user_no_redirect = User("username", follow_redirects=False)

# Get basic user information
print(f"User ID: {user.id}")
print(f"Name: {user.name}")
print(f"Profile created: {user.profile_set_up_at}")

# Check if the user was redirected (handle was renamed)
if user.was_redirected:
    print(f"Original handle '{user.original_username}' was redirected to '{user.username}'")

# Get the user's subscriptions
subscriptions = user.get_subscriptions()

# Get raw user data
user_data = user.get_raw_data()

# Using the standalone redirect resolver
from substack_api.user import resolve_handle_redirect

new_handle = resolve_handle_redirect("old_username")
if new_handle:
    print(f"The handle has been renamed to: {new_handle}")
```
