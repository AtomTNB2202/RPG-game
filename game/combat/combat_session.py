# game/combat/combat_session.py

from game.combat.combat import (
    choose_enemy_target,
    enemy_attack,
    make_combat_result,
    resolve_party_action,
)
from game.combat.combat_calculator import actor_goes_first


class CombatSession:
    def __init__(self, party, enemy):
        self.party = party
        self.enemy = enemy

        self.rounds = 0
        self.enemy_start_hp = enemy.hp

        self.logs = [f"A {enemy.name} appears!"]

        self.finished = False
        self.result = None

        self.enemy.choose_intent()

    def submit_action(self, action):
        if self.finished:
            return ["Combat is already finished."]

        if action["type"] == "invalid":
            return ["Invalid action."]

        round_logs = []
        self.rounds += 1

        enemy_target = choose_enemy_target(self.party)

        if enemy_target is None:
            self.finish("defeat")
            return ["No party member can be targeted."]

        if action["type"] in {"analyze", "run"}:
            party_logs, escaped = resolve_party_action(
                self.party,
                self.enemy,
                action
            )
            round_logs.extend(party_logs)

            if escaped:
                self.finish("escaped")
                self.logs.extend(round_logs)
                return round_logs

            if self.enemy.is_alive():
                round_logs.extend(
                    enemy_attack(enemy_target, self.enemy)
                )

        else:
            actor = action.get("actor")

            if actor is None:
                return ["No actor selected."]

            guarded_actor = None

            if action["type"] == "guard":
                guarded_actor = actor

            if actor_goes_first(actor, self.enemy):
                round_logs.append(f"{actor.name} acts first.")

                party_logs, escaped = resolve_party_action(
                    self.party,
                    self.enemy,
                    action
                )
                round_logs.extend(party_logs)

                if escaped:
                    self.finish("escaped")
                    self.logs.extend(round_logs)
                    return round_logs

                if self.enemy.is_alive():
                    guard_result = None

                    if guarded_actor == enemy_target:
                        guard_result = "perfect_guard"

                    round_logs.extend(
                        enemy_attack(enemy_target, self.enemy, guard_result)
                    )

            else:
                round_logs.append("Enemy acts first.")

                guard_result = None

                if guarded_actor == enemy_target:
                    guard_result = "partial_guard"

                round_logs.extend(
                    enemy_attack(enemy_target, self.enemy, guard_result)
                )

                if actor.is_alive() and not actor.is_unconscious():
                    party_logs, escaped = resolve_party_action(
                        self.party,
                        self.enemy,
                        action
                    )
                    round_logs.extend(party_logs)

                    if escaped:
                        self.finish("escaped")
                        self.logs.extend(round_logs)
                        return round_logs

                elif actor.is_unconscious():
                    round_logs.append(
                        f"{actor.name} is overwhelmed by pain before acting."
                    )

        for member in self.party.members:
            if member.is_alive() and member.is_unconscious():
                round_logs.extend(member.advance_unconscious_turn())

        if not self.enemy.is_alive():
            round_logs.append(f"The party defeated {self.enemy.name}.")
            self.finish("victory")

        elif self.party.is_defeated():
            round_logs.append("The party was defeated.")
            self.finish("defeat")

        else:
            self.enemy.choose_intent()

        self.logs.extend(round_logs)
        return round_logs

    def finish(self, outcome):
        self.finished = True
        self.result = make_combat_result(
            outcome=outcome,
            rounds=self.rounds,
            enemy_start_hp=self.enemy_start_hp,
            enemy=self.enemy
        )

    def get_latest_logs(self, limit=8):
        return self.logs[-limit:]

    def get_enemy_parts(self):
        return list(self.enemy.body_parts.items())

    def get_alive_party_members(self):
        return self.party.get_alive_members()