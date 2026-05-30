from typing import Any, Literal, NotRequired, Protocol, TypedDict
from game.skills.skill_manager import get_character_skills, get_skill

from game.combat.combat_calculator import (
    actor_goes_first,
    calculate_damage,
    calculate_enemy_hp_damage_from_part,
    calculate_guarded_damage,
    calculate_pain_gain,
    calculate_skill_damage,
    calculate_skill_hit_chance,
    check_dodge,
    choose_random_actor,
    roll_hit,
)


class PartyActor(Protocol):
    name: str
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    pain: int
    max_pain: int
    attack: int
    defense: int
    speed: int
    dodge_chance: float
    status_resistance: float
    unconscious_turns: int
    skill_ids: list[str]

    def is_alive(self) -> bool:
        ...

    def is_unconscious(self) -> bool:
        ...

    def get_pain_stage(self) -> str:
        ...

    def get_pain_effect(self) -> dict[str, Any]:
        ...

    def get_effective_attack(self) -> int:
        ...

    def get_effective_defense(self) -> int:
        ...

    def get_effective_speed(self) -> int:
        ...

    def get_effective_dodge_chance(self) -> float:
        ...

    def advance_unconscious_turn(self) -> list[str]:
        ...

    def get_pain_percent(self) -> float:
        ...

    def can_use_skill(self, skill_data) -> bool:
        ...

    def spend_mp(self, amount: int) -> bool:
        ...


class PartyAction(TypedDict):
    type: Literal["attack", "skill", "guard", "analyze", "run", "invalid"]
    actor: NotRequired[PartyActor]
    target_part: NotRequired[str]
    skill_id: NotRequired[str]


def make_combat_result(outcome, rounds, enemy_start_hp, enemy):
    """
    This is the data Encounter needs to calculate rewards.
    """
    return {
        "outcome": outcome,
        "rounds": rounds,
        "enemy_start_hp": enemy_start_hp,
        "enemy_end_hp": enemy.hp,
    }


def apply_damage_to_enemy_part(enemy, part_key, part_damage):
    target_part = enemy.body_parts[part_key]
    target_part.take_damage(part_damage)

    instant_death_triggered = False

    if target_part.is_disabled() and part_key in enemy.instant_death_parts:
        enemy.trigger_instant_death(part_key)
        instant_death_triggered = True
        return target_part, 0, instant_death_triggered

    hp_damage = calculate_enemy_hp_damage_from_part(part_key, part_damage)
    enemy.hp = max(0, enemy.hp - hp_damage)

    return target_part, hp_damage, instant_death_triggered


def apply_damage_to_character(character, hp_damage):
    character.hp = max(0, character.hp - hp_damage)
    pain_gain = character.add_pain(calculate_pain_gain(character, hp_damage))
    return hp_damage, pain_gain


def resolve_player_attack(player, enemy, part_key):
    logs = []

    if player.is_unconscious():
        return [f"{player.name} is unconscious and cannot attack."]

    target_part = enemy.body_parts[part_key]

    if not roll_hit(target_part.accuracy):
        logs.append(f"{player.name} missed the attack.")
        return logs

    if check_dodge(enemy):
        logs.append(f"{enemy.name} dodged the attack.")
        return logs

    part_damage = calculate_damage(player, enemy)
    damaged_part, hp_damage, instant_death = apply_damage_to_enemy_part(enemy, part_key, part_damage)

    logs.append(f"{player.name} attacked {enemy.name}'s {damaged_part.name}.")
    logs.append(f"Part damage: {part_damage}")

    if instant_death:
        logs.append(f"{enemy.name} was defeated instantly because a vital body part was disabled.")
        return logs

    logs.append(f"HP damage: {hp_damage}")

    if damaged_part.is_disabled():
        logs.append(f"{enemy.name}'s {damaged_part.name} is now disabled.")

    return logs


