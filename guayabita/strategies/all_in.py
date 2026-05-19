from __future__ import annotations

from .base import Strategy, StrategyContext


class AllInStrategy(Strategy):
    """Always bet the all pool amount."""

    name = "all_in"

    def decide_bet(self, context: StrategyContext) -> int:
        return context.pool
