from __future__ import annotations

from .base import Strategy, StrategyContext


class WilchesStrategy(Strategy):
    """Wilches's strategy."""

    name = "wilches"

    def decide_bet(self, context: StrategyContext) -> int:
        if context.first_roll == 2:
            return context.pool
        elif context.first_roll == 3:
            if context.player_stack>=context.pool:
                return context.pool
            else:
                return context.player_stack*0.3
        elif context.first_roll == 4:
            if context.player_stack >= context.pool:
                return context.player_stack*0.1
            else:
                return context.case
        elif context.first_roll == 5:
            return context.case
        else:
            return context.case