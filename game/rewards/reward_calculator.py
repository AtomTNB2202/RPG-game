from game.inventory.loot_table import LootTable
from game.rewards.reward import EncounterReward
from game.data_loader import get_enemy_data
from game.rewards.reward import EncounterReward


class RewardCalculator:
    @staticmethod
    def calculate_victory_reward(enemy, combat_result):
        enemy_data = get_enemy_data(enemy.enemy_id)

        if enemy_data is None:
            return EncounterReward()

        exp = enemy_data.get("exp_reward", 0)
        gold = enemy_data.get("gold_reward", 0)

        loot_data = enemy_data.get("loot", [])
        loot_table = LootTable.from_data(loot_data)
        loot = loot_table.roll()

        return EncounterReward(
            exp=exp,
            gold=gold,
            loot=loot
        )

    @staticmethod
    def calculate_escape_reward(enemy, combat_result):
        enemy_data = get_enemy_data(enemy.enemy_id)

        if enemy_data is None:
            return EncounterReward()

        base_exp = enemy_data.get("exp_reward", 0)

        rounds = combat_result["rounds"]
        enemy_start_hp = combat_result["enemy_start_hp"]
        enemy_end_hp = combat_result["enemy_end_hp"]

        damage_dealt = max(0, enemy_start_hp - enemy_end_hp)
        damage_ratio = damage_dealt / enemy_start_hp if enemy_start_hp > 0 else 0

        if rounds < 2 and damage_ratio <= 0:
            exp = 0
        else:
            exp_ratio = min(0.40, max(0.10, damage_ratio * 0.50))
            exp = int(base_exp * exp_ratio)

        return EncounterReward(
            exp=exp,
            gold=0,
            loot=[]
        )