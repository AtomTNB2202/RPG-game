from game.characters.player import Player
from game.characters.character_factory import create_character
from game.characters.party import Party
from game.enemies.enemy_factory import create_enemy as create_enemy_from_database
from game.combat.combat import start_combat
from game.combat.encounter import Encounter
from game.characters.attribute_menu import allocate_party_attribute_points


def create_player():
    party = Party([
        create_character("hero"),
        create_character("warrior"),
    ])

    return Player(
        name="Player",
        party=party
    )


def create_enemy():
    return create_enemy_from_database("bandit")


def show_encounter_result(result):
    print("\n" + "=" * 50)
    print("ENCOUNTER RESULT")

    if result.outcome == "victory":
        print("Outcome: Victory")
        print(f"EXP gained: {result.reward.exp}")
        print(f"Gold gained: {result.reward.gold}")

        if result.reward.loot:
            print("Loot:")
            for item in result.reward.loot:
                print(f"- {item['item_id']} x{item['amount']}")
        else:
            print("Loot: None")

    elif result.outcome == "escaped":
        print("Outcome: Escaped")
        print(f"EXP gained: {result.reward.exp}")
        print("Gold gained: 0")
        print("Loot: None")

    elif result.outcome == "defeat":
        print("Outcome: Defeat")
        print("Game Over.")

    else:
        print(f"Outcome: {result.outcome}")

    print("=" * 50)


def test_combat_only():
    print("\n===== TEST COMBAT ONLY =====")

    player = create_player()
    enemy = create_enemy()

    combat_result = start_combat(player.party, enemy)

    print("\nCombat returned:")
    print(combat_result)


def test_encounter():
    print("\n===== TEST ENCOUNTER SYSTEM =====")

    player = create_player()
    enemy = create_enemy()

    encounter = Encounter(player, enemy)
    result = encounter.start()

    show_encounter_result(result)

    print("\nParty after encounter:")
    print(f"Gold: {player.gold}")

    for member in player.party.members:
        print(
            f"{member.name} | "
            f"Level: {member.level} | "
            f"EXP: {member.exp}/{member.exp_to_next_level} | "
            f"HP: {member.hp}/{member.max_hp} | "
            f"Pain: {member.pain}/{member.max_pain}"
        )

    print("\nPlayer inventory:")
    player.inventory.show()

    print("\nAttribute upgrade phase:")
    allocate_party_attribute_points(player.party)

def test_inventory_only():
    print("\n===== TEST INVENTORY ONLY =====")

    player = create_player()

    player.inventory.add_item("torn_cloth", 3)
    player.inventory.add_item("rusty_knife", 1)
    player.inventory.add_item("small_coin_pouch", 2)

    player.inventory.show()

    print("\nRemove 1 Torn Cloth")
    player.inventory.remove_item("torn_cloth", 1)

    player.inventory.show()

    print(f"\nHas Rusty Knife: {player.inventory.has_item('rusty_knife')}")
    print(f"Total inventory value: {player.inventory.get_total_value()}")

def test_attribute_points_only():
    print("\n===== TEST ATTRIBUTE POINTS ONLY =====")

    player = create_player()
    hero = player.party.members[0]

    print("\nBefore:")
    print(f"Level: {hero.level}")
    print(f"Attribute Points: {hero.attribute_points}")
    print(f"STR: {hero.strength}")
    print(f"END: {hero.endurance}")
    print(f"AGI: {hero.agility}")
    print(f"INT: {hero.intelligence}")
    print(f"Attack: {hero.attack}")
    print(f"Defense: {hero.defense}")
    print(f"Max HP: {hero.max_hp}")
    print(f"Max MP: {hero.max_mp}")
    print(f"Speed: {hero.speed}")
    print(f"Dodge: {int(hero.dodge_chance * 100)}%")
    print(f"Status Resist: {int(hero.status_resistance * 100)}%")
    print(f"Pain Resist: {int(hero.pain_resistance * 100)}%")
    print(f"Max Pain: {hero.max_pain}")

    print("\nForce level up:")
    logs = hero.level_up()
    for log in logs:
        print(log)

    print("\nUpgrade Strength:")
    for log in hero.upgrade_attribute("strength", 1):
        print(log)

    print("\nUpgrade Endurance:")
    for log in hero.upgrade_attribute("endurance", 1):
        print(log)

    print("\nUpgrade Agility:")
    for log in hero.upgrade_attribute("agility", 1):
        print(log)

    print("\nAfter:")
    print(f"Level: {hero.level}")
    print(f"Attribute Points: {hero.attribute_points}")
    print(f"STR: {hero.strength}")
    print(f"END: {hero.endurance}")
    print(f"AGI: {hero.agility}")
    print(f"INT: {hero.intelligence}")
    print(f"Attack: {hero.attack}")
    print(f"Defense: {hero.defense}")
    print(f"Max HP: {hero.max_hp}")
    print(f"Max MP: {hero.max_mp}")
    print(f"Speed: {hero.speed}")
    print(f"Dodge: {int(hero.dodge_chance * 100)}%")
    print(f"Status Resist: {int(hero.status_resistance * 100)}%")
    print(f"Pain Resist: {int(hero.pain_resistance * 100)}%")
    print(f"Max Pain: {hero.max_pain}")

def test_attribute_upgrade_menu():
    print("\n===== TEST ATTRIBUTE UPGRADE MENU =====")

    player = create_player()

    for member in player.party.members:
        member.attribute_points = 3

    allocate_party_attribute_points(player.party)

    print("\nParty after upgrading:")

    for member in player.party.members:
        print(
            f"{member.name} | "
            f"STR: {member.strength} | "
            f"END: {member.endurance} | "
            f"AGI: {member.agility} | "
            f"INT: {member.intelligence} | "
            f"Points: {member.attribute_points}"
        )


def main():
    print("\nChoose test mode:")
    print("1. Test combat only")
    print("2. Test encounter system")
    print("3. Test both")
    print("4. Test inventory only")
    print("5. Test attribute points only")

    choice = input("> ")

    if choice == "1":
        test_combat_only()

    elif choice == "2":
        test_encounter()

    elif choice == "3":
        test_combat_only()
        test_encounter()

    elif choice == "4":
        test_inventory_only()
    
    elif choice == "5":
        test_attribute_points_only()

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()