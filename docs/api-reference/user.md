# User

The `User` class provides access to Substack user profiles.

## Class Definition

```python
User(username: str)
```

### Parameters

- `username` (str): The Substack username

## Methods

### `_fetch_user_data(force_refresh: bool = False) -> Dict[str, Any]`

Fetch the raw user data from the API and cache it.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `Dict[str, Any]`: Full user profile data

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

## Properties

### `id` -> int

Get the user's unique ID number.

### `name` -> str

Get the user's name.

### `profile_set_up_at` -> str

Get the date when the user's profile was set up.

## Example Usage

```python
from substack_api import User

# Create a user object
user = User("username")

# Get basic user information
print(f"User ID: {user.id}")
print(f"Name: {user.name}")
print(f"Profile created: {user.profile_set_up_at}")

# Get the user's subscriptions
subscriptions = user.get_subscriptions()

# Get raw user data
user_data = user.get_raw_data()
```
