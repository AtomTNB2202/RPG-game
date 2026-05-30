# game/body_part.py

class BodyPart:
    def __init__(self, name, max_hp, accuracy=0.8):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.accuracy = accuracy
        self.status = "stable"

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.update_status()

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        self.update_status()

    def update_status(self):
        if self.hp <= 0:
            self.status = "disabled"
        elif self.hp <= self.max_hp * 0.5:
            self.status = "wounded"
        else:
            self.status = "stable"

    def is_disabled(self):
        return self.status == "disabled"

    def __str__(self):
        return f"{self.name}: {self.hp}/{self.max_hp} ({self.status})"