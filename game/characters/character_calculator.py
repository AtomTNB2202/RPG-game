# game/characters/character_calculator.py

VALID_ATTRIBUTES = {
    "strength",
    "endurance",
    "agility",
    "intelligence",
}


def calculate_attack(base_attack: int, strength: int) -> int:
    return base_attack + strength * 2


def calculate_defense(base_defense: int, strength: int) -> int:
    return base_defense + strength


def calculate_max_hp(base_hp: int, endurance: int) -> int:
    return base_hp + endurance * 10


def calculate_max_mp(base_mp: int, intelligence: int) -> int:
    return base_mp + intelligence * 5


def calculate_speed(base_speed: int, agility: int) -> int:
    return base_speed + agility


def calculate_dodge_chance(agility: int) -> float:
    return min(0.40, agility * 0.015)


def calculate_status_resistance(endurance: int) -> float:
    return min(0.50, endurance * 0.02)


def calculate_pain_resistance(strength: int) -> float:
    return min(0.40, strength * 0.015)


def calculate_max_pain(base_max_pain: int, endurance: int) -> int:
    return base_max_pain + endurance * 5


def calculate_derived_stats(character) -> dict:
    return {
        "attack": calculate_attack(character.base_attack, character.strength),
        "defense": calculate_defense(character.base_defense, character.strength),
        "max_hp": calculate_max_hp(character.base_hp, character.endurance),
        "max_mp": calculate_max_mp(character.base_mp, character.intelligence),
        "speed": calculate_speed(character.base_speed, character.agility),
        "dodge_chance": calculate_dodge_chance(character.agility),
        "status_resistance": calculate_status_resistance(character.endurance),
        "pain_resistance": calculate_pain_resistance(character.strength),
        "max_pain": calculate_max_pain(character.base_max_pain, character.endurance),
    }


def calculate_effective_attack(attack: int, pain_effect: dict) -> int:
    multiplier = pain_effect["attack_multiplier"]
    return max(1, int(attack * multiplier))


def calculate_effective_defense(defense: int, pain_effect: dict) -> int:
    multiplier = pain_effect["defense_multiplier"]
    return max(0, int(defense * multiplier))


def calculate_effective_speed(speed: int, pain_effect: dict) -> int:
    multiplier = pain_effect["speed_multiplier"]
    return max(0, int(speed * multiplier))


def calculate_effective_dodge_chance(dodge_chance: float, pain_effect: dict) -> float:
    multiplier = pain_effect["dodge_multiplier"]
    return max(0.0, dodge_chance * multiplier)


def calculate_next_exp_requirement(current_requirement: int, exp_multiplier: float) -> int:
    return int(current_requirement * exp_multiplier)


def can_spend_resource(current_amount: int, cost: int) -> bool:
    return current_amount >= cost


def calculate_resource_after_spend(current_amount: int, cost: int) -> int:
    return current_amount - cost


def calculate_resource_after_restore(current_amount: int, max_amount: int, restore_amount: int) -> tuple[int, int]:
    new_amount = min(max_amount, current_amount + restore_amount)
    restored_amount = new_amount - current_amount

    return new_amount, restored_amount


def make_stat_snapshot(character) -> dict:
    return {
        "attack": character.attack,
        "defense": character.defense,
        "max_hp": character.max_hp,
        "max_mp": character.max_mp,
        "speed": character.speed,
        "dodge_chance": character.dodge_chance,
        "status_resistance": character.status_resistance,
        "pain_resistance": character.pain_resistance,
        "max_pain": character.max_pain,
    }