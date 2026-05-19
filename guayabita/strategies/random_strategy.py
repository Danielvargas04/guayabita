from __future__ import annotations

from .base import Strategy, StrategyContext


class RandomStrategy(Strategy):
    """Bet a uniformly random of 'case' and pool amount."""

    name = "random"

    def decide_bet(self, context: StrategyContext) -> int:
        return context.rng.randint(context.case, context.pool)
