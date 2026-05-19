"""Entry point.

Tiny demo: spin up a 3-player game with mixed strategies and print
high-level results. For deeper experiments see `examples/`.
"""

from __future__ import annotations

from guayabita import GameConfig, PlayerSpec, SimulationEngine
from guayabita.metrics import format_summary, per_strategy_summary
from guayabita.strategies import (
    AggressiveStrategy,
    ConservativeStrategy,
    MartingaleStrategy,
)


def main() -> None:
    specs = [
        PlayerSpec(1, ConservativeStrategy()),
        PlayerSpec(2, AggressiveStrategy(stack_fraction=0.2)),
        PlayerSpec(3, MartingaleStrategy(base_units=1, max_doublings=5)),
    ]
    config = GameConfig(
        case=100,
        initial_stack=30_000,
        ante_units=1,
        max_rounds=300,
    )
    sim = SimulationEngine(specs, config, master_seed=18).run(n_games=100)
    print(format_summary(per_strategy_summary(sim)))


if __name__ == "__main__":
    main()
