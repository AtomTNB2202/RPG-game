# game/character.py

from game.core.actor import Actor
from game.characters.pain_system import PainSystem
from game.characters.character_calculator import (
    VALID_ATTRIBUTES,
    calculate_derived_stats,
    calculate_effective_attack,
    calculate_effective_defense,
    calculate_effective_dodge_chance,
    calculate_effective_speed,
    calculate_next_exp_requirement,
    calculate_resource_after_restore,
    calculate_resource_after_spend,
    can_spend_resource,
    make_stat_snapshot,
)


class Character(Actor):
    def __init__(
        self,
        name,
        strength,
        endurance,
        agility,
        intelligence,
        base_hp,
        base_mp,
        base_attack,
        base_defense,
        base_speed,
        pain_profile,
        level=1,
        exp=0,
        exp_to_next_level=100,
        attribute_points=0,
        attribute_points_per_level=3,
        exp_multiplier=1.25,
        guard_stances=None,
        skill_ids=None
    ):
        self.strength = strength
        self.endurance = endurance
        self.agility = agility
        self.intelligence = intelligence

        self.base_hp = base_hp
        self.base_mp = base_mp
        self.base_attack = base_attack
        self.base_defense = base_defense
        self.base_speed = base_speed

        self.base_max_pain = pain_profile.get("max_pain", 100)

        derived_stats = calculate_derived_stats(self)

        max_hp = derived_stats["max_hp"]
        attack = derived_stats["attack"]
        defense = derived_stats["defense"]
        speed = derived_stats["speed"]

        super().__init__(
            name=name,
            max_hp=max_hp,
            attack=attack,
            defense=defense,
            speed=speed,
            instant_death_parts=None
        )

        self.max_mp = derived_stats["max_mp"]
        self.mp = self.max_mp

        self.level = level
        self.exp = exp
        self.exp_to_next_level = exp_to_next_level

        self.attribute_points = attribute_points
        self.attribute_points_per_level = attribute_points_per_level
        self.exp_multiplier = exp_multiplier

        self.pain_system = PainSystem(pain_profile)
        self.pain_system.max_pain = derived_stats["max_pain"]

        self.dodge_chance = derived_stats["dodge_chance"]
        self.status_resistance = derived_stats["status_resistance"]
        self.pain_resistance = derived_stats["pain_resistance"]

        self.guard_stances = guard_stances or {}

        self.skill_ids = skill_ids or []

    def gain_exp(self, amount):
        if amount <= 0:
            return []

        logs = []
        self.exp += amount
        logs.append(f"{self.name} gained {amount} EXP.")

        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            logs.extend(self.level_up())

        return logs

    def level_up(self):
        self.level += 1
        self.attribute_points += self.attribute_points_per_level

        self.exp_to_next_level = calculate_next_exp_requirement(
            current_requirement=self.exp_to_next_level,
            exp_multiplier=self.exp_multiplier
        )

        return [
            f"{self.name} leveled up!",
            f"Level: {self.level}",
            f"Gained {self.attribute_points_per_level} attribute point(s).",
            f"Available attribute points: {self.attribute_points}.",
            f"Next level requires {self.exp_to_next_level} EXP."
        ]


    def get_effective_attack(self):
        return calculate_effective_attack(
            attack=self.attack,
            pain_effect=self.get_pain_effect()
        )

    def get_effective_defense(self):
        return calculate_effective_defense(
            defense=self.defense,
            pain_effect=self.get_pain_effect()
        )


    def get_effective_speed(self):
        return calculate_effective_speed(
            speed=self.speed,
            pain_effect=self.get_pain_effect()
        )


    def get_effective_dodge_chance(self):
        return calculate_effective_dodge_chance(
            dodge_chance=self.dodge_chance,
            pain_effect=self.get_pain_effect()
        )

    @property
    def pain(self):
        return self.pain_system.pain


    @pain.setter
    def pain(self, value):
        self.pain_system.pain = max(0, min(self.max_pain, value))


    @property
    def max_pain(self):
        return self.pain_system.max_pain


    @property
    def unconscious_turns(self):
        return self.pain_system.unconscious_turns


    def get_pain_percent(self):
        return self.pain_system.get_percent()


    def is_unconscious(self):
        return self.pain_system.is_unconscious()


    def get_pain_stage(self):
        return self.pain_system.get_stage_name()


    def get_pain_effect(self):
        return self.pain_system.get_effect()


    def add_pain(self, amount):
        return self.pain_system.add_pain(amount)


    def reduce_pain(self, amount):
        return self.pain_system.reduce_pain(amount)


    def trigger_unconscious(self, turns=None):
        self.pain_system.trigger_unconscious(turns)


    def advance_unconscious_turn(self):
        logs = self.pain_system.advance_unconscious_turn()

        return [
            f"{self.name} {log}"
            for log in logs
        ]
    
    def refresh_derived_stats(self):
        old_stats = make_stat_snapshot(self)
        new_stats = calculate_derived_stats(self)

        self.attack = new_stats["attack"]
        self.defense = new_stats["defense"]
        self.speed = new_stats["speed"]

        self.max_hp = new_stats["max_hp"]
        self.max_mp = new_stats["max_mp"]
        self.pain_system.max_pain = new_stats["max_pain"]

        self.dodge_chance = new_stats["dodge_chance"]
        self.status_resistance = new_stats["status_resistance"]
        self.pain_resistance = new_stats["pain_resistance"]

        if self.max_hp > old_stats["max_hp"]:
            self.hp += self.max_hp - old_stats["max_hp"]

        if self.max_mp > old_stats["max_mp"]:
            self.mp += self.max_mp - old_stats["max_mp"]

        if self.max_pain < old_stats["max_pain"]:
            self.pain = min(self.pain, self.max_pain)

        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)

    def upgrade_attribute(self, attribute_name, amount=1):
        if attribute_name not in VALID_ATTRIBUTES:
            return [f"Invalid attribute: {attribute_name}."]

        if amount <= 0:
            return ["Upgrade amount must be positive."]

        if self.attribute_points < amount:
            return [
                f"Not enough attribute points. "
                f"Required: {amount}, available: {self.attribute_points}."
            ]

        old_stats = make_stat_snapshot(self)

        setattr(
            self,
            attribute_name,
            getattr(self, attribute_name) + amount
        )

        self.attribute_points -= amount
        self.refresh_derived_stats()
        new_stats = make_stat_snapshot(self)

        logs = [
            f"{self.name} increased {attribute_name} by {amount}.",
            f"Available attribute points: {self.attribute_points}."
        ]

        if new_stats["attack"] != old_stats["attack"]:
            logs.append(f"Attack: {old_stats['attack']} -> {new_stats['attack']}")

        if new_stats["defense"] != old_stats["defense"]:
            logs.append(f"Defense: {old_stats['defense']} -> {new_stats['defense']}")

        if new_stats["max_hp"] != old_stats["max_hp"]:
            logs.append(f"Max HP: {old_stats['max_hp']} -> {new_stats['max_hp']}")

        if new_stats["max_mp"] != old_stats["max_mp"]:
            logs.append(f"Max MP: {old_stats['max_mp']} -> {new_stats['max_mp']}")

        if new_stats["speed"] != old_stats["speed"]:
            logs.append(f"Speed: {old_stats['speed']} -> {new_stats['speed']}")

        if new_stats["dodge_chance"] != old_stats["dodge_chance"]:
            logs.append(
                f"Dodge: {int(old_stats['dodge_chance'] * 100)}% -> "
                f"{int(new_stats['dodge_chance'] * 100)}%"
            )

        if new_stats["status_resistance"] != old_stats["status_resistance"]:
            logs.append(
                f"Status Resist: {int(old_stats['status_resistance'] * 100)}% -> "
                f"{int(new_stats['status_resistance'] * 100)}%"
            )

        if new_stats["pain_resistance"] != old_stats["pain_resistance"]:
            logs.append(
                f"Pain Resist: {int(old_stats['pain_resistance'] * 100)}% -> "
                f"{int(new_stats['pain_resistance'] * 100)}%"
            )

        if new_stats["max_pain"] != old_stats["max_pain"]:
            logs.append(f"Max Pain: {old_stats['max_pain']} -> {new_stats['max_pain']}")

        return logs
    
    def get_pain_resistance(self):
        return self.pain_resistance
    
    def can_use_skill(self, skill_data):
        mp_cost = skill_data.get("mp_cost", 0)
        return can_spend_resource(self.mp, mp_cost)


    def spend_mp(self, amount):
        if amount <= 0:
            return True

        if not can_spend_resource(self.mp, amount):
            return False

        self.mp = calculate_resource_after_spend(self.mp, amount)
        return True


    def restore_mp(self, amount):
        if amount <= 0:
            return 0

        new_mp, restored_amount = calculate_resource_after_restore(
            current_amount=self.mp,
            max_amount=self.max_mp,
            restore_amount=amount
        )

        self.mp = new_mp
        return restored_amount


    def learn_skill(self, skill_id):
        if skill_id not in self.skill_ids:
            self.skill_ids.append(skill_id)