from unittest.mock import MagicMock

import pytest

from substack_api.chat import (
    Chat,
    ChatAccessDenied,
    ChatAuthenticationRequired,
    ChatError,
    ChatMessage,
    ChatNotFound,
    ChatPaymentRequired,
    ChatThread,
    ThreadNotFound,
)


@pytest.fixture
def sample_threads_data():
    return {
        "threads": [
            {
                "communityPost": {
                    "id": "test-thread-uuid-1",
                    "created_at": "2026-01-20T14:32:07.059Z",
                    "body": "Test thread body content",
                    "comment_count": 5,
                    "user_id": 12345,
                },
                "user": {
                    "id": 12345,
                    "name": "Test User",
                    "handle": "testuser",
                    "photo_url": "https://example.com/photo.jpg",
                },
            }
        ]
    }


@pytest.fixture
def sample_comments_data():
    return {
        "post": {
            "communityPost": {
                "id": "test-thread-uuid-1",
                "body": "Test thread body",
                "comment_count": 2,
            },
            "user": {"id": 12345, "name": "Test User"},
        },
        "replies": [
            {
                "comment": {
                    "id": "message-uuid-1",
                    "body": "First reply message",
                    "created_at": "2026-01-20T14:39:02.189Z",
                    "mediaAttachments": [],
                    "reaction_count": 0,
                },
                "user": {"id": 12345, "name": "Test User", "handle": "testuser"},
            },
            {
                "comment": {
                    "id": "message-uuid-2",
                    "body": "Second reply message",
                    "created_at": "2026-01-20T15:00:00.000Z",
                    "mediaAttachments": [{"type": "image", "url": "https://example.com/img.png"}],
                    "reaction_count": 2,
                },
                "user": {"id": 67890, "name": "Another User", "handle": "another"},
            },
        ],
        "more": False,
    }


@pytest.fixture
def mock_auth():
    """Create a mock authenticated SubstackAuth object."""
    auth = MagicMock()
    auth.authenticated = True
    return auth


@pytest.fixture
def mock_unauth():
    """Create a mock unauthenticated SubstackAuth object."""
    auth = MagicMock()
    auth.authenticated = False
    return auth


# ============================================================
# ChatMessage Tests
# ============================================================