def enemy_attack(target, enemy, guard_result=None):
    logs = []

    intent = enemy.current_intent

    if check_dodge(target):
        logs.append(f"{target.name} dodged the enemy attack.")
        return logs

    base_damage = calculate_damage(
        attacker=enemy,
        defender=target,
        multiplier=intent["damage_multiplier"]
    )

    hp_damage = calculate_guarded_damage(
        base_damage=base_damage,
        guard_result=guard_result
    )

    if guard_result == "perfect_guard":
        logs.append(f"{target.name} performed a perfect guard.")

    elif guard_result == "partial_guard":
        logs.append(f"{target.name} guarded, but reacted too late.")

    hp_damage, pain_gain = apply_damage_to_character(target, hp_damage)

    logs.append(f"{enemy.name} used {intent['name']} on {target.name}.")
    logs.append(f"{target.name} lost {hp_damage} HP.")
    logs.append(
        f"{target.name}'s pain increased by {pain_gain}. "
        f"Current pain: {target.pain}/{target.max_pain}."
    )

    if target.is_unconscious():
        logs.append(f"{target.name} collapses from overwhelming pain.")

    return logs


def show_combat_status(player, enemy):
    print("\n" + "=" * 50)

    pain_stage = player.get_pain_stage()
    pain_effect = player.get_pain_effect()

    print("\nPLAYER")
    print(
        f"{player.name} | "
        f"HP: {player.hp}/{player.max_hp} | "
        f"MP: {player.mp}/{player.max_mp} | "
        f"Pain: {player.pain}/{player.max_pain} ({pain_stage})"
    )

    print(f"Attack: {player.get_effective_attack()}/{player.attack} | Defense: {player.get_effective_defense()}/{player.defense}")
    print(f"Speed: {player.get_effective_speed()}/{player.speed} | Dodge: {int(player.get_effective_dodge_chance() * 100)}%/{int(player.dodge_chance * 100)}%")
    print(f"Status Resist: {int(player.status_resistance * 100)}%")
    print(f"Pain Effect: {pain_effect['description']}")

    if player.is_unconscious():
        print(f"Condition: Unconscious for {player.unconscious_turns} turn(s)")

    print("Defense System: Guard")

    print("\nENEMY")
    print(f"{enemy.name} | HP: {enemy.hp}/{enemy.max_hp}")
    print(f"Attack: {enemy.attack} | Defense: {enemy.defense}")
    print(f"Speed: {enemy.speed} | Dodge: {int(enemy.dodge_chance * 100)}%")

    for part in enemy.body_parts.values():
        print(f"- {part}")

    print("=" * 50)


def choose_player_action(player, enemy):
    if player.is_unconscious():
        return {
            "type": "unconscious"
        }

    print("\nChoose action:")
    print("1. Attack")
    print("2. Guard")
    print("3. Analyze")
    print("4. Run")

    choice = input("> ")

    if choice == "1":
        target_part = choose_attack_target(enemy)

        if target_part is None:
            return {
                "type": "invalid"
            }

        return {
            "type": "attack",
            "target_part": target_part
        }

    elif choice == "2":
        return {
            "type": "guard"
        }

    elif choice == "3":
        return {
            "type": "analyze"
        }

    elif choice == "4":
        return {
            "type": "run"
        }

    else:
        print("Invalid action.")
        return {
            "type": "invalid"
        }


def choose_attack_target(enemy):
    print("\nChoose enemy body part to attack:")

    part_keys = list(enemy.body_parts.keys())

    for i, key in enumerate(part_keys, start=1):
        part = enemy.body_parts[key]
        print(f"{i}. {part.name} | Accuracy: {int(part.accuracy * 100)}% | {part.status}")

    choice = input("> ")

    if not choice.isdigit():
        print("Invalid choice.")
        return None

    index = int(choice) - 1

    if index < 0 or index >= len(part_keys):
        print("Invalid choice.")
        return None

    return part_keys[index]

def choose_party_member(party) -> PartyActor | None:
    alive_members = party.get_alive_members()

    if not alive_members:
        return None

    print("\nChoose party member:")

    for i, member in enumerate(alive_members, start=1):
        condition = "unconscious" if member.is_unconscious() else "ready"
        pain_percent = int(member.get_pain_percent() * 100)

        print(
            f"{i}. {member.name} | "
            f"HP: {member.hp}/{member.max_hp} | "
            f"MP: {member.mp}/{member.max_mp} | "
            f"Pain: {member.pain}/{member.max_pain} "
            f"({pain_percent}%) | "
            f"{condition}"
        )

    choice = input("> ")

    if not choice.isdigit():
        print("Invalid choice.")
        return None

    index = int(choice) - 1

    if index < 0 or index >= len(alive_members):
        print("Invalid choice.")
        return None

    selected = alive_members[index]

    if selected.is_unconscious():
        print(f"{selected.name} is unconscious and cannot act.")
        return None

    return selected

