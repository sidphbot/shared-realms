from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, Iterable, List

from .economy import Economy
from .events import roll_event
from .models import Player, Role, WorldState


ROLE_ARTIFACT = {
    Role.FARMER: "seed_crown",
    Role.HERO: "valor_emblem",
    Role.ROYAL_GUARD: "oath_seal",
    Role.BOUNTY_HUNTER: "beast_trophy",
    Role.MAGE: "astral_focus",
}


@dataclass
class SimulationEngine:
    players: List[Player]
    rng_seed: int = 42
    world: WorldState = field(default_factory=WorldState)
    economy: Economy = field(default_factory=Economy)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.rng_seed)

    def tick(self) -> None:
        self.world.tick += 1
        if self.world.tick % 4 == 0:
            self.world.day += 1
        if self.world.day in (31, 61, 91):
            self._advance_season()

        self._apply_role_outputs()

        event = roll_event(self.rng)
        self.world.food_supply = max(100, self.world.food_supply + event.food_delta)
        self.world.monster_threat = max(0, self.world.monster_threat + event.threat_delta - self.world.defense_index // 20)
        self.world.magical_instability = max(0, self.world.magical_instability + event.instability_delta)
        self.world.defense_index = max(0, self.world.defense_index + event.defense_delta)
        self.world.push("event", event.description)

        self._npc_fill_offline_roles()
        self.economy.update(self.world.food_supply, self.world.monster_threat, self.world.magical_instability)
        self._update_narrative()
        self._guardrail_notifications()

    def _advance_season(self) -> None:
        seasons = ["spring", "summer", "autumn", "winter"]
        idx = seasons.index(self.world.season)
        self.world.season = seasons[(idx + 1) % len(seasons)]
        self.world.push("season", f"Season changed to {self.world.season}.")

    def _apply_role_outputs(self) -> None:
        for player in self.players:
            if player.role == Role.FARMER:
                produced = 40 + player.level * 4
                self.world.food_supply += produced
                player.add_item("food", 3)
            elif player.role == Role.HERO:
                self.world.monster_threat = max(0, self.world.monster_threat - (3 + player.level))
                player.add_item("valor_emblem", 1)
            elif player.role == Role.ROYAL_GUARD:
                self.world.defense_index += 5 + player.level
                player.add_item("oath_seal", 1)
            elif player.role == Role.BOUNTY_HUNTER:
                self.world.monster_threat = max(0, self.world.monster_threat - (2 + player.level))
                player.add_item("beast_trophy", 1)
            elif player.role == Role.MAGE:
                self.world.magical_instability = max(0, self.world.magical_instability - (2 + player.level))
                player.add_item("astral_focus", 1)

    def _npc_fill_offline_roles(self) -> None:
        online_roles = {p.role for p in self.players if p.online}
        for role in Role:
            if role not in online_roles:
                self._simulate_npc_role(role)
                self.world.push("npc", f"NPC bot covered role: {role.value}.")

    def _simulate_npc_role(self, role: Role) -> None:
        if role == Role.FARMER:
            self.world.food_supply += 30
        elif role in (Role.HERO, Role.BOUNTY_HUNTER):
            self.world.monster_threat = max(0, self.world.monster_threat - 3)
        elif role == Role.ROYAL_GUARD:
            self.world.defense_index += 4
        elif role == Role.MAGE:
            self.world.magical_instability = max(0, self.world.magical_instability - 3)

    def _update_narrative(self) -> None:
        if self.world.monster_threat > 80 or self.world.magical_instability > 80:
            phase = "crisis"
        elif self.world.monster_threat > 40 or self.world.magical_instability > 40:
            phase = "rising_tension"
        else:
            phase = "calm"

        if phase != self.world.narrative_phase:
            self.world.narrative_phase = phase
            self.world.push("story", f"Narrative shifted to {phase}.")

    def _guardrail_notifications(self) -> None:
        alerts = self.economy.guardrails()
        for item, status in alerts.items():
            self.world.push("economy", f"Guardrail alert on {item}: {status}")

    def can_switch_role(self, player: Player, target_role: Role) -> bool:
        required_artifact = ROLE_ARTIFACT[target_role]
        has_artifact = player.inventory.get(required_artifact, 0) > 0
        has_milestone = "seasonal_milestone" in player.milestones
        valid_window = self.world.season in {"autumn", "winter"}
        return has_artifact and has_milestone and valid_window

    def marketplace_buy(self, player: Player, item: str, quantity: int = 1) -> bool:
        price = self.economy.prices.get(item)
        if price is None:
            return False
        total = price * quantity
        if player.currency < total:
            return False
        player.currency -= total
        player.add_item(item, quantity)
        return True

    def direct_trade(self, seller: Player, buyer: Player, item: str, quantity: int, price: int) -> bool:
        if buyer.currency < price:
            return False
        if not seller.remove_item(item, quantity):
            return False
        buyer.currency -= price
        seller.currency += price
        buyer.add_item(item, quantity)
        return True

    def snapshot(self) -> Dict[str, object]:
        return {
            "world": {
                "tick": self.world.tick,
                "day": self.world.day,
                "season": self.world.season,
                "food_supply": self.world.food_supply,
                "monster_threat": self.world.monster_threat,
                "magical_instability": self.world.magical_instability,
                "defense_index": self.world.defense_index,
                "narrative_phase": self.world.narrative_phase,
            },
            "economy": dict(self.economy.prices),
            "players": [
                {
                    "name": p.name,
                    "role": p.role.value,
                    "currency": p.currency,
                    "inventory": dict(p.inventory),
                }
                for p in self.players
            ],
            "feed": [f"[{n.tick}] {n.category}: {n.message}" for n in self.world.notifications[-10:]],
        }


def default_players() -> Iterable[Player]:
    return [
        Player("Ari", Role.FARMER, level=3),
        Player("Bex", Role.HERO, level=4),
        Player("Cato", Role.ROYAL_GUARD, level=2),
        Player("Dara", Role.BOUNTY_HUNTER, level=3),
        Player("Ena", Role.MAGE, level=5),
    ]
