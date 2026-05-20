from __future__ import annotations

from .base import Strategy, StrategyContext


class BeltroxStrategy(Strategy):
    """Beltrox's strategy."""

    name = "Beltrox"

    def decide_bet(self, context: StrategyContext) -> int:
        
        if context.first_roll == 2:
            if context.player_stack>=context.pool:
                return 3.5/6*context.pool
            else:
                return 4/6*context.pool
        elif context.first_roll == 3:
            if context.player_stack>=context.pool:
                return 2.5/6*context.pool
            else:
                return 3/6*context.case
        elif context.first_roll == 4:
            if context.player_stack >= context.pool:
                return 1.5/6*context.player_stack*0.1
            else:
                return 2/6*context.case
        elif context.first_roll == 5:
            return context.case
        else:
            return context.case