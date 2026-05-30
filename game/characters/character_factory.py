# game/characters/character_factory.py

import json
from copy import deepcopy

from game.config import DATA_DIR
from game.characters.character import Character


PAIN_PROFILES_PATH = DATA_DIR / "pain_profiles.json"
CHARACTER_PRESETS_PATH = DATA_DIR / "character_presets.json"


def load_character_presets():
    with open(CHARACTER_PRESETS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_pain_profiles():
    with open(PAIN_PROFILES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def create_character(preset_id):
    presets = load_character_presets()
    pain_profiles = load_pain_profiles()

    if preset_id not in presets:
        raise ValueError(f"Unknown character preset: {preset_id}")

    data = presets[preset_id]

    attributes = data["attributes"]
    base_stats = data["base_stats"]
    progression = data.get("progression", {})

    pain_profile_id = data.get("pain_profile", "normal")

    if pain_profile_id not in pain_profiles:
        raise ValueError(f"Unknown pain profile: {pain_profile_id}")

    pain_config = deepcopy(pain_profiles[pain_profile_id])
    pain_config.update(data.get("pain", {}))

    guard_stances = data.get("guard_stances", {})

    for stance in guard_stances.values():
        stance["good_against"] = set(stance.get("good_against", []))

    return Character(
        name=data["name"],
        strength=attributes["strength"],
        endurance=attributes["endurance"],
        agility=attributes["agility"],
        intelligence=attributes["intelligence"],
        base_hp=base_stats["base_hp"],
        base_mp=base_stats["base_mp"],
        base_attack=base_stats["base_attack"],
        base_defense=base_stats["base_defense"],
        base_speed=base_stats.get("base_speed", 0),
        pain_profile=pain_config,
        level=progression.get("level", 1),
        exp=progression.get("exp", 0),
        exp_to_next_level=progression.get("exp_to_next_level", 100),
        attribute_points=progression.get("attribute_points", 0),
        attribute_points_per_level=progression.get("attribute_points_per_level", 3),
        exp_multiplier=progression.get("exp_multiplier", 1.25),
        guard_stances=guard_stances,
        skill_ids=data.get("skills", [])
    )