def choose_enemy_target(party) -> PartyActor | None:
    alive_members = party.get_alive_members()

    if not alive_members:
        return None

    return choose_random_actor(alive_members)

def resolve_player_action(player, enemy, action):
    action_type = action["type"]

    if action_type == "attack":
        return resolve_player_attack(player, enemy, action["target_part"]), False

    elif action_type == "guard":
        return [f"{player.name} holds their guard stance."], False

    elif action_type == "analyze":
        return analyze_enemy(enemy), False

    elif action_type == "run":
        return ["You escaped."], True

    elif action_type == "unconscious":
        return [f"{player.name} is unconscious and cannot act."], False

    return [], False

def show_party_status(party, enemy):
    print("\n" + "=" * 50)

    print("\nPARTY")

    for member in party.members:
        pain_stage = member.get_pain_stage()
        pain_effect = member.get_pain_effect()
        pain_percent = int(member.get_pain_percent() * 100)

        print(
            f"{member.name} | "
            f"HP: {member.hp}/{member.max_hp} | "
            f"MP: {member.mp}/{member.max_mp} | "
            f"Pain: {member.pain}/{member.max_pain} "
            f"({pain_percent}%, {pain_stage})"
        )

        print(
            f"  Attack: {member.get_effective_attack()}/{member.attack} | "
            f"Defense: {member.get_effective_defense()}/{member.defense} | "
            f"Speed: {member.get_effective_speed()}/{member.speed} | "
            f"Dodge: {int(member.get_effective_dodge_chance() * 100)}%/"
            f"{int(member.dodge_chance * 100)}%"
        )

        print(
            f"  STR: {member.strength} | "
            f"END: {member.endurance} | "
            f"AGI: {member.agility} | "
            f"INT: {member.intelligence} | "
            f"Attribute Points: {member.attribute_points}"
        )

        print(
            f"  Status Resist: {int(member.status_resistance * 100)}% | "
            f"Pain Resist: {int(member.pain_resistance * 100)}%"
        )

        print(f"  Pain Effect: {pain_effect['description']}")

        if member.is_unconscious():
            print(f"  Condition: Unable to fight for {member.unconscious_turns} turn(s)")

    print("\nENEMY")
    print(f"{enemy.name} | HP: {enemy.hp}/{enemy.max_hp}")
    print(f"Attack: {enemy.attack} | Defense: {enemy.defense}")
    print(f"Speed: {enemy.speed} | Dodge: {int(enemy.dodge_chance * 100)}%")

    for part in enemy.body_parts.values():
        print(f"- {part}")

    print("=" * 50)

def choose_party_action(party, enemy) -> PartyAction:
    print("\nChoose party action:")
    print("1. Attack")
    print("2. Skill")
    print("3. Guard")
    print("4. Analyze")
    print("5. Run")

    choice = input("> ")

    if choice == "1":
        actor = choose_party_member(party)

        if actor is None:
            return {"type": "invalid"}

        target_part = choose_attack_target(enemy)

        if target_part is None:
            return {"type": "invalid"}

        return {
            "type": "attack",
            "actor": actor,
            "target_part": target_part
        }
    
    elif choice == "2":
        actor = choose_party_member(party)

        if actor is None:
            return {"type": "invalid"}

        skill_id = choose_skill(actor)

        if skill_id is None:
            return {"type": "invalid"}

        skill_data = get_skill(skill_id)

        if skill_data is None:
            return {"type": "invalid"}

        action: PartyAction = {
            "type": "skill",
            "actor": actor,
            "skill_id": skill_id
        }

        if skill_data.get("target_part_required", False):
            target_part = choose_attack_target(enemy)

            if target_part is None:
                return {"type": "invalid"}

            action["target_part"] = target_part

        return action

    elif choice == "3":
        actor = choose_party_member(party)

        if actor is None:
            return {"type": "invalid"}

        return {
            "type": "guard",
            "actor": actor
        }

    elif choice == "4":
        return {
            "type": "analyze"
        }

    elif choice == "5":
        return {
            "type": "run"
        }

    else:
        print("Invalid action.")
        return {"type": "invalid"}
    
