# Chat

The chat module provides access to Substack publication subscriber chats, including threads and messages.

## Classes

- [`Chat`](#chat-class) - Publication chat room
- [`ChatThread`](#chatthread) - Thread within a chat
- [`ChatMessage`](#chatmessage) - Message/reply in a thread

## Exceptions

- [`ChatError`](#chaterror) - Base exception for chat-related errors
- [`ChatAuthenticationRequired`](#chatauthenticationrequired) - Authentication is required
- [`ChatAccessDenied`](#chataccessdenied) - Access is denied
- [`ChatNotFound`](#chatnotfound) - Chat/publication not found
- [`ThreadNotFound`](#threadnotfound) - Thread not found

---

## Chat Class

The `Chat` class represents a publication's community chat and provides access to threads.

### Class Definition

```python
Chat(publication_id: Union[str, int], auth: SubstackAuth)
```

### Parameters

- `publication_id` (Union[str, int]): The publication ID to access the chat for
- `auth` (SubstackAuth): Authentication handler for API requests

### Properties

#### `publication_id -> int`

The publication ID for this chat.

### Methods

#### `get_threads(limit: Optional[int] = None, force_refresh: bool = False) -> List[ChatThread]`

Get threads from the publication chat.

##### Parameters

- `limit` (Optional[int]): Maximum number of threads to return. If None, returns all.
- `force_refresh` (bool): If True, fetch fresh data from the API.

##### Returns

- `List[ChatThread]`: List of ChatThread objects.

##### Raises

- `ChatAuthenticationRequired`: If authentication is required.
- `ChatNotFound`: If the publication is not found.
- `ChatAccessDenied`: If access to the chat is denied.

#### `get_thread(thread_id: str) -> ChatThread`

Get a specific thread by its ID.

##### Parameters

- `thread_id` (str): The UUID of the thread to retrieve.

##### Returns

- `ChatThread`: The ChatThread object for the specified thread.

---

## ChatThread

The `ChatThread` class represents a thread within a publication chat.

### Class Definition

```python
ChatThread(publication_id: Union[str, int], thread_id: str, auth: SubstackAuth, _data: Optional[Dict] = None)
```

### Parameters

- `publication_id` (Union[str, int]): The publication ID this thread belongs to.
- `thread_id` (str): The unique identifier (UUID) for this thread.
- `auth` (SubstackAuth): Authentication handler for API requests.
- `_data` (Optional[Dict]): Pre-fetched thread data (for internal use).

### Properties

#### `id -> str`

The unique identifier (UUID) for this thread.

#### `body -> str`

The text content of the thread's original post.

#### `author -> Dict[str, Any]`

The author information dictionary. Contains keys like 'id', 'name', 'handle', 'photo_url'.

#### `created_at -> str`

The ISO timestamp when the thread was created.

#### `comment_count -> int`

The number of replies/comments in this thread.

#### `raw_data -> Optional[Dict[str, Any]]`

The raw thread data dictionary from the API.

### Methods

#### `get_messages(limit: Optional[int] = None, force_refresh: bool = False) -> List[ChatMessage]`

Get all messages/replies in this thread.

##### Parameters

- `limit` (Optional[int]): Maximum number of messages to return. If None, returns all.
- `force_refresh` (bool): If True, fetch fresh data from the API.

##### Returns

- `List[ChatMessage]`: List of ChatMessage objects.

##### Raises

- `ChatAuthenticationRequired`: If authentication is required.
- `ThreadNotFound`: If the thread is not found.
- `ChatAccessDenied`: If access to the thread is denied.

---

## ChatMessage

The `ChatMessage` class represents a message/reply in a chat thread.

### Class Definition

```python
ChatMessage(data: Dict[str, Any])
```

### Parameters

- `data` (Dict[str, Any]): The raw message data from the API, containing 'comment' and 'user' keys.

### Properties

#### `id -> str`

The unique identifier (UUID) for this message.

#### `body -> str`

The text content of the message.

#### `author -> Dict[str, Any]`

The author information dictionary. Contains keys like 'id', 'name', 'handle', 'photo_url'.

#### `created_at -> str`

The ISO timestamp when the message was created.

#### `media_attachments -> List[Dict[str, Any]]`

List of media attachments (images, etc.) in the message.

#### `reaction_count -> int`

The number of reactions on this message.

#### `raw_data -> Dict[str, Any]`

The complete raw data dictionary from the API.

---

## Exceptions

### ChatError

Base exception for chat-related errors. All other chat exceptions inherit from this.

```python
class ChatError(Exception): pass
```

### ChatAuthenticationRequired

Raised when authentication is required to access a chat or thread.

```python
class ChatAuthenticationRequired(ChatError): pass
```

### ChatAccessDenied

Raised when the user does not have permission to access a chat or thread.

```python
class ChatAccessDenied(ChatError): pass
```

### ChatNotFound

Raised when the specified chat/publication is not found.

```python
class ChatNotFound(ChatError): pass
```

### ThreadNotFound

Raised when the specified thread is not found.

```python
class ThreadNotFound(ChatError): pass
```

---

## Example Usage

### Basic Usage

```python
from substack_api import Chat, SubstackAuth

# Set up authentication (required for chat access)
auth = SubstackAuth(cookies_path="cookies.json")

# Access a publication's chat (using publication ID)
chat = Chat(4906951, auth=auth)

# Get recent threads
threads = chat.get_threads(limit=5)
for thread in threads:
    print(f"Thread: {thread.body[:80]}...")
    print(f"  By: {thread.author['name']} on {thread.created_at}")
    print(f"  {thread.comment_count} messages")
```

### Reading Messages in a Thread

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

        # Check for media attachments
        if msg.media_attachments:
            print(f"  Attachments: {len(msg.media_attachments)}")
```

### Accessing a Specific Thread

```python
from substack_api import Chat, SubstackAuth

auth = SubstackAuth(cookies_path="cookies.json")
chat = Chat(4906951, auth=auth)

# Get a specific thread by ID
thread = chat.get_thread("4e1f8bb1-cea6-4bc9-889d-e8856df852d0")
messages = thread.get_messages()

print(f"Thread has {len(messages)} messages")
```

### Error Handling

```python
from substack_api import Chat, SubstackAuth
from substack_api.chat import (
    ChatAuthenticationRequired,
    ChatAccessDenied,
    ChatNotFound,
    ThreadNotFound,
)

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
