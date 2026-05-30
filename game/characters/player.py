# game/player.py

from game.characters.party import Party
from game.inventory.inventory import Inventory


class Player:
    def __init__(self, name: str, party: Party):
        self.name = name
        self.gold = 0
        self.inventory = Inventory()
        self.party = party