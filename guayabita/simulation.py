"""Batch simulation engine.

Runs many independent games with deterministic per-game seeds and
collects `GameResult` objects for downstream metric / ML use.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import List, Optional, Sequence

from .config import GameConfig, PlayerSpec
from .game import Game
from .logging_utils import GameLogger
from .results import GameResult, SimulationResult


class SimulationEngine:
    def __init__(
        self,
        player_specs: Sequence[PlayerSpec],
        base_config: GameConfig,
        master_seed: Optional[int] = None,
    ) -> None:
        self.player_specs = list(player_specs)
        self.base_config = base_config
        self.master_seed = master_seed

    def _seeds(self, n: int) -> List[int]:
        rng = random.Random(self.master_seed)
        return [rng.randrange(2**31) for _ in range(n)]

    def run(self, n_games: int, verbose: bool = False) -> SimulationResult:
        seeds = self._seeds(n_games)
        results: List[GameResult] = []
        for i, seed in enumerate(seeds, start=1):
            print(f"Running game {i} of {n_games}")
            cfg = replace(self.base_config, seed=seed, verbose=verbose)
            game = Game(self.player_specs, cfg, logger=GameLogger(enabled=verbose))
            results.append(game.run())
        return SimulationResult(
            n_games=n_games,
            game_results=results,
            strategy_by_player={s.player_id: s.strategy.name for s in self.player_specs},
        )
