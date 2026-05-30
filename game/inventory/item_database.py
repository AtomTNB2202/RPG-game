# game/inventory/item_database.py

import json

from game.config import DATA_DIR


ITEMS_PATH = DATA_DIR / "items.json"

_items_cache = None


def load_items():
    global _items_cache

    if _items_cache is None:
        with open(ITEMS_PATH, "r", encoding="utf-8") as file:
            _items_cache = json.load(file)

    return _items_cache


def get_item_data(item_id):
    items = load_items()
    return items.get(item_id)


def item_exists(item_id):
    return get_item_data(item_id) is not None