class TestChatMessage:
    def test_init(self, sample_comments_data):
        """Test ChatMessage initialization."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message._data == reply_data

    def test_id_property(self, sample_comments_data):
        """Test ChatMessage.id property."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.id == reply_data["comment"]["id"]

    def test_body_property(self, sample_comments_data):
        """Test ChatMessage.body property."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.body == reply_data["comment"]["body"]

    def test_author_property(self, sample_comments_data):
        """Test ChatMessage.author property."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.author == reply_data["user"]
        assert "name" in message.author
        assert "handle" in message.author

    def test_created_at_property(self, sample_comments_data):
        """Test ChatMessage.created_at property."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.created_at == reply_data["comment"]["created_at"]

    def test_media_attachments_property(self, sample_comments_data):
        """Test ChatMessage.media_attachments property."""
        # Test message with attachments
        reply_with_media = sample_comments_data["replies"][1]
        message = ChatMessage(reply_with_media)
        assert message.media_attachments == reply_with_media["comment"]["mediaAttachments"]

    def test_media_attachments_empty(self):
        """Test ChatMessage.media_attachments returns empty list when none."""
        # Create minimal data with no attachments
        reply_data = {
            "comment": {
                "id": "test-id",
                "body": "Test message",
                "created_at": "2026-01-20T14:39:02.189Z",
                "reaction_count": 0,
            },
            "user": {"id": 12345, "name": "Test User", "handle": "testuser"},
        }
        message = ChatMessage(reply_data)
        assert message.media_attachments == []

    def test_reaction_count_property(self, sample_comments_data):
        """Test ChatMessage.reaction_count property."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.reaction_count == reply_data["comment"].get("reaction_count", 0)

    def test_raw_data_property(self, sample_comments_data):
        """Test ChatMessage.raw_data property returns full data."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert message.raw_data == reply_data

    def test_str_repr(self, sample_comments_data):
        """Test ChatMessage string representations."""
        reply_data = sample_comments_data["replies"][0]
        message = ChatMessage(reply_data)
        assert reply_data["comment"]["id"] in str(message)
        assert reply_data["comment"]["id"] in repr(message)


# ============================================================
# ChatThread Tests
# ============================================================


class TestChatThread:
    def test_init(self, mock_auth):
        """Test ChatThread initialization."""
        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )
        assert thread.publication_id == 4906951
        assert thread.thread_id == "test-uuid"
        assert thread.auth == mock_auth
        assert thread._thread_data is None

    def test_init_with_string_publication_id(self, mock_auth):
        """Test ChatThread initialization with string publication_id."""
        thread = ChatThread(
            publication_id="4906951",
            thread_id="test-uuid",
            auth=mock_auth,
        )
        assert thread.publication_id == 4906951
        assert isinstance(thread.publication_id, int)

    def test_init_with_data(self, mock_auth, sample_threads_data):
        """Test ChatThread initialization with pre-fetched data."""
        thread_data = sample_threads_data["threads"][0]
        thread = ChatThread(
            publication_id=4906951,
            thread_id=thread_data["communityPost"]["id"],
            auth=mock_auth,
            _data=thread_data,
        )
        assert thread._thread_data == thread_data

    def test_id_property(self, mock_auth):
        """Test ChatThread.id property returns thread_id."""
        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid-123",
            auth=mock_auth,
        )
        assert thread.id == "test-uuid-123"

    def test_body_property_with_data(self, mock_auth, sample_threads_data):
        """Test ChatThread.body property when data is pre-loaded."""
        thread_data = sample_threads_data["threads"][0]
        thread = ChatThread(
            publication_id=4906951,
            thread_id=thread_data["communityPost"]["id"],
            auth=mock_auth,
            _data=thread_data,
        )
        assert thread.body == thread_data["communityPost"]["body"]

    def test_author_property_with_data(self, mock_auth, sample_threads_data):
        """Test ChatThread.author property when data is pre-loaded."""
        thread_data = sample_threads_data["threads"][0]
        thread = ChatThread(
            publication_id=4906951,
            thread_id=thread_data["communityPost"]["id"],
            auth=mock_auth,
            _data=thread_data,
        )
        assert thread.author == thread_data["user"]

    def test_created_at_property_with_data(self, mock_auth, sample_threads_data):
        """Test ChatThread.created_at property when data is pre-loaded."""
        thread_data = sample_threads_data["threads"][0]
        thread = ChatThread(
            publication_id=4906951,
            thread_id=thread_data["communityPost"]["id"],
            auth=mock_auth,
            _data=thread_data,
        )
        assert thread.created_at == thread_data["communityPost"]["created_at"]

    def test_comment_count_property_with_data(self, mock_auth, sample_threads_data):
        """Test ChatThread.comment_count property when data is pre-loaded."""
        thread_data = sample_threads_data["threads"][0]
        thread = ChatThread(
            publication_id=4906951,
            thread_id=thread_data["communityPost"]["id"],
            auth=mock_auth,
            _data=thread_data,
        )
        assert thread.comment_count == thread_data["communityPost"]["comment_count"]

    def test_get_messages(self, mock_auth, sample_comments_data):
        """Test ChatThread.get_messages returns list of ChatMessage objects."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_comments_data
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )
        messages = thread.get_messages()

        assert len(messages) == len(sample_comments_data["replies"])
        assert all(isinstance(m, ChatMessage) for m in messages)
        mock_auth.get.assert_called_once()

    def test_get_messages_with_limit(self, mock_auth, sample_comments_data):
        """Test ChatThread.get_messages respects limit parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_comments_data
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )
        messages = thread.get_messages(limit=1)

        assert len(messages) == 1

    def test_get_messages_caching(self, mock_auth, sample_comments_data):
        """Test ChatThread.get_messages uses cached data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_comments_data
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )

        # First call - should fetch
        thread.get_messages()
        assert mock_auth.get.call_count == 1

        # Second call - should use cache
        thread.get_messages()
        assert mock_auth.get.call_count == 1

        # Force refresh - should fetch again
        thread.get_messages(force_refresh=True)
        assert mock_auth.get.call_count == 2

    def test_get_messages_paginates_before(self, mock_auth):
        """Test get_messages fetches all pages when moreBefore is True."""
        older_page = {
            "replies": [
                {"comment": {"id": "old-msg-1", "body": "Older message", "created_at": "2026-01-20T10:00:00.000Z", "mediaAttachments": [], "reaction_count": 0}, "user": {"id": 1, "name": "User A", "handle": "usera"}},
            ],
            "moreBefore": False,
            "moreAfter": False,
        }
        initial_page = {
            "post": {"communityPost": {"id": "test-uuid", "body": "thread", "comment_count": 2}, "user": {"id": 1, "name": "User A"}},
            "replies": [
                {"comment": {"id": "new-msg-1", "body": "Newer message", "created_at": "2026-01-20T14:00:00.000Z", "mediaAttachments": [], "reaction_count": 0}, "user": {"id": 2, "name": "User B", "handle": "userb"}},
            ],
            "moreBefore": True,
            "moreAfter": False,
        }

        def side_effect(url, params=None, timeout=None):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if params and "before_id" in params:
                mock_response.json.return_value = older_page
            else:
                mock_response.json.return_value = initial_page
            return mock_response

        mock_auth.get.side_effect = side_effect

        thread = ChatThread(publication_id=4906951, thread_id="test-uuid", auth=mock_auth)
        messages = thread.get_messages()

        assert len(messages) == 2
        assert messages[0].id == "old-msg-1"
        assert messages[1].id == "new-msg-1"
        assert mock_auth.get.call_count == 2

    def test_get_messages_unauthenticated(self, mock_unauth):
        """Test ChatThread.get_messages raises error when not authenticated."""
        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_unauth,
        )

        with pytest.raises(ChatAuthenticationRequired):
            thread.get_messages()

    def test_get_messages_401_response(self, mock_auth):
        """Test ChatThread.get_messages handles 401 response."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )

        with pytest.raises(ChatAuthenticationRequired):
            thread.get_messages()

    def test_get_messages_402_response(self, mock_auth):
        """Test ChatThread.get_messages handles 402 response."""
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )

        with pytest.raises(ChatPaymentRequired):
            thread.get_messages()

    def test_get_messages_403_response(self, mock_auth):
        """Test ChatThread.get_messages handles 403 response."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )

        with pytest.raises(ChatAccessDenied):
            thread.get_messages()

    def test_get_messages_404_response(self, mock_auth):
        """Test ChatThread.get_messages handles 404 response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_auth.get.return_value = mock_response

        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid",
            auth=mock_auth,
        )

        with pytest.raises(ThreadNotFound):
            thread.get_messages()

    def test_str_repr(self, mock_auth):
        """Test ChatThread string representations."""
        thread = ChatThread(
            publication_id=4906951,
            thread_id="test-uuid-123",
            auth=mock_auth,
        )
        assert "test-uuid-123" in str(thread)
        assert "4906951" in repr(thread)
        assert "test-uuid-123" in repr(thread)


# ============================================================
# Chat Tests
# ============================================================


class TestChat:
    def test_init(self, mock_auth):
        """Test Chat initialization."""
        chat = Chat(publication_id=4906951, auth=mock_auth)
        assert chat.publication_id == 4906951
        assert chat.auth == mock_auth
        assert chat._threads_data is None

    def test_init_with_string_publication_id(self, mock_auth):
        """Test Chat initialization with numeric string publication_id."""
        chat = Chat(publication_id="4906951", auth=mock_auth)
        assert chat.publication_id == 4906951
        assert isinstance(chat.publication_id, int)

    def test_init_with_subdomain(self, mock_auth, monkeypatch):
        """Test Chat initialization with a subdomain string."""
        from substack_api import chat as chat_module
        monkeypatch.setattr(chat_module, "_resolve_subdomain_to_id", lambda s: 4906951)
        c = Chat(publication_id="platformer", auth=mock_auth)
        assert c.publication_id == 4906951

    def test_init_with_unresolvable_subdomain(self, mock_auth, monkeypatch):
        """Test Chat raises ValueError when subdomain cannot be resolved."""
        from substack_api import chat as chat_module
        monkeypatch.setattr(chat_module, "_resolve_subdomain_to_id", lambda s: None)
        with pytest.raises(ValueError, match="Could not resolve subdomain"):
            Chat(publication_id="nonexistent", auth=mock_auth)

    def test_get_threads(self, mock_auth, sample_threads_data):
        """Test Chat.get_threads returns list of ChatThread objects."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_threads_data
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)
        threads = chat.get_threads()

        assert len(threads) == len(sample_threads_data["threads"])
        assert all(isinstance(t, ChatThread) for t in threads)
        mock_auth.get.assert_called_once()

    def test_get_threads_with_limit(self, mock_auth, sample_threads_data):
        """Test Chat.get_threads respects limit parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_threads_data
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)
        threads = chat.get_threads(limit=1)

        assert len(threads) == 1

    def test_get_threads_caching(self, mock_auth, sample_threads_data):
        """Test Chat.get_threads uses cached data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_threads_data
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)

        # First call - should fetch
        chat.get_threads()
        assert mock_auth.get.call_count == 1

        # Second call - should use cache
        chat.get_threads()
        assert mock_auth.get.call_count == 1

        # Force refresh - should fetch again
        chat.get_threads(force_refresh=True)
        assert mock_auth.get.call_count == 2

    def test_get_threads_unauthenticated(self, mock_unauth):
        """Test Chat.get_threads raises error when not authenticated."""
        chat = Chat(publication_id=4906951, auth=mock_unauth)

        with pytest.raises(ChatAuthenticationRequired):
            chat.get_threads()

    def test_get_threads_401_response(self, mock_auth):
        """Test Chat.get_threads handles 401 response."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)

        with pytest.raises(ChatAuthenticationRequired):
            chat.get_threads()

    def test_get_threads_402_response(self, mock_auth):
        """Test Chat.get_threads handles 402 response."""
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)

        with pytest.raises(ChatPaymentRequired):
            chat.get_threads()

    def test_get_threads_403_response(self, mock_auth):
        """Test Chat.get_threads handles 403 response."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)

        with pytest.raises(ChatAccessDenied):
            chat.get_threads()

    def test_get_threads_404_response(self, mock_auth):
        """Test Chat.get_threads handles 404 response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_auth.get.return_value = mock_response

        chat = Chat(publication_id=4906951, auth=mock_auth)

        with pytest.raises(ChatNotFound):
            chat.get_threads()

    def test_get_thread(self, mock_auth):
        """Test Chat.get_thread returns a ChatThread object."""
        chat = Chat(publication_id=4906951, auth=mock_auth)
        thread = chat.get_thread("specific-thread-uuid")

        assert isinstance(thread, ChatThread)
        assert thread.thread_id == "specific-thread-uuid"
        assert thread.publication_id == 4906951

    def test_str_repr(self, mock_auth):
        """Test Chat string representations."""
        chat = Chat(publication_id=4906951, auth=mock_auth)
        assert "4906951" in str(chat)
        assert "4906951" in repr(chat)


# ============================================================
# Exception Tests
# ============================================================


class TestExceptions:
    def test_chat_error_is_exception(self):
        """Test ChatError is an Exception."""
        assert issubclass(ChatError, Exception)

    def test_chat_authentication_required_is_chat_error(self):
        """Test ChatAuthenticationRequired inherits from ChatError."""
        assert issubclass(ChatAuthenticationRequired, ChatError)

    def test_chat_access_denied_is_chat_error(self):
        """Test ChatAccessDenied inherits from ChatError."""
        assert issubclass(ChatAccessDenied, ChatError)

    def test_chat_payment_required_is_chat_access_denied(self):
        """Test ChatPaymentRequired inherits from ChatAccessDenied."""
        assert issubclass(ChatPaymentRequired, ChatAccessDenied)

    def test_chat_not_found_is_chat_error(self):
        """Test ChatNotFound inherits from ChatError."""
        assert issubclass(ChatNotFound, ChatError)

    def test_thread_not_found_is_chat_error(self):
        """Test ThreadNotFound inherits from ChatError."""
        assert issubclass(ThreadNotFound, ChatError)

    def test_exception_message(self):
        """Test exceptions can have custom messages."""
        msg = "Custom error message"
        error = ChatError(msg)
        assert str(error) == msg


# ============================================================
# Integration-style Tests
# ============================================================


class TestIntegration:
    def test_chat_to_thread_to_messages_flow(
        self, mock_auth, sample_threads_data, sample_comments_data
    ):
        """Test the full flow from Chat -> Thread -> Messages."""
        # Mock responses for different endpoints
        def mock_get(url, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if "/posts" in url and "comments" not in url:
                mock_response.json.return_value = sample_threads_data
            else:
                mock_response.json.return_value = sample_comments_data
            return mock_response

        mock_auth.get.side_effect = mock_get

        # Get chat
        chat = Chat(publication_id=4906951, auth=mock_auth)

        # Get threads
        threads = chat.get_threads()
        assert len(threads) > 0

        # Get first thread
        thread = threads[0]
        assert isinstance(thread, ChatThread)

        # Get messages from thread
        messages = thread.get_messages()
        assert len(messages) > 0
        assert all(isinstance(m, ChatMessage) for m in messages)

        # Check message properties
        first_message = messages[0]
        assert first_message.id is not None
        assert first_message.body is not None
        assert first_message.created_at is not None


# ============================================================
# New property tests: reply_count, is_owner, pub_roles
# ============================================================


class TestChatMessageNewProperties:
    def _make_message(self, pub_roles=None, reply_count=0):
        return ChatMessage({
            "comment": {
                "id": "test-id",
                "body": "Test body",
                "created_at": "2026-01-20T14:39:02.189Z",
                "mediaAttachments": [],
                "reaction_count": 0,
                "reply_count": reply_count,
            },
            "user": {"id": 1, "name": "Test User", "handle": "testuser"},
            "pub_roles": pub_roles,
        })

    def test_reply_count_zero(self):
        msg = self._make_message(reply_count=0)
        assert msg.reply_count == 0

    def test_reply_count_nonzero(self):
        msg = self._make_message(reply_count=5)
        assert msg.reply_count == 5

    def test_is_owner_true(self):
        msg = self._make_message(pub_roles={"role": "admin"})
        assert msg.is_owner is True

    def test_is_owner_false_subscriber(self):
        msg = self._make_message(pub_roles={"role": None})
        assert msg.is_owner is False

    def test_is_owner_false_no_pub_roles(self):
        msg = self._make_message(pub_roles=None)
        assert msg.is_owner is False

    def test_pub_roles_present(self):
        roles = {"role": "admin", "membership_state": "subscribed"}
        msg = self._make_message(pub_roles=roles)
        assert msg.pub_roles == roles

    def test_pub_roles_none(self):
        msg = self._make_message(pub_roles=None)
        assert msg.pub_roles is None


# ============================================================
# get_sub_replies tests
# ============================================================


class TestGetSubReplies:
    def _sub_reply_data(self, reply_id, parent_id, body):
        return {
            "comment": {
                "id": reply_id,
                "body": body,
                "created_at": "2026-01-20T15:00:00.000Z",
                "mediaAttachments": [],
                "reaction_count": 0,
                "reply_count": 0,
                "parent_id": parent_id,
            },
            "user": {"id": 99, "name": "Replier", "handle": "replier"},
            "pub_roles": None,
        }

    def test_get_sub_replies_by_string_id(self, mock_auth):
        parent_id = "parent-uuid-1"
        sub_data = {
            "post": {},
            "parent": {},
            "replies": [
                self._sub_reply_data("sub-1", parent_id, "Sub-reply A"),
                self._sub_reply_data("sub-2", parent_id, "Sub-reply B"),
            ],
            "moreAfter": False,
            "moreBefore": False,
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sub_data
        mock_auth.get.return_value = mock_response

        thread = ChatThread(publication_id=1234, thread_id="thread-uuid", auth=mock_auth)
        sub_replies = thread.get_sub_replies(parent_id)

        assert len(sub_replies) == 2
        assert all(isinstance(sr, ChatMessage) for sr in sub_replies)
        assert sub_replies[0].id == "sub-1"
        assert sub_replies[1].id == "sub-2"
        # Verify the correct endpoint was called
        call_url = mock_auth.get.call_args[0][0]
        assert f"/community/comments/{parent_id}/comments" in call_url

    def test_get_sub_replies_by_chat_message(self, mock_auth):
        parent_id = "parent-uuid-2"
        parent_message = ChatMessage({
            "comment": {"id": parent_id, "body": "Parent", "created_at": "2026-01-20T14:00:00.000Z",
                        "mediaAttachments": [], "reaction_count": 0, "reply_count": 1},
            "user": {"id": 1, "name": "Author", "handle": "author"},
            "pub_roles": None,
        })
        sub_data = {
            "replies": [self._sub_reply_data("sub-only", parent_id, "Only sub-reply")],
            "moreAfter": False,
            "moreBefore": False,
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sub_data
        mock_auth.get.return_value = mock_response

        thread = ChatThread(publication_id=1234, thread_id="thread-uuid", auth=mock_auth)
        sub_replies = thread.get_sub_replies(parent_message)

        assert len(sub_replies) == 1
        assert sub_replies[0].body == "Only sub-reply"
        call_url = mock_auth.get.call_args[0][0]
        assert f"/community/comments/{parent_id}/comments" in call_url

    def test_get_sub_replies_401_raises(self, mock_auth):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_auth.get.return_value = mock_response

        thread = ChatThread(publication_id=1234, thread_id="thread-uuid", auth=mock_auth)
        with pytest.raises(ChatAuthenticationRequired):
            thread.get_sub_replies("some-parent-id")

    def test_get_sub_replies_404_raises(self, mock_auth):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_auth.get.return_value = mock_response

        thread = ChatThread(publication_id=1234, thread_id="thread-uuid", auth=mock_auth)
        with pytest.raises(ThreadNotFound):
            thread.get_sub_replies("nonexistent-parent-id")

    def test_get_sub_replies_paginates_after(self, mock_auth):
        parent_id = "parent-uuid-3"
        page1 = {
            "replies": [self._sub_reply_data("sub-a", parent_id, "Sub A")],
            "moreAfter": True,
            "moreBefore": False,
        }
        page2 = {
            "replies": [self._sub_reply_data("sub-b", parent_id, "Sub B")],
            "moreAfter": False,
            "moreBefore": False,
        }

        call_count = {"n": 0}

        def side_effect(url, params=None, timeout=None):
            call_count["n"] += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            if params and "after_id" in params:
                mock_response.json.return_value = page2
            else:
                mock_response.json.return_value = page1
            return mock_response

        mock_auth.get.side_effect = side_effect

        thread = ChatThread(publication_id=1234, thread_id="thread-uuid", auth=mock_auth)
        sub_replies = thread.get_sub_replies(parent_id)

        assert len(sub_replies) == 2
        assert sub_replies[0].id == "sub-a"
        assert sub_replies[1].id == "sub-b"
        assert call_count["n"] == 2
