from dataclasses import dataclass, field


@dataclass
class EncounterReward:
    exp: int = 0
    gold: int = 0
    loot: list = field(default_factory=list)