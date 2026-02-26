from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


BASELINE_PRICES = {
    "food": 10,
    "ore": 20,
    "mana_crystal": 35,
    "relic": 50,
    "military_supply": 25,
}


@dataclass
class Economy:
    prices: Dict[str, int] = field(default_factory=lambda: dict(BASELINE_PRICES))

    def update(self, food_supply: int, threat: int, instability: int) -> None:
        scarcity_factor = max(1, min(4, 2000 // max(1, food_supply)))
        self.prices["food"] = BASELINE_PRICES["food"] * scarcity_factor
        self.prices["military_supply"] = BASELINE_PRICES["military_supply"] + threat // 5
        self.prices["mana_crystal"] = BASELINE_PRICES["mana_crystal"] + instability // 4
        self.prices["relic"] = BASELINE_PRICES["relic"] + (threat + instability) // 8

    def guardrails(self) -> Dict[str, str]:
        alerts: Dict[str, str] = {}
        for item, price in self.prices.items():
            if price > BASELINE_PRICES[item] * 5:
                alerts[item] = "PRICE_SPIKE"
            elif price < max(1, BASELINE_PRICES[item] // 3):
                alerts[item] = "PRICE_COLLAPSE"
        return alerts