def resolve_party_action(party, enemy, action: PartyAction) -> tuple[list[str], bool]:
    action_type = action["type"]

    if action_type == "attack":
        actor = action.get("actor")
        target_part = action.get("target_part")

        if actor is None or target_part is None:
            return [], False

        return resolve_player_attack(actor, enemy, target_part), False
    
    elif action_type == "skill":
        actor = action.get("actor")
        skill_id = action.get("skill_id")
        target_part = action.get("target_part")

        if actor is None or skill_id is None:
            return [], False

        return resolve_player_skill(actor, enemy, skill_id, target_part), False

    elif action_type == "guard":
        actor = action.get("actor")

        if actor is None:
            return [], False

        return [f"{actor.name} prepares to guard."], False

    elif action_type == "analyze":
        return analyze_enemy(enemy), False

    elif action_type == "run":
        return ["The party escaped."], True

    return [], False


def analyze_enemy(enemy):
    logs = []

    logs.append("Analyze result:")
    logs.append(f"Enemy: {enemy.name}")

    if enemy.instant_death_parts:
        logs.append("Vital parts:")

        for part_key in enemy.instant_death_parts:
            part = enemy.body_parts.get(part_key)

            if part is not None:
                logs.append(
                    f"- {part.name}: disabling this part can instantly defeat {enemy.name}."
                )
    else:
        logs.append("Vital parts: None discovered.")

    if hasattr(enemy, "weak_parts") and enemy.weak_parts:
        logs.append("Weak points:")

        for part_key, description in enemy.weak_parts.items():
            part = enemy.body_parts.get(part_key)

            if part is not None:
                logs.append(
                    f"- {part.name}: {description}"
                )
    else:
        logs.append("Weak points: No obvious weakness discovered.")

    return logs


def start_combat(party, enemy):
    print(f"\nA {enemy.name} appears!")

    rounds = 0
    enemy_start_hp = enemy.hp

    while not party.is_defeated() and enemy.is_alive():
        enemy.choose_intent()
        show_party_status(party, enemy)

        print("\nEnemy Intent:")
        print(enemy.current_intent["hint"])

        party_action = choose_party_action(party, enemy)

        if party_action["type"] == "invalid":
            continue

        rounds += 1
        round_logs = []

        guarded_actor = None

        if party_action["type"] == "guard":
            guarded_actor = party_action.get("actor")

        enemy_target = choose_enemy_target(party)

        if enemy_target is None:
            break

        # Analyze/run are party-level actions.
        if party_action["type"] in {"analyze", "run"}:
            party_logs, escaped = resolve_party_action(party, enemy, party_action)
            round_logs.extend(party_logs)

            if escaped:
                print("\nRound Result:")
                for log in round_logs:
                    print(log)

                return make_combat_result(
                    outcome="escaped",
                    rounds=rounds,
                    enemy_start_hp=enemy_start_hp,
                    enemy=enemy
                )

            if enemy.is_alive():
                enemy_logs = enemy_attack(enemy_target, enemy)
                round_logs.extend(enemy_logs)

        else:
            actor = party_action.get("actor")

            if actor is None:
                continue

            if actor_goes_first(actor, enemy):
                round_logs.append(f"{actor.name} acts first.")

                party_logs, escaped = resolve_party_action(party, enemy, party_action)
                round_logs.extend(party_logs)

                if escaped:
                    print("\nRound Result:")
                    for log in round_logs:
                        print(log)

                    return make_combat_result(
                        outcome="escaped",
                        rounds=rounds,
                        enemy_start_hp=enemy_start_hp,
                        enemy=enemy
                    )

                if enemy.is_alive():
                    guard_result = None

                    if guarded_actor == enemy_target:
                        guard_result = "perfect_guard"

                    enemy_logs = enemy_attack(enemy_target, enemy, guard_result)
                    round_logs.extend(enemy_logs)

            else:
                round_logs.append("Enemy acts first.")

                guard_result = None

                if guarded_actor == enemy_target:
                    guard_result = "partial_guard"

                enemy_logs = enemy_attack(enemy_target, enemy, guard_result)
                round_logs.extend(enemy_logs)

                if actor.is_alive() and not actor.is_unconscious():
                    party_logs, escaped = resolve_party_action(party, enemy, party_action)
                    round_logs.extend(party_logs)

                    if escaped:
                        print("\nRound Result:")
                        for log in round_logs:
                            print(log)

                        return make_combat_result(
                            outcome="escaped",
                            rounds=rounds,
                            enemy_start_hp=enemy_start_hp,
                            enemy=enemy
                        )
                elif actor.is_unconscious():
                    round_logs.append(f"{actor.name} is overwhelmed by pain before acting.")

        for member in party.members:
            if member.is_alive() and member.is_unconscious():
                round_logs.extend(member.advance_unconscious_turn())

        print("\nRound Result:")
        for log in round_logs:
            print(log)

        if not enemy.is_alive():
            print(f"\nThe party defeated {enemy.name}.")
            return make_combat_result(
                outcome="victory",
                rounds=rounds,
                enemy_start_hp=enemy_start_hp,
                enemy=enemy
            )

        if party.is_defeated():
            print("\nThe party was defeated.")
            return make_combat_result(
                outcome="defeat",
                rounds=rounds,
                enemy_start_hp=enemy_start_hp,
                enemy=enemy
            )

    if party.is_defeated():
        return make_combat_result(
            outcome="defeat",
            rounds=rounds,
            enemy_start_hp=enemy_start_hp,
            enemy=enemy
        )

    return make_combat_result(
        outcome="victory",
        rounds=rounds,
        enemy_start_hp=enemy_start_hp,
        enemy=enemy
    )

