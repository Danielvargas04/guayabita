from __future__ import annotations

from .base import Strategy, StrategyContext


class ConservativeStrategy(Strategy):
    """Always bet the minimum unit (`case`)."""

    name = "conservative"

    def __init__(self, multiplier: float = 1.0) -> None:
        super().__init__()
        self.multiplier = multiplier

    def decide_bet(self, context: StrategyContext) -> int:
        return max(1, int(context.case * self.multiplier))
