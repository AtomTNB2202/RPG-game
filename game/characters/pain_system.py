# game/pain_system.py

class PainSystem:
    def __init__(self, config):
        self.max_pain = config.get("max_pain", 100)
        self.pain = config.get("starting_pain", 0)

        self.unconscious_turns = 0
        self.unconscious_duration = config.get("unconscious_duration", 1)
        self.recover_to_percent = config.get("recover_to_percent", 0.75)

        self.stages = config["stages"]

    def get_percent(self):
        if self.max_pain <= 0:
            return 0.0

        return self.pain / self.max_pain

    def is_unconscious(self):
        return self.unconscious_turns > 0

    def get_stage_name(self):
        if self.is_unconscious():
            return "unconscious"

        pain_percent = self.get_percent()

        selected_stage = "stable"
        selected_min = -1

        for stage_name, stage_data in self.stages.items():
            min_percent = stage_data["min_percent"]

            if pain_percent >= min_percent and min_percent > selected_min:
                selected_stage = stage_name
                selected_min = min_percent

        return selected_stage

    def get_effect(self):
        return self.stages[self.get_stage_name()]

    def add_pain(self, amount):
        if amount <= 0:
            return 0

        old_pain = self.pain
        self.pain = min(self.max_pain, self.pain + amount)
        actual_gain = self.pain - old_pain

        if self.get_percent() >= 1.0:
            self.trigger_unconscious()

        return actual_gain

    def reduce_pain(self, amount):
        if amount <= 0:
            return 0

        old_pain = self.pain
        self.pain = max(0, self.pain - amount)

        return old_pain - self.pain

    def trigger_unconscious(self, turns=None):
        self.pain = self.max_pain

        if turns is None:
            turns = self.unconscious_duration

        self.unconscious_turns = max(self.unconscious_turns, turns)

    def advance_unconscious_turn(self):
        logs = []

        if not self.is_unconscious():
            return logs

        self.unconscious_turns = max(0, self.unconscious_turns - 1)

        if self.unconscious_turns == 0:
            self.pain = int(self.max_pain * self.recover_to_percent)
            logs.append("is able to fight again, but still has high pain.")

        return logs