# API Reference

This section provides detailed documentation for all modules and classes in the Substack API library.

## Modules

- [User](user.md): Access to Substack user profiles and subscriptions
- [Newsletter](newsletter.md): Access to Substack publications, posts, and podcasts
- [Post](post.md): Access to individual Substack post content and metadata
- [Category](category.md): Discovery of newsletters by category

Each module documentation includes:

- Class properties and methods
- Method parameters
- Return types
- Example usage

## Common Patterns

Most classes in the library follow these patterns:

1. **Initialization**: Create an object by providing an identifier (URL, username, etc.)
2. **Data Retrieval**: Methods that fetch data from the Substack API
3. **Caching**: Data is cached to avoid unnecessary API requests
4. **Force Refresh**: Most methods accept a `force_refresh` parameter to bypass the cache

## Error Handling

The library uses standard Python exceptions:

- `requests.exceptions.HTTPError`: Raised when an HTTP request fails
- `ValueError`: Raised when invalid parameters are provided
- `KeyError`: Raised when expected data is not found in the API response

You should wrap API calls in try/except blocks to handle these exceptions gracefully.
