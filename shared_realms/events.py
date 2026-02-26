from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class Event:
    name: str
    description: str
    food_delta: int = 0
    threat_delta: int = 0
    instability_delta: int = 0
    defense_delta: int = 0


EVENT_TABLE = [
    Event("harvest_blossom", "A bountiful harvest improves food supply.", food_delta=150),
    Event("drought", "Drought damages crops and strains settlements.", food_delta=-220),
    Event("bandit_raid", "Bandits attack caravans and roads.", threat_delta=30),
    Event("monster_rampage", "An undefeatable monster ravages the frontier.", food_delta=-80, threat_delta=45),
    Event("arcane_storm", "A magical calamity distorts nearby realms.", instability_delta=40),
    Event("guard_drill", "Royal guard drills raise preparedness.", defense_delta=20, threat_delta=-10),
]


def roll_event(rng: random.Random) -> Event:
    return rng.choice(EVENT_TABLE)
