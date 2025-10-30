from importlib import metadata as _metadata

from .auth import SubstackAuth
from .category import Category, list_all_categories
from .newsletter import Newsletter
from .post import Post
from .user import User, resolve_handle_redirect

try:
    # Use distribution metadata so tag-based builds report the correct version.
    __version__ = _metadata.version("substack-api")
except _metadata.PackageNotFoundError:  # pragma: no cover - occurs for editable installs
    __version__ = "0.0.0"

__all__ = [
    "User",
    "Post",
    "Category",
    "Newsletter",
    "SubstackAuth",
    "resolve_handle_redirect",
    "list_all_categories",
    "__version__",
]
