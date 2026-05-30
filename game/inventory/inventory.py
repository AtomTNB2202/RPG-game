# game/inventory.py

from game.inventory.item_database import get_item_data, item_exists


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, item_id, amount=1):
        if amount <= 0:
            return False

        if not item_exists(item_id):
            raise ValueError(f"Unknown item_id: {item_id}")

        self.items[item_id] = self.items.get(item_id, 0) + amount
        return True

    def remove_item(self, item_id, amount=1):
        if amount <= 0:
            return False

        if item_id not in self.items:
            return False

        if self.items[item_id] < amount:
            return False

        self.items[item_id] -= amount

        if self.items[item_id] <= 0:
            del self.items[item_id]

        return True

    def has_item(self, item_id, amount=1):
        return self.items.get(item_id, 0) >= amount

    def get_amount(self, item_id):
        return self.items.get(item_id, 0)

    def is_empty(self):
        return len(self.items) == 0

    def get_items(self):
        result = []

        for item_id, amount in self.items.items():
            item_data = get_item_data(item_id)

            result.append({
                "item_id": item_id,
                "amount": amount,
                "data": item_data
            })

        return result

    def get_total_value(self):
        total = 0

        for item_id, amount in self.items.items():
            item_data = get_item_data(item_id)

            if item_data is None:
                continue

            total += item_data.get("value", 0) * amount

        return total

    def show(self):
        if self.is_empty():
            print("Inventory: Empty")
            return

        print("Inventory:")

        for item in self.get_items():
            item_id = item["item_id"]
            amount = item["amount"]
            data = item["data"]

            name = data.get("name", item_id)
            item_type = data.get("type", "unknown")
            value = data.get("value", 0)

            print(f"- {name} x{amount} | Type: {item_type} | Value: {value}")