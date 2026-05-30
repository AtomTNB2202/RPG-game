from game.enemies.enemy import Enemy
from game.data_loader import get_enemy_data


def create_enemy(enemy_id):
    enemy_data = get_enemy_data(enemy_id)

    if enemy_data is None:
        raise ValueError(f"Enemy id not found: {enemy_id}")

    enemy = Enemy(
        enemy_id=enemy_id,
        name=enemy_data["name"],
        strength=enemy_data["strength"],
        speed=enemy_data["speed"],
        endurance=enemy_data["endurance"],
        body_parts_data=enemy_data.get("body_parts", {}),
        instant_death_parts=enemy_data.get("instant_death_parts", []),
        weak_parts=enemy_data.get("weak_parts", {}),
        intents=enemy_data.get("intents", [])
    )

    return enemy