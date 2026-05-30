# game/enemy.py

import random
from game.core.actor import Actor
from game.core.body_part import BodyPart


class Enemy(Actor):
    def __init__(
    self,
    enemy_id,
    name,
    strength,
    speed,
    endurance,
    body_parts_data,
    instant_death_parts=None,
    weak_parts=None,
    intents=None
):
        self.enemy_id = enemy_id
        self.strength = strength
        self.endurance = endurance

        self.base_hp = 80
        self.base_attack = 4
        self.base_defense = 1

        max_hp = self.calculate_max_hp()
        attack = self.calculate_attack()
        defense = self.calculate_defense()

        # Enemy owns body parts, weak parts, and vital parts.
        super().__init__(
            name=name,
            max_hp=max_hp,
            attack=attack,
            defense=defense,
            speed=speed,
            instant_death_parts=instant_death_parts or []
        )

        self.dodge_chance = self.calculate_dodge_chance()
        self.status_resistance = self.calculate_status_resistance()

        self.body_parts = self.create_body_parts(body_parts_data)

        self.weak_parts = weak_parts or {}

        # target_zone describes what the enemy tries to hit on the player side.
        # It does not require player.body_parts to exist.
        self.intents = intents or []

        self.current_intent = None

    def calculate_attack(self):
        return self.base_attack + self.strength * 2

    def calculate_defense(self):
        return self.base_defense + self.strength

    def calculate_max_hp(self):
        return self.base_hp + self.endurance * 8

    def calculate_dodge_chance(self):
        return min(0.35, self.speed * 0.012)

    def calculate_status_resistance(self):
        return min(0.40, self.endurance * 0.015)

    def create_body_parts(self, body_parts_data):
        if not body_parts_data:
            raise ValueError(f"Enemy {self.enemy_id} has no body_parts data.")

        body_parts = {}

        for part_key, part_data in body_parts_data.items():
            base_hp = part_data.get("base_hp", 1)
            endurance_multiplier = part_data.get("endurance_multiplier", 0)
            max_hp = base_hp + self.endurance * endurance_multiplier

            body_parts[part_key] = BodyPart(
                name=part_data.get("name", part_key.title()),
                max_hp=max_hp,
                accuracy=part_data.get("accuracy", 0.8)
            )

        return body_parts

    def choose_intent(self):
        available_intents = []

        for intent in self.intents:
            required_part = intent.get("requires_part")

            if required_part is not None:
                required_body_part = self.body_parts.get(required_part)

                if required_body_part is not None and required_body_part.is_disabled():
                    continue

            available_intents.append(intent)

        if not available_intents:
            self.current_intent = {
                "name": "weak_attack",
                "hint": "The enemy struggles to move.",
                "target_zone": "body",
                "damage_multiplier": 0.5
            }
        else:
            self.current_intent = random.choice(available_intents)

        return self.current_intent
