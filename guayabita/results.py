"""Result / telemetry dataclasses.

Kept dependency-free so they can be serialized to JSON, dumped to
pandas, or pickled for ML pipelines without round-tripping through
business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TurnOutcome:
    round_index: int
    player_id: int
    first_roll: int
    second_roll: Optional[int]
    action: str  # "win6", "lose1", "bet_win", "bet_lose"
    bet: int
    delta_stack: int
    delta_pool: int
    stack_after: int
    pool_after: int


@dataclass
class RoundSnapshot:
    round_index: int
    pool: int
    stacks: Dict[int, int]
    active_players: List[int]
    turns: List[TurnOutcome] = field(default_factory=list)


@dataclass
class GameResult:
    seed: Optional[int]
    rounds_played: int
    winner_id: Optional[int]
    final_pool: int
    final_stacks: Dict[int, int]
    strategy_by_player: Dict[int, str]
    elimination_round: Dict[int, int]
    pool_evolution: List[int]
    stack_evolution: Dict[int, List[int]]
    invariant_ok: bool
    initial_total_money: int
    final_total_money: int

    @property
    def reached_max_rounds(self) -> bool:
        return self.winner_id is None


@dataclass
class SimulationResult:
    """Aggregated result over many `GameResult` instances."""

    n_games: int
    game_results: List[GameResult]
    strategy_by_player: Dict[int, str]

    def winners(self) -> List[Optional[int]]:
        return [g.winner_id for g in self.game_results]

    def final_stacks_by_player(self) -> Dict[int, List[int]]:
        out: Dict[int, List[int]] = {pid: [] for pid in self.strategy_by_player}
        for g in self.game_results:
            for pid, stack in g.final_stacks.items():
                out[pid].append(stack)
        return out
