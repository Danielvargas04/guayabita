"""Configuration objects for games and player specs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .strategies.base import Strategy


@dataclass(frozen=True)
class GameConfig:
    """Static configuration for a single Guayabita game.

    Attributes:
        case: Base wager unit (the original "case" in tools.py).
        initial_stack: Starting stack handed to every player.
        ante_units: How many `case` units each active player contributes
            to the pool at game start AND whenever the pool drains to 0.
            The pool itself always starts empty; it is funded purely by
            antes (matches real Guayabita).
        max_rounds: Hard cap on rounds; game ends earlier if only one
            active player remains.
        min_active_stack: Stack threshold under which a player is marked
            inactive (cannot afford to keep playing). Defaults to
            `(ante_units + 1) * case` so a player can always cover at
            least one ante and one minimum bet.
        allow_pool_overdraw: If False, payouts from pool are clamped to
            current pool balance (recommended; keeps accounting honest).
        seed: Master seed for the game RNG. `None` => non-deterministic.
        verbose: Emit per-turn logging when True.
    """

    case: int = 100
    initial_stack: int = 30_000
    ante_units: int = 1
    max_rounds: int = 500
    min_active_stack: Optional[int] = None
    allow_pool_overdraw: bool = False
    seed: Optional[int] = None
    verbose: bool = False

    def ante_amount(self) -> int:
        return max(0, self.ante_units) * self.case

    def effective_min_stack(self) -> int:
        if self.min_active_stack is not None:
            return self.min_active_stack
        return self.ante_amount() + self.case


@dataclass
class PlayerSpec:
    """Declarative description of a player to be instantiated by the engine."""

    player_id: int
    strategy: Strategy
    initial_stack: Optional[int] = None
    label: str = field(default="")

    def display_name(self) -> str:
        return self.label or f"P{self.player_id}({self.strategy.name})"