def choose_skill(actor):
    available_skills = get_character_skills(actor.skill_ids)

    if not available_skills:
        print(f"{actor.name} has no skills.")
        return None

    print("\nChoose skill:")

    for i, skill in enumerate(available_skills, start=1):
        skill_id = skill["skill_id"]
        data = skill["data"]

        mp_cost = data.get("mp_cost", 0)
        usable = actor.can_use_skill(data)
        status = "usable" if usable else "not enough MP"

        print(
            f"{i}. {data['name']} | "
            f"MP Cost: {mp_cost} | "
            f"{status} | "
            f"{data.get('description', '')}"
        )

    choice = input("> ")

    if not choice.isdigit():
        print("Invalid choice.")
        return None

    index = int(choice) - 1

    if index < 0 or index >= len(available_skills):
        print("Invalid choice.")
        return None

    selected = available_skills[index]
    skill_data = selected["data"]

    if not actor.can_use_skill(skill_data):
        print(f"{actor.name} does not have enough MP.")
        return None

    return selected["skill_id"]

def resolve_player_skill(actor, enemy, skill_id: str, part_key: str | None = None):
    logs = []

    if actor.is_unconscious():
        return [f"{actor.name} is unconscious and cannot use skills."]

    skill_data = get_skill(skill_id)

    if skill_data is None:
        return [f"Unknown skill: {skill_id}."]

    if not actor.can_use_skill(skill_data):
        return [f"{actor.name} does not have enough MP to use {skill_data['name']}."]

    skill_type = skill_data.get("type", "attack")

    if skill_type != "attack":
        return [f"{skill_data['name']} is not implemented yet."]

    if skill_data.get("target_part_required", False) and part_key is None:
        return [f"{skill_data['name']} requires a target body part."]

    mp_cost = skill_data.get("mp_cost", 0)
    actor.spend_mp(mp_cost)

    if part_key is not None:
        target_part = enemy.body_parts[part_key]
        hit_chance = calculate_skill_hit_chance(skill_data, target_part)

        if not roll_hit(hit_chance):
            logs.append(f"{actor.name} used {skill_data['name']} but missed.")
            logs.append(f"{actor.name} spent {mp_cost} MP.")
            return logs

    if check_dodge(enemy):
        logs.append(f"{actor.name} used {skill_data['name']}, but {enemy.name} dodged.")
        logs.append(f"{actor.name} spent {mp_cost} MP.")
        return logs

    damage = calculate_skill_damage(actor, enemy, skill_data)

    if part_key is not None:
        damaged_part, hp_damage, instant_death = apply_damage_to_enemy_part(
            enemy,
            part_key,
            damage
        )

        logs.append(f"{actor.name} used {skill_data['name']} on {enemy.name}'s {damaged_part.name}.")
        logs.append(f"{actor.name} spent {mp_cost} MP.")
        logs.append(f"Part damage: {damage}")

        if instant_death:
            logs.append(f"{enemy.name} was defeated instantly because a vital body part was disabled.")
            return logs

        logs.append(f"HP damage: {hp_damage}")

        if damaged_part.is_disabled():
            logs.append(f"{enemy.name}'s {damaged_part.name} is now disabled.")

    else:
        enemy.hp = max(0, enemy.hp - damage)

        logs.append(f"{actor.name} used {skill_data['name']} on {enemy.name}.")
        logs.append(f"{actor.name} spent {mp_cost} MP.")
        logs.append(f"HP damage: {damage}")

    return logs