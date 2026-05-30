# game/skills/skill_manager.py

import json

from game.config import DATA_DIR


SKILLS_PATH = DATA_DIR / "skills.json"

_skills_cache = None


def load_skills():
    global _skills_cache

    if _skills_cache is None:
        with open(SKILLS_PATH, "r", encoding="utf-8") as file:
            _skills_cache = json.load(file)

    return _skills_cache


def get_skill(skill_id):
    skills = load_skills()
    return skills.get(skill_id)


def skill_exists(skill_id):
    return get_skill(skill_id) is not None


def get_character_skills(skill_ids):
    result = []

    for skill_id in skill_ids:
        skill_data = get_skill(skill_id)

        if skill_data is not None:
            result.append({
                "skill_id": skill_id,
                "data": skill_data
            })

    return result