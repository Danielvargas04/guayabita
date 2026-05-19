from __future__ import annotations

from .base import Strategy, StrategyContext


class AggressiveStrategy(Strategy):
    """Bet a fixed fraction of the current stack (default 25%)."""

    name = "aggressive"

    def __init__(self, stack_fraction: float = 0.25) -> None:
        super().__init__()
        if not 0 < stack_fraction <= 1:
            raise ValueError("stack_fraction must be in (0, 1]")
        self.stack_fraction = stack_fraction

    def decide_bet(self, context: StrategyContext) -> int:
        return max(context.case, int(context.player_stack * self.stack_fraction))
