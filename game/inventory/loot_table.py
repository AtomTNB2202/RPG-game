# game/loot_table.py

import random


class LootEntry:
    def __init__(self, item_id, chance, min_amount=1, max_amount=1):
        self.item_id = item_id
        self.chance = chance
        self.min_amount = min_amount
        self.max_amount = max_amount


class LootTable:
    def __init__(self, entries=None):
        self.entries = entries or []

    @classmethod
    def from_data(cls, loot_data):
        entries = []

        for entry in loot_data:
            entries.append(
                LootEntry(
                    item_id=entry["item_id"],
                    chance=entry.get("chance", 1.0),
                    min_amount=entry.get("min_amount", 1),
                    max_amount=entry.get("max_amount", 1)
                )
            )

        return cls(entries)
    
    def roll(self):
        drops = []

        for entry in self.entries:
            if random.random() <= entry.chance:
                amount = random.randint(entry.min_amount, entry.max_amount)

                drops.append({
                    "item_id": entry.item_id,
                    "amount": amount
                })

        return drops