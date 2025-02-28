import math
from time import sleep
from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


class Newsletter:
    """
    Newsletter class for interacting with Substack newsletters
    """

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"Newsletter: {self.url}"

    def __repr__(self):
        return f"Newsletter(url={self.url})"


def get_newsletter_post_metadata(
    newsletter_subdomain: str,
    slugs_only: bool = False,
    start_offset: int = None,
    end_offset: int = None,
) -> List:
    """
    Get available post metadata for newsletter

    Parameters
    ----------
    newsletter_subdomain : Substack subdomain of newsletter
    slugs_only : Whether to return only post slugs (needed for post content collection)
    start_page : Start page for paginated API results
    end_page : End page for paginated API results
    """
    offset_start = 0 if start_offset is None else start_offset
    offset_end = math.inf if end_offset is None else end_offset

    last_id_ref = 0
    all_posts = []

    full_url = f"https://{newsletter_subdomain}.substack.com/api/v1/archive?sort=new&search=&offset={offset_start}&limit=10"
    posts = requests.get(full_url, headers=HEADERS, timeout=30).json()

    if len(posts) == 0:
        return all_posts

    if slugs_only:
        all_posts.extend([i["slug"] for i in posts])
    else:
        all_posts.extend(posts)

    # Continue pagination only if not slugs_only
    if not slugs_only:
        last_id_ref = posts[-1]["id"]
        offset_start += 10
        sleep(1)

        while offset_start < offset_end:
            full_url = f"https://{newsletter_subdomain}.substack.com/api/v1/archive?sort=new&search=&offset={offset_start}&limit=10"
            posts = requests.get(full_url, headers=HEADERS, timeout=30).json()

            if len(posts) == 0:
                break

            last_id = posts[-1]["id"]
            if last_id == last_id_ref:
                break

            last_id_ref = last_id

            all_posts.extend(posts)

            offset_start += 10
            sleep(1)

    return all_posts


def get_post_contents(
    newsletter_subdomain: str, slug: str, html_only: bool = False
) -> Union[Dict, str]:
    """
    Gets individual post metadata and contents

    Parameters
    ----------
    newsletter_subdomain : Substack subdomain of newsletter
    slug : Slug of post to retrieve (can be retrieved from `get_newsletter_post_metadata`)
    html_only : Whether to get only HTML of body text, or all metadata/content
    """
    endpoint = f"https://{newsletter_subdomain}.substack.com/api/v1/posts/{slug}"
    post_info = requests.get(endpoint, headers=HEADERS, timeout=30).json()
    if html_only:
        return post_info["body_html"]

    return post_info


def get_newsletter_recommendations(newsletter_subdomain: str) -> List[Dict[str, str]]:
    """
    Gets recommended newsletters for a given newsletter

    Parameters
    ----------
    newsletter_subdomain : Substack subdomain of newsletter
    """
    endpoint = f"https://{newsletter_subdomain}.substack.com/recommendations"
    r = requests.get(endpoint, headers=HEADERS, timeout=30)
    recs = r.text
    soup = BeautifulSoup(recs, "html.parser")
    div_elements = soup.find_all("div", class_="publication-content")
    a_elements = [div.find("a") for div in div_elements]
    titles = [i.text for i in soup.find_all("div", {"class": "publication-title"})]
    links = [i["href"].split("?")[0] for i in a_elements]
    results = [{"title": t, "url": u} for t, u in zip(titles, links)]

    return results
