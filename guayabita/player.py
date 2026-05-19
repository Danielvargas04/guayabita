"""Player entity.

Players are passive data holders + strategy delegates; the `Game`
mutates their stack and active flag. All betting decisions are routed
through `self.strategy.decide_bet(...)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .strategies.base import Strategy, StrategyContext


@dataclass
class Player:
    id: int
    stack: int
    strategy: "Strategy"
    active: bool = True
    eliminated_round: int = -1
    stack_history: List[int] = field(default_factory=list)

    def can_afford(self, min_stack: int) -> bool:
        return self.stack >= min_stack

    def deactivate(self, round_index: int) -> None:
        self.active = False
        self.eliminated_round = round_index

    def decide_bet(self, context: "StrategyContext") -> int:
        return int(self.strategy.place_bet(context))

    def record_stack(self) -> None:
        self.stack_history.append(self.stack)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Player(id={self.id}, stack={self.stack}, active={self.active}, strategy={self.strategy.name})"
