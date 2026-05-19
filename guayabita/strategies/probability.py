"""Probability-aware strategy.

Given first roll `r` (2..5), P(second_roll > r) for a fair 6-sided die:

    r=2 -> 4/6,  r=3 -> 3/6,  r=4 -> 2/6,  r=5 -> 1/6

The strategy bets proportionally to that edge: large bet when the odds
favor the player, minimum bet (or pass-equivalent) when they don't.
"""

from __future__ import annotations

from .base import Strategy, StrategyContext

WIN_PROB = {2: 4 / 6, 3: 3 / 6, 4: 2 / 6, 5: 1 / 6}


class ProbabilityStrategy(Strategy):
    name = "probability"

    def __init__(self, max_fraction: float = 0.20, threshold: float = 0.5) -> None:
        super().__init__()
        if not 0 < max_fraction <= 1:
            raise ValueError("max_fraction must be in (0, 1]")
        self.max_fraction = max_fraction
        self.threshold = threshold

    def decide_bet(self, context: StrategyContext) -> int:
        p = WIN_PROB.get(context.first_roll, 0.0)
        if p < self.threshold:
            return context.case
        scale = (p - self.threshold) / (1.0 - self.threshold) if self.threshold < 1 else 1.0
        target = context.player_stack * self.max_fraction * scale
        return max(context.case, int(target))
