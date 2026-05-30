# demo_combat_ui.py

from game.combat.combat_session import CombatSession
from game.UI.pygame_combat_ui import CombatUI

from game.characters.character_factory import create_character
from game.enemies.enemy_factory import create_enemy


class DemoParty:
    def __init__(self, members):
        self.members = members

    def get_alive_members(self):
        return [
            member
            for member in self.members
            if member.is_alive()
        ]

    def is_defeated(self):
        return len(self.get_alive_members()) == 0


def create_default_party():
    hero = create_character("hero")

    return DemoParty([
        hero
    ])


def main():
    party = create_default_party()
    enemy = create_enemy("bandit")

    session = CombatSession(party, enemy)
    ui = CombatUI(session)
    ui.run()


if __name__ == "__main__":
    main()