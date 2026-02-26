from shared_realms.engine import SimulationEngine, default_players
from shared_realms.models import Player, Role


def test_tick_advances_world_and_generates_feed():
    engine = SimulationEngine(list(default_players()), rng_seed=1)
    engine.tick()
    snap = engine.snapshot()
    assert snap["world"]["tick"] == 1
    assert len(snap["feed"]) >= 1


def test_npc_bots_cover_offline_role():
    players = [
        Player("f", Role.FARMER, online=False),
        Player("h", Role.HERO),
        Player("g", Role.ROYAL_GUARD),
        Player("b", Role.BOUNTY_HUNTER),
        Player("m", Role.MAGE),
    ]
    engine = SimulationEngine(players, rng_seed=2)
    food_before = engine.world.food_supply
    engine.tick()
    assert engine.world.food_supply > food_before
    assert any("NPC bot covered role: farmer" in n.message for n in engine.world.notifications)


def test_role_switch_requirements():
    player = Player("switcher", Role.HERO)
    player.milestones.add("seasonal_milestone")
    player.add_item("astral_focus", 1)
    engine = SimulationEngine([player], rng_seed=3)
    engine.world.season = "autumn"
    assert engine.can_switch_role(player, Role.MAGE)


def test_marketplace_and_direct_trade():
    seller = Player("seller", Role.FARMER)
    buyer = Player("buyer", Role.HERO)
    seller.add_item("food", 5)
    engine = SimulationEngine([seller, buyer], rng_seed=4)

    ok = engine.marketplace_buy(buyer, "food", quantity=2)
    assert ok
    assert buyer.inventory["food"] >= 2

    before_seller = seller.currency
    before_buyer = buyer.currency
    traded = engine.direct_trade(seller, buyer, "food", quantity=1, price=12)
    assert traded
    assert seller.currency == before_seller + 12
    assert buyer.currency == before_buyer - 12
