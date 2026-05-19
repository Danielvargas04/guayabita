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
)


def main() -> None:
    specs = [
        PlayerSpec(1, ConservativeStrategy()),
        PlayerSpec(2, AggressiveStrategy(stack_fraction=0.15)),
        PlayerSpec(3, MartingaleStrategy(base_units=1, max_doublings=5)),
        PlayerSpec(4, ProbabilityStrategy(max_fraction=0.20)),
        PlayerSpec(5, AllInStrategy()),
    ]
    config = GameConfig(
        case=100,
        initial_stack=5_000,
        ante_units=1,
        max_rounds=50,
        seed=18,
        verbose=True,
    )
    result = Game(specs, config).run()
    print(f"\nwinner={result.winner_id}  rounds={result.rounds_played}  invariant_ok={result.invariant_ok}")
    print(f"final_stacks={result.final_stacks}  final_pool={result.final_pool}")
    print(f"money: initial={result.initial_total_money}  final={result.final_total_money}")


if __name__ == "__main__":
    main()
