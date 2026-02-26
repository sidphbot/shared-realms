from __future__ import annotations

import json

from .engine import SimulationEngine, default_players


def main() -> None:
    engine = SimulationEngine(list(default_players()))
    for _ in range(12):
        engine.tick()
    print(json.dumps(engine.snapshot(), indent=2))


if __name__ == "__main__":
    main()
