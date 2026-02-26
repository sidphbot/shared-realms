from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class Role(str, Enum):
    FARMER = "farmer"
    HERO = "hero"
    ROYAL_GUARD = "royal_guard"
    BOUNTY_HUNTER = "bounty_hunter"
    MAGE = "mage"


@dataclass
class Player:
    name: str
    role: Role
    level: int = 1
    currency: int = 100
    inventory: Dict[str, int] = field(default_factory=dict)
    milestones: Set[str] = field(default_factory=set)
    online: bool = True

    def add_item(self, item: str, qty: int = 1) -> None:
        self.inventory[item] = self.inventory.get(item, 0) + qty

    def remove_item(self, item: str, qty: int = 1) -> bool:
        if self.inventory.get(item, 0) < qty:
            return False
        self.inventory[item] -= qty
        if self.inventory[item] == 0:
            self.inventory.pop(item)
        return True


@dataclass
class Notification:
    tick: int
    category: str
    message: str


@dataclass
class WorldState:
    tick: int = 0
    day: int = 1
    season: str = "spring"
    food_supply: int = 1000
    monster_threat: int = 20
    magical_instability: int = 15
    defense_index: int = 20
    narrative_phase: str = "calm"
    notifications: List[Notification] = field(default_factory=list)

    def push(self, category: str, message: str) -> None:
        self.notifications.append(Notification(self.tick, category, message))
