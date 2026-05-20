from __future__ import annotations

from .base import Strategy, StrategyContext

class SnowballStrategy(Strategy):
    """Snowball's strategy."""

    name = "snowball"

    def decide_bet(self, context: StrategyContext) -> int:
        if context.player_stack > context.initial_stack:
            "winner streak"
            if context.first_roll in (2,3):
                return context.pool
            elif context.first_roll == 4:
                return context.player_stack*0.05
            else:
                return context.case
        else:
            "loser streak"
            if context.first_roll ==2:
                return context.player_stack*0.8
            else:
                return context.case