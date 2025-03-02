# Category

The `Category` class provides access to Substack newsletter categories.

## Module Functions

### `list_all_categories() -> List[Tuple[str, int]]`

Get name/id representations of all newsletter categories.

#### Returns

- `List[Tuple[str, int]]`: List of tuples containing (category_name, category_id)

## Class Definition

```python
Category(name: Optional[str] = None, id: Optional[int] = None)
```

### Parameters

- `name` (Optional[str]): The name of the category
- `id` (Optional[int]): The ID of the category

### Raises

- `ValueError`: If neither name nor id is provided, or if the provided name/id is not found

## Methods

### `_get_id_from_name() -> None`

Lookup category ID based on name.

#### Raises

- `ValueError`: If the category name is not found

### `_get_name_from_id() -> None`

Lookup category name based on ID.

#### Raises

- `ValueError`: If the category ID is not found

### `_fetch_newsletters_data(force_refresh: bool = False) -> List[Dict[str, Any]]`

Fetch the raw newsletter data from the API and cache it.

#### Parameters

- `force_refresh` (bool): Whether to force a refresh of the data, ignoring the cache

#### Returns

- `List[Dict[str, Any]]`: Full newsletter metadata

### `get_newsletter_urls() -> List[str]`

Get only the URLs of newsletters in this category.

#### Returns

- `List[str]`: List of newsletter URLs

### `get_newsletters() -> List[Newsletter]`

Get Newsletter objects for all newsletters in this category.

#### Returns

- `List[Newsletter]`: List of Newsletter objects

### `get_newsletter_metadata() -> List[Dict[str, Any]]`

Get full metadata for all newsletters in this category.

#### Returns

- `List[Dict[str, Any]]`: List of newsletter metadata dictionaries

### `refresh_data() -> None`

Force refresh of the newsletter data cache.

## Example Usage

```python
from substack_api import Category
from substack_api.category import list_all_categories

# List all available categories
categories = list_all_categories()
print("Available categories:")
for name, id in categories:
    print(f"- {name} (ID: {id})")

# Create a category object by name
tech_category = Category(name="Technology")
print(f"Selected category: {tech_category}")

# Get newsletters in this category
newsletters = tech_category.get_newsletters()
print(f"Found {len(newsletters)} newsletters in {tech_category.name} category")

# Print the first 5 newsletters
for i, newsletter in enumerate(newsletters[:5]):
    print(f"{i+1}. {newsletter.url}")

# Get detailed metadata
metadata = tech_category.get_newsletter_metadata()
for entry in metadata[:3]:
    print(f"Newsletter ID: {entry['id']}")
    print(f"Description: {entry.get('description', 'No description')[:100]}...")
    print("-" * 40)
```
