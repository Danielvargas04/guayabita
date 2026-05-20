from __future__ import annotations

from .base import Strategy, StrategyContext


class ManuelStrategy(Strategy):
    """Manuel's strategy."""

    name = "manuel"

    def decide_bet(self, context: StrategyContext) -> int:
        if context.first_roll == 2:
            return context.pool
        else:
            return context.case
