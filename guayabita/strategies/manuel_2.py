from __future__ import annotations

from .base import Strategy, StrategyContext


class ManuelStrategy_2(Strategy):
    """Manuel's strategy."""

    name = "manuel_2"

    def decide_bet(self, context: StrategyContext) -> int:
        if context.first_roll == 2 or context.first_roll == 3:
            return context.pool
        else:
            return context.case
