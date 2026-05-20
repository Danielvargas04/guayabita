"""Run a single verbose Guayabita game between 4 strategies."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from guayabita import Game, GameConfig, PlayerSpec
from guayabita.strategies import (
    AggressiveStrategy,
    ConservativeStrategy,
    MartingaleStrategy,
    ProbabilityStrategy,
    AllInStrategy,
    ManuelStrategy, 
    ManuelStrategy_2,
    BadBunny,
    WilchesStrategy,
    SnowballStrategy,
)   


def main() -> None:
    specs = [
        PlayerSpec(1, ConservativeStrategy()),
        #PlayerSpec(2, AggressiveStrategy(stack_fraction=0.15)),
        #PlayerSpec(3, MartingaleStrategy(base_units=1, max_doublings=5)),
        #PlayerSpec(4, ProbabilityStrategy(max_fraction=0.20)),
        #PlayerSpec(5, AllInStrategy()),
        #PlayerSpec(6, ManuelStrategy()),
        #PlayerSpec(7, ManuelStrategy_2()),
        #PlayerSpec(8, BadBunny()),
        #PlayerSpec(9, WilchesStrategy()),
        PlayerSpec(10, SnowballStrategy()),
    ]
    config = GameConfig(
        case=200,
        initial_stack=10_000,
        ante_units=1,
        max_rounds=50,
        seed=42,
        verbose=True,
    )
    result = Game(specs, config).run()
    print(f"\nwinner={result.winner_id}  rounds={result.rounds_played}  invariant_ok={result.invariant_ok}")
    print(f"final_stacks={result.final_stacks}  final_pool={result.final_pool}")
    print(f"money: initial={result.initial_total_money}  final={result.final_total_money}")

    export = True
    if export:
        import pandas as pd
        stacks = result.stack_evolution
        stacks_df = pd.DataFrame(stacks)
        pool_evolution = result.pool_evolution
        pool_df=pd.DataFrame({
            "pool": pool_evolution,
        })
        df = pd.concat([pool_df, stacks_df], axis=1)
        df.to_csv("results.csv", index=False)
        print(f"Results exported to results.csv")   

if __name__ == "__main__":
    main()
