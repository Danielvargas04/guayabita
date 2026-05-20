####
from __future__ import annotations

from .base import Strategy, StrategyContext

class BadBunny(Strategy):
    name = "BadBunny"

    def decide_bet(self, context: StrategyContext) -> int:
        FR = context.first_roll
        if context.pool < context.player_stack:
            if FR in (2, 3):
                return context.pool

            return context.case
        if context.pool >= context.player_stack:
            if FR == 2:
                return context.pool//3
            else:
                return context.case
