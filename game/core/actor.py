# game/actor.py

class Actor:
    def __init__(self, name, max_hp, attack, defense, speed, instant_death_parts=None):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed

        # Only actors that actually use body targeting need to fill this.
        # Player can leave this empty and use another combat system.
        self.body_parts = {}

        self.instant_death_parts = set(instant_death_parts or [])
        self.death_reason = None

    def is_alive(self):
        return self.hp > 0

    def trigger_instant_death(self, part_key):
        self.hp = 0
        self.death_reason = f"{self.name}'s {part_key} was disabled."

    def show_status(self):
        print(f"\n{self.name}")
        print(f"HP: {self.hp}/{self.max_hp}")

        if self.body_parts:
            for part in self.body_parts.values():
                print(f"- {part}")
