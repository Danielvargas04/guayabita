"""Strategy base classes.

A `Strategy` is a stateful policy. The engine hands it a fully
populated `StrategyContext` and expects an integer bet >= 0.

The base class wraps every `decide_bet` result through `place_bet`,
which snaps the amount down to the nearest multiple of `case` (real
Guayabita only accepts bets in whole `case` units). Concrete
strategies therefore never need to worry about rounding.

The engine still clamps the final value against pool / stack, so
strategies also never need to defend against illegal values.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class StrategyContext:
    """Read-only snapshot delivered to a strategy each decision."""

    round_index: int
    player_id: int
    player_stack: int
    initial_stack: int
    pool: int
    case: int
    first_roll: int
    rng: random.Random
    own_history: List["BetOutcome"] = field(default_factory=list)


@dataclass(frozen=True)
class BetOutcome:
    round_index: int
    first_roll: int
    second_roll: int
    bet: int
    won: bool


class Strategy(ABC):
    """Base class for all betting strategies."""

    name: str = "base"

    def __init__(self) -> None:
        self._history: List[BetOutcome] = []

    @abstractmethod
    def decide_bet(self, context: StrategyContext) -> int:
        """Return desired bet amount (engine clamps to legal range)."""

    def place_bet(self, context: StrategyContext) -> int:
        """Final bet seen by the engine: `decide_bet` snapped to `case` units.

        bet = (raw // case) * case, always >= 0.
        Concrete strategies should NOT override this; override
        `decide_bet` instead.
        """
        raw = int(self.decide_bet(context))
        if raw <= 0 or context.case <= 0:
            return 0
        return (raw // context.case) * context.case

    def observe(self, outcome: BetOutcome) -> None:
        """Hook invoked after the engine resolves the second roll."""
        self._history.append(outcome)

    def reset(self) -> None:
        """Reset internal state between games (engine calls this)."""
        self._history.clear()

    @property
    def history(self) -> List[BetOutcome]:
        return self._history
