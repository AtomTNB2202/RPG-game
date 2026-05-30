import random


def get_attack(actor) -> int:
    if hasattr(actor, "get_effective_attack"):
        return actor.get_effective_attack()
    return actor.attack


def get_defense(actor) -> int:
    if hasattr(actor, "get_effective_defense"):
        return actor.get_effective_defense()
    return actor.defense


def get_speed(actor) -> int:
    if hasattr(actor, "get_effective_speed"):
        return actor.get_effective_speed()
    return actor.speed


def get_dodge_chance(actor) -> float:
    if hasattr(actor, "get_effective_dodge_chance"):
        return actor.get_effective_dodge_chance()
    return actor.dodge_chance


def roll_turn_priority(actor) -> int:
    return get_speed(actor) + random.randint(1, 6)

def choose_random_actor(actors):
    return random.choice(actors)


def actor_goes_first(actor, enemy) -> bool:
    return roll_turn_priority(actor) >= roll_turn_priority(enemy)


def check_dodge(target) -> bool:
    if hasattr(target, "is_unconscious") and target.is_unconscious():
        return False

    return random.random() < get_dodge_chance(target)


def calculate_damage(attacker, defender, multiplier: float = 1.0) -> int:
    raw_damage = int(get_attack(attacker) * multiplier) - get_defense(defender)
    return max(1, raw_damage)


def calculate_pain_gain(character, hp_damage: int) -> int:
    base_pain = max(4, int(hp_damage * 0.7))

    if hasattr(character, "get_pain_resistance"):
        pain_resistance = character.get_pain_resistance()
    else:
        pain_resistance = 0.0

    reduced_pain = int(base_pain * (1.0 - pain_resistance))

    return max(1, reduced_pain)


def calculate_guarded_damage(base_damage: int, guard_result: str | None) -> int:
    if guard_result == "perfect_guard":
        return max(1, int(base_damage * 0.25))

    if guard_result == "partial_guard":
        return max(1, int(base_damage * 0.65))

    return max(1, base_damage)


def calculate_enemy_hp_damage_from_part(part_key: str, part_damage: int) -> int:
    if part_key == "body":
        return part_damage

    return int(part_damage * 0.5)


def calculate_skill_damage(actor, enemy, skill_data: dict) -> int:
    damage_multiplier = skill_data.get("damage_multiplier", 1.0)

    scaling_attribute = skill_data.get("scaling_attribute")
    scaling_multiplier = skill_data.get("scaling_multiplier", 0.0)

    scaling_bonus = 0

    if scaling_attribute is not None:
        scaling_value = getattr(actor, scaling_attribute, 0)
        scaling_bonus = int(scaling_value * scaling_multiplier)

    raw_damage = (
        int(get_attack(actor) * damage_multiplier)
        + scaling_bonus
        - get_defense(enemy)
    )

    return max(1, raw_damage)


def calculate_skill_hit_chance(skill_data: dict, target_part) -> float:
    skill_accuracy = skill_data.get("accuracy", 1.0)
    return skill_accuracy * target_part.accuracy


def roll_hit(hit_chance: float) -> bool:
    return random.random() <= hit_chance