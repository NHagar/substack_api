from typing import List, Tuple

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


def list_all_categories() -> List[Tuple[str, int]]:
    """
    Get name / id representations of all newsletter categories
    """
    endpoint_cat = "https://substack.com/api/v1/categories"
    r = requests.get(endpoint_cat, headers=HEADERS, timeout=30)
    categories = [(i["name"], i["id"]) for i in r.json()]
    return categories


class Category:
    """
    Top-level newsletter category
    """

    def __init__(self, name: str = None, id: int = None):
        self.name = name
        self.id = id

        # Retrieve missing attributes if only one of name or id is provided
        if self.name and self.id is None:
            self._get_id_from_name()
        elif self.id and self.name is None:
            self._get_name_from_id()

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return f"Category(name={self.name}, id={self.id})"

    def _get_id_from_name(self):
        """
        Lookup category ID based on name
        """
        categories = list_all_categories()
        for name, id in categories:
            if name == self.name:
                self.id = id
                return
        raise ValueError(f"Category name '{self.name}' not found")

    def _get_name_from_id(self):
        """
        Lookup category name based on ID
        """
        categories = list_all_categories()
        for name, id in categories:
            if id == self.id:
                self.name = name
                return
        raise ValueError(f"Category ID {self.id} not found")

    def get_newsletters(self, include_all_metadata: bool = False) -> List[str]:
        """
        Get newsletters in category
        """
        endpoint = f"https://substack.com/api/v1/category/public/{self.id}/all"
        r = requests.get(endpoint, headers=HEADERS, timeout=30)
        r.raise_for_status()

        if include_all_metadata:
            newsletters = r.json()["publications"]
        else:
            newsletters = [i["id"] for i in r.json()["publications"]]
        return newsletters
