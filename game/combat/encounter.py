# game/encounter.py

from dataclasses import dataclass
from game.rewards.reward import EncounterReward
from game.combat.combat import start_combat
from game.rewards.reward_calculator import RewardCalculator

@dataclass
class EncounterResult:
    outcome: str
    reward: EncounterReward
    game_over: bool = False


class Encounter:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def start(self):
        combat_result = start_combat(self.player.party, self.enemy)
        

        # Safety fallback, in case an older combat.py still returns None.
        if combat_result is None:
            combat_result = self.infer_combat_result()
        
        self.combat_result = combat_result

        outcome = combat_result["outcome"]

        if outcome == "victory":
            return self.handle_victory()

        if outcome == "escaped":
            return self.handle_escape(combat_result)

        if outcome == "defeat":
            return self.handle_defeat()

        return EncounterResult(
            outcome="unknown",
            reward=EncounterReward(),
            game_over=False
        )

    def infer_combat_result(self):
        if self.player.party.is_defeated():
            outcome = "defeat"
        elif not self.enemy.is_alive():
            outcome = "victory"
        else:
            outcome = "escaped"

        return {
            "outcome": outcome,
            "rounds": 0,
            "enemy_start_hp": getattr(self.enemy, "max_hp", self.enemy.hp),
            "enemy_end_hp": self.enemy.hp,
        }

    def handle_victory(self):
        reward = RewardCalculator.calculate_victory_reward(
            self.enemy,
            self.combat_result
        )

        self.give_exp(reward.exp)
        self.give_gold(reward.gold)
        self.give_loot(reward.loot)

        return EncounterResult(
            outcome="victory",
            reward=reward,
            game_over=False
        )

    def handle_escape(self, combat_result):
        reward = RewardCalculator.calculate_escape_reward(
            self.enemy,
            combat_result
        )

        self.give_exp(reward.exp)

        return EncounterResult(
            outcome="escaped",
            reward=reward,
            game_over=False
        )

    def handle_defeat(self):
        return EncounterResult(
            outcome="defeat",
            reward=EncounterReward(),
            game_over=True
        )

    def give_exp(self, amount):
        if amount <= 0:
            return

        alive_members = self.player.party.get_alive_members()

        if not alive_members:
            return

        for member in alive_members:
            if hasattr(member, "gain_exp"):
                member.gain_exp(amount)

    def give_gold(self, amount):
        if amount <= 0:
            return

        self.player.gold = getattr(self.player, "gold", 0) + amount

    def give_loot(self, loot):
        if not loot:
            return

        if getattr(self.player, "inventory", None) is not None:
            for item in loot:
                self.player.inventory.add_item(
                    item["item_id"],
                    item["amount"]
                )
        else:
            self.player.loot = getattr(self.player, "loot", [])
            self.player.loot.extend(loot)
