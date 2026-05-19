"""Run many games to compare strategies head-to-head."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from guayabita import GameConfig, PlayerSpec, SimulationEngine
from guayabita.metrics import average_pool_evolution, format_summary, per_strategy_summary
from guayabita.strategies import (
    AggressiveStrategy,
    ConservativeStrategy,
    MartingaleStrategy,
    ProbabilityStrategy,
    RandomStrategy,
    AllInStrategy,
)


def build_specs() -> list[PlayerSpec]:
    return [
        PlayerSpec(1, ConservativeStrategy()),
        PlayerSpec(2, AggressiveStrategy(stack_fraction=0.20)),
        PlayerSpec(3, RandomStrategy()),
        PlayerSpec(4, MartingaleStrategy(base_units=1, max_doublings=5)),
        PlayerSpec(5, ProbabilityStrategy(max_fraction=0.20)),
        PlayerSpec(6, AllInStrategy()),
    ]


def main() -> None:
    config = GameConfig(
        case=100,
        initial_stack=10_000,
        ante_units=1,
        max_rounds=1000,
        seed=18,
    )
    engine = SimulationEngine(build_specs(), config, master_seed=42)
    sim = engine.run(n_games=500)

    print(format_summary(per_strategy_summary(sim)))

    pool_avg = average_pool_evolution(sim)
    if pool_avg:
        sample_pts = [0, len(pool_avg) // 4, len(pool_avg) // 2, 3 * len(pool_avg) // 4, len(pool_avg) - 1]
        print("\navg pool at sampled rounds:")
        for t in sample_pts:
            print(f"  round {t:>4}: {pool_avg[t]:.1f}")


if __name__ == "__main__":
    main()
