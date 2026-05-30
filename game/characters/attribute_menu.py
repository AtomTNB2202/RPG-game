# game/characters/attribute_menu.py

ATTRIBUTE_OPTIONS = {
    "1": {
        "key": "strength",
        "name": "Strength",
        "description": "Increase attack, defense, and pain resistance."
    },
    "2": {
        "key": "endurance",
        "name": "Endurance",
        "description": "Increase max HP, status resistance, and max pain."
    },
    "3": {
        "key": "agility",
        "name": "Agility",
        "description": "Increase speed and dodge chance."
    },
    "4": {
        "key": "intelligence",
        "name": "Intelligence",
        "description": "Increase max MP and magic skill damage."
    }
}


def show_character_attributes(character):
    print("\n" + "-" * 50)
    print(f"{character.name}")
    print(f"Level: {character.level}")
    print(f"Available attribute points: {character.attribute_points}")

    print(
        f"STR: {character.strength} | "
        f"END: {character.endurance} | "
        f"AGI: {character.agility} | "
        f"INT: {character.intelligence}"
    )

    print(
        f"Attack: {character.attack} | "
        f"Defense: {character.defense} | "
        f"Max HP: {character.max_hp} | "
        f"Max MP: {character.max_mp}"
    )

    print(
        f"Speed: {character.speed} | "
        f"Dodge: {int(character.dodge_chance * 100)}% | "
        f"Status Resist: {int(character.status_resistance * 100)}% | "
        f"Pain Resist: {int(character.pain_resistance * 100)}% | "
        f"Max Pain: {character.max_pain}"
    )
    print("-" * 50)


def allocate_attribute_points(character):
    if character.attribute_points <= 0:
        print(f"{character.name} has no attribute points.")
        return

    while character.attribute_points > 0:
        show_character_attributes(character)

        print("\nChoose attribute to upgrade:")
        for option_id, option in ATTRIBUTE_OPTIONS.items():
            print(
                f"{option_id}. {option['name']} - "
                f"{option['description']}"
            )

        print("0. Stop upgrading")

        choice = input("> ")

        if choice == "0":
            break

        if choice not in ATTRIBUTE_OPTIONS:
            print("Invalid choice.")
            continue

        attribute_key = ATTRIBUTE_OPTIONS[choice]["key"]

        logs = character.upgrade_attribute(attribute_key, 1)

        print("\nUpgrade Result:")
        for log in logs:
            print(log)

    print(f"\nFinished upgrading {character.name}.")


def allocate_party_attribute_points(party):
    while True:
        members_with_points = [
            member for member in party.members
            if member.attribute_points > 0
        ]

        if not members_with_points:
            print("\nNo party member has attribute points.")
            return

        print("\nChoose party member to upgrade:")

        for i, member in enumerate(members_with_points, start=1):
            print(
                f"{i}. {member.name} | "
                f"Level: {member.level} | "
                f"Attribute Points: {member.attribute_points}"
            )

        print("0. Stop upgrading party")

        choice = input("> ")

        if choice == "0":
            return

        if not choice.isdigit():
            print("Invalid choice.")
            continue

        index = int(choice) - 1

        if index < 0 or index >= len(members_with_points):
            print("Invalid choice.")
            continue

        selected_member = members_with_points[index]
        allocate_attribute_points(selected_member)