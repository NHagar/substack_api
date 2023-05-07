# Substack-api

**An unofficial Python wrapper around Substack's API.**

I developed this package as a lightweight tool to help researchers collect data about Substack newsletters, and to help writers archive their work off-platform. This is not a tool designed for bulk text extraction/web scraping. It supports the following functionality:

* Download full JSON metadata about newsletters by category
* Download full JSON metadata about posts by newsletter
* Download text of individual, publicly-available posts
* List newsletter categories

## Installation

`pip install substack-api`

## Usage

```from substack_api import substack_api```

List all categories on Substack:

```
substack_api.list_all_categories()
```

Get metadata for the first 2 pages of Technology newsletters:

```
substack_api.get_newsletters_in_category(4, start_page=0, end_page=2)
```

Get post metadata for the most recent 30 posts from a newsletter:

```
substack_api.get_newsletter_post_metadata("platformer", start_offset=0, end_offset=30)
```

Get post contents (HTML only) from one newsletter post:

```
substack_api.get_post_contents("platformer", "how-a-single-engineer-brought-down", html_only=True)
```