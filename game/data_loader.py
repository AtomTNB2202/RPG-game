# game/data_loader.py

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_items():
    return load_json("items.json")


def load_enemies():
    return load_json("enemies.json")


def load_skills():
    return load_json("skills.json")


def load_quests():
    return load_json("quests.json")


def get_item_data(item_id):
    items = load_items()
    return items.get(item_id)


def get_enemy_data(enemy_id):
    enemies = load_enemies()
    return enemies.get(enemy_id)