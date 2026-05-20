"""Run many games to compare strategies head-to-head."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from guayabita import GameConfig, PlayerSpec, SimulationEngine
from guayabita.metrics import average_pool_evolution, format_summary, per_strategy_summary, stack_evolution, pool_evolution
from guayabita.strategies import (
    AggressiveStrategy,
    ConservativeStrategy,
    MartingaleStrategy,
    ProbabilityStrategy,
    RandomStrategy,
    AllInStrategy,
    ManuelStrategy,
    ManuelStrategy_2,
    BadBunny,
    WilchesStrategy,
    BeltroxStrategy,    
    SnowballStrategy,
)


def build_specs() -> list[PlayerSpec]:
    return [
        PlayerSpec(1, ConservativeStrategy()),
        PlayerSpec(2, AggressiveStrategy(stack_fraction=0.20)),
        PlayerSpec(3, RandomStrategy()),
        PlayerSpec(4, MartingaleStrategy(base_units=1, max_doublings=5)),
        PlayerSpec(5, ProbabilityStrategy(max_fraction=0.20)),
        PlayerSpec(6, AllInStrategy()),
        PlayerSpec(7, ManuelStrategy()),
        PlayerSpec(8, ManuelStrategy_2()),
        PlayerSpec(9, BadBunny()),
        PlayerSpec(10, WilchesStrategy()),
        PlayerSpec(11, BeltroxStrategy()),
        PlayerSpec(12, SnowballStrategy()),
    ]

import argparse
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Export results to CSV")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    config = GameConfig(
        case=200,
        initial_stack=20_000,
        ante_units=1,
        max_rounds=5000,
        seed=18,
    )
    engine = SimulationEngine(build_specs(), config, master_seed=18)
    sim = engine.run(n_games=1000)

    print(format_summary(per_strategy_summary(sim)))

    pool_avg = average_pool_evolution(sim)
    if pool_avg:
        sample_pts = [0, len(pool_avg) // 4, len(pool_avg) // 2, 3 * len(pool_avg) // 4, len(pool_avg) - 1]
        print("\navg pool at sampled rounds:")
        for t in sample_pts:
            print(f"  round {t:>4}: {pool_avg[t]:.1f}")
    #--------------------------------------------------------
    #---------------------EXPORT RESULTS---------------------
    #--------------------------------------------------------
    if args.export:
        import pandas as pd
        import pathlib
        path = pathlib.Path("results")
        path.mkdir(parents=True, exist_ok=True)
        stacks_evolution = stack_evolution(sim)
        pools_evolution = pool_evolution(sim)

        i = 0
        for stacks, pool in zip(stacks_evolution, pools_evolution):
            stacks_df = pd.DataFrame(stacks)
            pool_df = pd.DataFrame({"pool": pool})
            df = pd.concat([pool_df, stacks_df], axis=1)
            df.to_csv(path / f"game_{i}.csv", index=False)
            i += 1
        print(f"Results exported to {i} games") 


if __name__ == "__main__":
    main()
