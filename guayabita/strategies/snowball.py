from __future__ import annotations

from .base import Strategy, StrategyContext

class SnowballStrategy(Strategy):
    """Snowball's strategy."""

    name = "snowball"

    def decide_bet(self, context: StrategyContext) -> int:
        if context.player_stack*2 > context.initial_stack:
            "winner streak"
            if context.first_roll == (2):
                return context.pool
            elif context.first_roll == 3:
                return context.player_stack*0.4
            elif context.first_roll == 4:
                return context.player_stack*0.05
            else:
                return context.case
        else:
            "loser streak"
            if context.first_roll == 2:
                return context.player_stack
            else:
                return context.case